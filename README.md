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
- A VYRA Liquid Glass master switch now gates the verified upstream glass navigation capsule and the upstream glass miniplayer. It defaults OFF, so stock navigation remains the default. This is a real opt-in glass control, not yet an app-wide renderer.
- The overlay generates a VYRA-branded 8-second Lottie splash from the supplied glass monogram, registers it as an Android raw resource, and routes the native YouTube splash hook to it through a VYRA setting. The Rive-only branch is excluded for the pinned target baseline.
- The overlay and generated splash pass CI validation, and the pinned Morphe source compiles into an .mpp bundle. Runtime behavior still requires installation and device smoke tests.
- GitHub Actions can build the .mpp patch bundle. An .mpp is **not** an installable APK.

## Approved prototype scope
- `Sıvı Cam Alt Menü.html` is a reference only for the bottom navigation capsule. Only its five-tab menu, central Create action, glass selection indicator, and translucent capsule are in scope; its demo page bodies and theme demo are not part of the app.
- `yukleme-animasyonu.html` is a reference only for a future update/download progress indicator (glass orb, ring, percentage, completion state). Its timed demo progress is not used; real progress must come from the actual download operation.
- The stock YouTube navigation remains the default. When the user enables Glass, VYRA defaults are a clearer capsule (opacity 14/100), rounded ends, and navigation animations enabled.

## Automatic patch-source updates
- Add this repository to Morphe Manager as a **Remote** source: `mm2ultimatehub-rgb/VYRA-YOUTUBE`.
- A successful patch-bundle build is published as a versioned GitHub Release, then `patches-bundle.json` is refreshed to point at that release asset.
- Morphe Manager can refresh remote sources in the background using its Updates schedule. The source card's Update action forces an immediate check.
- The glass-orb loader prototype is reserved for a future real download-progress surface; it is not a fake progress screen and does not replace Morphe Manager's own update UI.



## Full Liquid Glass status
The requested end state is glass styling across Home/feed, Search, Player, Shorts, Subscriptions, Library, dialogs, and menus, while leaving video frames and thumbnails untouched. The pinned upstream runtime currently exposes verified glass rendering for the navigation capsule and compatible miniplayer only. Other screens use YouTube Litho components and do not expose a verified general-purpose glass/blur hook in this patch baseline. Those screens must not be marked complete or given fake controls; each needs a verified component hook and device testing before it is shipped.

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
