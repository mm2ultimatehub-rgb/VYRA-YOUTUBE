package app.morphe.extension.youtube.updater;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import androidx.core.content.FileProvider;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class VYRAUpdateActivity extends Activity {
    private static final String STATUS_URL =
            "https://raw.githubusercontent.com/mm2ultimatehub-rgb/VYRA-YOUTUBE/vyra-apk-final-build/updater/update-status.json";
    private static final String MANIFEST_URL =
            "https://raw.githubusercontent.com/mm2ultimatehub-rgb/VYRA-YOUTUBE/vyra-apk-final-build/updater/update-manifest.json";
    private static final long MAX_APK_BYTES = 300L * 1024L * 1024L;

    private WebView web;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private volatile File verifiedApk;
    private long currentBuildNumber = 1L;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        int buildId = getResources().getIdentifier("vyra_build_number", "string", getPackageName());
        if (buildId != 0) {
            try { currentBuildNumber = Long.parseLong(getString(buildId)); }
            catch (NumberFormatException ignored) { currentBuildNumber = 1L; }
        }

        web = new WebView(this);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(false);
        web.getSettings().setAllowFileAccess(false);
        web.getSettings().setAllowContentAccess(false);
        web.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return true;
            }
            @Override public void onPageFinished(WebView view, String url) {
                checkForUpdate();
            }
        });
        web.setWebChromeClient(new WebChromeClient());
        web.addJavascriptInterface(new InstallerBridge(), "VYRAInstaller");

        int pageId = getResources().getIdentifier("vyra_update", "raw", getPackageName());
        if (pageId == 0) {
            setContentView(web);
            fail("VYRA güncelleme ekranı bulunamadı.");
            return;
        }
        try (InputStream input = getResources().openRawResource(pageId)) {
            String html = readStream(input);
            setContentView(web);
            web.loadDataWithBaseURL("https://vyra.local/", html, "text/html", "UTF-8", null);
        } catch (Exception error) {
            setContentView(web);
            fail("Güncelleme ekranı açılamadı.");
        }
    }

    private void js(String script) {
        runOnUiThread(() -> {
            if (web != null) web.evaluateJavascript(script, null);
        });
    }

    private void status(String title, String detail) {
        js("window.VYRAUpdater&&window.VYRAUpdater.setStatus("
                + JSONObject.quote(title) + "," + JSONObject.quote(detail) + ")");
    }

    private void fail(String message) {
        js("window.VYRAUpdater&&window.VYRAUpdater.setError(" + JSONObject.quote(message) + ")");
    }

    private void checkForUpdate() {
        status("Güncelleme kontrol ediliyor", "VYRA sürüm bilgisi güvenli bağlantıdan alınıyor…");
        executor.execute(() -> {
            try {
                JSONObject release = new JSONObject(readHttps(STATUS_URL));
                if (!"published".equals(release.optString("status"))) {
                    status("VYRA güncel", release.optString("message",
                            "Şu anda yayınlanmış yeni bir sürüm bulunmuyor."));
                    return;
                }

                JSONObject manifest = new JSONObject(readHttps(MANIFEST_URL));
                String packageName = manifest.getString("package_name");
                if (!getPackageName().equals(packageName)) {
                    throw new IllegalArgumentException("Güncelleme paketi VYRA ile eşleşmiyor.");
                }
                long remoteBuild = manifest.getLong("build_number");
                if (remoteBuild <= currentBuildNumber) {
                    status("VYRA güncel", "Yüklü sürüm zaten en son sürüm.");
                    return;
                }

                String apkUrl = manifest.getString("apk_url");
                if (!apkUrl.startsWith("https://")) throw new IllegalArgumentException("APK bağlantısı güvenli değil.");
                long expectedSize = manifest.getLong("size_bytes");
                String expectedHash = manifest.getString("sha256").toLowerCase(Locale.US);
                if (expectedSize <= 0 || expectedSize > MAX_APK_BYTES
                        || !expectedHash.matches("[a-f0-9]{64}")) {
                    throw new IllegalArgumentException("Güncelleme dosyası bilgileri geçersiz.");
                }
                status("Yeni VYRA sürümü bulundu", "Sürüm " + manifest.optString("version") + " indiriliyor…");
                downloadAndVerify(apkUrl, expectedSize, expectedHash);
            } catch (Exception error) {
                fail(error.getMessage() == null ? "Güncelleme kontrol edilemedi." : error.getMessage());
            }
        });
    }

    private String readHttps(String address) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(address).openConnection();
        connection.setConnectTimeout(15000);
        connection.setReadTimeout(20000);
        connection.setInstanceFollowRedirects(true);
        try {
            if (!"https".equalsIgnoreCase(connection.getURL().getProtocol())
                    || connection.getResponseCode() < 200 || connection.getResponseCode() > 299) {
                throw new IllegalStateException("Güncelleme bilgisi alınamadı.");
            }
            try (InputStream input = connection.getInputStream()) {
                return readStream(input);
            }
        } finally {
            connection.disconnect();
        }
    }

    private static String readStream(InputStream input) throws Exception {
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        byte[] buffer = new byte[8192];
        int count;
        while ((count = input.read(buffer)) != -1) output.write(buffer, 0, count);
        return new String(output.toByteArray(), java.nio.charset.StandardCharsets.UTF_8);
    }

    private void downloadAndVerify(String address, long expectedSize, String expectedHash) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(address).openConnection();
        connection.setConnectTimeout(15000);
        connection.setReadTimeout(30000);
        connection.setInstanceFollowRedirects(true);
        File directory = new File(getFilesDir(), "updates");
        if (!directory.exists() && !directory.mkdirs()) throw new IllegalStateException("İndirme klasörü oluşturulamadı.");
        File apk = new File(directory, "vyra-update.apk");
        try {
            int response = connection.getResponseCode();
            String host = connection.getURL().getHost().toLowerCase(Locale.US);
            if (response < 200 || response > 299 || !"https".equalsIgnoreCase(connection.getURL().getProtocol())
                    || !(host.equals("github.com") || host.endsWith(".githubusercontent.com"))) {
                throw new IllegalStateException("APK indirme bağlantısı doğrulanamadı.");
            }

            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            long downloaded = 0L;
            long started = System.currentTimeMillis();
            try (InputStream input = connection.getInputStream();
                 FileOutputStream output = new FileOutputStream(apk)) {
                byte[] buffer = new byte[64 * 1024];
                int n;
                while ((n = input.read(buffer)) != -1) {
                    downloaded += n;
                    if (downloaded > expectedSize || downloaded > MAX_APK_BYTES) {
                        throw new IllegalStateException("İndirilen dosya beklenen boyutu aştı.");
                    }
                    output.write(buffer, 0, n);
                    digest.update(buffer, 0, n);
                    long elapsed = Math.max(1L, System.currentTimeMillis() - started);
                    long speed = downloaded * 1000L / elapsed;
                    js("window.VYRAUpdater&&window.VYRAUpdater.setProgress("
                            + downloaded + "," + expectedSize + "," + speed + ")");
                }
            }

            if (downloaded != expectedSize) throw new IllegalStateException("Dosya boyutu doğrulanamadı.");
            String actualHash = toHex(digest.digest());
            if (!actualHash.equals(expectedHash)) throw new IllegalStateException("SHA-256 doğrulaması başarısız.");

            verifyPackageAndSignature(apk);
            verifiedApk = apk;
            js("window.VYRAUpdater&&window.VYRAUpdater.setReady()");
        } catch (Exception error) {
            apk.delete();
            throw error;
        } finally {
            connection.disconnect();
        }
    }

    private static String toHex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) result.append(String.format(Locale.US, "%02x", value & 0xff));
        return result.toString();
    }

    @SuppressWarnings("deprecation")
    private void verifyPackageAndSignature(File apk) throws Exception {
        int flags = Build.VERSION.SDK_INT >= 28
                ? PackageManager.GET_SIGNING_CERTIFICATES : PackageManager.GET_SIGNATURES;
        PackageInfo downloaded = getPackageManager().getPackageArchiveInfo(apk.getAbsolutePath(), flags);
        if (downloaded == null || !getPackageName().equals(downloaded.packageName)) {
            throw new IllegalArgumentException("İndirilen dosya VYRA YouTube APK'sı değil.");
        }
        PackageInfo installed = getPackageManager().getPackageInfo(getPackageName(), flags);
        Set<String> installedSigners = signerSet(installed);
        Set<String> downloadedSigners = signerSet(downloaded);
        if (installedSigners.isEmpty() || !installedSigners.equals(downloadedSigners)) {
            throw new IllegalArgumentException("APK imzası mevcut VYRA kurulumuyla eşleşmiyor.");
        }
    }

    @SuppressWarnings("deprecation")
    private Set<String> signerSet(PackageInfo info) {
        Set<String> result = new HashSet<>();
        if (Build.VERSION.SDK_INT >= 28 && info.signingInfo != null) {
            android.content.pm.Signature[] signatures = info.signingInfo.getApkContentsSigners();
            if (signatures != null) for (android.content.pm.Signature signature : signatures) result.add(signature.toCharsString());
        } else if (info.signatures != null) {
            for (android.content.pm.Signature signature : info.signatures) result.add(signature.toCharsString());
        }
        return result;
    }

    private void installVerified() {
        File apk = verifiedApk;
        if (apk == null || !apk.isFile()) {
            fail("Önce doğrulanmış bir güncelleme indirilmeli.");
            return;
        }
        if (Build.VERSION.SDK_INT >= 26 && !getPackageManager().canRequestPackageInstalls()) {
            startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                    Uri.parse("package:" + getPackageName())));
            Toast.makeText(this, "VYRA için bu kaynaktan uygulama yükleme iznini aç.", Toast.LENGTH_LONG).show();
            return;
        }
        try {
            Uri uri = FileProvider.getUriForFile(this,
                    getPackageName() + ".vyra.updater.fileprovider", apk);
            Intent intent = new Intent(Intent.ACTION_INSTALL_PACKAGE);
            intent.setDataAndType(uri, "application/vnd.android.package-archive");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(intent);
        } catch (Exception error) {
            fail("Android kurulum ekranı açılamadı.");
        }
    }

    public final class InstallerBridge {
        @JavascriptInterface
        public void installUpdate() {
            runOnUiThread(VYRAUpdateActivity.this::installVerified);
        }
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            web.removeJavascriptInterface("VYRAInstaller");
            web.destroy();
            web = null;
        }
        executor.shutdownNow();
        super.onDestroy();
    }
}
