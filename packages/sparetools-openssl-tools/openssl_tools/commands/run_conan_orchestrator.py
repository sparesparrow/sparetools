from pathlib import Path
import runpy, sys

def main() -> int:
    script = Path(__file__).parents[3] / "scripts" / "conan" / "conan_orchestrator.py"
    sys.argv[0] = str(script)
    runpy.run_path(str(script), run_name="__main__")
    return 0
