# Sparetools Cognitive Architecture Integration Roadmap

## Executive Summary

Transform **sparetools** from a simple devtools wrapper into a **self-improving cognitive development assistant** that learns from your work across all four projects (esp32-bpm-detector, mia, cliphist-android, sparetools itself), stores successful patterns, and applies them intelligently.

## The Big Picture: How Everything Connects

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTS                            │
│  "Analyze my ESP32 project" / "Why is this crashing?" / etc.    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SPARETOOLS CLI                                │
│              (Your main interface)                               │
│  • sparetools analyze <project>                                  │
│  • sparetools diagnose <symptoms>                                │
│  • sparetools learn --from-success                               │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│          COGNITIVE ORCHESTRATOR (New in sparetools)              │
│                                                                   │
│  Layer 1: Context Detection                                      │
│    • Detects: ESP32, Android, Python, C++                        │
│    • Identifies: Build system, frameworks, constraints           │
│                                                                   │
│  Layer 2-3: Knowledge Query                                      │
│    • "Have I seen this before?"                                  │
│    • "What do I know about ESP32 memory issues?"                 │
│                                                                   │
│  Layer 4: Workflow Execution                                     │
│    • Runs analysis with learned configurations                   │
│    • Adapts tools to project characteristics                     │
│                                                                   │
│  Layer 5: Meta-Learning                                          │
│    • "Should I save this successful approach?"                   │
│    • "Can I generalize this pattern?"                            │
│                                                                   │
│  Layer 6: Transfer Learning                                      │
│    • "This Android pattern applies to ESP32 too"                 │
│                                                                   │
│  Layer 7: Quality Assessment                                     │
│    • "How good was this analysis?"                               │
│    • "Did it actually help?"                                     │
└────────┬──────────────────────────────┬──────────────────────────┘
         │                              │
         │                              │
    ┌────▼─────┐                  ┌─────▼─────┐
    │          │                  │           │
    │  MCP-    │                  │ UNIFIED-  │
    │ PROMPTS  │                  │ DEV-TOOLS │
    │          │                  │           │
    │ Storage  │                  │ Execution │
    │          │                  │           │
    └────┬─────┘                  └─────┬─────┘
         │                              │
         │  Stores/retrieves            │  Executes
         │  learned patterns            │  tools
         │                              │
         │                              │
         ▼                              ▼
┌──────────────────┐          ┌────────────────────────┐
│  PROMPT CATALOG  │          │   DEVELOPMENT TOOLS    │
│                  │          │                        │
│ • Episodes       │          │ • cppcheck             │
│ • Workflows      │          │ • valgrind             │
│ • Configurations │          │ • pytest               │
│ • Patterns       │          │ • gradle               │
│                  │          │ • platformio           │
└──────────────────┘          │ • adb                  │
                              │ • conan                │
                              └────────────────────────┘
```

## Integration Architecture: Three Systems Working Together

### System 1: Sparetools (Orchestration + Intelligence)

**Location**: `~/projects/dev-tools/sparetools`

**Role**: The "brain" that coordinates everything

**Key Components**:
```
sparetools/
├── mcp/
│   └── client.py          # Unified MCP client
├── cognitive/
│   ├── context.py         # Layer 1: Perception
│   ├── memory.py          # Layer 2-3: Episodes + Knowledge
│   ├── workflows.py       # Layer 4: Procedures
│   ├── meta.py            # Layer 5: Strategy
│   ├── transfer.py        # Layer 6: Cross-domain
│   └── evaluation.py      # Layer 7: Quality
├── orchestrator.py        # Main intelligence loop
└── cli/
    ├── analyze.py
    ├── diagnose.py
    └── learn.py
