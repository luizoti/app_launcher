# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
