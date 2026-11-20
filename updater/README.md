# VYRA updater

The updater UI lives in `update-progress.html` and preserves the supplied liquid-glass orb/V animation. Unlike the original visual prototype, this page has no simulated download timer: its progress is driven only by native Android byte counts.

See [bridge-contract.md](bridge-contract.md) for the Android WebView contract and security requirements, and [update-manifest.schema.json](update-manifest.schema.json) for the release metadata format.

**Current limitation:** the repository builds and publishes a Morphe `.mpp` patch bundle. It does not contain an Android app module or a verified signed APK release. The updater must not install an `.mpp` file. Native Android integration and a same-certificate APK release are still required.
