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