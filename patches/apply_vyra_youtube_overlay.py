#!/usr/bin/env python3
"""Apply the pinned VYRA settings overlay to a Morphe Patches checkout.

This deliberately edits only checked upstream anchors. If upstream changes,
fail closed rather than silently producing a partial patch.
"""
from pathlib import Path
import sys
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path.cwd()
NAV = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/buttons/navigation/NavigationBarPatch.kt"
SETTINGS = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/misc/settings/SettingsPatch.kt"
BRANDING = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/branding/CustomBrandingPatch.kt"
SEEKBAR = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/seekbar/SeekbarColorPatch.kt"
SPLASH_PATCH = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/theme/SplashAnimationPatch.kt"
SPLASH_RESOURCES = ROOT / "patches/src/main/kotlin/app/morphe/patches/shared/layout/branding/StartupAnimationResourcePatch.kt"
GLOW_RESOURCES = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/layout/theme/GlowMorpheAnimationPatch.kt"
VYRA_LOGO = ROOT.parent / "vyra-youtube/branding/assets/vyra-glass-monogram-256.webp"
SETTINGS_LOGO = ROOT / "patches/src/main/resources/settings/drawable/vyra_glass_monogram.webp"
YOUTUBE_STRINGS = ROOT / "patches/src/main/resources/addresources/values/youtube/strings.xml"
SPLASH_STRINGS = ROOT / "patches/src/main/resources/addresources/values/shared-youtube/strings.xml"
PATCH_BUILD = ROOT / "patches/build.gradle.kts"
EXTENSION_SETTINGS = ROOT / "extensions/youtube/src/main/java/app/morphe/extension/youtube/settings/Settings.java"
EXTENSION_NAVIGATION = ROOT / "extensions/youtube/src/main/java/app/morphe/extension/youtube/patches/NavigationBarPatch.java"
EXTENSION_THEME = ROOT / "extensions/youtube/src/main/java/app/morphe/extension/youtube/patches/theme/ThemePatch.java"
EXTENSION_WIDE_SEARCH = ROOT / "extensions/youtube/src/main/java/app/morphe/extension/youtube/patches/WideSearchBarPatch.java"
EXTENSION_PLAYER = ROOT / "extensions/youtube/src/main/java/app/morphe/extension/youtube/patches/LegacyPlayerControlsPatch.java"
EXTENSION_GLASS_NAV = ROOT / "extensions/youtube/src/main/java/app/morphe/extension/youtube/patches/YouTubeGlassNavigationBar.java"
PLAYER_PATCH = ROOT / "patches/src/main/kotlin/app/morphe/patches/youtube/misc/playercontrols/LegacyPlayerControlsPatch.kt"
NAVIGATION_RESOURCES = ROOT / "patches/src/main/resources/navigationbar/drawable"

def fail(message: str) -> None:
    print(f"VYRA overlay error: {message}", file=sys.stderr)
    raise SystemExit(2)

for path in (NAV, SETTINGS, BRANDING, SEEKBAR, SPLASH_PATCH, SPLASH_RESOURCES, GLOW_RESOURCES, YOUTUBE_STRINGS, SPLASH_STRINGS, PATCH_BUILD, EXTENSION_SETTINGS, EXTENSION_NAVIGATION, EXTENSION_THEME, EXTENSION_WIDE_SEARCH, EXTENSION_PLAYER, EXTENSION_GLASS_NAV, PLAYER_PATCH):
    if not path.is_file():
        fail(f"missing pinned upstream file: {path}")

# Keep the native YouTube splash hook, but strip the newer Rive-only branch.
# The VYRA animation is a self-contained Lottie composition supported by 21.30.216.
branding = BRANDING.read_text(encoding="utf-8")
splash_import = "import app.morphe.patches.youtube.layout.theme.splashAnimationPatch" + chr(10)
if branding.count(splash_import) != 1:
    fail("expected one upstream splashAnimationPatch import")
splash_dependency = "            // Owns the hook that loads the startup animation." + chr(10) + "            splashAnimationPatch," + chr(10)
if branding.count(splash_dependency) != 1:
    fail("expected one upstream splashAnimationPatch dependency")
BRANDING.write_text(branding, encoding="utf-8")

seekbar = SEEKBAR.read_text(encoding="utf-8")
if seekbar.count(splash_import) != 1:
    fail("expected one splashAnimationPatch import in SeekbarColorPatch")
seekbar_dependency = "        // Owns the hook that loads the splash screen animation." + chr(10) + "        splashAnimationPatch," + chr(10)
if seekbar.count(seekbar_dependency) != 1:
    fail("expected one splashAnimationPatch dependency in SeekbarColorPatch")
SEEKBAR.write_text(seekbar, encoding="utf-8")

