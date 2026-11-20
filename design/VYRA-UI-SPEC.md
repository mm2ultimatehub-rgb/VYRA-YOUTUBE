# VYRA UI implementation specification

## Global visual language
- Base: near-black / charcoal surfaces with subtle gradients, not purple or neon.
- Material: restrained silver/chrome highlights, glass rims, translucent floating surfaces, soft shadows.
- Typography: clean sans-serif; wide letter spacing for brand headings, compact readable metadata.
- Cards: cinematic edge-to-edge thumbnails, rounded corners, thin low-contrast outlines.
- Icons: consistent thin silver line icons; selected states use brighter silver fill/glow.
- Motion: smooth and restrained; respect Android reduced-motion settings.
- Preserve the stock YouTube experience when VYRA mode is disabled.

## Screen references

### Home
- VYRA wordmark at the top left; cast, search, and profile actions at the top right.
- Horizontal category chips: All, Music, Gaming, Live, Podcasts, Mixes.
- Large cinematic video thumbnails with rounded corners, duration, title, channel avatar, views, and overflow menu.
- Floating glass bottom capsule with Home, Shorts, central V action, Subscriptions, and Library.

### Player
- Large cinematic player surface with subtle overlay controls.
- Below: title, channel identity and subscribe action, compact action row, expandable description, and Up next list.
- Keep all YouTube playback controls and behaviors intact: seek, pause, quality, captions, speed, cast, fullscreen, and rotation.

### Shorts
- Full-screen vertical video with dark cinematic treatment.
- Right-side action rail for like/dislike, comments, share, remix, and related actions.
- Creator identity and subscribe action near the bottom; keep swipe navigation and playback behavior unchanged.

### Subscriptions
- VYRA header with avatar/channel strip.
- Filter chips such as All and Today, plus a newest-first sort control.
- Clean vertical list of cinematic video cards and creator metadata.

### Search
- Wide translucent search field with microphone action.
- Recent searches with clear/remove controls, suggested search chips, then results.
- Maintain native search submission, keyboard, voice search, and result navigation.

### Library
- Two-column cards for Watch history, Playlists, Downloads, and Liked videos.
- Secondary rows for Your videos and Watch later.
- Keep counts, offline status, and navigation behavior supplied by YouTube.

### Profile / You
- VYRA cover banner with the glass V mark.
- Account avatar, display name, handle, subscriber count, and Edit profile action.
- Manage Google Account and Your channel actions, followed by History, Playlists, Downloads, Settings, and Help.
- Never alter account identity or Google account flows.

### VYRA MOD
- Header: glass V mark, VYRA MOD, and the subtitle 'YouTube, Reimagined'.
- Liquid Glass master control and opacity slider.
- Navigation choices: Default, Floating Capsule, Minimal.
- Animation style and speed selectors.
- Accent palette: Silver, Graphite, Red, Blue, Green, Amber.
- Icon customization selector with preview.
- Player appearance selector with preview.
- Reset to VYRA defaults.

## Approved prototype scope
- From `Sıvı Cam Alt Menü.html`, use only the bottom navigation capsule: five native YouTube destinations (Home, Shorts, Create, Subscriptions, You), the central Create action, selected-tab movement, and the translucent glass surface. Do not port the sample Home/Shorts/Subscriptions page mockups or its theme-picker/demo controls.
- The capsule should read as clear silver glass rather than a dark slab: low tint/opacity, visible but restrained rim highlight, rounded ends, and smooth selection motion. Preserve the upstream Glass renderer and real YouTube navigation actions.
- Keep the original YouTube navigation when Glass is disabled. The Glass preference stays OFF by default; when enabled, VYRA defaults use a more transparent opacity (14/100), rounded ends, and navigation animations enabled.
- From `yukleme-animasyonu.html`, use only the glass orb, circular progress ring, percentage, and completion/check animation as the visual for a future VYRA patch-download/update progress surface. Do not port its sample stage, replay demo, decorative theme, or fixed 5.4-second/48 MB simulated progress. Any shipped progress must be driven by actual byte/download progress.
- The loading orb is not the YouTube launch splash. Keep startup branding separate; do not delay YouTube launch by running a fake download animation.

## Implementation mapping and limits
- The current pinned Morphe stack already provides the Glass capsule renderer, opacity, corner shape, size/width/spacing preview, navigation animation toggle, player icon styles, Shorts icon styles, feed-card layout, player overlay opacity, and theme color preferences.
- Current VYRA overlay brands the settings entry as VYRA MOD and groups the existing General, Feed, Player, and Shorts settings under VYRA Appearance, VYRA Home & Feed, VYRA Player, and VYRA Shorts.
- The reference's exact custom animation speed/type, six-color accent palette, icon pack preview, and global Player appearance selector still require dedicated runtime settings and hooks; do not show these as implemented until their settings actually change the app.
- A full screen redesign requires verified hooks for the relevant YouTube UI components. Avoid replacing server-driven layouts blindly; preserve accessibility and interaction semantics.
- The 8-second splash concept is a visual reference only. Prefer Android's native startup surface and a short native-compatible transition rather than delaying app launch with a full-screen video.

