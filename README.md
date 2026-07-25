# AI Butler

Local AI tool-calling assistant for [Ulauncher](https://ulauncher.io), powered by
[Needle](https://huggingface.co/Cactus-Compute/needle) running via [Cactus](https://github.com/cactus-compute/cactus).

## How it works

```
ulauncher (keyword: bt) -> main.py -> HTTP POST localhost:8420 -> daemon
    -> Needle resolves intent -> dispatcher -> real action -> result back to ulauncher
```

**Runtime note:** Needle runs via the pure-Python/JAX route (`needle` package), not
[Cactus](https://github.com/cactus-compute/cactus) — Cactus's compiled engine requires
64-bit ARM and does not build on x86_64. If you're on an ARM machine, Cactus may be
worth revisiting for its faster inference (6000 tok/s prefill claimed in prod).

## Setup

### 1. Daemon

```bash
cd daemon
uv sync
# force CPU-only jax - needle's deps otherwise pull CUDA wheels (~500MB+) even
# on machines that don't need them for a 26M param model
uv pip install "jax[cpu]" jaxlib --force-reinstall
mkdir -p checkpoints
uv run python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(repo_id='Cactus-Compute/needle', filename='needle.pkl', local_dir='checkpoints')
"
uv run uvicorn daemon.main:app --host 127.0.0.1 --port 8420   # test run
```

Install as a systemd user service:

```bash
mkdir -p ~/.config/systemd/user
cp systemd/ai-butler.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now ai-butler.service
```

### 2. Ulauncher extension

Symlink this repo root into ulauncher's extensions directory:

```bash
ln -s "$(pwd)" ~/.local/share/ulauncher/extensions/ai-butler
```

Restart Ulauncher. Type `bt <your query>` to use.

## Status

Early scaffold. Tools implemented: none yet (stubs only). See `daemon/daemon/tools.json`
for registry and `daemon/dispatcher/actions/` for handlers.
