const { app, BrowserWindow, Menu, shell, ipcMain } = require('electron');
const path = require('path');

const TARGET_URL = 'https://meharfillingstation.pro/erp';
const APP_TITLE = 'Mehar Filling Station ERP';

let mainWindow = null;

// Enforce single instance lock
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        if (mainWindow) {
            if (mainWindow.isMinimized()) mainWindow.restore();
            mainWindow.focus();
        }
    });

    app.whenReady().then(createWindow);
}

function createWindow() {
    // Hide default menu bar across the app
    Menu.setApplicationMenu(null);

    const iconPath = process.platform === 'win32'
        ? path.join(__dirname, 'build', 'icon.ico')
        : path.join(__dirname, 'build', 'icon.png');

    mainWindow = new BrowserWindow({
        width: 1366,
        height: 768,
        minWidth: 1024,
        minHeight: 640,
        title: APP_TITLE,
        icon: iconPath,
        autoHideMenuBar: true,
        backgroundColor: '#070B14',
        show: false, // Show when ready-to-show to prevent white flash
        webPreferences: {
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: true,
            preload: path.join(__dirname, 'preload.js'),
            spellcheck: false,
        }
    });

    // Graceful presentation once page is painted
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Load Live ERP Portal
    loadPortal();

    // Handle connection failures with local offline fallback
    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
        // Ignore aborted loads (e.g. user navigated before page finished)
        if (errorCode === -3) return;

        console.warn(`[Electron] Page failed to load (${errorCode}): ${errorDescription}`);
        mainWindow.loadFile(path.join(__dirname, 'offline.html'));
    });

    // Handle new-window requests (window.open, target="_blank", printing popups)
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        try {
            const parsed = new URL(url);
            
            // Allow internal invoice/print popups to open within new managed windows
            if (parsed.hostname.includes('meharfillingstation.pro')) {
                return {
                    action: 'allow',
                    overrideBrowserWindowOptions: {
                        autoHideMenuBar: true,
                        backgroundColor: '#070B14',
                        icon: iconPath,
                        webPreferences: {
                            contextIsolation: true,
                            nodeIntegration: false,
                            sandbox: true,
                        }
                    }
                };
            }
            
            // External links (WhatsApp, Google Maps, external payment gateways) open in OS browser
            shell.openExternal(url);
            return { action: 'deny' };
        } catch (e) {
            shell.openExternal(url);
            return { action: 'deny' };
        }
    });

    // Handle in-page navigation away from the domain
    mainWindow.webContents.on('will-navigate', (event, url) => {
        try {
            const parsed = new URL(url);
            if (!parsed.hostname.includes('meharfillingstation.pro') && parsed.protocol !== 'file:') {
                event.preventDefault();
                shell.openExternal(url);
            }
        } catch (e) {
            // keep standard behavior
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

function loadPortal() {
    if (!mainWindow) return;
    mainWindow.loadURL(TARGET_URL).catch((err) => {
        console.warn('[Electron] Failed to load URL, serving offline fallback', err);
        mainWindow.loadFile(path.join(__dirname, 'offline.html'));
    });
}

// IPC listener for offline retry button
ipcMain.on('retry-connection', () => {
    loadPortal();
});

// Lifecycle events
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
