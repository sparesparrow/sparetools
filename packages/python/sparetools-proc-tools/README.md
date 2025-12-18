# SpareTools Process Tools

Process management and command execution utilities for SpareTools projects.

## Features

- **Command Execution**: Flexible command execution with comprehensive output handling
- **Timeout Support**: Prevent hanging processes with configurable timeouts
- **Async Execution**: Run commands asynchronously without blocking
- **Silent Operation**: Execute commands with all output suppressed
- **Cross-Platform**: Works consistently across Windows, Linux, and macOS
- **Environment Control**: Custom environment variable support

## Usage

```python
from sparetools_proc_tools import (
    execute_command,
    run_command_with_timeout,
    execute_command_silently,
    run_command_async,
    wait_for_process
)

# Execute with full output control
code, output = execute_command(
    ["ls", "-la"],
    print_command=True,    # Show command being executed
    print_out=True,        # Show stdout
    print_error=True,      # Show stderr
    print_err_code=True    # Show exit code
)

# Run with timeout to prevent hanging
code, output = run_command_with_timeout(
    ["python", "long_script.py"],
    timeout=300  # 5 minutes
)

# Silent execution for background tasks
code, _ = execute_command_silently("mkdir -p /tmp/output")

# Async execution for parallel processing
process = run_command_async(["python", "worker.py"])
# Do other work...
code, output = wait_for_process(process)
```

## Conan Package

```bash
conan install sparetools-proc-tools/1.0.0@
```

## Command Building

```python
from sparetools_proc_tools import build_command_args

# Build complex commands programmatically
cmd = build_command_args(
    "conan", "install", ".",
    build="missing",
    profile="release",
    settings=["os=Linux", "arch=x86_64"]
)
# Results in: ["conan", "install", ".", "--build=missing", "--profile=release", "--settings=os=Linux", "--settings=arch=x86_64"]
```