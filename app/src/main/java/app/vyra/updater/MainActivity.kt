package app.vyra.updater

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.util.Locale
import java.util.concurrent.Executors
import androidx.core.content.FileProvider

class MainActivity : Activity() {
    private lateinit var web: WebView
    private val executor = Executors.newSingleThreadExecutor()
    private var verifiedApk: File? = null
    private val statusUrl = "https://raw.githubusercontent.com/mm2ultimatehub-rgb/VYRA-YOUTUBE/main/updater/update-status.json"
    private val manifestUrl = "https://raw.githubusercontent.com/mm2ultimatehub-rgb/VYRA-YOUTUBE/main/updater/update-manifest.json"
    private val expectedPackage = "com.google.android.youtube"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        web = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = false
            settings.allowFileAccess = true
            settings.allowContentAccess = false
            settings.javaScriptCanOpenWindowsAutomatically = false
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean = true
            }
            webChromeClient = WebChromeClient()
            addJavascriptInterface(InstallerBridge(), "VYRAInstaller")
            loadUrl("file:///android_asset/vyra-update.html")
        }
        setContentView(web)
        checkForUpdate()
    }

    private fun js(script: String) = runOnUiThread { web.evaluateJavascript(script, null) }
    private fun status(title: String, detail: String) {
        val a = JSONObject.quote(title); val b = JSONObject.quote(detail)
        js("window.VYRAUpdater&&window.VYRAUpdater.setStatus($a,$b)")
    }
    private fun fail(message: String) {
        val safe = JSONObject.quote(message)
        js("window.VYRAUpdater&&window.VYRAUpdater.setError($safe)")
    }

    private fun checkForUpdate() {
        status("Güncelleme kontrol ediliyor", "VYRA sürüm bilgisi alınıyor…")
        executor.execute {
            try {
                val releaseStatus = JSONObject(readHttps(statusUrl))
                if (releaseStatus.optString("status") != "published") {
                    status("Henüz güncelleme yok", releaseStatus.optString(
                        "message",
                        "Şu anda yayınlanmış doğrulanmış bir APK bulunmuyor."
                    ))
                    return@execute
                }
                val json = JSONObject(readHttps(manifestUrl))
                val pkg = json.getString("package_name")
                require(pkg == expectedPackage) { "Beklenmeyen paket adı." }
                val apkUrl = json.getString("apk_url")
                require(apkUrl.startsWith("https://")) { "APK bağlantısı HTTPS olmalı." }
                val expectedSize = json.getLong("size_bytes")
                val expectedHash = json.getString("sha256").lowercase(Locale.US)
                require(expectedSize > 0 && expectedHash.matches(Regex("[a-f0-9]{64}"))) { "Manifest bilgileri geçersiz." }
                status("Güncelleme bulundu", "Sürüm ${json.optString("version")} indiriliyor…")
                downloadAndVerify(apkUrl, expectedSize, expectedHash)
            } catch (e: Exception) {
                fail(e.message ?: "Güncelleme kontrol edilemedi.")
            }
        }
    }

    private fun readHttps(address: String): String {
        val connection = (URL(address).openConnection() as HttpURLConnection).apply {
            connectTimeout = 15000; readTimeout = 20000; instanceFollowRedirects = false
        }
        try {
            require(connection.responseCode in 200..299) { "Manifest alınamadı: HTTP ${connection.responseCode}" }
            return connection.inputStream.bufferedReader().use { it.readText() }
        } finally { connection.disconnect() }
    }

    private fun downloadAndVerify(address: String, expectedSize: Long, expectedHash: String) {
        val url = URL(address)
        require(url.protocol == "https") { "Güvensiz indirme bağlantısı." }
        val connection = (url.openConnection() as HttpURLConnection).apply {
            connectTimeout = 15000; readTimeout = 30000; instanceFollowRedirects = false
        }
        val folder = File(filesDir, "updates").apply { mkdirs() }
        val apk = File(folder, "vyra-update.apk")
        try {
            require(connection.responseCode in 200..299) { "APK indirilemedi: HTTP ${connection.responseCode}" }
            val digest = MessageDigest.getInstance("SHA-256")
            var count = 0L
            val start = System.currentTimeMillis()
            connection.inputStream.use { input ->
                FileOutputStream(apk).use { output ->
                    val buffer = ByteArray(64 * 1024)
                    while (true) {
                        val n = input.read(buffer); if (n < 0) break
                        output.write(buffer, 0, n); digest.update(buffer, 0, n); count += n
                        val elapsed = (System.currentTimeMillis() - start).coerceAtLeast(1)
                        val rate = count * 1000 / elapsed
                        val total = expectedSize
                        js("window.VYRAUpdater&&window.VYRAUpdater.setProgress($count,$total,$rate)")
                    }
                }
            }
            require(count == expectedSize) { "Dosya boyutu doğrulanamadı." }
            val actual = digest.digest().joinToString("") { "%02x".format(it) }
            require(actual == expectedHash) { "SHA-256 doğrulaması başarısız." }
            verifyPackageAndSignature(apk)
            verifiedApk = apk
            js("window.VYRAUpdater&&window.VYRAUpdater.setReady()")
        } catch (e: Exception) {
            apk.delete()
            throw e
        } finally { connection.disconnect() }
    }

    private fun verifyPackageAndSignature(apk: File) {
        val archive = packageManager.getPackageArchiveInfo(apk.absolutePath, android.content.pm.PackageManager.GET_SIGNING_CERTIFICATES)
            ?: throw IllegalArgumentException("İndirilen dosya geçerli bir APK değil.")
        require(archive.packageName == expectedPackage) { "APK YouTube paketine ait değil." }
        val installed = packageManager.getPackageInfo(expectedPackage, android.content.pm.PackageManager.GET_SIGNING_CERTIFICATES)
        val installedSigners = installed.signingInfo?.apkContentsSigners?.map { it.toCharsString() }?.toSet()
        val downloadedSigners = archive.signingInfo?.apkContentsSigners?.map { it.toCharsString() }?.toSet()
        require(!installedSigners.isNullOrEmpty() && installedSigners == downloadedSigners) {
            "İmza sertifikası mevcut uygulamayla eşleşmiyor. Bu APK güncelleme olarak kurulamaz."
        }
    }

    private fun installVerified() {
        val apk = verifiedApk ?: run { fail("Önce doğrulanmış bir güncelleme indirilmeli."); return }
        if (!packageManager.canRequestPackageInstalls()) {
            startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:$packageName")))
            Toast.makeText(this, "VYRA Updater için uygulama yükleme iznini aç.", Toast.LENGTH_LONG).show()
            return
        }
        val uri = FileProvider.getUriForFile(this, "app.vyra.updater.fileprovider", apk)
        val intent = Intent(Intent.ACTION_INSTALL_PACKAGE).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(intent)
    }

    inner class InstallerBridge {
        @JavascriptInterface fun installUpdate() { runOnUiThread { installVerified() } }
    }

    override fun onDestroy() {
        web.removeJavascriptInterface("VYRAInstaller")
        web.destroy()
        executor.shutdownNow()
        super.onDestroy()
    }
}
