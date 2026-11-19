# Implementation roadmap

## Milestone 0 — foundation
- [x] Create project layout and record target versions.
- [x] Prepare validation workflow and ignore proprietary inputs.
- [ ] Upload the nine mockups and branding assets to this repository.

## Milestone 1 — reproduce and fix patch compilation
- [ ] Validate a clean original YouTube 21.30.216 APK locally.
- [ ] Run the pinned patcher with the smallest supported patch set.
- [ ] Reproduce the missing $startup_animation_dark__9 resource error.
- [ ] Trace the missing resource reference and generated file mapping; add a regression test.
- [ ] Produce a compiled and signed baseline APK before branding changes.

## Milestone 2 — VYRA settings and navigation
- [ ] Add VYRA MOD without changing default YouTube appearance.
- [ ] Wire Liquid Glass enable/disable to the actual navigation renderer.
- [ ] Add opacity, capsule style, animation, accent color, and reset preferences.
- [ ] Verify persistence and reversibility.

## Milestone 3 — player and surfaces
- [ ] Adapt player controls while preserving playback behavior.
- [ ] Adapt profile/library/search/subscriptions/Shorts where upstream hooks permit.
- [ ] Verify dark/light/system behavior and accessibility fallbacks.

## Milestone 4 — VYRA identity
- [ ] Generate launcher icon assets from the supplied glass V mark.
- [ ] Convert the splash prototype to a native-compatible startup treatment.
- [ ] Verify cold start, warm start, timing, and no looping.

## Milestone 5 — release verification
- [ ] Build from a clean input APK.
- [ ] Sign with a user-controlled key (never commit it).
- [ ] Install and test on Android 16 / API 36.
- [ ] Verify package, version, launch, feed, playback, navigation, settings, and account flows.
- [ ] Publish only a verified APK and build metadata.
