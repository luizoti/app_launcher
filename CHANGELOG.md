# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.3] - 2026-04-15

### Changed

- **Versão calculada pela contagem de commits**: `src/version.py` usa
  `git rev-list --count HEAD` e monta `0.{n // 100}.{n % 100}` (1 commit =
  `0.0.1`, 10 = `0.0.10`, 100 = `0.1.0`, 250 = `0.2.50`). A lógica de
  `git describe` (tags/sha/distance) foi removida.
- Working tree com mudanças não commitadas ganha sufixo `-dirty`
- `build-arm64.sh` calcula a versão por contagem no host e passa como build-arg
  `APP_LAUNCHER_VERSION`
- **Nome do app re-centralizado**: a barra inferior agora tem dois stretches
  (um de cada lado do `info_label`), devolvendo o nome ao centro geométrico da
  janela com a versão no canto inferior esquerdo
- `tests/test_version.py` reescrito para os casos de contagem (1, 10, 99, 100,
  101, 250, dirty, git falho, contagem não numérica)

## [1.3.2] - 2026-04-15

### Added

- **Label de versão no canto inferior esquerdo** da janela (Arial 7, cinza,
  com tooltip). A versão é resolvida nesta ordem:
  1. variável de ambiente `APP_LAUNCHER_VERSION` (override manual);
  2. `src/_build_version.py`, gerado no build e congelado no bundle;
  3. `git describe` — tags quando existem, short sha + dirty quando não
     (`1.3.1+7.5863191` ou `0.0.0+5863191-dirty`);
  4. `version` de `pyproject.toml`;
  5. `"dev"`.
- `src/version.py` com a resolução e `write_build_version()`, chamado por
  `install.py build()` e pelo `Dockerfile.build`
- `build-arm64.sh` passa `git describe` como build-arg (`APP_LAUNCHER_VERSION`)
  para o bundle congelado carregar a versão dos commits sem precisar de git em
  tempo de execução
- Stub `typings/src/_build_version.pyi` para o pyright strict não reclamar do
  módulo gerado
- `tests/test_version.py` (25 testes) cobrindo tags, distance, dirty, sha-only,
  pyproject, override por env e escrita do arquivo gerado

## [1.3.1] - 2026-04-15

### Added

- **ARM64 cross build via Docker + QEMU**: `Dockerfile.build` and
  `build-arm64.sh` build the Pi binary from an x86_64 host, with the
  architecture asserted at the end of the image build
- `.dockerignore` keeping the host `.venv`, `build/` and `dist/` out of the
  build context

### Changed

- Dependencies are managed only by `uv`; **`requirements.txt` was removed**. It
  was missing `pydantic-settings` and `pyudev`, both imported by `src/`, so a
  build from it produced a binary that failed at import
- Cross build runs on `python:3.10-slim-bookworm`, matching the target's
  glibc 2.36 and the pinned CPython 3.10.8
- Build image installs a C toolchain and kernel headers. `evdev 1.7.1`
  publishes no wheels, only an sdist, so `uv` compiles it from source and it
  needs `linux/input.h`
- Build image installs `libdouble-conversion3`, `libsm6` and `libice6`, which
  close the dependency chain of QtCore/QtGui/QtWidgets, of `pyside6-rcc` and of
  the xcb platform plugin. PySide6 also ships Qt modules the app never imports
  (WebEngine, Wayland), whose libraries are deliberately not installed
- The image build now fails early on a PySide6 import error instead of
  surfacing it later as a `pyside6-rcc` failure
- Qt/X11 runtime libraries are installed in the build image; PySide6 wheels do
  not bundle them
- Dropped hidden imports not reached by the bundle: `requests`,
  `systemd.journal`, `PySide6.QtOpenGL`
- Dropped the redundant `rc_icons.py` data entry, the module is already bundled
- README documents `uv sync`, both build paths and the deploy step

### Fixed

- **False positives on `block_if_running`**:
  - Zombie processes are ignored. A closing app lingers as `<defunct>` keeping
    its name and cmdline, which blocked every launch until its parent reaped it
  - Match is no longer a substring scan of the whole command line. Only the
    process own executable and the program handed to a wrapper flag
    (`-e`, `-c`, `--command`, `--exec`) count, so `grep -r kodi .`,
    `tail -f kodi.log` and `less settings.json` no longer block
  - Removed reverse containment (`name in term`), so `moonlight-setup` no
    longer matches the term `moonlight`
  - The launcher own PID and PID 0 are excluded
  - Binary suffixes (`.exe`, `.bin`, `.AppImage`) are normalized away

