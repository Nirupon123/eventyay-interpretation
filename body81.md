## Objective
This is the final backend cutover phase. With the OAuth handshake working and tokens being saved, we need to completely sever reliance on the old legacy API keys. We must update core backend functions (like `sync_booths` and start/stop actions) to use the new Bearer tokens. Additionally, we need to implement the event handlers for the verified webhooks and ensure the video area UI correctly displays the captions coming from the plugin.

- parent : #77 

## Context
As noted by the co-developer: *"We need to update the `sync_booths()` function and the start/stop buttons to actually use these new Bearer tokens instead of falling back to the old legacy API keys and get the remaining part of showing the captions in the video area through the plugin working."*

## Tasks & Implementation Steps

### 1. Final Backend Cutover to OAuth
* **Update `sync_booths()`:** Modify `interpretation/backends/voxbento.py` so that `sync_booths()` fetches the `access_token` from the `VoxbentoOAuthGrant` model and uses it as a Bearer token in the `Authorization` header, fully replacing the old `get_voxbento_api_key()` fallback.
* **Update Start/Stop Buttons:** Ensure that any API calls triggered by the start/stop interpretation buttons in the UI are also utilizing the correct OAuth Bearer token. 
* **Cleanup:** Remove any remaining traces of the legacy API key settings if they are no longer required.

### 2. Webhook Event Handlers
* Within the secure receiver built in Phase 3, route the verified JSON payload to specific handler functions based on `event_type`:
  * **`session.status_changed`:** Update the `status` field of the `RoomInterpretation` model.
  * **`booth.interpreter.joined`:** Log interpreter connections or update live participant rosters.
  * **`booth.transcription.started` / `booth.transcription.stopped`:** Update backend states indicating that transcription is active.

### 3. Video Area UI - Captions & Audio Integration (Eventyay Core)
* **Architecture:** The Eventyay Video Area (`webapp/video`) acts as the single source of truth for rendering the organizer's configured video (e.g. native YouTube iframe, Vimeo, Jitsi). VoxBento integration must happen *around* this native player.
* **UI Integration:** Inject the `AudioTranslationDropdown.vue` component directly below the main video player in `MediaSource.vue`.
* **State Management:** 
  * When an attendee selects a language from the dropdown, mute the native Eventyay video player (e.g., mute the YouTube iframe).
  * Connect the hidden `<audio ref="whepAudioEl">` tag to the VoxBento WHEP URL to pull the translated audio.
  * Connect to the VoxBento `caption_url` WebSocket and render captions in a floating `<div>` overlay on top of the native player.
* **Playback Synchronization:** Bind the native player's lifecycle events (`play`, `pause`, `stop`) to the VoxBento streams. If the attendee pauses a pre-recorded YouTube video, the UI must intelligently pause or disconnect the WHEP/Caption WebSockets to prevent them from drifting completely out of sync with the video timeline.

## Acceptance Criteria
- [ ] `sync_booths()` and Start/Stop actions strictly use the OAuth Bearer token from `VoxbentoOAuthGrant`.
- [ ] Legacy API key fallbacks are removed.
- [ ] Webhook payloads successfully update the `RoomInterpretation` status and transcription states in the database.
- [ ] Live captions are successfully displayed in the frontend video area utilizing the `caption_url` provided by the plugin.
- [ ] The entire backend cutover is complete and functioning end-to-end.

