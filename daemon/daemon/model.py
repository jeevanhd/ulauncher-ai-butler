"""
Loads Needle once at daemon startup and keeps it resident.
Uses the JAX/pure-python route (needle repo), not cactus (ARM-only, doesn't
build on x86_64 - confirmed dead end on this machine).
No idle-unload - 26M params is negligible RAM, not worth the complexity.
"""

import json
from pathlib import Path

from needle import load_checkpoint, generate, SimpleAttentionNetwork, get_tokenizer

CHECKPOINT_PATH = Path(__file__).parent.parent / "checkpoints" / "needle.pkl"
TOOLS_PATH = Path(__file__).parent / "tools.json"

_model = None
_params = None
_tokenizer = None


def load_model():
    global _model, _params, _tokenizer
    if _model is None:
        _params, config = load_checkpoint(str(CHECKPOINT_PATH))
        _model = SimpleAttentionNetwork(config)
        _tokenizer = get_tokenizer()
    return _model, _params, _tokenizer


def load_tools() -> str:
    # needle expects tools as a JSON string, not a python list
    with open(TOOLS_PATH) as f:
        tools = json.load(f)
    return json.dumps(tools)


def query_needle(text: str) -> list[dict]:
    """
    Returns list of tool_call dicts, e.g.
    [{"name": "sort_files", "arguments": {"folder": "Downloads"}}]
    """
    model, params, tokenizer = load_model()
    tools = load_tools()

    result = generate(
        model,
        params,
        tokenizer,
        query=text,
        tools=tools,
        stream=False,
    )
    # generate() returns a JSON string per model card example
    return json.loads(result)
