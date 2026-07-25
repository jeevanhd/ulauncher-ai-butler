"""
Loads Needle once at daemon startup and keeps it resident.
No idle-unload - 26M params is negligible RAM, not worth the complexity.
"""
import json
from pathlib import Path

from cactus.bindings.cactus import cactus_init, cactus_complete
from cactus.cli.download import download_bundle

TOOLS_PATH = Path(__file__).parent / "tools.json"

_model = None


def load_model():
    global _model
    if _model is None:
        bundle_path = download_bundle("Cactus-Compute/needle")
        _model = cactus_init(str(bundle_path))
    return _model


def load_tools():
    with open(TOOLS_PATH) as f:
        return json.load(f)


def query_needle(text: str) -> list[dict]:
    """
    Returns list of tool_call dicts, e.g.
    [{"name": "sort_files", "arguments": {"folder": "Downloads"}}]
    """
    model = load_model()
    tools = load_tools()
    result = cactus_complete(
        model,
        [{"role": "user", "content": text}],
        json.dumps({"tools": tools, "max_tokens": 256}),
    )
    return json.loads(result)