```

### System 2: MCP-Prompts (Knowledge Storage)

**What it stores**:
- **Prompts**: Successful analysis configurations
- **Episodes**: "I tried X, it worked because Y"
- **Workflows**: Multi-step procedures that work
- **Patterns**: Abstract knowledge that transfers

**How sparetools uses it**:
```python
# Store a successful pattern
await mcp_client.store_prompt(
    name="esp32-memory-leak-diagnosis",
    content={
        "steps": ["1. Run valgrind", "2. Check heap usage", ...],
        "config": {"valgrind": {"leak-check": "full"}},
        "when_to_use": "ESP32 projects with memory crashes"
    },
    tags=["esp32", "memory", "diagnosis"]
)

# Retrieve when needed
pattern = await mcp_client.get_prompt("esp32-memory-leak-diagnosis")
```

### System 3: Unified-Dev-Tools (Tool Execution)

**What it provides**:
- **ESP32 tools**: Serial monitoring, flashing, profiling
- **Android tools**: ADB, device management, APK installation
- **Build tools**: Conan package management
- **Knowledge ops**: Query/capture development patterns

**How sparetools uses it**:
```python
# Query for known patterns
knowledge = await dev_tools.query_development_knowledge(
    domain="esp32",
    topic="BPM detection performance optimization"
)

# Execute composed workflow
result = await dev_tools.composed_embedded_workflow(
    target_platform="esp32",
    workflow_type="build",
    config={
        "project_path": "/path/to/esp32-bpm-detector",
        "optimizations": knowledge.get("recommended_flags")
    }
)

# Capture successful outcomes
await dev_tools.capture_development_learning(
    domain="esp32",
    pattern="BPM detection optimized by using...",
    context="ESP32-S3 with I2S audio input",
    tags=["bpm", "audio", "performance"]
)
```

## The Learning Loop in Action

### Example 1: ESP32 Build Failure → Learned Pattern

```
1. USER ACTION:
   $ sparetools analyze ~/projects/embedded/esp32-bpm-detector

2. LAYER 1 (Perception):
   Detects: ESP32 project, C++17, PlatformIO, FlatBuffers dependency

3. LAYER 2 (Episodic Memory):
   Query: "Have I seen ESP32 + FlatBuffers issues before?"
   Result: YES! Found episode from 2 weeks ago

4. LAYER 3 (Semantic Knowledge):
   Retrieves: "FlatBuffers type mismatches on ESP32 are usually..."

5. LAYER 4 (Procedural):
   Executes workflow:
   - Check schema versions
   - Verify include paths
   - Validate generated code

6. OUTCOME:
   Found: Schema version mismatch in platformio.ini

7. LAYER 5 (Meta-cognitive):
   Decision: This is the 3rd time this pattern helped
   Action: Upgrade it to "well-established pattern"

8. STORAGE:
   Store in mcp-prompts as:
   "diagnose-esp32-flatbuffers-version-conflict"
   
   Tag with: esp32, flatbuffers, build-failure, high-confidence
```

### Example 2: Cross-Domain Transfer (Android → ESP32)

```
1. OBSERVATION in cliphist-android:
   Pattern: Memory cleanup using try-with-resources prevents leaks

2. LAYER 6 (Transfer):
   Abstract pattern: "Resource cleanup at scope boundaries prevents leaks"

3. ADAPTATION to ESP32:
   C++ equivalent: RAII with smart pointers
   
4. CONCRETE APPLICATION:
   In esp32-bpm-detector:
   - Old: Manual I2S buffer management
   - New: std::unique_ptr for auto-cleanup
   
5. VALIDATION:
   Test shows: 40% reduction in heap fragmentation

6. STORAGE:
   Store cross-domain pattern:
   "resource-cleanup-scope-boundaries"
   Applicable: [android, esp32, python]
