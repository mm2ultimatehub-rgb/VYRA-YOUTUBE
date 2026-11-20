#!/usr/bin/env python3
"""Integrate the native VYRA APK updater into the patched YouTube application."""
from pathlib import Path
import os
import shutil
import sys
import xml.etree.ElementTree as ET

UPSTREAM = Path(sys.argv[1]).resolve()
PROJECT = Path(sys.argv[2]).resolve()

def fail(message: str) -> None:
    raise SystemExit(f"VYRA updater integration error: {message}")

def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        fail(f"expected one {label} anchor, found {count}")
    return source.replace(old, new, 1)

# Compile the updater Activity into the same DEX as the YouTube extension.
activity_source = PROJECT / "patches/extension-src/VYRAUpdateActivity.java"
activity_target = UPSTREAM / "extensions/youtube/src/main/java/app/morphe/extension/youtube/updater/VYRAUpdateActivity.java"
if not activity_source.is_file():
    fail(f"missing updater Activity source: {activity_source}")
activity_target.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(activity_source, activity_target)

# Compile against AndroidX Core's FileProvider already supplied by YouTube at runtime.
extension_build = UPSTREAM / "extensions/youtube/build.gradle.kts"
gradle = extension_build.read_text(encoding="utf-8")
dependency_anchor = "    implementation(libs.annotation)"
if gradle.count(dependency_anchor) != 1:
    fail("YouTube extension dependency anchor changed")
gradle = gradle.replace(
    dependency_anchor,
    '    compileOnly("androidx.core:core:1.15.0")\\n' + dependency_anchor,
    1,
)
extension_build.write_text(gradle, encoding="utf-8")

# The updater WebView is bundled locally; it never loads remote HTML or scripts.
html_source = PROJECT / "app/src/main/assets/vyra-update.html"
raw_dir = UPSTREAM / "patches/src/main/resources/custom-branding/raw"
raw_dir.mkdir(parents=True, exist_ok=True)
shutil.copyfile(html_source, raw_dir / "vyra_update.html")

xml_dir = UPSTREAM / "patches/src/main/resources/settings/xml"
xml_dir.mkdir(parents=True, exist_ok=True)
(xml_dir / "vyra_updater_file_paths.xml").write_text(
    '<?xml version="1.0" encoding="utf-8"?>\n'
    '<paths xmlns:android="http://schemas.android.com/apk/res/android">'
    '<files-path name="updates" path="updates/"/>'
    '</paths>\n',
    encoding="utf-8",
)

# Make the bundled HTML available as an Android raw resource.
splash_resources = UPSTREAM / "patches/src/main/kotlin/app/morphe/patches/shared/layout/branding/StartupAnimationResourcePatch.kt"
source = splash_resources.read_text(encoding="utf-8")
source = replace_once(
    source,
    '"morphe_startup_animation_play.json"',
    '"morphe_startup_animation_play.json",\n                "vyra_update.html"',
    "VYRA updater HTML resource",
)
splash_resources.write_text(source, encoding="utf-8")

settings_path = UPSTREAM / "patches/src/main/kotlin/app/morphe/patches/youtube/misc/settings/SettingsPatch.kt"
settings = settings_path.read_text(encoding="utf-8")

# Add a VYRA Updates row to the existing VYRA MOD settings screen.
preference_anchor = '            SwitchPreference("vyra_glass_mode", summary = true),'
settings = replace_once(
    settings,
    preference_anchor,
    preference_anchor + """
            IntentPreference(
                key = "vyra_updates",
                titleKey = "vyra_updates_title",
                summaryKey = "vyra_updates_summary",
                intent = IntentPreference.Intent(
                    data = "",
                    targetClass = "app.morphe.extension.youtube.updater.VYRAUpdateActivity",
                    targetPackageSupplier = { "app.vyra.youtube" }
                )
            ),""",
    "VYRA updater preference",
)

# Register the in-app screen and a private FileProvider for the verified APK.
manifest_anchor = '            apiActivity.setAttribute("android:theme", "@style/Theme.AppCompat.DayNight.NoActionBar")'
settings = replace_once(
    settings,
    manifest_anchor,
    manifest_anchor + """
            manifest.insertChild(0, "uses-permission") {
                setAttribute("android:name", "android.permission.REQUEST_INSTALL_PACKAGES")
            }
            val application = apiActivity.parent!!
            application.appendChild("activity") {
                setAttribute("android:name", "app.morphe.extension.youtube.updater.VYRAUpdateActivity")
                setAttribute("android:exported", "false")
                setAttribute("android:theme", "@android:style/Theme.Material.NoActionBar")
            }
            application.appendChild("provider") {
                setAttribute("android:name", "androidx.core.content.FileProvider")
                setAttribute("android:authorities", "app.vyra.youtube.vyra.updater.fileprovider")
                setAttribute("android:exported", "false")
                setAttribute("android:grantUriPermissions", "true")
                appendChild("meta-data") {
                    setAttribute("android:name", "android.support.FILE_PROVIDER_PATHS")
                    setAttribute("android:resource", "@xml/vyra_updater_file_paths")
                }
            }""",
    "VYRA updater manifest",
)

copy_anchor = """        )

        // Remove horizontal divider from the settings Preferences"""
settings = replace_once(
    settings,
    copy_anchor,
    """        )
        copyResources("settings", ResourceGroup("xml", "vyra_updater_file_paths.xml"))

        // Remove horizontal divider from the settings Preferences""",
    "VYRA updater FileProvider XML",
)
settings_path.write_text(settings, encoding="utf-8")

# A monotonically increasing CI run number distinguishes successive builds even
# when the upstream YouTube versionName remains unchanged.
build_number = os.environ.get("VYRA_BUILD_NUMBER", "1")
if not build_number.isdigit():
    fail("VYRA_BUILD_NUMBER must be an integer")

resources = [
    UPSTREAM / "patches/src/main/resources/addresources/values/youtube/strings.xml",
    UPSTREAM / "patches/src/main/resources/addresources/values-tr-rTR/youtube/strings.xml",
]
for index, path in enumerate(resources):
    xml = path.read_text(encoding="utf-8")
    labels = (
        ("vyra_updates_title", "VYRA Güncellemeleri" if index else "VYRA Updates"),
        ("vyra_updates_summary", "Sürümü kontrol et ve yeni VYRA sürümünü yükle" if index else "Check for and install new VYRA releases"),
        ("vyra_build_number", build_number),
    )
    for key, value in labels:
        if f'name="{key}"' not in xml:
            xml = xml.replace("</resources>", f'    <string name="{key}">{value}</string>\n</resources>', 1)
    path.write_text(xml, encoding="utf-8")
    ET.parse(path)

print(f"Integrated VYRA updater Activity and UI (build {build_number}).")