### Changed

- `_focus_process` shares the matcher with `check_running_processes`, removing
  the phantom focus on a dying or unrelated process

## [1.3.0] - 2026-04-15

### Added

- **Hotplug Device Monitoring**:
  - Automatic tray icon update on device connect/disconnect
  - Improved device name detection with fallback chain
  - Enhanced logging for hotplug events
  - Monitor.start() with error handling for udev netlink

- **Installation Permissions**:
  - New `permissions` command in install.py
  - Automatic group setup (input, plugdev)
  - Udev rules for input device access
  - Auto-reload of udev rules
  - Auto-run full install flow when executed with sudo

### Changed

- **Code Organization**:
  - Extracted types to dedicated `src/types/` package
  - Protocols in `src/types/protocols/` (device.py, command.py)
  - Schemas in `src/types/schemas/` (settings.py)
  - Consistent import paths across codebase

- **Code Cleanup**:
  - Removed dead code and unused QThread
  - Improved type hints in protocols
  - Better logging for diagnostics

## [1.2.0] - 2026-04-14

### Added

- **Navigation Improvements**:
  - Fluid circular navigation (wraps at edges)
  - LEFT on first item goes to last item of previous row
  - RIGHT on last item goes to first item of next row
  - KeyPressFilter to handle navigation when window is not focused
  - FORCE_FOCUS_ON_NAVIGATE toggle to control window focus behavior

- **Debug Mode**:
  - DEBUG_MODE auto-detected based on PyInstaller (dev=True if not frozen)
  - Detailed debug logging for device mapping (scancodes, actions)

- **Error Handling**:
  - Errors displayed in interface label
  - on_success callback for hide-on-success behavior
  - Window stays visible on error, hides on success

- **Button Improvements**:
  - Added on_success and on_error callbacks to CustomButton

### Changed

- Removed automatic hide after entering app (now controlled by on_success)
- Changed button scancode lookup to try both string and int keys

## [1.1.0] - 2026-04-14

### Added

- **Security Improvements**:
  - Command blacklist (shell and elevation commands)
  - Root user execution blocking
  - Timeout of 3 seconds for command execution
  - Input validation (None/empty commands)
  - Test suite with 26 tests

- **Window Modes**:
  - Borderless mode (default)
  - Maximized mode
  - Fullscreen mode
  - TAB key to cycle between modes

- **Tray Icon Status**:
  - Connected icon when device with tray=True is connected
  - Disconnected icon when no device is connected

- **Navigation Improvements**:
  - Fluid circular navigation (wraps at edges)
  - LEFT on first item goes to last item of last row
  - RIGHT on last item goes to first item of next row
  - Navigation only works when app is visible

- **Toggle View**:
  - toggle_view works even when app is hidden
  - Other actions (enter, navigation) blocked when hidden

### Changed

- Refactored command_executor to use dependency injection
- Improved logging levels (debug for frequent, info for important)
- Improved error handling in grid navigation

## [1.0.0] - 2026-03-29

### Added

- **Core System**:
  - Application launcher with controller-friendly interface
  - Single instance control using PID file
  - System tray integration with dynamic icons
  - Device monitoring for gamepads and keyboards (pyudev/evdev)
  - Settings management via JSON with Pydantic validation
  - Command execution with subprocess.Popen

- **Graphical Interface**:
  - Custom application grid with navigation (up/down/left/right)
  - Custom buttons with icons and animations
  - Context menus with actions
  - Fullscreen mode support
  - Centralized window resolution

- **Features**:
  - Support for multiple device mappings
  - Icon cache loader
  - Logger setup with file output
  - Context menu separator

### Changed

- **Refactoring**:
  - Migrated from PyQt5 to PySide6
  - Replaced deprecated typing with generic typing
  - Simplified ActionManager with string-based signals
  - CommandExecutor reworked to stateless function
  - Pydantic models for settings validation

- **Code Quality**:
  - Comprehensive type hints throughout
  - Fixed type warnings
  - Improved code legibility
  - Auto formatting with Ruff

### Fixed

- Button alignment on grid
- Type warnings on multiple modules
- Missing logging configuration
- QCoreApplication event handling
- Various bug fixes and improvements

## [0.1.0] - 2024-XX-XX

### Added

- Initial release with basic launcher functionality
- System tray support
- Game controller input handling

---

For older releases, please refer to the git history.
