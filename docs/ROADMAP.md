# VYRA YouTube implementation roadmap

## Milestone 0 — reproducible foundation
- [x] Create the project structure and pin upstream versions.
- [x] Keep user APKs, signing material, and generated packages out of Git.
- [x] Add guarded source overlay and CI validation.
- [x] Build the first VYRA .mpp bundle successfully.
- [ ] Add the original nine screen references and final logo/splash source assets to the design folder.

## Milestone 1 — VYRA settings shell
- [x] Rename the YouTube patch settings entry to **VYRA MOD**.
- [x] Organize General, Feed, Player, and Shorts categories under VYRA-branded names.
- [x] Add navigation animation, navigation style, Glass toggle, opacity, rounded capsule, and size preview controls to VYRA Appearance.
- [x] Expose Glass on/off, opacity, rounded capsule, and size preview (height, width, button spacing).
- [x] Set VYRA Glass defaults to clear opacity 14/100, rounded ends, and navigation animations ON while keeping Glass OFF until the user enables it.
- [x] Add the VYRA splash preference and connect it to the native YouTube Lottie hook.
- [ ] Verify all VYRA category screens in the patched app and confirm preferences persist after force-stop/relaunch.
- [ ] Verify Glass OFF restores the normal YouTube navigation bar.
- [ ] Verify the five native destinations and central Create action remain functional with the Glass capsule enabled.
- [ ] Verify the VYRA splash starts, completes, and falls back safely on the target device.

## Milestone 2 — complete VYRA appearance
- [ ] Implement only the approved five-item bottom capsule from the HTML reference; do not port the prototype's sample page content.
- [ ] Add VYRA theme mode and accent-color controls with persisted settings.
- [ ] Add icon/label styling controls only where a real upstream hook exists.
- [ ] Add animation speed/type controls only where they can be wired to runtime behavior.
- [ ] Add reset-to-VYRA-defaults action.
- [ ] Respect Android reduced-motion settings and provide a non-blur fallback.

## Milestone 3 — screen-by-screen visual layer
- [ ] Home/feed: black/silver surfaces, restrained dividers, cinematic video cards; preserve feed data and actions.
- [ ] Player: VYRA-styled controls and panels; preserve playback, captions, quality, speed, and casting.
- [ ] Shorts: consistent glass controls and overlays; preserve swipe/navigation behavior.
- [ ] Subscriptions and search: consistent typography, icon weights, and spacing.
- [ ] Library/profile: V cover/profile card treatment without changing account identity or account flows.
- [ ] Compare each screen with the user's nine supplied references before marking it complete.

## Milestone 4 — VYRA identity
- [ ] Integrate the supplied liquid-glass V launcher icon in all Android adaptive-icon densities.
- [x] Generate the approved 8-second splash as a native-compatible Lottie resource and wire it to the native splash hook.
- [ ] Verify the splash on-device for startup timing, rendering, and reduced-motion/fallback behavior.
- [ ] Reserve the glass-orb progress visual for real VYRA patch downloads; replace the HTML demo timer with actual byte progress.
- [ ] Do not ship a video splash if it causes startup delay, looping, or accessibility issues; use a short native animation/fallback.
- [ ] Reproduce and fix the previous missing drawable reference error (`$startup_animation_dark__9`) with a regression test.

## Milestone 5 — APK release verification
- [ ] Patch only a clean YouTube 21.30.216 APK.
- [ ] Compile resources without dangling drawable references.
- [ ] Sign using a user-controlled key stored outside Git.
- [ ] Install on Android 16 / API 36.
- [ ] Smoke-test cold start, home, search, Shorts, player, subscriptions, profile, settings, Glass ON/OFF, and account flows.
- [ ] Publish a signed APK only after all tests pass, with build provenance and checksum.
