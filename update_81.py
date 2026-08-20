with open("body81.md", "r") as f:
    body = f.read()

new_ui_section = """### 3. Video Area UI - Captions & Audio Integration (Eventyay Core)
* **Architecture:** The Eventyay Video Area (`webapp/video`) acts as the single source of truth for rendering the organizer's configured video (e.g. native YouTube iframe, Vimeo, Jitsi). VoxBento integration must happen *around* this native player.
* **UI Integration:** Inject the `AudioTranslationDropdown.vue` component directly below the main video player in `MediaSource.vue`.
* **State Management:** 
  * When an attendee selects a language from the dropdown, mute the native Eventyay video player (e.g., mute the YouTube iframe).
  * Connect the hidden `<audio ref="whepAudioEl">` tag to the VoxBento WHEP URL to pull the translated audio.
  * Connect to the VoxBento `caption_url` WebSocket and render captions in a floating `<div>` overlay on top of the native player.
* **Playback Synchronization:** Bind the native player's lifecycle events (`play`, `pause`, `stop`) to the VoxBento streams. If the attendee pauses a pre-recorded YouTube video, the UI must intelligently pause or disconnect the WHEP/Caption WebSockets to prevent them from drifting completely out of sync with the video timeline."""

body = body.replace(
    "### 3. Video Area UI - Captions Integration\n* **Expose Caption URLs:** Ensure the data returned by `sync_booths()` (which includes `caption_url`, `whip_url`, `whep_url`) is correctly serialized and passed to the frontend video component.\n* **UI Integration:** Get the remaining part of showing the captions in the video area working. The frontend must consume the `caption_url` provided by the backend to render the live captions over the video player.",
    new_ui_section,
)

with open("body81.md", "w") as f:
    f.write(body)
