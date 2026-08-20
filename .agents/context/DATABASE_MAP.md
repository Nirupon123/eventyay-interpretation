# Database Map

All models are defined in `interpretation/models.py`.

## Models
- `VoxbentoOAuthGrant`: Stores the OAuth credentials for a connected VoxBento instance at the Event level. Contains `webhook_secret_key` (encrypted) and `webhook_subscription_id`.
- `RoomInterpretation`: Maps an Eventyay `Room` to specific interpretation settings (e.g. which interpreter platform is being used).

## Security
Sensitive fields like `webhook_secret_key` are encrypted at rest using Django's or Eventyay's encrypted fields.