```

## Practical Implementation Phases

### Phase 1: Foundation (Week 1-2) - IMMEDIATE PRIORITY

**Goal**: Get basic intelligence loop working

**Tasks**:
1. ✅ **Set up MCP servers**
   ```bash
   # Install mcp-prompts
   cd ~/projects
   git clone https://github.com/sparesparrow/mcp-prompts.git
   cd mcp-prompts
   pnpm install
   pnpm build
   
   # Test it
   node dist/index.js
   ```

2. ✅ **Install unified-dev-tools** (if not already)
   ```bash
   # Check if it exists in your MCP config
   cat ~/.config/claude/claude_desktop_config.json
   
   # If not, add it to MCP servers
   ```

3. ✅ **Create sparetools MCP client**
   - Use the code from `sparetools_mcp_quickstart.py`
   - Test connection to both servers
   - Verify you can store/retrieve prompts

4. ✅ **Implement context detection**
   - Run on all 4 projects
   - Verify it correctly identifies each type
   - Store results as baseline

5. ✅ **Create first learned prompt manually**
   ```bash
   # Analyze esp32-bpm-detector
   cd ~/projects/embedded/esp32-bpm-detector
   # Note what tools you use, what configurations work
   # Store as prompt
   python sparetools_mcp_quickstart.py --mode learn --project esp32-bpm-detector
   ```

**Success Criteria**:
- ✓ Can connect to both MCP servers
- ✓ Can detect context for all 4 projects
- ✓ At least 1 prompt stored and retrievable
- ✓ CLI works: `sparetools analyze <project>`

### Phase 2: Intelligent Orchestration (Week 3-4)

**Goal**: Make analysis decisions based on learned patterns

**Tasks**:
1. **Query-before-execute pattern**
   - Before any analysis, query mcp-prompts
   - If pattern found, use it
   - If not, use defaults but prepare to learn

2. **Project-specific configurations**
   - Store optimal cppcheck configs for C++ projects
   - Store optimal pytest configs for Python projects
   - Store optimal gradle configs for Android

3. **Success tracking**
   - After each analysis, ask: "Did this help?"
   - Track effectiveness scores
   - Auto-update prompts with usage stats

4. **First cross-project pattern**
   - Find a pattern used in multiple projects
   - Abstract it (Layer 6)
   - Test that abstraction actually transfers

**Success Criteria**:
- ✓ Reuses patterns 50%+ of the time
- ✓ Measurably faster on repeated tasks
- ✓ At least 1 cross-domain pattern working

### Phase 3: Self-Improvement Loop (Week 5-6)

**Goal**: System actively learns without prompting

**Tasks**:
1. **Automatic pattern detection**
   - After successful outcomes, auto-capture
   - No manual "did this help?" needed

2. **Pattern evolution**
   - Track which steps get skipped
   - Track which parameters get overridden
   - Auto-refine prompts based on usage

3. **Anomaly detection**
   - Notice when learned pattern fails
   - Mark for review or deprecation
   - Learn from failures too

4. **Knowledge graph**
   - Connect related prompts
   - Build "if X fails, try Y" relationships
   - Enable smarter workflow routing

**Success Criteria**:
- ✓ System proposes new patterns unprompted
- ✓ Patterns improve over time automatically
- ✓ Can explain why it chose a specific approach

### Phase 4: Multi-Project Intelligence (Week 7-8)

**Goal**: Leverage knowledge across all projects

**Tasks**:
1. **Universal analyzer**
   ```bash
   sparetools analyze-all \
     --learn-from-all \
     --find-common-patterns
   ```

2. **Comparative analysis**
   - "Show me memory patterns across all C++ projects"
   - "Which testing approaches work best where?"

3. **Proactive suggestions**
   - "I notice mia has good error handling, should we apply this to esp32?"
   - "cliphist-android's build is slow, I know a pattern from sparetools that might help"

4. **Knowledge export**
   - Generate markdown reports of learned patterns
   - Export prompts for sharing
   - Build a personal knowledge base

**Success Criteria**:
- ✓ Can analyze all 4 projects in one command
- ✓ Identifies patterns across projects
- ✓ Proactive improvement suggestions

## Integration with Existing Tools

### ESP32 Development (esp32-bpm-detector)

**MCP Tools to Use**:
- `esp32_serial_monitor_start` - Monitor during testing
- `composed_embedded_workflow` - Unified build/flash/test
- `query_development_knowledge` - "How to optimize BPM algorithm?"

**Patterns to Learn**:
- Optimal PlatformIO configurations
- I2S audio buffer management
- Real-time performance tuning
- FlatBuffers integration quirks

**Example workflow**:
```python
# Stored in mcp-prompts
{
  "name": "optimize-esp32-bpm-detection",
  "steps": [
    "Profile with serial output timing",
    "Identify I2S buffer bottlenecks",
    "Tune buffer sizes based on sample rate",
    "Verify timing constraints met"
  ],
  "config": {
    "platformio": {
      "build_flags": ["-O2", "-DCORE_DEBUG_LEVEL=3"]
    }
  }
}
```

### Android Development (cliphist-android)

**MCP Tools to Use**:
- `android_device_list` - Check connected devices
- `android_install_apk` - Install for testing
- `android_logcat_start` - Monitor logs

**Patterns to Learn**:
- Kotlin best practices that worked
- UI testing strategies
- Performance profiling approaches

### Python/C++ Integration (sparetools, mia)

**MCP Tools to Use**:
- `conan_create_package` - Package C++ components
- `conan_search_packages` - Find dependencies
- `repo_cleanup_scan` - Maintain codebase health

**Patterns to Learn**:
- C++ extension building tricks
- Conan dependency resolution
- Mixed-language debugging

## Measuring Success

### Quantitative Metrics

Track these in mcp-prompts metadata:

1. **Knowledge Growth**
   - Number of prompts stored
   - Prompt categories diversity
   - Cross-domain patterns identified

2. **Pattern Reuse**
   - % analyses using learned patterns
   - Average reuse per pattern
   - Most valuable patterns

3. **Time Savings**
   - Time to diagnose similar issues (before/after)
   - Repeated task automation
   - Reduced manual configuration

4. **Quality Improvement**
   - Issues caught that weren't before
   - False positive reduction
   - Analysis completeness scores

### Qualitative Indicators

1. **Insight Quality**
   - Do suggestions actually help?
   - Are explanations clear?
   - Does context awareness work?

2. **Learning Effectiveness**
   - Do patterns generalize?
   - Do cross-domain transfers work?
   - Do prompts evolve meaningfully?

3. **User Experience**
   - Is it faster to use sparetools?
   - Does it reduce cognitive load?
   - Does it teach you things?

## Next Steps: What to Do Tomorrow

1. **Morning: Setup**
   ```bash
   cd ~/projects/dev-tools/sparetools
   python sparetools_mcp_quickstart.py --mode setup
   ```

2. **Afternoon: First Analysis**
   ```bash
   # Run on esp32-bpm-detector
   python sparetools_mcp_quickstart.py --mode analyze --project esp32-bpm-detector
   
   # Capture what worked
   python sparetools_mcp_quickstart.py --mode learn --project esp32-bpm-detector
   ```

3. **Evening: Test Reuse**
   ```bash
   # Make a small change to esp32 project
   # Run analysis again
   # Verify it uses the learned pattern
   
   python sparetools_mcp_quickstart.py --mode list
   # Should show your new prompt
   ```

4. **This Week: Expand**
   - Repeat for mia, cliphist-android
   - Find your first cross-project pattern
   - Start building your knowledge base

## Vision: 6 Months from Now

When someone asks "How do you manage 4 complex projects?", you'll say:

> "I built a self-improving development assistant. It learned from every issue I solved, every configuration that worked, every optimization I discovered. Now it:
> 
> - Diagnoses ESP32 build failures instantly because it's seen them before
> - Suggests Android optimizations based on patterns from my Python projects  
> - Knows exactly which analysis tools to run for each project type
> - Gets smarter every time I use it
> 
> It's not just automation—it's accumulated intelligence."

That's what we're building. Start today with the quick start script, and iterate from there!
