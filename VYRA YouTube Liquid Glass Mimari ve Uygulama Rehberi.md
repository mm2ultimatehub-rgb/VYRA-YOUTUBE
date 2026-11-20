# PROJECT: VYRA YOUTUBE — FULL LIQUID GLASS
**Hedef Paket:** `com.google.android.youtube`  
**Hedef Sürüm:** `21.30.216`  
**Hedef Platform:** Android 16 (API 36)  
**Mimari:** Morphe Patching System (`.mpp` + Extension DEX)

---

## 1. Repository ve Modül Mimarisi

Morphe yama kaynağınızda (`VYRA-YOUTUBE`) aşağıdaki dosya yapısını oluşturun:

```text
vyra-youtube/
├── patches/src/main/kotlin/app/morphe/patches/youtube/layout/vyraglass/
│   ├── VyraLiquidGlassPatch.kt          # Sürüm korumalı ana yama giriş noktası
│   ├── Fingerprints.kt                  # v21.30.216 UI yüzeyleri için bytecode parmak izleri
│   └── VyraSettingsPatch.kt             # VYRA MOD ayar ekranı ve canlı ön izleme enjeksiyonu
└── extensions/youtube/src/main/java/app/morphe/extension/youtube/vyraglass/
    ├── VyraGlassConfig.java             # SharedPreferences durumu, varsayılanlar (OFF) ve dinleyiciler
    ├── VyraGlassEngine.java             # API 36 RenderEffect / AGSL / Fallback işleme motoru
    ├── VyraGlassDrawable.java           # Gümüş kenar ışığı, speküler parlama ve yuvarlatılmış köşeler
    ├── VyraSurfaceHookRegistry.java     # ViewTreeObserver ve Litho/RecyclerView yüzey yakalayıcı
    ├── VyraMotionController.java        # Reduce-motion uyumlu yumuşak geçiş animasyonları
    └── ui/VyraModSettingsFragment.java  # VYRA MOD kontrol paneli ve gerçek zamanlı ön izleme
```

---

## 2. Çekirdek Tasarım Kimliği ve Renk Tokenları

Tüm render katmanları yalnızca monokrom siyah-gümüş paleti kullanır (mor, pembe, neon veya renkli gradyan içermez). `SurfaceView`, `TextureView`, video küçük resimleri ve kanal avatarları hiçbir zaman bulanıklaştırılmaz veya renklendirilmez.

| Token | Hex / ARGB | Liquid Glass Motorundaki Rolü |
| :--- | :--- | :--- |
| **Primary Background** | `#050505` | Derin obsidyen ana zemin (`Window` ve kök `CoordinatorLayout`) |
| **Secondary Background** | `#101214` | Yarı saydam cam katmanlarının arkasındaki ikincil yüzey zemini |
| **Primary Text** | `#FFFFFF` | Yüksek kontrastlı başlıklar, aktif sekmeler ve ana kontroller |
| **Secondary Text** | `#A7A9AD` | Meta veriler, zaman damgaları, pasif etiketler ve açıklamalar |
| **Glass Base Fill** | `argb(alpha, 16, 18, 20)` | Kullanıcı tarafından ayarlanabilen koyu grafit cam dolgusu (`%15–%88`) |
| **Silver Rim Light** | `#4DFFFFFF` → `#14A7A9AD` | 1.25dp yönlü gümüş kenar aydınlatması (sol üst parlak kenar) |
| **Specular Highlight** | `#2EE2E5E9` | Üst kenar iç kırılma yansıması (`LinearGradient` / AGSL shader) |

---

## 3. Global Liquid Glass Motoru (Android 16 / API 36)

### A. `VyraGlassEngine.java`

