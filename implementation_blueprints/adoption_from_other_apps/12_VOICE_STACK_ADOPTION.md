# Voice Stack Adoption

## Source Modules
- `code_of_other_apps_that_can_be_adopted/voice_bridge.py`
- `code_of_other_apps_that_can_be_adopted/chatterbox/README.md`
- `code_of_other_apps_that_can_be_adopted/whisper/README.md`

## Roadmap Fit
- Optional extension after core roadmap stability.

## Reusable Pieces
- Cross-platform command auto-detection for record/playback.
- Defensive voice subsystem wrappers and cleanup patterns.
- Whisper STT and Chatterbox TTS bridge concepts.

## Required Adaptations
- Move voice controls behind explicit runtime feature flag.
- Separate CLI-only commands from containerized deployment mode.
- Add strict timeout and max-size caps for audio artifacts.

## Acceptance Criteria
- Voice failure never interrupts text interaction loop.
- STT/TTS can be enabled/disabled without restart.
- Logs include audio pipeline stage and failure cause.
