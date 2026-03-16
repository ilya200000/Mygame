import os

# Структура папок
folders = [
    "app/src/main/java/com/starlink/bypass",
    "app/src/main/res/layout",
    "app/src/main/res/values",
    "app/src/main/res/drawable",
    ".github/workflows"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

# 1. Инструкция для GitHub Actions (авто-сборка)
with open(".github/workflows/main.yml", "w", encoding="utf-8") as f:
    f.write("""name: Build APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - name: Setup Gradle
        run: chmod +x gradlew && ./gradlew assembleDebug
      - name: Upload
        uses: actions/upload-artifact@v4
        with:
          name: Bypass-YouTube-APK
          path: app/build/outputs/apk/debug/*.apk""")

# 2. Манифест (Разрешения для VPN)
with open("app/src/main/AndroidManifest.xml", "w", encoding="utf-8") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <application android:label="Starlink Bypass" android:theme="@android:style/Theme.DeviceDefault.NoActionBar">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <service android:name=".BypassVpnService" android:permission="android.permission.BIND_VPN_SERVICE" android:exported="false">
            <intent-filter><action android:name="android.net.VpnService" /></intent-filter>
        </service>
    </application>
</manifest>""")

# 3. Дизайн кнопки (Синий круг)
with open("app/src/main/res/drawable/round_btn.xml", "w", encoding="utf-8") as f:
    f.write("""<shape xmlns:android="http://schemas.android.com" android:shape="oval">
    <solid android:color="#0066CC" /><size android:width="150dp" android:height="150dp" /></shape>""")

# 4. Разметка экрана
with open("app/src/main/res/layout/activity_main.xml", "w", encoding="utf-8") as f:
    f.write("""<RelativeLayout xmlns:android="http://schemas.android.com" 
    android:layout_width="match_parent" android:layout_height="match_parent" android:background="#0F0F0F">
    <Button android:id="@+id/connectBtn" android:layout_width="180dp" android:layout_height="180dp" 
    android:layout_centerInParent="true" android:background="@drawable/round_btn" 
    android:text="ПОДКЛЮЧИТЬ" android:textColor="#FFFFFF" android:textStyle="bold" /></RelativeLayout>""")

# 5. Главный Java-код (Связь кнопки и VPN)
with open("app/src/main/java/com/starlink/bypass/MainActivity.java", "w", encoding="utf-8") as f:
    f.write("""package com.starlink.bypass;
import android.app.Activity;
import android.content.Intent;
import android.net.VpnService;
import android.os.Bundle;
import android.widget.Button;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        findViewById(R.id.connectBtn).setOnClickListener(v -> {
            Intent intent = VpnService.prepare(this);
            if (intent != null) startActivityForResult(intent, 0);
            else onActivityResult(0, RESULT_OK, null);
        });
    }
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (resultCode == RESULT_OK) startService(new Intent(this, BypassVpnService.class));
    }
}""")

# 6. Файлы сборки (Gradle)
with open("build.gradle", "w") as f: f.write("// Root build file")
with open("settings.gradle", "w") as f: f.write("include ':app'")
with open("app/build.gradle", "w") as f:
    f.write("plugins { id 'com.android.application' }\nandroid { namespace 'com.starlink.bypass'; compileSdk 33; defaultConfig { applicationId 'com.starlink.bypass'; minSdk 24; targetSdk 33; versionCode 1; versionName '1.0' } }")

print("✅ Проект собран! Теперь закидывай все файлы в репозиторий GitHub.")