```java
package app.morphe.extension.youtube.vyraglass;

import android.app.Dialog;
import android.graphics.RenderEffect;
import android.graphics.RuntimeShader;
import android.graphics.Shader;
import android.os.Build;
import android.view.SurfaceView;
import android.view.TextureView;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.ImageView;

public final class VyraGlassEngine {

    // AGSL Liquid Glass Kenar Işığı + Speküler Kırılma Shader'ı (Monokrom Siyah & Gümüş)
    private static final String LIQUID_GLASS_AGSL =
        "uniform shader content;\n" +
        "uniform float2 iResolution;\n" +
        "uniform float iOpacity;\n" +
        "uniform float iRimIntensity;\n" +
        "uniform float iHighlightShift;\n" +
        "half4 main(float2 fragCoord) {\n" +
        "    float2 uv = fragCoord / iResolution;\n" +
        "    half4 base = content.eval(fragCoord);\n" +
        "    float edgeX = min(fragCoord.x, iResolution.x - fragCoord.x);\n" +
        "    float edgeY = min(fragCoord.y, iResolution.y - fragCoord.y);\n" +
        "    float edgeDist = min(edgeX, edgeY);\n" +
        "    float rimMask = 1.0 - smoothstep(0.0, 2.2, edgeDist);\n" +
        "    float diag = clamp((1.0 - uv.y) * 0.65 + (1.0 - uv.x) * 0.35 + iHighlightShift, 0.0, 1.0);\n" +
        "    half3 obsidian = half3(0.062, 0.070, 0.078); // #101214\n" +
        "    half3 silver = half3(0.84, 0.86, 0.89);\n" +
        "    half3 tinted = mix(base.rgb, obsidian, iOpacity);\n" +
        "    tinted += silver * (rimMask * iRimIntensity * (0.25 + 0.75 * diag));\n" +
        "    return half4(tinted, max(base.a, iOpacity));\n" +
        "}";

    private VyraGlassEngine() {}

    public static void applyGlassSurface(View target, SurfaceType type) {
        if (target == null || !VyraGlassConfig.isMasterEnabled()) return;
        if (isProtectedMediaView(target)) return;

        float opacity = VyraGlassConfig.getGlassOpacity();
        float blurRadius = VyraGlassConfig.getBlurIntensity();
        float rimIntensity = VyraGlassConfig.getRimIntensity();

        target.setClipToOutline(true);
        VyraGlassDrawable drawable = new VyraGlassDrawable(
            type.cornerRadiusDp,
            opacity,
            rimIntensity,
            type.elevationDp
        );
        target.setBackground(drawable);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                && target.isHardwareAccelerated()
                && blurRadius > 0.5f
                && type.supportsBackdropBlur) {
            try {
                RenderEffect blur = RenderEffect.createBlurEffect(
                    blurRadius, blurRadius, Shader.TileMode.CLAMP
                );
                if (target.getWidth() > 0 && target.getHeight() > 0) {
                    RuntimeShader shader = new RuntimeShader(LIQUID_GLASS_AGSL);
                    shader.setFloatUniform("iResolution", target.getWidth(), target.getHeight());
                    shader.setFloatUniform("iOpacity", opacity);
                    shader.setFloatUniform("iRimIntensity", rimIntensity);
                    shader.setFloatUniform("iHighlightShift", 0.0f);
                    RenderEffect agslEffect = RenderEffect.createRuntimeShaderEffect(shader, "content");
                    target.setRenderEffect(RenderEffect.createChainEffect(agslEffect, blur));
                } else {
                    target.setRenderEffect(blur);
                }
            } catch (Throwable ignored) {
                target.setRenderEffect(null);
            }
        } else {
            target.setRenderEffect(null);
        }

        if (VyraGlassConfig.isAnimationsEnabled()) {
            VyraMotionController.attachSoftEntrance(target, type);
        }
    }

    public static void applyDialogWindowBlur(Dialog dialog) {
        if (dialog == null || !VyraGlassConfig.isMasterEnabled()) return;
        Window window = dialog.getWindow();
        if (window == null) return;

        int blurPx = Math.round(VyraGlassConfig.getBlurIntensity() * 1.4f);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && blurPx > 0) {
            window.addFlags(WindowManager.LayoutParams.FLAG_BLUR_BEHIND);
            WindowManager.LayoutParams params = window.getAttributes();
            params.setBlurBehindRadius(blurPx);
            window.setAttributes(params);
            window.setBackgroundBlurRadius(blurPx);
        }
        View decor = window.getDecorView();
        applyGlassSurface(decor, SurfaceType.DIALOG_SHEET);
    }

    public static boolean isProtectedMediaView(View view) {
        if (view instanceof SurfaceView || view instanceof TextureView) return true;
        if (view instanceof ImageView) {
            int id = view.getId();
            if (id != View.NO_ID) {
                String name = safeResourceName(view, id);
                if (name.contains("thumbnail") || name.contains("avatar")
                        || name.contains("channel_art") || name.contains("player")
                        || name.contains("reel_player")) {
                    return true;
                }
            }
            float density = view.getResources().getDisplayMetrics().density;
            return view.getWidth() > (36 * density) || view.getHeight() > (36 * density);
        }
        if (view instanceof ViewGroup) {
            String tag = String.valueOf(view.getTag());
            return tag.contains("video_surface") || tag.contains("exo_content_frame");
        }
        return false;
    }

    private static String safeResourceName(View v, int id) {
        try {
            return v.getResources().getResourceEntryName(id);
        } catch (Exception e) {
            return "";
        }
    }

    public enum SurfaceType {
        APP_BAR(0f, 6f, true),
        BOTTOM_NAV(24f, 12f, true),
        CHIP_PILL(18f, 2f, false),
        FEED_CARD_CHROME(16f, 4f, false),
        PLAYER_CONTROL_PILL(22f, 8f, true),
        SHORTS_ACTION_RAIL(24f, 6f, true),
        DIALOG_SHEET(26f, 16f, true),
        SETTINGS_CARD(14f, 3f, false);

        public final float cornerRadiusDp;
        public final float elevationDp;
        public final boolean supportsBackdropBlur;

        SurfaceType(float cornerRadiusDp, float elevationDp, boolean supportsBackdropBlur) {
            this.cornerRadiusDp = cornerRadiusDp;
            this.elevationDp = elevationDp;
            this.supportsBackdropBlur = supportsBackdropBlur;
        }
    }
}
```

