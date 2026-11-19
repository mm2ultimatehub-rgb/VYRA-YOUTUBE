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
- [ ] Verify all VYRA category screens in the patched app and confirm preferences persist after force-stop/relaunch.
- [ ] Verify Glass OFF restores the normal YouTube navigation bar.

## Milestone 2 — complete VYRA appearance
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
- [ ] Convert the approved 8-second splash direction to native-compatible Android resources.
- [ ] Do not ship a video splash if it causes startup delay, looping, or accessibility issues; use a short native animation/fallback.
- [ ] Reproduce and fix the previous missing drawable reference error (`$startup_animation_dark__9`) with a regression test.

## Milestone 5 — APK release verification
- [ ] Patch only a clean YouTube 21.30.216 APK.
- [ ] Compile resources without dangling drawable references.
- [ ] Sign using a user-controlled key stored outside Git.
- [ ] Install on Android 16 / API 36.
- [ ] Smoke-test cold start, home, search, Shorts, player, subscriptions, profile, settings, Glass ON/OFF, and account flows.
- [ ] Publish a signed APK only after all tests pass, with build provenance and checksum.