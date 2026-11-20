# VYRA UI implementation specification

## Global visual language
- Apply one restrained Liquid Glass system across the complete YouTube interface, not only the bottom navigation: top app bars, search, category chips, feed cards and metadata surfaces, menus and sheets, player controls, Shorts action rail, subscription filters, Library/Profile surfaces, and VYRA MOD settings.
- Base: near-black / charcoal canvas with subtle gradients; keep large video/content areas visually clear rather than placing opaque glass panels over everything.
- Material: translucent silver/chrome glass, subtle background blur when supported, thin reflective rims, soft shadows, and layered depth. Use stronger glass for floating controls and overlays; lighter glass for chips, cards, and inline controls.
- Typography: clean sans-serif, wide letter spacing for brand headings, compact readable metadata, and strong contrast over moving video.
- Cards: cinematic edge-to-edge thumbnails with rounded corners; apply glass to supporting controls and metadata surfaces without obscuring thumbnails.
- Icons: consistent thin silver line icons; selected states use brighter silver fill/glow.
- Motion: smooth and restrained (about 260 ms where appropriate); respect Android reduced-motion settings and avoid animating every element at once.
- Accessibility: maintain readable contrast, touch targets, focus/selection states, and native YouTube accessibility semantics.
- Preserve stock YouTube behavior and appearance when VYRA mode is disabled.

## Screen references
### Home
- VYRA wordmark at the top left; cast, search, and profile actions at the top right in a subtle glass action group.
- Horizontal category chips use a light translucent glass treatment.
- Large cinematic video thumbnails remain visible; use glass only for duration badges, overflow actions, and compact metadata where legible.
- Floating glass bottom capsule with Home, Shorts, central V action, Subscriptions, and You.

### Player
- Large cinematic player remains unobstructed; transport controls and transient overlays use glass surfaces.
- Below: title, channel identity and subscribe action, compact action row, expandable description, and Up next list with restrained glass controls/cards.
- Keep all YouTube playback controls and behaviors intact: seek, pause, quality, captions, speed, cast, fullscreen, and rotation.

### Shorts
- Full-screen vertical video remains the dominant surface.
- Right-side action rail uses compact translucent glass buttons with strong contrast against video.
- Creator identity and subscribe action near the bottom use a subtle glass panel; keep swipe navigation and playback behavior unchanged.

### Subscriptions
- VYRA header with avatar/channel strip and light glass filter chips.
- Newest-first sort control and overflow actions use glass.
- Clean vertical list of cinematic video cards and creator metadata.

### Search
- Wide translucent search field with microphone action.
- Recent searches with clear/remove controls and suggested search chips use light glass surfaces, then results.
- Maintain native search submission, keyboard, voice search, and result navigation.

### Library
- Two-column cards for Watch history, Playlists, Downloads, and Liked videos; use restrained glass framing without obscuring artwork.
- Secondary rows for Your videos and Watch later.
- Keep counts, offline status, and navigation behavior supplied by YouTube.

### Profile / You
- VYRA cover banner with the glass V mark.
- Account avatar, display name, handle, subscriber count, and Edit profile action remain clear and legible.
- Manage Google Account and Your channel actions, followed by History, Playlists, Downloads, Settings, and Help; use consistent glass action surfaces.
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

## Approved visual direction
- The Sıvı Cam Alt Menü.html reference establishes the material language: clear silver glass, low tint, visible but restrained rim highlight, rounded ends, layered translucency, and smooth selection motion.
- Extend that same material language across the entire interface as described above. Do not copy the reference's demo page bodies, theme-picker/demo controls, or simulated interactions.
- Use stronger blur/translucency for floating navigation, action groups, dialogs, and player/Shorts overlays; use lighter glass borders and surfaces for chips, cards, and inline controls.
- Preserve native YouTube content hierarchy and real actions. Avoid a uniform opaque panel behind every section; the glass should create depth, not clutter.
- When VYRA glass is disabled, restore the original YouTube appearance and navigation.

## Implementation mapping and limits
- The current pinned Morphe stack already provides the Glass capsule renderer, opacity, corner shape, size/width/spacing preview, navigation animation toggle, player icon styles, Shorts icon styles, feed-card layout, player overlay opacity, and theme color preferences.
- Current VYRA overlay brands the settings entry as VYRA MOD and groups the existing General, Feed, Player, and Shorts settings under VYRA Appearance, VYRA Home & Feed, VYRA Player, and VYRA Shorts.
- The VYRA source overlay now wires a master glass setting to the floating bottom navigation renderer, the top toolbar, the injected wide-search field, native top/bottom player control views, and the Shorts lower action container. The VYRA splash resource and settings entry are also wired.
- These new toolbar/player hooks are source-level changes pending a fresh Morphe bundle build and APK runtime verification. Do not describe them as tested on-device until the patched 21.30.216 APK has been installed and exercised.
- Home feed cards, category chips, Shorts action rail, subscription filters, Library/Profile cards, and modal sheets still need their own verified component hooks. A full interface treatment must be implemented incrementally; do not claim those surfaces are glass-enabled yet.
- Do not replace server-driven layouts blindly; preserve accessibility, native interactions, account flows, and playback behavior.
- The exact custom animation speed/type, six-color accent palette, icon pack preview, and global Player appearance selector still require dedicated runtime settings and hooks; do not show these as implemented until their settings actually change the app.
- The 8-second splash concept is a visual reference only. Prefer Android's native startup surface and a short native-compatible transition rather than delaying app launch with a full-screen video.

## Asset references
- vyra_home.png
- vyra_player.png
- vyra_shorts.png
- vyra_subscriptions.png
- vyra_search.png
- vyra_library.png
- vyra_profile.png
- vyra_mod_settings.png
- vyra_liquid_glass_navigation.png
- vyra-glass-monogram.png
- vyra_splash_liquid.mp4

These references were supplied in the VYRA starter/mockup archives. Keep originals intact; use resized derivatives for Android resources and retain the source references for visual comparison.
