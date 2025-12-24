# App Launcher

## 📌 Project Idea

**App Launcher** is a desktop application developed in **Python using PyQt5** designed to be a **controller-friendly application launcher**.

The main idea of the project is to allow users to **use and map any joystick or keyboard** to fully control the launcher. This makes it especially useful for **HTPCs (Home Theater PCs)** or living‑room setups, where users interact directly with a graphical desktop environment such as **KDE, GNOME, or similar** using a game controller instead of a mouse and keyboard.

With App Launcher, the user can:

* Map **any joystick or keyboard button** to launcher actions
* Use controller buttons to **navigate the interface**, launch applications, and trigger system actions
* Assign special buttons (e.g. **PlayStation / Home button**) to **show or hide the launcher interface** at any time
* Seamlessly access the desktop environment without leaving the couch

This approach turns the launcher into a **bridge between traditional desktop environments and game‑console‑like interaction**, improving usability in media centers and controller‑based setups.

---

## ⚙️ General Functionality

When the application starts:

1. The system checks if another instance is already running using a **PID file**.
2. If an active instance is found, the new execution is automatically terminated.
3. If no instance is running, the main graphical interface is loaded.
4. The user interacts with a main window containing buttons, an application grid, and context menus.
5. The application can be minimized to the **system tray**, remaining active in the background.

---

## 🧠 Project Architecture

The project follows a modular structure to make maintenance and future improvements easier:

```
app_launcher/
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
├── settings.json           # Application settings
├── assets/                 # Icons and images
├── src/
│   ├── gui/
│   │   ├── app.py          # Main window
│   │   ├── action_manager.py
│   │   ├── centralized_resolution.py
│   │   └── components/     # Reusable UI components
│   │       ├── grid.py
│   │       ├── tray_icon.py
│   │       ├── context_menu.py
│   │       ├── custom_button.py
│   │       └── device_monitor.py
│   └── insancie.py         # Single-instance control (PID)
└── tests/                  # Automated tests
```

---

## 🪟 Graphical Interface

The interface is built with **PyQt5** and uses custom components such as:

* **Application grid**: visually organizes application shortcuts
* **Custom buttons**: configurable actions with icons
* **Context menus**: quick actions via right-click
* **System tray integration**: allows the app to run in the background

---

## 🔒 Single Instance Control

The single-instance mechanism works by:

* Writing the current process PID to a file
* Checking whether the stored PID is still active
* Automatically blocking multiple executions

This ensures that only one instance of the launcher runs at a time.

---

## 🧪 Testing

The project includes automated tests to validate critical features, such as checking whether processes are running.

---

## 🚀 How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python main.py
```

---

## 🏗️ Build (PyInstaller)

You can generate a standalone executable using **PyInstaller**.

### Build Command

````bash
pyinstaller \
  --onefile \
  --hidden-import=requests \
  --hidden-import=PyQt5.QtWidgets \
  --hidden-import=PyQt5.QtGui \
  --hidden-import=PyQt5.QtCore \
  --hidden-import=systemd.journal \
  main.py
````

After the build completes, the binary will be available in the `dist/` directory.

### Auto-start Installation (RetroPie Example)

To copy the generated binary to RetroPie autostart:

```bash
cp ./dist/main /opt/retropie/configs/all/autostart
```

This allows the launcher to start automatically when the system boots.

---

## 🔧 Possible Improvements

* Visual editor for application configuration
* Support for multiple profiles
* Customizable themes
* Global keyboard shortcuts

---

## 📄 License

This project is free to use for educational and personal purposes.

---

If you want, I can adapt this README for a more **professional**, **commercial**, or **open-source** tone.