splash = SPLASH_PATCH.read_text(encoding="utf-8")
rive_dependency = "        startupAnimationResourcePatch,\n        glowMorpheAnimationResourcePatch"
if splash.count(rive_dependency) != 1:
    fail("expected one splash Rive resource dependency")
splash = splash.replace(rive_dependency, "        startupAnimationResourcePatch", 1)
rive_start = "        // The Rive styles are not available before 21.30:"
end_marker = "        splashScreenStyleFingerprint.method.apply {"
if splash.count(rive_start) != 1:
    fail("pinned Rive splash start anchor changed")
start_index = splash.index(rive_start)
end_index = splash.rfind(end_marker)
if end_index <= start_index:
    fail("pinned Rive splash end anchor changed")
# Remove the complete Rive-only branch while retaining the native Lottie hook below it.
splash = splash[:start_index] + end_marker + splash[end_index + len(end_marker):]
SPLASH_PATCH.write_text(splash, encoding="utf-8")

# Offer only the two supported VYRA splash choices; Rive styles are deliberately disabled.
style_suffix = """val arrayKeySuffix = when {
            is_21_39_or_greater -> "_21_39"
            is_21_30_or_greater -> "_21_30"
            else -> ""
        }"""
if splash.count(style_suffix) != 1:
    fail("splash style-version selector anchor changed")
splash = splash.replace(style_suffix, 'val arrayKeySuffix = ""', 1)
SPLASH_PATCH.write_text(splash, encoding="utf-8")

splash_strings = SPLASH_STRINGS.read_text(encoding="utf-8")
for old, new in (
    ('<string name="morphe_splash_screen_style_title">Startup animation</string>',
     '<string name="morphe_splash_screen_style_title">VYRA splash screen</string>'),
    ('<string name="morphe_splash_screen_style_entry_3">Morphe Color</string>',
     '<string name="morphe_splash_screen_style_entry_3">VYRA</string>'),
    ('<string name="morphe_splash_screen_style_entry_5">Morphe Monochrome</string>',
     '<string name="morphe_splash_screen_style_entry_5">VYRA Monochrome</string>'),
):
    if splash_strings.count(old) != 1:
        fail(f"expected one VYRA splash label anchor: {old}")
    splash_strings = splash_strings.replace(old, new, 1)
SPLASH_STRINGS.write_text(splash_strings, encoding="utf-8")

# Generate the approved VYRA liquid-glass Lottie animation into upstream raw resources.
generator = ROOT.parent / "vyra-youtube/patches/generate_vyra_splash.py"
raw_resources = ROOT / "patches/src/main/resources/custom-branding/raw"
if not generator.is_file():
    fail(f"missing VYRA splash generator: {generator}")
subprocess.run([sys.executable, str(generator), str(VYRA_LOGO), str(raw_resources)], check=True)

# Ship the dedicated VYRA Lottie file without replacing Morphe's own resources.
splash_resources = SPLASH_RESOURCES.read_text(encoding="utf-8")
resource_anchor = '                "morphe_startup_animation_play.json"'
if splash_resources.count(resource_anchor) != 1:
    fail("startup animation resource list anchor changed")
splash_resources = splash_resources.replace(
    resource_anchor,
    resource_anchor + ',\n                "vyra_startup_animation.json"',
    1
)
SPLASH_RESOURCES.write_text(splash_resources, encoding="utf-8")

