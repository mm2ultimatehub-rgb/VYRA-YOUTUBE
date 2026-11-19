# Architecture and non-negotiable constraints

## Product layers
1. Upstream patch layer — pinned Morphe patches and patcher versions.
2. VYRA patch overlay — YouTube-specific settings, navigation, player, and branding changes. Every source edit needs anchor assertions and regression checks.
3. Branding layer — app icon assets and splash treatment. The HTML prototype is a design reference, not an Android runtime component.
4. Build layer — accepts a clean original APK, applies patches, compiles resources, signs output, and records provenance.
5. Verification layer — checks package/version/signature, installs on a test device/emulator, and runs startup/navigation/player smoke tests.

## Rules
- Input APK must be clean and match the supported version.
- A Morphe marker such as MORPHE_BRANDING.TXT is a hard stop.
- An .mpp is not an installable APK.
- Never commit proprietary APKs, signing keys, or tokens.
- Do not report completion until resource compilation, signing, installation, and smoke tests pass.

## Previous failure to prevent
A prior patch attempt failed while encoding resources because a drawable XML referenced a missing generated drawable ($startup_animation_dark__9). Reproduce this in a clean test, trace the resource transformation, and fix the packaging layer. Do not delete arbitrary resources or disable unrelated patches without proving the dependency.

## UI principle
Mockups are visual targets, not permission to replace YouTube flows. Preserve YouTube behavior by default. VYRA styling is opt-in and reversible. Every preference needs real implementation, persistence, reset, and a fallback when blur is unavailable.