## Asset references
- `vyra_home.png`
- `vyra_player.png`
- `vyra_shorts.png`
- `vyra_subscriptions.png`
- `vyra_search.png`
- `vyra_library.png`
- `vyra_profile.png`
- `vyra_mod_settings.png`
- `vyra_liquid_glass_navigation.png`
- `vyra-glass-monogram.png`
- `vyra_splash_liquid.mp4`

These references were supplied in the VYRA starter/mockup archives. Keep originals intact; use resized derivatives for Android resources and retain the source references for visual comparison.

## VYRA Full Liquid Glass system — new approved scope

The previous bottom-navigation-only prototype scope is superseded by this requirement. VYRA Liquid Glass must be a coherent, app-wide visual layer, not a navigation-bar skin.

### Global material contract
- Use a black/graphite foundation with clear silver glass; no purple/neon styling.
- Apply translucent glass material to YouTube-owned UI surfaces throughout Home/feed, search, player controls and sheets, Shorts controls, subscriptions, Library, profile/You, and VYRA settings.
- Glass surfaces use layered translucency, background sampling/blur where supported, a fine silver rim, restrained specular highlights, soft elevation, and consistent corner radii. Avoid opaque dark slabs.
- Preserve readable contrast and text/icon legibility. Use a non-blur translucent fallback on devices or surfaces where blur is unavailable or too expensive.
- Do not blur, tint, crop, or otherwise alter video frames, thumbnails, channel artwork, or user-provided media. Glass applies to UI chrome and panels only.
- Preserve native YouTube actions, accessibility labels, focus/keyboard behavior, scrolling, playback, gestures, and account flows.

### Required screen coverage
- Home/feed: app bars, search affordance, category chips, feed cards' UI chrome, overflow sheets, dialogs, and bottom navigation.
- Search: search field, filters/chips, suggestion and history surfaces, result actions, and menus.
- Player: player overlay controls, action rows, channel/description panels, settings sheets, quality/captions/speed menus, and Up next panels.
- Shorts: action rail surfaces, creator/metadata overlays, comments/share/remix sheets, and menus.
- Subscriptions: header controls, filters, feed actions, and menus.
- Library and Profile/You: cards, list containers, action surfaces, account/settings entry points, and dialogs.
- Settings and VYRA MOD: preference rows, dialogs, selectors, sliders, and preview surfaces.

### Verified runtime coverage — current pinned baseline

The pinned Morphe 2.3.0 source provides a real Glass capsule renderer for the bottom navigation and a compatible Glass miniplayer renderer. The current VYRA implementation adds an OFF-by-default master gate around those two verified surfaces. Enabling it does not claim to glass-style every YouTube screen.

No general-purpose, app-wide blur/material hook has been verified for the target YouTube Litho surfaces. Home/feed cards, Search, Shorts action rail, Subscriptions, Library, Profile, dialogs, and menus remain unimplemented until a safe component-specific hook is identified and tested. Do not simulate this with a global overlay, blanket background replacement, or fake settings.

### Master control and behavior
- Add one persisted VYRA Liquid Glass master switch under YouTube Settings > VYRA MOD.
- Master switch defaults OFF to preserve stock YouTube on first launch. OFF must restore original view backgrounds, elevations, and navigation appearance.
- When ON, apply the glass material consistently to every verified supported surface. Do not expose a screen as complete until its runtime hooks are implemented and tested.
- Provide global glass opacity/intensity and blur strength controls only where they are actually wired to the runtime renderer. Provide a reduced-motion / reduced-transparency fallback and honor Android accessibility settings.
- Keep navigation-specific shape, animation, and sizing controls as refinements, not as the whole Liquid Glass feature.

### Implementation and verification rules
- Build a screen-by-screen hook inventory against the pinned YouTube 21.30.216 and Morphe Patches 2.3.0 sources before editing runtime behavior.
- Use narrowly scoped, version-guarded hooks; fail closed when an upstream fingerprint changes.
- Avoid blind global resource replacement and avoid changing server-driven content layouts.
- Add runtime tests or deterministic patch checks for each screen family and for master ON/OFF restoration.
- The .mpp bundle is only the patch package. A release APK is separate and must be built from a clean matching YouTube APK, signed, installed, launched, and smoke-tested before being called complete.
