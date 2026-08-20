# Repository Context: Eventyay Interpretation

## Stack Overview
- **Framework**: Django (v6.1+)
- **Ecosystem**: Eventyay (Pretix core architecture)
- **Language**: Python 3.12+
- **Background Jobs**: Celery
- **Package Manager**: `uv`

## Plugin Architecture
Eventyay loads plugins dynamically via Python entry points defined in `pyproject.toml`:
```toml
[project.entry-points."pretix.plugin"]
interpretation = "interpretation"
```
The plugin hooks into the main application via `signals.py`, intercepting events like navigation rendering or video room initialization.

## Inter-Service Communication (VoxBento)
- **OAuth 2.0 (PKCE)**: The organizer dashboard securely connects to VoxBento.
- **REST API**: We call VoxBento to subscribe to webhooks or fetch metadata.
- **Webhooks**: We receive real-time updates from VoxBento (e.g. interpreter joined, channel active).
