"""
Workflow Manager

Enhanced session management system supporting multi-tool workflows,
tool chaining, and complex analysis sequences.
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from concurrent.futures import ThreadPoolExecutor

from .tool_adapters.base_adapter import ToolResult


class WorkflowStatus(Enum):
    """Workflow execution status"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Individual workflow step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    step_id: str
    tool_name: str
    target_path: Union[str, Path]
    arguments: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Step IDs this depends on
    condition: Optional[str] = None  # Condition to check before running
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 0

    # Runtime fields
    status: StepStatus = StepStatus.PENDING
    result: Optional[ToolResult] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_attempt: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = {
            'step_id': self.step_id,
            'tool_name': self.tool_name,
            'target_path': str(self.target_path),
            'arguments': self.arguments,
            'dependencies': self.dependencies,
            'condition': self.condition,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'error_message': self.error_message,
            'retry_attempt': self.retry_attempt,
        }
        if self.result:
            data['result'] = self.result.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        """Create from dictionary"""
        # Convert status back to enum
        data['status'] = StepStatus(data['status'])

        # Convert timestamps
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])

        # Convert result if present
        if 'result' in data:
            data['result'] = ToolResult.from_dict(data['result'])

        return cls(**data)

    def is_ready(self, completed_steps: Dict[str, WorkflowStep]) -> bool:
        """Check if this step is ready to run (all dependencies satisfied)"""
        for dep_id in self.dependencies:
            if dep_id not in completed_steps:
                return False
            if completed_steps[dep_id].status != StepStatus.COMPLETED:
                return False
        return True

    def should_retry(self) -> bool:
        """Check if step should be retried"""
        return (self.status == StepStatus.FAILED and
                self.retry_attempt < self.max_retries)

    def evaluate_condition(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition for running this step"""
        if not self.condition:
            return True

        try:
            # Simple condition evaluation (can be extended)
            if self.condition.startswith('result.'):
                # Check previous step results
                parts = self.condition.split('.')
                if len(parts) >= 3:
                    step_id = parts[1]
                    check_type = parts[2]

                    if step_id in context and isinstance(context[step_id], WorkflowStep):
                        step = context[step_id]
                        if check_type == 'success' and step.result:
                            return step.result.success
                        elif check_type == 'failed' and step.result:
                            return not step.result.success
                        elif check_type == 'issues_found' and step.result:
                            return len(step.result.issues) > 0

            return True
        except Exception:
            return False


@dataclass
class WorkflowSession:
    """Workflow session for multi-tool analysis sequences"""
    workflow_id: str
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'description': self.description,
            'steps': [step.to_dict() for step in self.steps],
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'current_step': self.current_step,
            'progress': self.progress,
            'error_message': self.error_message,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowSession':
        """Create from dictionary"""
        data_copy = data.copy()

        # Convert enums and timestamps
        data_copy['status'] = WorkflowStatus(data['status'])
        data_copy['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            data_copy['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data_copy['completed_at'] = datetime.fromisoformat(data['completed_at'])

        # Convert steps
        data_copy['steps'] = [WorkflowStep.from_dict(step) for step in data.get('steps', [])]

        return cls(**data_copy)

    def get_completed_steps(self) -> Dict[str, WorkflowStep]:
        """Get dictionary of completed steps"""
        return {
            step.step_id: step
            for step in self.steps
            if step.status == StepStatus.COMPLETED
        }

    def get_pending_steps(self) -> List[WorkflowStep]:
        """Get list of pending steps that are ready to run"""
        completed = self.get_completed_steps()
        return [
            step for step in self.steps
            if step.status == StepStatus.PENDING and step.is_ready(completed)
        ]

    def update_progress(self):
        """Update workflow progress based on completed steps"""
        if not self.steps:
            self.progress = 100.0 if self.status == WorkflowStatus.COMPLETED else 0.0
            return

        completed_count = sum(1 for step in self.steps if step.status == StepStatus.COMPLETED)
        self.progress = (completed_count / len(self.steps)) * 100.0

    def get_execution_time(self) -> Optional[timedelta]:
        """Get total execution time"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return datetime.now() - self.started_at
        return None


class WorkflowManager:
    """
    Manager for workflow sessions with tool chaining and dependency management
    """

    def __init__(self,
                 tool_registry: Dict[str, Any],
                 storage_path: str = "~/.mcp/workflows.json",
                 max_concurrent_steps: int = 2):
        """
        Initialize workflow manager

        Args:
            tool_registry: Dictionary mapping tool names to adapter instances
            storage_path: Path to store workflow sessions
            max_concurrent_steps: Maximum number of steps to run concurrently
        """
        self.tool_registry = tool_registry
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_concurrent_steps = max_concurrent_steps
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # In-memory storage
        self._workflows: Dict[str, WorkflowSession] = {}
        self._lock = threading.RLock()
        self._executors: Dict[str, ThreadPoolExecutor] = {}

        # Load existing workflows
        self._load_workflows()

    def _load_workflows(self):
        """Load workflows from persistent storage"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for workflow_data in data.get('workflows', []):
                        workflow = WorkflowSession.from_dict(workflow_data)
                        self._workflows[workflow.workflow_id] = workflow
        except Exception as e:
            self.logger.warning(f"Failed to load workflows: {e}")

    def _save_workflows(self):
        """Save workflows to persistent storage"""
        try:
            with self._lock:
                data = {
                    'workflows': [w.to_dict() for w in self._workflows.values()],
                    'last_updated': datetime.now().isoformat()
                }
                with open(self.storage_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"Failed to save workflows: {e}")

    def create_workflow(self,
                       name: str,
                       steps: List[Dict[str, Any]],
                       description: Optional[str] = None) -> WorkflowSession:
        """
        Create a new workflow session

        Args:
            name: Workflow name
            steps: List of step definitions
            description: Optional description

        Returns:
            Created WorkflowSession
        """
        workflow_id = str(uuid.uuid4())

        # Convert step definitions to WorkflowStep objects
        workflow_steps = []
        for step_def in steps:
            step = WorkflowStep(
                step_id=step_def.get('step_id', str(uuid.uuid4())),
                tool_name=step_def['tool_name'],
                target_path=step_def['target_path'],
                arguments=step_def.get('arguments', {}),
                dependencies=step_def.get('dependencies', []),
                condition=step_def.get('condition'),
                timeout=step_def.get('timeout'),
                max_retries=step_def.get('max_retries', 0),
            )
            workflow_steps.append(step)

        workflow = WorkflowSession(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps
        )

        with self._lock:
            self._workflows[workflow_id] = workflow

        self._save_workflows()
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowSession]:
        """Get workflow by ID"""
        with self._lock:
            return self._workflows.get(workflow_id)

    def list_workflows(self) -> List[WorkflowSession]:
        """List all workflows"""
        with self._lock:
            return list(self._workflows.values())

    def start_workflow(self, workflow_id: str) -> bool:
        """
        Start executing a workflow

        Args:
            workflow_id: Workflow ID to start

        Returns:
            True if started successfully, False otherwise
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False

        if workflow.status != WorkflowStatus.CREATED:
            return False

        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()

        # Start execution in background
        executor = ThreadPoolExecutor(max_workers=self.max_concurrent_steps, thread_name_prefix=f"workflow-{workflow_id}")
        self._executors[workflow_id] = executor

        executor.submit(self._execute_workflow, workflow)

        self._save_workflows()
        return True

    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow"""
        workflow = self.get_workflow(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.RUNNING:
            return False

        workflow.status = WorkflowStatus.PAUSED
        self._save_workflows()
        return True

    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        workflow = self.get_workflow(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.PAUSED:
            return False

        workflow.status = WorkflowStatus.RUNNING

        # Restart execution
        if workflow_id in self._executors:
            executor = self._executors[workflow_id]
            executor.submit(self._execute_workflow, workflow)

        self._save_workflows()
        return True

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow execution"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False

        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.now()

        # Shutdown executor if running
        if workflow_id in self._executors:
            self._executors[workflow_id].shutdown(wait=False)
            del self._executors[workflow_id]

        self._save_workflows()
        return True

    def _execute_workflow(self, workflow: WorkflowSession):
        """Execute workflow steps in dependency order"""
        try:
            while workflow.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
                if workflow.status == WorkflowStatus.PAUSED:
                    time.sleep(1)  # Wait while paused
                    continue

                # Get next steps to execute
                pending_steps = workflow.get_pending_steps()

                if not pending_steps:
                    # Check if all steps are completed
                    if all(step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]
                           for step in workflow.steps):
                        workflow.status = WorkflowStatus.COMPLETED
                        workflow.completed_at = datetime.now()
                        break
                    else:
                        # Wait for dependencies or manual intervention
                        time.sleep(0.5)
                        continue

                # Execute ready steps (up to max_concurrent_steps)
                executing_steps = [
                    step for step in workflow.steps
                    if step.status == StepStatus.RUNNING
                ]

                available_slots = self.max_concurrent_steps - len(executing_steps)

                for step in pending_steps[:available_slots]:
                    # Check condition
                    context = {s.step_id: s for s in workflow.steps}
                    if not step.evaluate_condition(context):
                        step.status = StepStatus.SKIPPED
                        continue

                    # Start step execution
                    workflow.current_step = step.step_id
                    self._execute_step(workflow, step)

                workflow.update_progress()
                self._save_workflows()
                time.sleep(0.1)  # Small delay to prevent busy waiting

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(e)
            workflow.completed_at = datetime.now()

        finally:
            workflow.update_progress()
            self._save_workflows()

            # Clean up executor
            if workflow.workflow_id in self._executors:
                del self._executors[workflow.workflow_id]

    def _execute_step(self, workflow: WorkflowSession, step: WorkflowStep):
        """Execute a single workflow step"""
        step.status = StepStatus.RUNNING
        step.start_time = datetime.now()
        step.retry_attempt += 1

        try:
            # Get tool adapter
            if step.tool_name not in self.tool_registry:
                raise ValueError(f"Unknown tool: {step.tool_name}")

            adapter = self.tool_registry[step.tool_name]

            # Execute tool
            timeout = step.timeout or 300  # Default 5 minutes
            result = adapter.execute_sync(
                step.target_path,
                timeout=timeout,
                **step.arguments
            )

            step.result = result
            step.end_time = datetime.now()

            if result.success:
                step.status = StepStatus.COMPLETED
            else:
                if step.should_retry():
                    step.status = StepStatus.PENDING  # Will retry
                    step.retry_count += 1
                else:
                    step.status = StepStatus.FAILED
                    step.error_message = result.error_message or "Tool execution failed"

        except Exception as e:
            step.end_time = datetime.now()
            step.error_message = str(e)

            if step.should_retry():
                step.status = StepStatus.PENDING
                step.retry_count += 1
            else:
                step.status = StepStatus.FAILED

        self._save_workflows()

    def cleanup_old_workflows(self, max_age_days: int = 30):
        """Clean up old completed/failed workflows"""
        cutoff = datetime.now() - timedelta(days=max_age_days)

        with self._lock:
            to_remove = [
                wid for wid, workflow in self._workflows.items()
                if workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]
                and workflow.completed_at and workflow.completed_at < cutoff
            ]

            for wid in to_remove:
                del self._workflows[wid]

        self._save_workflows()