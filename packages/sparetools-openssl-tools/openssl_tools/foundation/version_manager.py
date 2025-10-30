from datetime import datetime
import subprocess
from typing import Optional

def get_openssl_version(semantic_version: str, is_fips: bool = False, git_hash: Optional[str] = None) -> str:
    if not is_fips:
        return semantic_version
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    if git_hash is None:
        try:
            git_hash = subprocess.check_output(["git", "rev-parse", "--short=8", "HEAD"], text=True).strip()
        except Exception:
            git_hash = "00000000"
    return f"{semantic_version}+fips.{timestamp}.{git_hash}"

def parse_openssl_version(version_string: str) -> dict:
    parts = version_string.split("+")
    result = {"semantic": parts[0], "metadata": {}}
    if len(parts) > 1:
        meta_parts = parts[1].split(".")
        if len(meta_parts) >= 3:
            result["metadata"] = {
                "build_type": meta_parts[0],
                "timestamp": meta_parts[1],
                "git_hash": meta_parts[2],
            }
    return result
