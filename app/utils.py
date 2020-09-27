from pathlib import Path


def list_files(path, wildcard):
    path = Path(path)
    files = sorted(path.rglob(wildcard))
    if len(files) == 0:
        raise RuntimeError(f'No {wildcard} files found in {path}')

    return files
