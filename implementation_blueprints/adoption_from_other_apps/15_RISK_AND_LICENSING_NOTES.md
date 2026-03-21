# Risk And Licensing Notes

## Technical Risks
- Hidden game-specific assumptions in source modules may conflict with OpenClaw runtime.
- Cross-module imports in adopted code can create circular dependencies.
- Large third-party stacks (`whisper`, `chatterbox`, `ollama`) increase deployment complexity.

## Adaptation Risks
- Field/schema drift between old save-state models and new runtime contracts.
- Prompt bloat if narrative-heavy context builders are imported without trimming.
- Security regressions if path/file handling is copied without tighter policy wrappers.

## Mitigation
- Adopt through thin adapters and typed contracts only.
- Introduce each module behind feature flags.
- Require unit + integration tests before enabling in main loop.

## Licensing Checkpoints
- Verify origin and license compatibility for bundled external trees:
  - `code_of_other_apps_that_can_be_adopted/chatterbox/`
  - `code_of_other_apps_that_can_be_adopted/whisper/`
  - `code_of_other_apps_that_can_be_adopted/ollama/`
- Keep attribution files intact for any code copied into production paths.
