#!/usr/bin/env python3
"""Apply the pinned VYRA settings overlay to a Morphe Patches checkout.

This deliberately edits only checked upstream anchors. If upstream changes,
fail closed rather than silently producing a partial patch.
"""
from pathlib import Path
import sys

ROOT = Path.cwd()
NAV = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/buttons/navigation/NavigationBarPatch.kt"
SETTINGS = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/misc/settings/SettingsPatch.kt"
YOUTUBE_STRINGS = ROOT / "patches/src/main/resources/addresources/values/youtube/strings.xml"
PATCH_BUILD = ROOT / "patches/build.gradle.kts"

def fail(message: str) -> None:
    print(f"VYRA overlay error: {message}", file=sys.stderr)
    raise SystemExit(2)

for path in (NAV, SETTINGS, YOUTUBE_STRINGS, PATCH_BUILD):
    if not path.is_file():
        fail(f"missing pinned upstream file: {path}")

source = NAV.read_text(encoding="utf-8")
old_group = '''        navPreferences += listOf(
            SwitchPreference("morphe_hide_navigation_new_content_dot"),
            SwitchPreference("morphe_navigation_bar_animations", summary = true),
            ListPreference("morphe_navigation_bar_style"),
            SwitchPreference("morphe_navigation_bar_glass", summary = true),
            NonInteractivePreference(
                key = "morphe_navigation_bar_glass_opacity",
                tag = "app.morphe.extension.shared.settings.preference.SeekBarPreference"
            ),
            SwitchPreference("morphe_navigation_bar_glass_round", summary = true),
            // Height, width and button spacing, with a preview.
            NonInteractivePreference(
                key = "morphe_navigation_bar_glass_height",
                titleKey = "morphe_navigation_bar_glass_size_title",
                summaryKey = "morphe_navigation_bar_glass_size_summary",
                tag = "app.morphe.extension.youtube.settings.preference.YouTubeGlassNavigationBarPreference",
                selectable = true
            )
        )'''
new_group = '''        // Keep ordinary navigation controls in General. VYRA appearance controls
        // are registered on their own screen below.
        navPreferences += listOf(
            SwitchPreference("morphe_hide_navigation_new_content_dot"),
            ListPreference("morphe_navigation_bar_style")
        )'''
if source.count(old_group) != 1:
    fail("the pinned NavigationBarPatch preference block changed; refusing a partial edit")
source = source.replace(old_group, new_group, 1)

anchor = '''        )

        // Swap create with notifications button.'''
addition = '''        )

        // VYRA-owned appearance screen. Keep original preference keys because the
        // upstream Glass navigation renderer reads these exact values.
        PreferenceScreen.GENERAL.addPreferences(
            PreferenceScreenPreference(
                key = "vyra_appearance_screen",
                titleKey = "vyra_appearance_title",
                sorting = Sorting.UNSORTED,
                preferences = mutableSetOf(
                    SwitchPreference("morphe_navigation_bar_animations", summary = true),
                    SwitchPreference("morphe_navigation_bar_glass", summary = true),
                    NonInteractivePreference(
                        key = "morphe_navigation_bar_glass_opacity",
                        tag = "app.morphe.extension.shared.settings.preference.SeekBarPreference"
                    ),
                    SwitchPreference("morphe_navigation_bar_glass_round", summary = true),
                    NonInteractivePreference(
                        key = "morphe_navigation_bar_glass_height",
                        titleKey = "morphe_navigation_bar_glass_size_title",
                        summaryKey = "morphe_navigation_bar_glass_size_summary",
                        tag = "app.morphe.extension.youtube.settings.preference.YouTubeGlassNavigationBarPreference",
                        selectable = true
                    )
                )
            )
        )

        // Swap create with notifications button.'''
if source.count(anchor) != 1:
    fail("navigation settings insertion anchor changed; review upstream before applying")
NAV.write_text(source.replace(anchor, addition, 1), encoding="utf-8")

settings = SETTINGS.read_text(encoding="utf-8")
old_title = 'titleKey = "morphe_settings_title"'
if settings.count(old_title) != 2:
    fail("expected exactly two YouTube root-title references in SettingsPatch.kt")
SETTINGS.write_text(settings.replace(old_title, 'titleKey = "vyra_settings_title"'), encoding="utf-8")

xml = YOUTUBE_STRINGS.read_text(encoding="utf-8")
if 'name="vyra_settings_title"' not in xml:
    xml = xml.replace("<resources>", '<resources>\n    <string name="vyra_settings_title" translatable="false">VYRA MOD</string>', 1)
if 'name="vyra_appearance_title"' not in xml:
    xml = xml.replace("</resources>", '    <string name="vyra_appearance_title">VYRA Appearance</string>\n</resources>', 1)
if 'name="vyra_settings_title"' not in xml or 'name="vyra_appearance_title"' not in xml:
    fail("failed to add VYRA YouTube-only string resources")
YOUTUBE_STRINGS.write_text(xml, encoding="utf-8")

build_script = PATCH_BUILD.read_text(encoding="utf-8")
metadata_replacements = {
    'name = "Morphe Patches"': 'name = "VYRA YouTube Patches"',
    'description = "Patches for Morphe"': 'description = "VYRA visual and experience patches for YouTube"',
    'source = "git@github.com:MorpheApp/morphe-patches.git"': 'source = "https://github.com/mm2ultimatehub-rgb/VYRA-YOUTUBE"',
    'author = "MorpheApp"': 'author = "VYRA Project"',
}
for old, new in metadata_replacements.items():
    if build_script.count(old) != 1:
        fail(f"expected exactly one patch bundle metadata anchor: {old}")
    build_script = build_script.replace(old, new, 1)
PATCH_BUILD.write_text(build_script, encoding="utf-8")
print("VYRA overlay applied: YouTube settings title, Appearance screen and bundle identity are wired.")
