"""
MCP Prompts Client

Client for communicating with the MCP-Prompts server to fetch
interpretation templates, configurations, and analysis guidance.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import aiohttp
import requests

from ..tool_adapters.base_adapter import ToolResult


class MCPPromptsClient:
    """
    Client for MCP-Prompts server integration.

    Provides methods to query the MCP-Prompts server for:
    - Tool-specific interpretation templates
    - Project configuration recommendations
    - Analysis workflow suggestions
    - Result interpretation guidance
    """

    def __init__(self,
                 server_url: str = "http://localhost:3000",
                 timeout: int = 30,
                 api_key: Optional[str] = None):
        """
        Initialize the MCP-Prompts client.

        Args:
            server_url: URL of the MCP-Prompts server
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
        """
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self.api_key = api_key
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()

    def __enter__(self):
        """Sync context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit"""
        pass

    async def _ensure_session(self):
        """Ensure we have an active HTTP session"""
        if self._session is None:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            headers['Content-Type'] = 'application/json'

            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def _close_session(self):
        """Close the HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests"""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    async def get_interpretation_prompt(self,
                                       tool_name: str,
                                       context: Dict[str, Any]) -> Optional[str]:
        """
        Get interpretation prompt for a specific tool and context.

        Args:
            tool_name: Name of the analysis tool
            context: Context information (project type, severity, etc.)

        Returns:
            Interpretation prompt string or None if not found
        """
        await self._ensure_session()

        endpoint = f"{self.server_url}/api/prompts/interpretation"
        payload = {
            'tool_name': tool_name,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }

        try:
            async with self._session.post(endpoint, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('prompt')
                else:
                    self.logger.warning(f"Failed to get interpretation prompt: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching interpretation prompt: {e}")
            return None

    async def get_configuration_template(self,
                                       tool_name: str,
                                       project_type: str,
                                       language: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get configuration template for a tool and project type.

        Args:
            tool_name: Name of the analysis tool
            project_type: Type of project (web, library, cli, etc.)
            language: Primary programming language

        Returns:
            Configuration dictionary or None if not found
        """
        await self._ensure_session()

        endpoint = f"{self.server_url}/api/prompts/configuration"
        payload = {
            'tool_name': tool_name,
            'project_type': project_type,
            'language': language,
            'timestamp': datetime.now().isoformat()
        }

        try:
            async with self._session.post(endpoint, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('configuration')
                else:
                    self.logger.warning(f"Failed to get configuration template: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching configuration template: {e}")
            return None

    async def get_workflow_recommendations(self,
                                         project_context: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Get workflow recommendations based on project analysis.

        Args:
            project_context: Project context (languages, size, type, etc.)

        Returns:
            List of recommended workflows or None if not found
        """
        await self._ensure_session()

        endpoint = f"{self.server_url}/api/prompts/workflows"
        payload = {
            'project_context': project_context,
            'timestamp': datetime.now().isoformat()
        }

        try:
            async with self._session.post(endpoint, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('workflows', [])
                else:
                    self.logger.warning(f"Failed to get workflow recommendations: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching workflow recommendations: {e}")
            return None

    async def store_analysis_result(self,
                                  tool_name: str,
                                  result: ToolResult,
                                  context: Dict[str, Any]) -> bool:
        """
        Store analysis result for learning and improvement.

        Args:
            tool_name: Name of the analysis tool
            result: ToolResult object
            context: Additional context information

        Returns:
            True if stored successfully, False otherwise
        """
        await self._ensure_session()

        endpoint = f"{self.server_url}/api/results/store"
        payload = {
            'tool_name': tool_name,
            'result': result.to_dict(),
            'context': context,
            'timestamp': datetime.now().isoformat()
        }

        try:
            async with self._session.post(endpoint, json=payload) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Error storing analysis result: {e}")
            return False

    async def get_analysis_insights(self,
                                  tool_name: str,
                                  results: List[ToolResult],
                                  context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get AI-powered insights from analysis results.

        Args:
            tool_name: Name of the analysis tool
            results: List of ToolResult objects
            context: Additional context information

        Returns:
            Insights dictionary or None if not available
        """
        await self._ensure_session()

        endpoint = f"{self.server_url}/api/analysis/insights"
        payload = {
            'tool_name': tool_name,
            'results': [result.to_dict() for result in results],
            'context': context,
            'timestamp': datetime.now().isoformat()
        }

        try:
            async with self._session.post(endpoint, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('insights')
                else:
                    self.logger.warning(f"Failed to get analysis insights: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching analysis insights: {e}")
            return None

    # Synchronous versions for backward compatibility
    def get_interpretation_prompt_sync(self,
                                      tool_name: str,
                                      context: Dict[str, Any]) -> Optional[str]:
        """Synchronous version of get_interpretation_prompt"""
        return asyncio.run(self.get_interpretation_prompt(tool_name, context))

    def get_configuration_template_sync(self,
                                       tool_name: str,
                                       project_type: str,
                                       language: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Synchronous version of get_configuration_template"""
        return asyncio.run(self.get_configuration_template(tool_name, project_type, language))

    def get_workflow_recommendations_sync(self,
                                        project_context: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Synchronous version of get_workflow_recommendations"""
        return asyncio.run(self.get_workflow_recommendations(project_context))

    def store_analysis_result_sync(self,
                                  tool_name: str,
                                  result: ToolResult,
                                  context: Dict[str, Any]) -> bool:
        """Synchronous version of store_analysis_result"""
        return asyncio.run(self.store_analysis_result(tool_name, result, context))

    def get_analysis_insights_sync(self,
                                  tool_name: str,
                                  results: List[ToolResult],
                                  context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Synchronous version of get_analysis_insights"""
        return asyncio.run(self.get_analysis_insights(tool_name, results, context))

    async def health_check(self) -> bool:
        """
        Check if the MCP-Prompts server is healthy and responding.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            await self._ensure_session()
            async with self._session.get(f"{self.server_url}/health") as response:
                return response.status == 200
        except Exception:
            return False

    def health_check_sync(self) -> bool:
        """Synchronous version of health_check"""
        return asyncio.run(self.health_check())