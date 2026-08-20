# Route Map

All routes are defined in `interpretation/urls.py` and are namespaced under `plugins:interpretation`.

## Organizer Dashboard
- `GET /control/event/{org}/{event}/interpretation/`: Main dashboard
- `GET/POST /control/event/{org}/{event}/interpretation/settings/`: Plugin settings

## OAuth 2.0 Flow
- `GET /control/event/{org}/{event}/interpretation/oauth/voxbento/login/`: Initiates PKCE flow
- `GET /control/event/{org}/{event}/interpretation/oauth/voxbento/callback/`: Handles OAuth redirect, issues token request

## Webhooks
- `POST /interpretation/webhooks/voxbento/`: Receives payloads from VoxBento. Bypasses CSRF but enforces HMAC-SHA256 signature validation.