### B. `VyraGlassDrawable.java`

```java
package app.morphe.extension.youtube.vyraglass;

import android.content.res.Resources;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.ColorFilter;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.drawable.Drawable;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

public class VyraGlassDrawable extends Drawable {
    private final Paint fillPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint specularPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint rimPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF boundsRect = new RectF();
    private final float cornerRadiusPx;
    private final float opacity;
    private final float rimIntensity;

    public VyraGlassDrawable(float cornerRadiusDp, float opacity, float rimIntensity, float elevationDp) {
        float density = Resources.getSystem().getDisplayMetrics().density;
        this.cornerRadiusPx = cornerRadiusDp * density;
        this.opacity = Math.max(0.08f, Math.min(0.95f, opacity));
        this.rimIntensity = Math.max(0f, Math.min(1f, rimIntensity));

        int fillAlpha = Math.round(this.opacity * 255f);
        fillPaint.setStyle(Paint.Style.FILL);
        fillPaint.setColor(Color.argb(fillAlpha, 16, 18, 20)); // #101214

        rimPaint.setStyle(Paint.Style.STROKE);
        rimPaint.setStrokeWidth(1.25f * density);
    }

    @Override
    public void draw(@NonNull Canvas canvas) {
        boundsRect.set(getBounds());
        if (boundsRect.isEmpty()) return;

        float inset = rimPaint.getStrokeWidth() * 0.5f;
        boundsRect.inset(inset, inset);

        // 1. Yarı saydam obsidyen dolgu
        canvas.drawRoundRect(boundsRect, cornerRadiusPx, cornerRadiusPx, fillPaint);

        // 2. Üstten alta gümüş speküler yansıma
        int topSpecAlpha = Math.round(38f * rimIntensity);
        specularPaint.setShader(new LinearGradient(
            0f, boundsRect.top, 0f, boundsRect.top + (boundsRect.height() * 0.45f),
            new int[]{Color.argb(topSpecAlpha, 235, 238, 242), Color.TRANSPARENT},
            null, Shader.TileMode.CLAMP
        ));
        canvas.drawRoundRect(boundsRect, cornerRadiusPx, cornerRadiusPx, specularPaint);

        // 3. Yönlü gümüş kenar aydınlatması
        if (rimIntensity > 0.01f) {
            int rimBright = Color.argb(Math.round(115f * rimIntensity), 255, 255, 255);
            int rimMid    = Color.argb(Math.round(45f * rimIntensity), 167, 169, 173); // #A7A9AD
            int rimDim    = Color.argb(Math.round(22f * rimIntensity), 255, 255, 255);
            rimPaint.setShader(new LinearGradient(
                boundsRect.left, boundsRect.top, boundsRect.right, boundsRect.bottom,
                new int[]{rimBright, rimMid, rimDim},
                new float[]{0f, 0.5f, 1f},
                Shader.TileMode.CLAMP
            ));
            canvas.drawRoundRect(boundsRect, cornerRadiusPx, cornerRadiusPx, rimPaint);
        }
    }

    @Override public void setAlpha(int alpha) { fillPaint.setAlpha(alpha); }
    @Override public void setColorFilter(@Nullable ColorFilter cf) { fillPaint.setColorFilter(cf); }
    @Override public int getOpacity() { return PixelFormat.TRANSLUCENT; }
}
```

---

## 4. Ekran Bazlı Runtime Kancaları (YouTube `21.30.216`)

