# VYRA YouTube

A VYRA-branded visual customization layer for YouTube Android, built on a pinned Morphe patcher stack.

## Product intent
- Stock YouTube remains the default appearance.
- A dedicated **VYRA MOD** entry appears in YouTube settings.
- **VYRA Appearance** owns the glass navigation controls.
- The supplied design direction is black and silver, with a liquid-glass V mark, restrained lighting, and a floating glass navigation capsule with a central V.
- The supplied splash direction is an 8-second black/silver animation: glass V descends, a thin circular light ring appears, spaced VYRA lettering fades in, and a thin loading line completes.

## Current implementation
- VYRA patch overlay is applied to pinned Morphe Patches source.
- Root settings branding is renamed to VYRA MOD.
- The VYRA MOD root organizes the existing General, Feed, Player, and Shorts settings categories as **VYRA Appearance**, **VYRA Home & Feed**, **VYRA Player**, and **VYRA Shorts**.
- VYRA Appearance exposes the upstream navigation animation, navigation style, glass toggle, opacity, rounded capsule, and live size/width/spacing preview controls.
- VYRA Player, Home & Feed, and Shorts retain their upstream working controls (including player/Shorts icon styles and feed-card layout).
- The upstream Glass renderer remains responsible for drawing and measuring the capsule; this project does not pretend to replace that runtime.
- The upstream Rive/Lottie splash hook is temporarily excluded from VYRA's patch bundle to isolate the reported Android resource-encoding failure; a VYRA-native splash is still pending.
- GitHub Actions can build the .mpp patch bundle. An .mpp is **not** an installable APK.

## Approved prototype scope
- `Sıvı Cam Alt Menü.html` is a reference only for the bottom navigation capsule. Only its five-tab menu, central Create action, glass selection indicator, and translucent capsule are in scope; its demo page bodies and theme demo are not part of the app.
- `yukleme-animasyonu.html` is a reference only for a future update/download progress indicator (glass orb, ring, percentage, completion state). Its timed demo progress is not used; real progress must come from the actual download operation.
- The stock YouTube navigation remains the default. When the user enables Glass, VYRA defaults are a clearer capsule (opacity 14/100), rounded ends, and navigation animations enabled.

## Target baseline
- Android package: `com.google.android.youtube`
- Target version: `21.30.216`
- Pinned Morphe Manager: `2.6.0`
- Pinned Morphe Patcher: `2.4.0`
- Pinned Morphe Patches: `2.3.0`
- Test target: Android 16 / API 36

## Build and safety rules
- Start only from a clean, unmodified YouTube APK matching the target baseline.
- Reject an APK containing `MORPHE_BRANDING.TXT`; never patch a previously patched APK.
- Never commit YouTube APKs, keystores, tokens, or other signing secrets.
- Do not publish an APK until resources compile, it signs, installs, launches, and passes smoke tests.
- Preserve original YouTube behavior when VYRA options are disabled.

## Repository map
- `patches/`: guarded overlay against pinned upstream patch source
- `design/`: VYRA design tokens and design references
- `docs/`: architecture and staged implementation plan
- `input/`: local-only clean APK placeholder (APK files are Git-ignored)
- `.github/workflows/`: validation and patch-bundle workflows

See [the roadmap](docs/ROADMAP.md) for the remaining implementation and verification work.