NAVIGATION_RESOURCES.mkdir(parents=True, exist_ok=True)
for filename, content in (
    ("vyra_navigation_home.xml", "<vector xmlns:android=\"http://schemas.android.com/apk/res/android\" android:width=\"24dp\" android:height=\"24dp\" android:viewportWidth=\"24\" android:viewportHeight=\"24\"><path android:fillColor=\"#00000000\" android:strokeColor=\"#E5E7EB\" android:strokeWidth=\"1.75\" android:strokeLineCap=\"round\" android:strokeLineJoin=\"round\" android:pathData=\"M4.5,11.2 L12,4.8 L19.5,11.2 V18.5 A1.5,1.5 0,0 1,18,20 H14.5 V14.8 A2.5,2.5 0,0 0,9.5,14.8 V20 H6 A1.5,1.5 0,0 1,4.5,18.5 Z\"/></vector>"),
    ("vyra_navigation_shorts.xml", "<vector xmlns:android=\"http://schemas.android.com/apk/res/android\" android:width=\"24dp\" android:height=\"24dp\" android:viewportWidth=\"24\" android:viewportHeight=\"24\"><path android:fillColor=\"#00000000\" android:strokeColor=\"#E5E7EB\" android:strokeWidth=\"1.75\" android:strokeLineCap=\"round\" android:strokeLineJoin=\"round\" android:pathData=\"M9.5,3.5 H14.5 A3.5,3.5 0,0 1,18,7 V17 A3.5,3.5 0,0 1,14.5,20.5 H9.5 A3.5,3.5 0,0 1,6,17 V7 A3.5,3.5 0,0 1,9.5,3.5 Z\"/><path android:fillColor=\"#E5E7EB\" android:pathData=\"M10.8,9.8 L15,12 L10.8,14.2 Z\"/></vector>"),
    ("vyra_navigation_subscriptions.xml", "<vector xmlns:android=\"http://schemas.android.com/apk/res/android\" android:width=\"24dp\" android:height=\"24dp\" android:viewportWidth=\"24\" android:viewportHeight=\"24\"><path android:fillColor=\"#00000000\" android:strokeColor=\"#E5E7EB\" android:strokeWidth=\"1.75\" android:strokeLineCap=\"round\" android:strokeLineJoin=\"round\" android:pathData=\"M6.3,8.5 H17.7 A2.8,2.8 0,0 1,20.5,11.3 V16.7 A2.8,2.8 0,0 1,17.7,19.5 H6.3 A2.8,2.8 0,0 1,3.5,16.7 V11.3 A2.8,2.8 0,0 1,6.3,8.5 Z\"/><path android:fillColor=\"#00000000\" android:strokeColor=\"#E5E7EB\" android:strokeWidth=\"1.75\" android:strokeLineCap=\"round\" android:pathData=\"M7.5,5 H16.5\"/><path android:fillColor=\"#E5E7EB\" android:pathData=\"M10.8,11.8 L14.5,14 L10.8,16.2 Z\"/></vector>"),
):
    (NAVIGATION_RESOURCES / filename).write_text(content, encoding="utf-8")

# VYRA glass defaults: leave stock navigation selected until the user enables Glass,
# but make the VYRA capsule clear, fully rounded and animated when enabled.
extension_settings = EXTENSION_SETTINGS.read_text(encoding="utf-8")
setting_defaults = {
    'new BooleanSetting("morphe_navigation_bar_animations", FALSE, parentNot(HIDE_NAVIGATION_BAR))':
        'new BooleanSetting("morphe_navigation_bar_animations", TRUE, parentNot(HIDE_NAVIGATION_BAR))',
    'new IntegerSetting("morphe_navigation_bar_glass_opacity", 20, true, parentsAll(parent(NAVIGATION_BAR_GLASS)':
        'new IntegerSetting("morphe_navigation_bar_glass_opacity", 14, true, parentsAll(parent(NAVIGATION_BAR_GLASS)',
    'new BooleanSetting("morphe_navigation_bar_glass_round", FALSE, true, parentsAll(parent(NAVIGATION_BAR_GLASS)':
        'new BooleanSetting("morphe_navigation_bar_glass_round", TRUE, true, parentsAll(parent(NAVIGATION_BAR_GLASS)',
}
for old, new in setting_defaults.items():
    if extension_settings.count(old) != 1:
        fail(f"expected exactly one VYRA navigation default anchor: {old}")
    extension_settings = extension_settings.replace(old, new, 1)
# Enable the Glass capsule by default; the VYRA master switch can disable it globally.
old_nav_glass = 'public static final BooleanSetting NAVIGATION_BAR_GLASS = new BooleanSetting("morphe_navigation_bar_glass", FALSE, true, parentsAll(parentNot(HIDE_NAVIGATION_BAR), new GlassAvailability()));'
new_nav_glass = old_nav_glass.replace(", FALSE,", ", TRUE,")
if extension_settings.count(old_nav_glass) != 1:
    fail("VYRA navigation glass default anchor changed")
extension_settings = extension_settings.replace(old_nav_glass, new_nav_glass, 1)
glass_master_anchor = new_nav_glass
if extension_settings.count(glass_master_anchor) != 1:
    fail("VYRA glass master setting insertion anchor changed")
extension_settings = extension_settings.replace(glass_master_anchor, glass_master_anchor + '\n    public static final BooleanSetting VYRA_GLASS_MODE = new BooleanSetting("vyra_glass_mode", true, true);', 1)
if extension_settings.count('new BooleanSetting("morphe_navigation_bar_glass", TRUE, true, parentsAll(') != 1:
    fail("VYRA must enable Glass by default")
if extension_settings.count('new EnumSetting<>("morphe_navigation_bar_style", NavigationBarStyle.DEFAULT') != 1:
    fail("VYRA must preserve the upstream default navigation style")
splash_setting_anchor = new_nav_glass
if extension_settings.count(splash_setting_anchor) != 1:
    fail("VYRA splash setting insertion anchor changed")
