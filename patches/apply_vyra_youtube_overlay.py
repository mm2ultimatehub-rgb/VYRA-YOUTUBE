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
        navPreferences += SwitchPreference("morphe_hide_navigation_new_content_dot")'''
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
                    ListPreference("morphe_navigation_bar_style"),
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

# Give the existing player, Shorts, and feed icon/layout preferences their own
# VYRA sub-screens. These controls reuse upstream preference keys and runtime
# implementations; no decorative-only switches are introduced.
PLAYER_ICONS = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/player/icons/PlayerIconStylePatch.kt"
SHORTS_ICONS = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/shortsicons/ShortsIconStylePatch.kt"
FEED_CARDS = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/feedcards/FeedCardLayoutPatch.kt"
THEME_PATCH = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/theme/ThemePatch.kt"

def move_preference_to_vyra_screen(path: Path, old: str, new: str, imports: tuple[str, ...]) -> None:
    content = path.read_text(encoding="utf-8")
    if content.count(old) != 1:
        fail(f"expected one preference registration in {path.name}")
    content = content.replace(old, new, 1)
    for line in imports:
        if line not in content:
            import_anchor = "import app.morphe.patches.shared.misc.settings.preference."
            index = content.find(import_anchor)
            if index < 0:
                fail(f"could not find preference imports in {path.name}")
            content = content[:index] + line + "\n" + content[index:]
    path.write_text(content, encoding="utf-8")

move_preference_to_vyra_screen(
    PLAYER_ICONS,
    """        PreferenceScreen.PLAYER.addPreferences(
            if (customPlayerIcons == null) {""",
    """        val vyraPlayerIconPreference = if (customPlayerIcons == null) {""",
    (
        "import app.morphe.patches.shared.misc.settings.preference.PreferenceScreenPreference",
        "import app.morphe.patches.shared.misc.settings.preference.PreferenceScreenPreference.Sorting",
    ),
)
player_end = """            }
        )

        // The base icons are the Thin style"""
player_replacement = """            }
        PreferenceScreen.GENERAL.addPreferences(
            PreferenceScreenPreference(
                key = "vyra_player_screen",
                titleKey = "vyra_player_title",
                sorting = Sorting.UNSORTED,
                preferences = mutableSetOf(vyraPlayerIconPreference)
            )
        )

        // The base icons are the Thin style"""
if PLAYER_ICONS.read_text(encoding="utf-8").count(player_end) != 1:
    fail("player icon preference closing anchor changed")
PLAYER_ICONS.write_text(PLAYER_ICONS.read_text(encoding="utf-8").replace(player_end, player_replacement, 1), encoding="utf-8")

move_preference_to_vyra_screen(
    SHORTS_ICONS,
    """        PreferenceScreen.SHORTS.addPreferences(
            if (custom == null) {""",
    """        val vyraShortsIconPreference = if (custom == null) {""",
    (
        "import app.morphe.patches.shared.misc.settings.preference.PreferenceScreenPreference",
        "import app.morphe.patches.shared.misc.settings.preference.PreferenceScreenPreference.Sorting",
    ),
)
shorts_end = """            }
        )

        copyIconStyles("""
shorts_replacement = """            }
        PreferenceScreen.GENERAL.addPreferences(
            PreferenceScreenPreference(
                key = "vyra_shorts_screen",
                titleKey = "vyra_shorts_title",
                sorting = Sorting.UNSORTED,
                preferences = mutableSetOf(vyraShortsIconPreference)
            )
        )

        copyIconStyles("""
if SHORTS_ICONS.read_text(encoding="utf-8").count(shorts_end) != 1:
    fail("Shorts icon preference closing anchor changed")
SHORTS_ICONS.write_text(SHORTS_ICONS.read_text(encoding="utf-8").replace(shorts_end, shorts_replacement, 1), encoding="utf-8")

move_preference_to_vyra_screen(
    FEED_CARDS,
    """        PreferenceScreen.FEED.addPreferences(
            ListPreference("morphe_feed_card_layout")
        )""",
    """        PreferenceScreen.GENERAL.addPreferences(
            PreferenceScreenPreference(
                key = "vyra_feed_screen",
                titleKey = "vyra_feed_title",
                sorting = Sorting.UNSORTED,
                preferences = mutableSetOf(ListPreference("morphe_feed_card_layout"))
            )
        )""",
    (
        "import app.morphe.patches.shared.misc.settings.preference.PreferenceScreenPreference",
        "import app.morphe.patches.shared.misc.settings.preference.PreferenceScreenPreference.Sorting",
    ),
)

theme_content = THEME_PATCH.read_text(encoding="utf-8")
theme_old = """        PreferenceScreen.GENERAL.addPreferences(
            *colorPreferences,
            SwitchPreference("morphe_gradient_loading_screen", summary = true)
        )"""
theme_new = """        PreferenceScreen.GENERAL.addPreferences(
            PreferenceScreenPreference(
                key = "vyra_theme_screen",
                titleKey = "vyra_theme_title",
                sorting = Sorting.UNSORTED,
                preferences = colorPreferences.toMutableSet().apply {
                    add(SwitchPreference("morphe_gradient_loading_screen", summary = true))
                }
            )
        )"""
if theme_content.count(theme_old) != 1:
    fail("theme settings insertion anchor changed")
theme_content = theme_content.replace(theme_old, theme_new, 1)
for line in (
    "import app.morphe.patches.shared.misc.settings.preference.PreferenceScreenPreference",
    "import app.morphe.patches.shared.misc.settings.preference.PreferenceScreenPreference.Sorting",
):
    if line not in theme_content:
        import_anchor = "import app.morphe.patches.shared.misc.settings.preference."
        index = theme_content.find(import_anchor)
        if index < 0:
            fail("could not find theme preference imports")
        theme_content = theme_content[:index] + line + "\n" + theme_content[index:]
THEME_PATCH.write_text(theme_content, encoding="utf-8")

xml = YOUTUBE_STRINGS.read_text(encoding="utf-8")
for key, value in (
    ("vyra_player_title", "VYRA Player"),
    ("vyra_shorts_title", "VYRA Shorts"),
    ("vyra_feed_title", "VYRA Home & Feed"),
    ("vyra_theme_title", "VYRA Theme"),
):
    if f'name="{key}"' not in xml:
        xml = xml.replace("</resources>", f'    <string name="{key}">{value}</string>\n</resources>', 1)
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
