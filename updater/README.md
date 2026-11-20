# VYRA updater

The updater UI lives in `update-progress.html` and preserves the supplied liquid-glass orb/V animation. Unlike the original visual prototype, this page has no simulated download timer: its progress is driven only by native Android byte counts.

See [bridge-contract.md](bridge-contract.md) for the Android WebView contract and security requirements, and [update-manifest.schema.json](update-manifest.schema.json) for the release metadata format.

**Current limitation:** the repository builds and publishes a Morphe `.mpp` patch bundle. It does not contain an Android app module or a verified signed APK release. The updater must not install an `.mpp` file. Native Android integration and a same-certificate APK release are still required.

## Native Android companion app

A separate Android project now lives at the repository root (app/, settings.gradle.kts, and build.gradle.kts). It embeds the liquid-glass progress UI locally, fetches the HTTPS manifest, streams real download progress, checks byte count and SHA-256, checks the APK package ID and installed signing certificate, then launches Android's user-confirmed package installer. CI builds a debug companion APK artifact.

Important: this is a VYRA Updater companion APK, not a patched YouTube APK. It cannot replace an existing YouTube installation unless the downloaded APK has the same package ID and signing certificate as the installed app. A public update manifest and a compatible signed VYRA YouTube APK have not yet been published, so the updater will not complete an install today. The companion app's own debug APK is not a production-signed release.