| Ekran / Yüzey | `com.google.android.youtube` (`21.30.216`) Hedefleri | Uygulanan Cam İşlemi |
| :--- | :--- | :--- |
| **A. Home & Global Chrome** | `MainActivity`, `AppBarLayout`, `PivotBar`, `ChipCloud` | `#050505` kök pencere, yüzen cam alt navigasyon barı, gümüş kenarlı kategori çipleri. |
| **B. Video Player** | `NextGenWatchLayout`, `youtube_controls_overlay`, `EngagementPanel` | Oynatma kontrolleri için `PLAYER_CONTROL_PILL`, açıklama/sıradaki/kalite menüleri için `DIALOG_SHEET`. |
| **C. Shorts** | `ReelWatchFragment`, `reel_right_action_bar`, `reel_channel_bar` | Sağ aksiyon çubuğu ve içerik üretici hapı için `SHORTS_ACTION_RAIL`; yorum/remix panelleri için pencere bulanıklığı. |
| **D. Search** | `SearchResultsFragment`, `SearchView`, öneri satırları | Arama kutusu, geçmiş/öneri satırları ve filtre panelleri için `#101214` cam yüzey. |
| **E. Subscriptions** | `SubscriptionsChannelBar`, filtre çipleri, akış kartları | Kanal avatarları korunarak kanal şeridi ve kart alt bilgilerine cam çerçeve. |
| **F. Library & Profile** | Hesap sekmesi kartları, geçmiş, oynatma listeleri, indirilenler | Küçük resimler korunarak raf ve kart arayüzlerine `FEED_CARD_CHROME`. |
| **G. Settings & VYRA MOD** | `PreferenceFragmentCompat`, `BottomSheetDialog`, `AlertDialog` | Tüm diyaloglarda API 36 `setBackgroundBlurRadius()` ve en üstte **VYRA MOD** kontrol paneli. |

---

## 5. Morphe Bytecode Yaması (`VyraLiquidGlassPatch.kt`)

```kotlin
package app.morphe.patches.youtube.layout.vyraglass

import app.morphe.patcher.extensions.InstructionExtensions.addInstruction
import app.morphe.patcher.extensions.InstructionExtensions.getInstruction
import app.morphe.patcher.patch.BytecodePatch
import app.morphe.patcher.patch.PatchException
import app.morphe.patcher.patch.annotation.CompatiblePackage
import app.morphe.patcher.patch.annotation.Patch
import app.morphe.patches.youtube.misc.extension.sharedExtensionPatch
import app.morphe.patches.youtube.misc.settings.settingsPatch
import com.android.tools.smali.dexlib2.iface.instruction.OneRegisterInstruction

private const val EXTENSION_CLASS =
    "Lapp/morphe/extension/youtube/vyraglass/VyraSurfaceHookRegistry;"
private const val ENGINE_CLASS =
    "Lapp/morphe/extension/youtube/vyraglass/VyraGlassEngine;"

@Patch(
    name = "VYRA Liquid Glass",
    description = "Applies the VYRA black-and-silver Liquid Glass visual system across YouTube.",
    compatiblePackages = [
        CompatiblePackage(
            name = "com.google.android.youtube",
            versions = ["21.30.216"]
        )
    ],
    dependsOn = [
        sharedExtensionPatch::class,
        settingsPatch::class,
        VyraSettingsPatch::class
    ]
)
@Suppress("unused")
object VyraLiquidGlassPatch : BytecodePatch(
    setOf(
        MainActivityOnCreateFingerprint,
        PivotBarInflationFingerprint,
        BottomSheetDialogShowFingerprint,
        AlertDialogShowFingerprint,
        EngagementPanelContainerFingerprint,
        ShortsOverlayInflationFingerprint,
        LithoComponentHostMountFingerprint
    )
) {
    override fun execute(context: BytecodeContext) {
        MainActivityOnCreateFingerprint.result?.mutableMethod?.addInstruction(
            0,
            "invoke-static {p0}, $EXTENSION_CLASS->onActivityCreated(Landroid/app/Activity;)V"
        ) ?: throw PatchException("Version guard failure: MainActivityOnCreateFingerprint not found for 21.30.216")

        PivotBarInflationFingerprint.result?.let { result ->
            val index = result.scanResult.patternScanResult!!.endIndex
            val register = result.mutableMethod.getInstruction<OneRegisterInstruction>(index).registerA
            result.mutableMethod.addInstruction(
                index + 1,
                "invoke-static {v$register}, $EXTENSION_CLASS->attachBottomNavGlass(Landroid/view/ViewGroup;)V"
            )
        }

        BottomSheetDialogShowFingerprint.result?.mutableMethod?.addInstruction(
            0,
            "invoke-static {p0}, $ENGINE_CLASS->applyDialogWindowBlur(Landroid/app/Dialog;)V"
        )

        AlertDialogShowFingerprint.result?.mutableMethod?.addInstruction(
            0,
            "invoke-static {p0}, $ENGINE_CLASS->applyDialogWindowBlur(Landroid/app/Dialog;)V"
        )

        EngagementPanelContainerFingerprint.result?.let { result ->
            val index = result.scanResult.patternScanResult!!.endIndex
            val register = result.mutableMethod.getInstruction<OneRegisterInstruction>(index).registerA
            result.mutableMethod.addInstruction(
                index + 1,
                "invoke-static {v$register}, $EXTENSION_CLASS->attachEngagementPanelGlass(Landroid/view/View;)V"
            )
        }

        ShortsOverlayInflationFingerprint.result?.let { result ->
            val index = result.scanResult.patternScanResult!!.endIndex
            val register = result.mutableMethod.getInstruction<OneRegisterInstruction>(index).registerA
            result.mutableMethod.addInstruction(
                index + 1,
                "invoke-static {v$register}, $EXTENSION_CLASS->attachShortsOverlayGlass(Landroid/view/ViewGroup;)V"
            )
        }

        LithoComponentHostMountFingerprint.result?.mutableMethod?.addInstruction(
            0,
            "invoke-static {p0}, $EXTENSION_CLASS->onLithoHostAttached(Landroid/view/ViewGroup;)V"
        )
    }
}
```