extension_settings = extension_settings.replace(
    splash_setting_anchor,
    splash_setting_anchor + '\n    public static final BooleanSetting VYRA_SPLASH_SCREEN = new BooleanSetting("vyra_splash_screen", TRUE, true);',
    1
)

EXTENSION_SETTINGS.write_text(extension_settings, encoding="utf-8")

# Wire the shared VYRA glass master switch into General settings.
general_pref_anchor = '            SwitchPreference("morphe_native_snackbar", summary = true),'
if settings.count(general_pref_anchor) != 1:
    fail("VYRA glass master preference anchor changed")
settings = settings.replace(general_pref_anchor, '            SwitchPreference("vyra_glass_mode", summary = true),\n' + general_pref_anchor, 1)
SETTINGS.write_text(settings, encoding="utf-8")

# Route the native YouTube Lottie splash hook to the VYRA resource when enabled.
theme_source = EXTENSION_THEME.read_text(encoding="utf-8")
method_anchor = """    public static void setSplashAnimationLottie(LottieAnimationView view, int resourceId) {
        try {
            // The Morphe styles replace the YouTube logo animation with the Morphe one."""
method_replacement = """    public static void setSplashAnimationLottie(LottieAnimationView view, int resourceId) {
        try {
            if (Settings.VYRA_SPLASH_SCREEN.get()) {
                int vyraAnimation = ResourceUtils.getIdentifier(ResourceType.RAW, "vyra_startup_animation");
                if (vyraAnimation != 0) {
                    view.patch_setAnimation(vyraAnimation);
                    return;
                }
            }
            // The Morphe styles replace the YouTube logo animation with the Morphe one."""
if theme_source.count(method_anchor) != 1:
    fail("ThemePatch Lottie splash hook anchor changed")
theme_source = theme_source.replace(method_anchor, method_replacement, 1)
old_boolean = """        return SharedYouTubeSettings.SPLASH_SCREEN_STYLE.get() != SplashScreenAnimationStyle.DISABLED && original;"""
new_boolean = """        return (Settings.VYRA_SPLASH_SCREEN.get()
                || SharedYouTubeSettings.SPLASH_SCREEN_STYLE.get() != SplashScreenAnimationStyle.DISABLED) && original;"""
if theme_source.count(old_boolean) != 1:
    fail("ThemePatch splash visibility boolean anchor changed")
theme_source = theme_source.replace(old_boolean, new_boolean, 1)
old_int = """        if (SharedYouTubeSettings.SPLASH_SCREEN_STYLE.get() != SplashScreenAnimationStyle.DISABLED || i != i2) {
            return i;
        }
        return i - 1;"""
new_int = """        if (Settings.VYRA_SPLASH_SCREEN.get()
                || SharedYouTubeSettings.SPLASH_SCREEN_STYLE.get() != SplashScreenAnimationStyle.DISABLED || i != i2) {
            return i;
        }
        return i - 1;"""
if theme_source.count(old_int) != 1:
    fail("ThemePatch splash visibility integer anchor changed")
theme_source = theme_source.replace(old_int, new_int, 1)
old_type = """        SplashScreenAnimationStyle style = SharedYouTubeSettings.SPLASH_SCREEN_STYLE.get();

        if (style == SplashScreenAnimationStyle.DISABLED) {"""
new_type = """        if (Settings.VYRA_SPLASH_SCREEN.get()) {
            return 1; // Valid native Lottie splash style; the VYRA resource replaces its animation.
        }
        SplashScreenAnimationStyle style = SharedYouTubeSettings.SPLASH_SCREEN_STYLE.get();

        if (style == SplashScreenAnimationStyle.DISABLED) {"""
if theme_source.count(old_type) != 1:
    fail("ThemePatch splash style selection anchor changed")
theme_source = theme_source.replace(old_type, new_type, 1)
EXTENSION_THEME.write_text(theme_source, encoding="utf-8")

# Apply the shared glass treatment to the real top toolbar and wide search field.
wide_source = EXTENSION_WIDE_SEARCH.read_text(encoding="utf-8")
wide_anchor = """    public static void initializeWideSearchbar(View toolbar) {
        try {
            if (!WIDE_SEARCHBAR_ENABLED) {
                return;
            }"""
wide_replacement = """    public static void initializeWideSearchbar(View toolbar) {
        try {
            if (Settings.VYRA_GLASS_MODE.get() && toolbar != null) {
                GradientDrawable toolbarGlass = new GradientDrawable(
                        GradientDrawable.Orientation.TOP_BOTTOM,
                        new int[]{0xB81B1D22, 0xA8111216});
                toolbarGlass.setCornerRadius(Dim.dp(18));
                toolbarGlass.setStroke(Dim.dp(1), 0x66D9DCE2);
                toolbar.setBackground(toolbarGlass);
                toolbar.setElevation(Dim.dp(5));
            }
            if (!WIDE_SEARCHBAR_ENABLED) {
                return;
            }"""
