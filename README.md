# Mehar Filling Station ERP — Cross-Platform Apps

Official Windows Desktop and Android Mobile client applications for **Mehar Filling Station (Vital Petroleum Franchise) ERP**.

- **Live ERP Web Portal:** [https://meharfillingstation.pro/erp](https://meharfillingstation.pro/erp)
- **Application ID / Package Name:** `pro.meharfillingstation.app`
- **Application Name:** Mehar Filling Station ERP

---

## Architecture Overview

This repository houses the dedicated desktop and mobile wrappers for the Mehar Filling Station management system:

```
├── .github/
│   └── workflows/
│       ├── build-windows.yml      # Automated GitHub Actions workflow for Windows .exe
│       └── build-android.yml      # Automated GitHub Actions workflow for Android .apk
├── desktop-app/                   # Electron 31 + Electron Builder (Windows target)
│   ├── build/                     # App icons (ICO, PNG) & NSIS installer graphics
│   ├── main.js                    # Main process (frameless 1366x768, single instance, print handling)
│   ├── preload.js                 # Secure context bridge
│   ├── offline.html               # Dark glassmorphism offline retry screen
│   └── package.json               # Build scripts & NSIS/Portable configuration
├── android-app/                   # Capacitor 6 Android application
│   ├── android/                   # Native Android Studio / Gradle project
│   │   ├── app/src/main/res/      # Generated mipmap icons & splash drawables
│   │   └── gradlew                # Executable Gradle wrapper
│   ├── www/                       # Local assets & dark glassmorphism splash loader
│   ├── capacitor.config.json      # Server URL, splash, and status bar configuration
│   └── package.json               # Capacitor plugins & build scripts
└── scripts/
    └── generate_all_assets.py     # Python PIL generator for all icons & splash screens
```

---

## 🚀 Automated GitHub Actions CI/CD

Both client builds are fully automated via GitHub Actions:

### 1. Windows Desktop App (`build-windows.yml`)
- **Runner:** `windows-latest`
- **Build Output:**
  - Standard NSIS Windows Installer (`.exe`)
  - Standalone Portable Executable (`.exe`)
- **Artifact Name:** `Mehar-Filling-Station-Windows-Setup`

### 2. Android Mobile App (`build-android.yml`)
- **Runner:** `ubuntu-latest` with **Java JDK 17 (Zulu)** & Node.js 20
- **Build Output:**
  - Native Debug APK (`app-debug.apk`)
- **Artifact Name:** `Mehar-Filling-Station-Android-APK`

### Manual Trigger:
You can trigger any build anytime by navigating to **GitHub → Actions → Select Workflow → Click "Run workflow"**.

---

## 🛠️ Local Development & Manual Builds

### Windows Desktop App
```bash
cd desktop-app
npm install
npm start          # Run locally in development
npm run build:win  # Build NSIS installer and portable EXE
```

### Android Mobile App
```bash
cd android-app
npm install
npx cap sync android
cd android
./gradlew assembleDebug   # Builds debug APK in app/build/outputs/apk/debug/
```

### Asset Generation
All multi-resolution icons, adaptive launcher icons, NSIS headers/sidebars, and splash screens can be regenerated using:
```bash
python3 scripts/generate_all_assets.py
```

---

## 🛡️ Security & Privacy
- Zero nodeIntegration in renderer processes with strict `contextIsolation: true`.
- Sandboxed webviews preventing unauthorized script execution.
- External browser delegation for third-party links (WhatsApp, external payment gateways).
- Single-instance locking prevents duplicate background processes.