### Yüzey Yakalayıcı (`VyraSurfaceHookRegistry.java`)

```java
package app.morphe.extension.youtube.vyraglass;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewTreeObserver;

public final class VyraSurfaceHookRegistry {

    public static void onActivityCreated(Activity activity) {
        if (activity == null || !VyraGlassConfig.isMasterEnabled()) return;
        activity.getWindow().setBackgroundDrawable(new ColorDrawable(Color.parseColor("#050505")));
        activity.getWindow().setNavigationBarColor(Color.TRANSPARENT);
        activity.getWindow().setStatusBarColor(Color.TRANSPARENT);

        View root = activity.getWindow().getDecorView();
        root.getViewTreeObserver().addOnGlobalLayoutListener(new ViewTreeObserver.OnGlobalLayoutListener() {
            @Override
            public void onGlobalLayout() {
                if (!VyraGlassConfig.isMasterEnabled()) return;
                scanNamedSurfaces(root);
            }
        });
    }

    public static void attachBottomNavGlass(ViewGroup pivotBar) {
        if (pivotBar == null || !VyraGlassConfig.isMasterEnabled()) return;
        VyraGlassEngine.applyGlassSurface(pivotBar, VyraGlassEngine.SurfaceType.BOTTOM_NAV);
    }

    public static void attachEngagementPanelGlass(View panel) {
        if (panel == null || !VyraGlassConfig.isMasterEnabled()) return;
        VyraGlassEngine.applyGlassSurface(panel, VyraGlassEngine.SurfaceType.DIALOG_SHEET);
    }

    public static void attachShortsOverlayGlass(ViewGroup shortsRoot) {
        if (shortsRoot == null || !VyraGlassConfig.isMasterEnabled()) return;
        traverseAndStyle(shortsRoot, 0);
    }

    public static void onLithoHostAttached(ViewGroup host) {
        if (host == null || !VyraGlassConfig.isMasterEnabled()) return;
        if (VyraGlassEngine.isProtectedMediaView(host)) return;

        float density = host.getResources().getDisplayMetrics().density;
        int h = host.getHeight();
        int w = host.getWidth();
        if (h > 0 && h <= (52 * density) && w >= (40 * density) && host.isClickable()) {
            VyraGlassEngine.applyGlassSurface(host, VyraGlassEngine.SurfaceType.CHIP_PILL);
        }
    }

    private static void scanNamedSurfaces(View root) {
        if (!(root instanceof ViewGroup)) return;
        ViewGroup vg = (ViewGroup) root;
        int id = vg.getId();
        if (id != View.NO_ID) {
            try {
                String name = vg.getResources().getResourceEntryName(id);
                if (name.contains("toolbar") || name.contains("search_bar")) {
                    VyraGlassEngine.applyGlassSurface(vg, VyraGlassEngine.SurfaceType.APP_BAR);
                } else if (name.contains("controls_overlay") || name.contains("player_control")) {
                    VyraGlassEngine.applyGlassSurface(vg, VyraGlassEngine.SurfaceType.PLAYER_CONTROL_PILL);
                } else if (name.contains("reel_right") || name.contains("reel_channel")) {
                    VyraGlassEngine.applyGlassSurface(vg, VyraGlassEngine.SurfaceType.SHORTS_ACTION_RAIL);
                }
            } catch (Exception ignored) {}
        }
        for (int i = 0; i < vg.getChildCount(); i++) {
            scanNamedSurfaces(vg.getChildAt(i));
        }
    }

    private static void traverseAndStyle(View view, int depth) {
        if (depth > 8 || VyraGlassEngine.isProtectedMediaView(view)) return;
        if (view.isClickable() && view instanceof ViewGroup) {
            VyraGlassEngine.applyGlassSurface(view, VyraGlassEngine.SurfaceType.SHORTS_ACTION_RAIL);
        }
        if (view instanceof ViewGroup) {
            ViewGroup vg = (ViewGroup) view;
            for (int i = 0; i < vg.getChildCount(); i++) {
                traverseAndStyle(vg.getChildAt(i), depth + 1);
            }
        }
    }
}
```