if wide_source.count(wide_anchor) != 1:
    fail("VYRA toolbar glass hook anchor changed")
wide_source = wide_source.replace(wide_anchor, wide_replacement, 1)
search_bg_anchor = """            searchBackground.setColor(backgroundColor);"""
if wide_source.count(search_bg_anchor) != 1:
    fail("VYRA search glass background anchor changed")
wide_source = wide_source.replace(search_bg_anchor, """            if (Settings.VYRA_GLASS_MODE.get()) {
                searchBackground.setColor(0xA8111216);
                searchBackground.setStroke(Dim.dp(1), 0x66D9DCE2);
            } else {
                searchBackground.setColor(backgroundColor);
            }""", 1)
EXTENSION_WIDE_SEARCH.write_text(wide_source, encoding="utf-8")

# Make the VYRA master switch control the actual floating navigation renderer.
glass_nav_source = EXTENSION_GLASS_NAV.read_text(encoding="utf-8")
glass_enabled_anchor = """    private static final boolean ENABLED = Settings.NAVIGATION_BAR_GLASS.get()
            && Settings.NAVIGATION_BAR_STYLE.get() != NavigationBarStyle.OPAQUE"""
glass_enabled_replacement = """    private static final boolean ENABLED = Settings.VYRA_GLASS_MODE.get()
            && Settings.NAVIGATION_BAR_GLASS.get()
            && Settings.NAVIGATION_BAR_STYLE.get() != NavigationBarStyle.OPAQUE"""
if glass_nav_source.count(glass_enabled_anchor) != 1:
    fail("VYRA global glass navigation gate anchor changed")
glass_nav_source = glass_nav_source.replace(glass_enabled_anchor, glass_enabled_replacement, 1)
EXTENSION_GLASS_NAV.write_text(glass_nav_source, encoding="utf-8")

# Style each real player control view after YouTube inflates it.
player_source = EXTENSION_PLAYER.read_text(encoding="utf-8")
player_import_anchor = "import android.graphics.Rect;" + chr(10)
if player_source.count(player_import_anchor) != 1:
    fail("VYRA player drawable import anchor changed")
player_source = player_source.replace(player_import_anchor, player_import_anchor + "import android.graphics.drawable.GradientDrawable;" + chr(10), 1)
player_method = """
    /** Applies a restrained glass capsule to native player controls without changing click behavior. */
    public static void styleVYRAPlayerControl(View view) {
        if (view == null || !Settings.VYRA_GLASS_MODE.get()) return;
        try {
            final float density = view.getResources().getDisplayMetrics().density;
            GradientDrawable glass = new GradientDrawable(
                    GradientDrawable.Orientation.TOP_BOTTOM,
                    new int[]{0xB81B1D22, 0xA8111216});
            glass.setCornerRadius(28f * density);
            glass.setStroke(Math.max(1, Math.round(density)), 0x66D9DCE2);
            view.setBackground(glass);
            view.setElevation(3f * density);
        } catch (Exception ex) {
            Logger.printException(() -> "VYRA player glass styling failed", ex);
        }
    }

"""
if player_source.count("\n}") < 1:
    fail("VYRA player class closing brace missing")
last = player_source.rfind("\n}")
player_source = player_source[:last] + "\n" + player_method + player_source[last:]
EXTENSION_PLAYER.write_text(player_source, encoding="utf-8")

player_patch = PLAYER_PATCH.read_text(encoding="utf-8")
top_anchor = """internal fun initializeTopControl(descriptor: String) {
    inflateTopControlMethodRef.get()!!.addInstruction(
        inflateTopControlInsertIndex++,
        "invoke-static { v$inflateTopControlRegister }, $descriptor->" +
                "initializeLegacyButton(Landroid/view/View;)V",
    )
}"""
top_replacement = """internal fun initializeTopControl(descriptor: String) {
    inflateTopControlMethodRef.get()!!.addInstruction(
        inflateTopControlInsertIndex++,
        "invoke-static { v$inflateTopControlRegister }, $EXTENSION_CLASS->styleVYRAPlayerControl(Landroid/view/View;)V",
    )
    inflateTopControlMethodRef.get()!!.addInstruction(
        inflateTopControlInsertIndex++,
        "invoke-static { v$inflateTopControlRegister }, $descriptor->" +
                "initializeLegacyButton(Landroid/view/View;)V",
    )
}"""
if player_patch.count(top_anchor) != 1:
    fail("VYRA top player control hook anchor changed")
