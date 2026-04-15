from src.types.schemas import (
    AppsModel,
    DeviceMappingsModel,
    IconsModel,
    MenuModel,
    WindowMode,
    WindowModel,
)

DEFAULT_APPS: dict[str, AppsModel] = {
    "Kodi": AppsModel(cmd="kodi", enabled=True, icon="kodi.ico"),
    "Pegasus": AppsModel(
        cmd="/usr/bin/moonlight-qt stream nitro app 'Pegasus'",
        enabled=True,
        icon="pegasus.ico",
    ),
    "Retropie": AppsModel(
        cmd="x-terminal-emulator -e emulationstation",
        enabled=True,
        icon="retropie.ico",
    ),
}

DEFAULT_MAPPINGS: dict[str, DeviceMappingsModel] = {
    "DualSense Wireless Controller": DeviceMappingsModel(
        buttons={"302": "enter", "316": "toggle_view"},
        tray=True,
    ),
    "Keyszer (virtual) Keyboard": DeviceMappingsModel(
        buttons={"172": "toggle_view", "28": "enter"},
        tray=False,
    ),
    "Microsoft X-Box 360 pad": DeviceMappingsModel(
        buttons={"304": "enter", "316": "toggle_view"},
        tray=True,
    ),
    "PLAYSTATION(R)3 Controller": DeviceMappingsModel(
        buttons={"302": "enter", "304": "toggle_view"},
        tray=True,
    ),
    "Sony Computer Entertainment Game Controller": DeviceMappingsModel(
        buttons={"172": "toggle_view", "28": "button_enter"},
        tray=True,
    ),
    "Wireless Controller": DeviceMappingsModel(
        buttons={"304": "enter", "316": "toggle_view"},
        tray=True,
    ),
    "Sony Computer Entertainment Wireless Controller": DeviceMappingsModel(
        buttons={"304": "enter", "316": "toggle_view"},
        tray=True,
    ),
    "Sony Interactive Entertainment DualSense Wireless Controller": DeviceMappingsModel(
        buttons={"304": "enter", "316": "toggle_view"},
        tray=True,
    ),
    "Virtual Joystick": DeviceMappingsModel(
        buttons={"304": "enter", "316": "toggle_view"},
        tray=True,
    ),
}

DEFAULT_TRAY = IconsModel(
    connected="connected.ico",
    disconnected="disconnected.ico",
    standby="standby.ico",
)


DEFAULT_WINDOW = WindowModel(
    apps_per_row=6,
    button_size=256,
    fullScreen=False,
    height=500,
    width=1000,
    window_mode=WindowMode.BORDERLESS,
)

DEFAULT_MENU = MenuModel(
    hide="menu_hide.ico",
    settings="menu_settings.ico",
)
