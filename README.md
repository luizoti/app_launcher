# App Launcher

## 📌 Project Idea

**App Launcher** is a desktop application developed in **Python using PySide6** designed to be a **controller-friendly application launcher**.

The main idea of the project is to allow users to **use and map any joystick or keyboard** to fully control the launcher. This makes it especially useful for **HTPCs (Home Theater PCs)** or living‑room setups, where users interact directly with a graphical desktop environment such as **KDE, GNOME, or similar** using a game controller instead of a mouse and keyboard.

With App Launcher, the user can:

- Map **any joystick or keyboard button** to launcher actions
- Use controller buttons to **navigate the interface**, launch applications, and trigger system actions
- Assign special buttons (e.g. **PlayStation / Home button**) to **show or hide the launcher interface** at any time
- Seamlessly access the desktop environment without leaving the couch

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
├── pyproject.toml          # Project metadata and dependencies
├── uv.lock                 # Locked dependency versions
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

The interface is built with **PySide6** and uses custom components such as:

- **Application grid**: visually organizes application shortcuts
- **Custom buttons**: configurable actions with icons
- **Context menus**: quick actions via right-click
- **System tray integration**: allows the app to run in the background

---

## 🔒 Single Instance Control

The single-instance mechanism works by:

- Writing the current process PID to a file
- Checking whether the stored PID is still active
- Automatically blocking multiple executions

This ensures that only one instance of the launcher runs at a time.

---

## 🧪 Testing

The project includes automated tests to validate critical features, such as checking whether processes are running.

---

## 🚀 How to Run

Dependencies are managed with [uv](https://docs.astral.sh/uv/); there is no
`requirements.txt`. The lockfile pins CPython 3.10.8 and only resolves on
aarch64 Linux, which is the target platform.

1. Install dependencies and create the virtualenv:

```bash
uv sync
```

2. Run the application:

```bash
uv run python main.py
```

---

## 🏗️ Build (PyInstaller)

### Native build (on the Raspberry Pi)

```bash
uv run python install.py build
```

The binary is written to `dist/app_launcher`.

### Cross build (x86_64 host, ARM64 output)

`./build-arm64.sh` builds the same binary through Docker + QEMU, so no ARM64
machine is needed:

```bash
./build-arm64.sh              # uses the Docker layer cache
./build-arm64.sh --no-cache   # full rebuild
```

How it works:

- `Dockerfile.build` uses `python:3.10-slim-bookworm`, which matches the
  target's glibc 2.36 and the pinned CPython 3.10.8.
- The build runs as `linux/arm64`. This is required, not just for speed:
  `pyproject.toml` declares `required-environments` for aarch64, so `uv`
  refuses to sync in any other environment.
- `uv sync --frozen` installs exactly what `uv.lock` pins, without rewriting it.
- Qt/X11 runtime libraries (`libgl1`, `libegl1`, `libxkbcommon0`, …) are
  installed because PySide6 wheels do not bundle them; without them
  PyInstaller cannot resolve `PySide6.QtGui`'s dependencies.
- The build finishes with a check that the output really is ARM aarch64.

`.dockerignore` excludes `.venv`, since its absolute paths point at the build
machine and would break `uv sync` inside the image.

### Build Command

The flags used by both builds, kept in sync with `install.py build()`:

```bash
uv run pyinstaller \
  --onefile \
  --clean \
  --noconfirm \
  --name=app_launcher \
  --hidden-import=PySide6.QtCore \
  --hidden-import=PySide6.QtGui \
  --hidden-import=PySide6.QtWidgets \
  --hidden-import=src.gui.icons.rc_icons \
  --add-data=icons:icons \
  main.py
```

After the build completes, the binary will be available in the `dist/` directory.

Deploy to the Pi with:

```bash
scp ./dist/app_launcher home:~/.local/bin/app_launcher
```

### Auto-start Installation (RetroPie Example)

To copy the generated binary to RetroPie autostart:

```bash
cp ./dist/app_launcher /opt/retropie/configs/all/autostart
```

This allows the launcher to start automatically when the system boots.

---

## 🔧 Possible Improvements

- Visual editor for application configuration
- Support for multiple profiles
- Customizable themes
- Global keyboard shortcuts

---

## 📄 License

This project is free to use for educational and personal purposes.

---

If you want, I can adapt this README for a more **professional**, **commercial**, or **open-source** tone.