player_patch = player_patch.replace(top_anchor, top_replacement, 1)
bottom_anchor = """fun initializeLegacyBottomControl(descriptor: String) {
    inflateBottomControlMethodRef.get()!!.addInstruction(
        inflateBottomControlInsertIndex++,
        "invoke-static { v$inflateBottomControlRegister }, $descriptor->" +
                "initializeLegacyButton(Landroid/view/View;)V",
    )
}"""
bottom_replacement = """fun initializeLegacyBottomControl(descriptor: String) {
    inflateBottomControlMethodRef.get()!!.addInstruction(
        inflateBottomControlInsertIndex++,
        "invoke-static { v$inflateBottomControlRegister }, $EXTENSION_CLASS->styleVYRAPlayerControl(Landroid/view/View;)V",
    )
    inflateBottomControlMethodRef.get()!!.addInstruction(
        inflateBottomControlInsertIndex++,
        "invoke-static { v$inflateBottomControlRegister }, $descriptor->" +
                "initializeLegacyButton(Landroid/view/View;)V",
    )
}"""
if player_patch.count(bottom_anchor) != 1:
    fail("VYRA bottom player control hook anchor changed")
player_patch = player_patch.replace(bottom_anchor, bottom_replacement, 1)
top_setup_anchor = """        PlayerTopControlsInflateFingerprint.let {
            it.method.apply {
                inflateTopControlMethodRef = WeakReference(this)

                val inflateReturnObjectIndex = it.instructionMatches.last().index
                inflateTopControlRegister = getInstruction<OneRegisterInstruction>(inflateReturnObjectIndex).registerA
                inflateTopControlInsertIndex = inflateReturnObjectIndex + 1
            }
        }

        if (is_21_05_or_greater) {"""
if player_patch.count(top_setup_anchor) != 1:
    fail("VYRA top player inflate hook anchor changed")
player_patch = player_patch.replace(
    top_setup_anchor,
    top_setup_anchor.replace(
        "\n        if (is_21_05_or_greater) {",
        "\n        initializeTopControl(EXTENSION_ADD_ON_API_CLASS_DESCRIPTOR)\n\n        if (is_21_05_or_greater) {",
        1
    ),
    1
)
PLAYER_PATCH.write_text(player_patch, encoding="utf-8")

source = NAV.read_text(encoding="utf-8")
splash_import = "import app.morphe.patches.youtube.misc.settings.settingsPatch" + chr(10)
if source.count(splash_import) != 1:
    fail("navigation patch splash dependency import anchor changed")
source = source.replace(splash_import, splash_import + "import app.morphe.patches.youtube.layout.theme.splashAnimationPatch" + chr(10), 1)
resource_patch_anchor = "private val navigationBarResourcePatch = patch {" + chr(10) + "    execute {"
if source.count(resource_patch_anchor) != 1:
    fail("navigation resource patch dependency anchor changed")
source = source.replace(resource_patch_anchor, resource_patch_anchor.replace("    execute {", "    dependsOn(splashAnimationPatch)" + chr(10) + "    execute {"), 1)
# Inject the VYRA Home, Shorts and Subscriptions glyphs into real YouTube navigation views.
java_source = EXTENSION_NAVIGATION.read_text(encoding="utf-8")
drawable_import = "import android.graphics.drawable.ColorDrawable;" + chr(10)
if java_source.count(drawable_import) != 1:
    fail("NavigationBarPatch drawable import anchor changed")
java_source = java_source.replace(drawable_import, drawable_import + "import android.graphics.drawable.Drawable;" + chr(10) + "import android.graphics.drawable.GradientDrawable;" + chr(10), 1)
weak_import = "import java.lang.ref.WeakReference;" + chr(10)
if java_source.count(weak_import) != 1:
    fail("NavigationBarPatch WeakReference import anchor changed")
java_source = java_source.replace(weak_import, weak_import + "import java.util.WeakHashMap;" + chr(10), 1)
java_anchor = """    /**
     * Injection point.
     */
    public static void navigationTabCreated(NavigationBar.NavigationButton button, View tabView) {
        YouTubeGlassNavigationBar.navigationTabCreated(button, tabView);"""
