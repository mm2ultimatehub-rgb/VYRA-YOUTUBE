# VYRA updater integration contract

This repository currently contains a Morphe patch overlay and web design assets, not a standalone Android application module. The HTML updater is therefore a WebView presentation surface; Android must own network I/O, file storage, integrity checks, and package installation.

## Trusted bridge

Load the bundled asset from the app's local assets only (for example, `file:///android_asset/vyra-update.html`). Restrict WebView navigation to that local asset. Do not expose a JavaScript bridge to arbitrary websites.

Android calls these functions through `evaluateJavascript`:

- `window.VYRAUpdater.setProgress(downloadedBytes, totalBytes, speedBytesPerSecond)`
- `window.VYRAUpdater.setReady()` — call only after exact size, SHA-256, package ID, and signing-certificate checks pass.
- `window.VYRAUpdater.setStatus(message, detail)`
- `window.VYRAUpdater.setPaused()`
- `window.VYRAUpdater.setError(message)`

The page exposes one native action:

- `window.VYRAInstaller.installUpdate()` — invoke only after the native downloader has completed and verified the APK. The implementation must launch Android's package installer using a content URI from a narrowly scoped FileProvider and handle the user's confirmation flow.

## Required native update sequence

1. Fetch the HTTPS update manifest and validate its schema.
2. Compare the manifest version with the installed VYRA version.
3. Download the APK to app-private storage. Send actual byte counts and measured throughput to `setProgress`; never synthesize percentages.
4. Verify exact byte size and SHA-256 before enabling the install button.
5. Confirm package name and signing-certificate continuity with the installed package.
6. Request installation through Android's package installer. Android may require the user to enable “Install unknown apps” for this app and confirm the update; do not attempt silent installation.
7. Report cancellation/failure through `setError`, and delete partial or invalid downloads.

## Release requirements

A release must contain the APK as a release asset plus a manifest with a versioned, immutable asset URL and SHA-256. The existing CI currently publishes an `.mpp` Morphe patch bundle, not an APK. Do not point the updater at an `.mpp` file or label it as an APK.

## Security requirements

- HTTPS only; reject redirects to non-HTTPS destinations.
- Accept only the expected package ID.
- Require SHA-256 and exact size from the signed/trusted release metadata.
- Keep signing keys and tokens out of Git.
- Keep WebView debugging disabled in production and block external navigation.
- The APK update must be signed with the same signing certificate as the installed build.