---

## 6. VYRA MOD Ayarları ve Kalıcılık (`VyraGlassConfig`)

| Kontrol | Tercih Anahtarı | Varsayılan | Çalışma Zamanı Etkisi |
| :--- | :--- | :--- | :--- |
| **Master Liquid Glass** | `vyra_glass_enabled` | `false` (OFF) | Tüm cam kancalarını açar/kapatır; kapalıyken orijinal YouTube arayüzünü geri yükler. |
| **Glass Opacity** | `vyra_glass_opacity` | `0.58f` (`%58`) | `#101214` dolgu saydamlığını ve AGSL `iOpacity` değerini ayarlar. |
| **Background Blur Intensity** | `vyra_glass_blur` | `24.0f` (`24px`) | `RenderEffect.createBlurEffect` yarıçapını ve pencere bulanıklığını belirler. |
| **Rim-Light Intensity** | `vyra_glass_rim` | `0.65f` (`%65`) | Gümüş kenar ışığı ve üst speküler yansıma parlaklığını ayarlar. |
| **Glass Animations** | `vyra_glass_anim` | `true` (ON) | Yumuşak panel geçişlerini kontrol eder (Android sistem animasyonları kapalıysa otomatik devre dışı kalır). |
| **Navigation Appearance** | `vyra_glass_nav_mode` | `FLOATING_PILL` | Alt navigasyonu `FLOATING_PILL`, `FULL_DOCK` veya `COMPACT_ICON_ONLY` olarak değiştirir. |
| **Icon Appearance** | `vyra_glass_icon_style` | `SILVER_CHROME` | Desteklenen ikonlara monokrom `#FFFFFF` / `#A7A9AD` gümüş tonlaması uygular. |
| **Live Preview** | *(Canlı ön izleme)* | Etkileşimli | Ayar değişikliklerini anlık olarak mini oynatıcı ve navigasyon ön izlemesinde gösterir. |
| **Reset to VYRA Defaults** | *(Sıfırlama düğmesi)* | Varsayılana döner | Tüm ayarları fabrika VYRA değerlerine sıfırlar. |

---

## 7. Derleme, İmzalama ve Android 16 Doğrulama Komutları

```bash
# 1. Morphe MPP yama paketini derle
cd ~/VYRA-YOUTUBE
./gradlew build

# 2. Temiz YouTube 21.30.216 APK üzerine yamayı uygula
java -jar morphe-cli.jar patch \
  --patches patches/build/libs/vyra-patches-*.mpp \
  --include "VYRA Liquid Glass" \
  --out youtube-21.30.216-vyra-patched.apk \
  youtube-21.30.216-clean.apk

# 3. Android 16 (API 36) uyumlu v2/v3/v4 imza uygula
$ANDROID_HOME/build-tools/36.0.0/apksigner sign \
  --ks vyra-release.keystore \
  --ks-key-alias vyra \
  --out youtube-21.30.216-vyra-signed.apk \
  youtube-21.30.216-vyra-patched.apk

# 4. Cihaza kur ve başlat
adb install -r youtube-21.30.216-vyra-signed.apk
adb shell am start -n com.google.android.youtube/com.google.android.youtube.app.honeycomb.Shell\$HomeActivity
```