java_replacement = """    /** Applies the shared VYRA glass surface to the Shorts lower action container. */
    public static void styleVYRAShortsBottomBar(View view) {
        if (view == null || !Settings.VYRA_GLASS_MODE.get()) return;
        try {
            final float density = view.getResources().getDisplayMetrics().density;
            GradientDrawable glass = new GradientDrawable(
                    GradientDrawable.Orientation.TOP_BOTTOM,
                    new int[]{0xB81B1D22, 0xA8111216});
            glass.setCornerRadius(24f * density);
            glass.setStroke(Math.max(1, Math.round(density)), 0x66D9DCE2);
            view.setBackground(glass);
            view.setElevation(3f * density);
        } catch (Exception ex) {
            Logger.printException(() -> "VYRA Shorts glass styling failed", ex);
        }
    }

    // VYRA replaces only Home, Shorts and Subscriptions glyphs in Glass mode.
    // Create remains the native YouTube action and You keeps the real account avatar.
    private static final Map<ImageView, Drawable> VYRA_ORIGINAL_NAV_ICONS = new WeakHashMap<>();

    @Nullable
    private static ImageView findVYRAIcon(View view) {
        if (view instanceof ImageView image) return image;
        if (!(view instanceof ViewGroup group)) return null;
        ImageView best = null;
        int bestArea = -1;
        for (int i = 0; i < group.getChildCount(); i++) {
            ImageView candidate = findVYRAIcon(group.getChildAt(i));
            if (candidate == null) continue;
            int area = candidate.getWidth() * candidate.getHeight();
            if (area > bestArea) { best = candidate; bestArea = area; }
        }
        return best;
    }

    private static void applyVYRAIcon(NavigationBar.NavigationButton button, View tabView) {
        if (!Settings.NAVIGATION_BAR_GLASS.get()) {
            View iconContainer = tabView.findViewById(YouTubeGlassNavigationBar.BUTTON_ICON);
            ImageView icon = findVYRAIcon(iconContainer != null ? iconContainer : tabView);
            if (icon != null) {
                Drawable original = VYRA_ORIGINAL_NAV_ICONS.get(icon);
                if (original != null) icon.setImageDrawable(original);
            }
            return;
        }
        final String name;
        if (button == NavigationBar.NavigationButton.HOME) name = "vyra_navigation_home";
        else if (button == NavigationBar.NavigationButton.SHORTS) name = "vyra_navigation_shorts";
        else if (button == NavigationBar.NavigationButton.SUBSCRIPTIONS) name = "vyra_navigation_subscriptions";
        else return;
        tabView.post(() -> {
            View iconContainer = tabView.findViewById(YouTubeGlassNavigationBar.BUTTON_ICON);
            ImageView icon = findVYRAIcon(iconContainer != null ? iconContainer : tabView);
            if (icon == null) return;
            int resourceId = icon.getResources().getIdentifier(name, "drawable", icon.getContext().getPackageName());
            if (resourceId == 0) { Logger.printException(() -> "VYRA navigation drawable missing: " + name); return; }
            VYRA_ORIGINAL_NAV_ICONS.putIfAbsent(icon, icon.getDrawable());
            Drawable replacement = icon.getResources().getDrawable(resourceId, icon.getContext().getTheme()).mutate();
            icon.setImageDrawable(replacement);
        });
    }

    /**
     * Injection point.
     */
    public static void navigationTabCreated(NavigationBar.NavigationButton button, View tabView) {
        applyVYRAIcon(button, tabView);
        YouTubeGlassNavigationBar.navigationTabCreated(button, tabView);"""
if java_source.count(java_anchor) != 1:
    fail("NavigationBarPatch navigationTabCreated hook anchor changed")
java_source = java_source.replace(java_anchor, java_replacement, 1)
EXTENSION_NAVIGATION.write_text(java_source, encoding="utf-8")

if source.count("        copyResources(\"navigationbar\", ResourceGroup(\"drawable\", \"morphe_watch_later_selected.xml\"))") != 1:
    fail("pinned navigation resource-copy anchor changed")
source = source.replace("        copyResources(\"navigationbar\", ResourceGroup(\"drawable\", \"morphe_watch_later_selected.xml\"))", "        copyResources(\n            \"navigationbar\",\n            ResourceGroup(\n                \"drawable\",\n                \"morphe_watch_later_selected.xml\",\n                \"vyra_navigation_home.xml\",\n                \"vyra_navigation_shorts.xml\",\n                \"vyra_navigation_subscriptions.xml\"\n            )\n        )", 1)
shorts_hook_anchor = """        ShortsBottomBarContainerFingerprint.method.apply {
            addInstruction(
                0,
                "invoke-static { p1 }, $EXTENSION_CLASS->setShortsPlayerBottomInset(Landroid/view/View;)V"
            )"""
if source.count(shorts_hook_anchor) != 1:
    fail("VYRA Shorts bottom container hook anchor changed")
source = source.replace(
    shorts_hook_anchor,
    shorts_hook_anchor + """
            addInstruction(
                1,
                "invoke-static { p1 }, $EXTENSION_CLASS->styleVYRAShortsBottomBar(Landroid/view/View;)V"
            )""",
    1
)
NAV.write_text(source, encoding="utf-8")

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
            SwitchPreference("morphe_navigation_bar_animations", summary = true),
            SwitchPreference("vyra_splash_screen", summary = true),
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

        // Swap create with notifications button.'''
