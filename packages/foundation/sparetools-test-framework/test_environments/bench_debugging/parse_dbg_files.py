import glob
import re
from pathlib import Path

from ngapy.util.custom_logging import setup_logging_from_config


def find_source_paths(build_root, file_pattern='**/*.dbg'):
    dbg_files = {}
    for file in glob.glob(str(build_root / file_pattern), recursive=True):
        with open(file, "rb") as opened_file:
            opened_content = opened_file.read().decode('ansi')
            finds = re.findall(r'/cygdrive[/a-zA-Z0-9_-]*', opened_content)
            dbg_files[file] = finds
    return dbg_files


def compose_source_map(build_root, file_pattern='**/*.dbg'):
    dbg_files = find_source_paths(Path(build_root), file_pattern)
    source_map = '"sourceFileMap": {\n'
    unique_source_path = set()
    target_map = Path(build_root) / r"SOURCE\\EXTERNAL_DEPENDENCIES"
    for sources in dbg_files.values():
        for source in sources:
            # source_map += rf'"{source}": \{ "editorPath": {source_path} ", useForBreakpoints": true \}'
            source_parent = Path(source).parent
            if 'scm/Deos' in source:
                continue
            if source_parent in unique_source_path:
                continue
            else:
                unique_source_path.add(source_parent)
            source_map += f'"{source_parent}":'
            source_map += '{ "editorPath": '
            source_map += f'"{target_map}", "useForBreakpoints": true '
            source_map += '},\n'

    source_map += f'"../SOURCE":'
    source_map += '{ "editorPath": '
    source_map += f'"{Path(build_root) / "SOURCE"}", "useForBreakpoints": true '
    source_map += '},\n'

    source_map += '},\n'
    return source_map.replace('\\', '\\\\')


def compose_ld_library_path(build_root, file_pattern='**/*.dbg'):
    dbg_files = find_source_paths(Path(build_root), file_pattern)
    unique_dbg_file_path = set()
    for dbg_file in dbg_files.keys():
        dbg_file_folder = Path(dbg_file).parent
        if dbg_file_folder in unique_dbg_file_path:
            continue
        else:
            if 'EXTERNAL_DEPENDENCIES' in str(dbg_file_folder):
                unique_dbg_file_path.add(dbg_file_folder)
    ld_paths = ':'.join(
        [str(x.relative_to(build_root)).replace('\\', '/') for x in unique_dbg_file_path])
    return f'set environment LD_LIBRARY_PATH={ld_paths}:$LD_LIBRARY_PATH'
    pass


if __name__ == "__main__":
    setup_logging_from_config()
    source_path = r'd:\User\Michal\Repos\oms-dev\_Build'
    print(compose_source_map(source_path))
    print(compose_ld_library_path(source_path))
