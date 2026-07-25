from pathlib import Path


def run(folder: str) -> dict:
    target = Path(folder).expanduser()
    if not target.is_dir():
        return {"summary": f"Not a folder: {folder}", "detail": ""}

    # TODO: real sort-by-extension logic
    count = sum(1 for _ in target.iterdir())
    return {"summary": f"Would sort {count} items in {target.name}", "detail": "sort_files not yet implemented"}