if source.count(anchor) != 1:
    fail("navigation settings insertion anchor changed; review upstream before applying")
NAV.write_text(source.replace(anchor, addition, 1), encoding="utf-8")

settings = SETTINGS.read_text(encoding="utf-8")
old_title = 'titleKey = "morphe_settings_title"'
if settings.count(old_title) != 2:
    fail("expected exactly two YouTube root-title references in SettingsPatch.kt")
settings = settings.replace(old_title, 'titleKey = "vyra_settings_title"')
# Copy the user-approved glass V mark into the patch resources and use it
# for the VYRA MOD settings entry.
if not VYRA_LOGO.is_file():
    fail(f"missing VYRA logo asset: {VYRA_LOGO}")
SETTINGS_LOGO.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(VYRA_LOGO, SETTINGS_LOGO)

resource_anchor = """                "morphe_settings_icon_bold_dark.xml",
                "morphe_settings_screen_00_about.xml","""
resource_replacement = """                "morphe_settings_icon_bold_dark.xml",
                "vyra_glass_monogram.webp",
                "morphe_settings_screen_00_about.xml","""
if settings.count(resource_anchor) != 1:
    fail("settings resource list anchor changed")
settings = settings.replace(resource_anchor, resource_replacement, 1)
icon_anchor = 'icon = "@drawable/morphe_settings_icon_dynamic"'
if settings.count(icon_anchor) != 1:
    fail("expected one VYRA MOD settings icon anchor")
settings = settings.replace(icon_anchor, 'icon = "@drawable/vyra_glass_monogram"', 1)
SETTINGS.write_text(settings, encoding="utf-8")

xml = YOUTUBE_STRINGS.read_text(encoding="utf-8")
if 'name="vyra_settings_title"' not in xml:
    xml = xml.replace("<resources>", '<resources>\n    <string name="vyra_settings_title" translatable="false">VYRA MOD</string>', 1)
if 'name="vyra_appearance_title"' not in xml:
    xml = xml.replace("</resources>", '    <string name="vyra_appearance_title">VYRA Appearance</string>\n</resources>', 1)
if 'name="vyra_settings_title"' not in xml or 'name="vyra_appearance_title"' not in xml:
    fail("failed to add VYRA YouTube-only string resources")
YOUTUBE_STRINGS.write_text(xml, encoding="utf-8")

# Rename existing upstream settings categories so the VYRA MOD root
# contains complete working feature groups, not duplicate or empty sub-screens.
screen_replacements = {
    """        key = "morphe_settings_screen_03_feed",
        summaryKey = null,""": """        key = "morphe_settings_screen_03_feed",
        titleKey = "vyra_feed_title",
        summaryKey = null,""",
    """        key = "morphe_settings_screen_04_general",
        summaryKey = null,""": """        key = "morphe_settings_screen_04_general",
        titleKey = "vyra_appearance_title",
        summaryKey = null,""",
    """        key = "morphe_settings_screen_06_player",
        titleKey = "morphe_settings_screen_05_player_title",""": """        key = "morphe_settings_screen_06_player",
        titleKey = "vyra_player_title",""",
    """        key = "morphe_settings_screen_09_shorts",
        titleKey = "morphe_settings_screen_06_shorts_title",""": """        key = "morphe_settings_screen_09_shorts",
        titleKey = "vyra_shorts_title",""",
}
for old, new in screen_replacements.items():
    if settings.count(old) != 1:
        fail("VYRA settings category title anchor changed")
    settings = settings.replace(old, new, 1)
SETTINGS.write_text(settings, encoding="utf-8")

xml = YOUTUBE_STRINGS.read_text(encoding="utf-8")
for key, value in (
    ("vyra_appearance_title", "VYRA Appearance"),
    ("vyra_splash_screen_title", "VYRA splash screen"),
    ("vyra_splash_screen_summary", "Play the VYRA liquid-glass animation when YouTube starts"),
    ("vyra_glass_mode_title", "VYRA Liquid Glass"),
    ("vyra_glass_mode_summary", "Apply the VYRA glass treatment to supported YouTube surfaces and player controls"),
    ("vyra_feed_title", "VYRA Home &amp; Feed"),
    ("vyra_player_title", "VYRA Player"),
    ("vyra_shorts_title", "VYRA Shorts"),
):
    if f'name="{key}"' not in xml:
        xml = xml.replace("</resources>", f'    <string name="{key}">{value}</string>\n</resources>', 1)
YOUTUBE_STRINGS.write_text(xml, encoding="utf-8")
ET.parse(YOUTUBE_STRINGS)

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
print("VYRA overlay applied: settings, Glass navigation, native splash hook and dedicated VYRA Lottie resource are wired.")
