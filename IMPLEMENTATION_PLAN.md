# Plano de Melhorias e Refatoração

## Visão Geral do Projeto

O App Launcher é um menu de aplicativos PySide6 com suporte a controle remoto via gamepads/keyboards.

---

## ESTÁGIO 1: Limpeza de Código Morto

### 1.1 Remover código comentado em device_monitor.py

**Local**: `src/gui/components/device_monitor.py:62-81`

**Código morto identificado**:

```python
#     self._tray: bool | None = None
#     self._mappings: dict[typing.Any, typing.Any] | None = None

# @property
# def tray(self):
#     if self._tray is None:
#         self._tray = True

# @property
# def mappings(self):
#     if self._mappings is None:
#         self._mappings = {
#             ecodes.EV_KEY: self._get_device_mapping(
# self.input_device.name,
#  event=event),
#             ecodes.EV_ABS: {  # type: ignore
#                 ecodes.ABS_HAT0X: {-1: "right", 1: "left"},  # type: ignore
#                 ecodes.ABS_HAT0Y: {-1: "up", 1: "down"},  # type: ignore
#             },  # type: ignore
#         }
```

**Ação**: Remover completamente essas linhas.

---

### 1.2 Remover prints de debug

**Local**: `src/gui/components/device_monitor.py`

**Código a remover**:

- Linha 115: `print(QThread.currentThread())`
- Linha 149: `self._print_detected()`
- Linha 150: `print("--------------------------------")`
- Linha 151: `self._print_allowed()`
- Linha 165-177: Métodos `_print_detected()` e `_print_allowed()`

**Local**: `src/gui/components/grid.py`

**Código a remover**:

- Linha 74: `print("focused_app", self.current_row, self.current_app)`
- Linha 106: `print("up")`
- Linha 114: `print("down")`
- Linha 122: `print("left")`
- Linha 131: `print("right")`

**Ação**: Remover todos os prints de debug.

---

### 1.3 Remover código comentado em app.py

**Local**: `src/gui/app.py:33-35`

```python
# self.setWindowFlags(
#     Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
# )
```

**Ação**: Decidir se vai usar frameless ou não, remover código comentado.

---

### 1.4 Remover arquivo enums.py não utilizado

**Local**: `src/enums.py`

**Problema**: Arquivo existe mas não é importado em nenhum lugar.

**Código**:

```python
actions_map: dict[int, str] = {
    1: "up",
    2: "down",
    3: "left",
    4: "right",
    5: "enter",
    6: "options",
    7: "toggle_view",
    8: "close",
}

actions_map_reversed: dict[str, int] = {y: x for x, y in actions_map.items()}
```

**Ação**: Remover arquivo `src/enums.py` completamente.

---

### 1.5 Remover Base64 do cache_loader

**Local**: `src/gui/icons/cache_loader.py`

**Código a remover**:

- Linha 1: `import base64`
- Linhas 32-39: Função `_load_icon_from_base64`
- Linhas 70-73: Tentativa de carregar base64 em `get_icon`

**Ação**:

1. Remover import
2. Remover função `_load_icon_from_base64`
3. Simplificar `get_icon` para apenas caminhos de arquivo

---

## ESTÁGIO 2: Correção de Bugs

### 2.1 device_monitor.py - Tray Action nunca é emitido

**Local**: `src/gui/components/device_monitor.py:208-234`

**Problema**: O método `_refresh_devices` detecta "add" e "remove" mas **NUNCA emite** `tray_action` para mudar o ícone.

**Fluxo atual**:

```
device connect → _refresh_devices("add") → cria worker → NÃO EMITE tray_action
device disconnect → _refresh_devices("remove") → NÃO EMITE tray_action
```

**Código faltando**:

```python
# Em _refresh_devices, após detectar "add":
self.tray_action.emit("connected")

# Em _refresh_devices, após detectar "remove":
self.tray_action.emit("disconnected")
```

**Ação**: Adicionar emissão de `tray_action` em `_refresh_devices`.

---

### 2.2 device_monitor.py - worker não emite tray_action

**Local**: `src/gui/components/device_monitor.py:203-206`

**Problema**: Ao criar worker, não verifica se o dispositivo tem `tray: true` para emitir ação.

**Ação**: Verificar `device_mappings.tray` antes de emitir.

---

### 2.3 App Grid - up() e down() são idênticos

**Local**: `src/gui/components/grid.py:105-119`

**Problema**:

```python
def up(self) -> None:
    if self.current_row > 0:
        self.current_row -= 1
    else:
        self.current_row += 1  # ERRO: deveria ir para última row
    self.__set_focus(self.current_row, self.current_app)

def down(self) -> None:
    if self.current_row > 0:
        self.current_row -= 1  # ERRO: está igual ao up()
    else:
        self.current_row += 1
    self.__set_focus(self.current_row, self.current_app)
```

**Ação**: Corrigir lógica:

- `up()`: decrementar row (se row == 0, ir para última)
- `down()`: incrementar row (se row >= max, ir para primeira)

---

### 2.4 App Grid - left() sem bounds checking

**Local**: `src/gui/components/grid.py:121-128`

**Problema**: Ao navegar para край esquerda e não existirem items, incrementa row sem verificar límites.

**Ação**: Adicionar verificação de límites do grid.

---

## ESTÁGIO 3: Tipagem e Estrutura

### 3.1 settings.py - Ler JSON antes dos defaults (Abordagem Pydantic)

**Local**: `src/settings.py`

**Problema atual**: O código usa `pydantic_settings.BaseSettings` com `env_prefix` pointing to JSON file, mas:

- É complexo e confuso
- Não mescla corretamente JSON + defaults
- Tem código comentado não utilizado

**Solução via pydantic_settings**:

Usar `model_validator` para mesclar JSON com defaults:

```python
import json
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

from src.settings_model import (
    AppsModel,
    DeviceMappingsModel,
    IconsModel,
    MenuModel,
    SettingsModel,
    WindowModel,
)

CONFIG_FILE_NAME = "settings.json"

def _find_config_file() -> Path:
    """Encontra o arquivo de configuração."""
    paths = [
        Path.home() / ".config" / "app_launcher" / CONFIG_FILE_NAME,
        Path(__file__).parent.parent / CONFIG_FILE_NAME,
    ]
    for p in paths:
        if p.exists():
            return p
    raise FileNotFoundError(f"Config file not found: {paths}")

def _load_json() -> dict:
    """Carrega settings.json como dicionário."""
    config_path = _find_config_file()
    with open(config_path) as f:
        return json.load(f)

# Defaults usando Pydantic Models (para validação de tipo)
_DEFAULT_APPS = {
    "Kodi": AppsModel(cmd="kodi", enabled=True, icon="kodi.ico"),
}

_DEFAULT_MAPPINGS = {
    "DualSense Wireless Controller": DeviceMappingsModel(
        buttons={302: "enter", 316: "toggle_view"}, tray=True
    ),
}

_DEFAULT_TRAY = IconsModel(
    connected="connected.ico",
    disconnected="disconnected.ico",
    standby="standby.ico"
)

_DEFAULT_WINDOW = WindowModel(
    apps_per_row=6,
    button_size=256,
    fullscreen=False,
    height=500,
    width=1000,
)

_DEFAULT_MENU = MenuModel(
    hide="hide.ico",
    settings="settings.ico",
)


class Settings(BaseSettings):
    """Settings com merge de JSON + defaults."""

    apps: dict[str, AppsModel] = Field(default_factory=lambda: _DEFAULT_APPS.copy())
    mappings: dict[str, DeviceMappingsModel] = Field(default_factory=lambda: _DEFAULT_MAPPINGS.copy())
    tray: IconsModel = Field(default_factory=lambda: _DEFAULT_TRAY)
    window: WindowModel = Field(default_factory=lambda: _DEFAULT_WINDOW)
    menu: MenuModel = Field(default_factory=lambda: _DEFAULT_MENU)
    icons_directory: Path | None = None

    @model_validator(mode="before")
    @classmethod
    def load_json_and_merge(cls, values: dict) -> dict:
        """Carrega JSON e mescla com defaults (JSON sobrescreve)."""
        try:
            json_data = _load_json()
        except FileNotFoundError:
            return values  # Usa defaults apenas

        # Para cada campo, se existir no JSON, usa; senão usa default
        defaults = {
            "apps": cls.model_fields["apps"].default_factory(),
            "mappings": cls.model_fields["mappings"].default_factory(),
            "tray": cls.model_fields["tray"].default_factory(),
            "window": cls.model_fields["window"].default_factory(),
            "menu": cls.model_fields["menu"].default_factory(),
        }

        # Mescla: JSON sobrescreve defaults
        for key in defaults:
            if key in json_data:
                # Deep merge para dicts aninhados
                if isinstance(json_data[key], dict) and isinstance(defaults[key], dict):
                    merged = {**defaults[key], **json_data[key]}
                    defaults[key] = merged
                else:
                    defaults[key] = json_data[key]

        # Adiciona icons_directory
        config_path = _find_config_file()
        defaults["icons_directory"] = config_path.parent / "icons"

        return defaults


# Singleton
_settings_instance: Settings | None = None

def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
```

**Abordagem alternativa (mais simples)**:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Campos com defaults
    apps: dict[str, AppsModel] = Field(default=DEFAULT_APPS)
    ...

    # Override via JSON
    model_config = {
        "extra": "allow"  # Permite campos extras do JSON
    }

    @classmethod
    def from_json(cls, json_path: Path) -> "Settings":
        """Carrega do JSON, merge com defaults."""
        with open(json_path) as f:
            json_data = json.load(f)
        # Pydantic usa campos do JSON + defaults
        return cls(**json_data)
```

**Resumo das abordagens**:

| Abordagem            | Complexidade | Controle |
| -------------------- | ------------ | -------- |
| model_validator      | Média        | Total    |
| from_json + defaults | Baixa        | Bom      |
| Merge manual (dict)  | Baixa        | Total    |

---

### 3.2 settings_model.py - Adicionar type hints ausentes

**Local**: `src/settings_model.py`

**Problemas encontrados**:

- `AppsModel.icon` deveria ser opcional? (`str | None`)
- `WindowModel.button_size` não está sendo usado corretamente
- Faltam campos opcionais com valores padrão

**Ação**: Revisar modelo:

```python
class AppsModel(BaseModel):
    cmd: list[str] | str
    enabled: bool = True  # valor padrão
    icon: str | None = None  # opcional
```

---

### 3.2 tray_icon.py - Atribuição duplicada

**Local**: `src/gui/components/tray_icon.py:19 e 22`

**Problema**:

```python
def __init__(self, parent, settings):
    self.settings = settings           # linha 19
    ...
    self.settings: SettingsModel = (   # linha 22 - DUPLICADO!
        settings if settings else SettingsManager().get_settings()
    )
```

**Ação**: Remover atribuição duplicada, manter apenas uma.

---

### 3.3 action_manager.py - Type hints

**Local**: `src/gui/action_manager.py`

**Melhorias**:

- Adicionar tipo para `method`
- Usar `typing.Optional` em vez de `| None` para compatibilidade

```python
def action_handler(self, action_name: str) -> None:
    method: typing.Callable[[], None] | None = getattr(self, action_name, None)
    if method is not None:
        method()
```

---

### 3.4 command_executor.py - Type hints

**Local**: `src/command_executor.py`

**Problemas**:

- `*_: typing.Any` desnecessário
- `__command_processor` retorna `list[str]` mas não valida entrada

**Ação**:

- Remover `*_`
- Adicionar validação de tipo

---

### 3.5 instance.py - Minor typing issues

**Local**: `src/instance.py`

**Problema**:

- `pid_file.close()` é desnecessário (context manager já fecha)

**Ação**: Remover `pid_file.close()`

---

### 3.6 context_menu.py - Atributos dinâmicos

**Local**: `src/gui/components/context_menu.py:15-17`

**Problema**: Atributos adicionados dinamicamente sem type hints:

```python
self.change_visibility_action = self.addAction("Hide/Show")
self.exit_action = self.addAction("Exit")
```

**Ação**: Adicionar type hints ou usar dataclass/TypedDict.

---

### 3.7 device_monitor.py - Protocolos de Tipo

**Local**: `src/gui/components/device_monitor.py:19-40`

**Problema**: Protocols definidos mas incompletos e causam LSP errors:

- `InputEventProtocol` não tem `type`, `code`, `value`
- `InputDeviceEvDevProtocol` não tem `read_loop`

**Ação**:

1. Remover protocols se não forem essenciais
2. Ou definir corretamente com todos os atributos necessários

---

### 3.8 cache_loader.py - Type hints

**Local**: `src/gui/icons/cache_loader.py`

**Melhorias**:

- Adicionar tipo de retorno para funções
- Usar `pathlib.Path` em vez de `str`

```python
def _get_icons_dir() -> Path:
    settings = _get_settings()
    return Path(settings.icons_directory)
```

---

## ESTÁGIO 4: Melhorias de Funcionalidade

### 4.1 Sistema de Ícones da Tray

**Fluxo esperado**:

1. Dispositivo conecta → `device_monitor` emite `tray_action.emit("connected")`
2. `app.py` conecta: `device_monitor.tray_action → tray_icon.handler_switch_icon`
3. `tray_icon` muda ícone para `settings.tray.connected`

**Verificações necessárias**:

- [ ] `tray_action` é emitido em device add/remove
- [ ] `tray_icon.handler_switch_icon` existe e funciona
- [ ] Ícones existem em `icons/` (connected.ico, disconnected.ico, standby.ico)
- [ ] Conexão de sinais em `app.py` está correta

---

### 4.2 Settings - Ícones Base64

**Local**: `settings.json`

**Problema**: Muitos ícones estão em base64 inline:

- `menu.hide` (linha 164)
- `menu.settings` (linha 165)

**Ação**: Converter para caminhos de arquivo:

```json
"menu": {
  "hide": "hide.ico",
  "settings": "settings.ico"
}
```

---

## ESTÁGIO 5: Refatoração Arquitetural

### 5.1 DeviceMonitor - QThread não usado

**Local**: `src/gui/components/device_monitor.py:159`

**Problema**: Cria `self.worker_thread = QThread()` mas nunca o inicia ou usa.

**Código**:

```python
self.worker_thread = QThread()
self.observer = MonitorObserver(self.monitor)
```

**Ação**: Remover `worker_thread` se não for usado, ou iniciar a thread.

---

### 5.2 Signals classe redundante

**Local**: `src/gui/components/device_monitor.py:43-48`

**Problema**: Cria classe `Signals` interna mas `DeviceEventWorker` também herda de `QRunnable`.

**Ação**: Decidir se usa a classe `Signals` interna ou conecta diretamente no worker.

---

### 5.3 Pydantic Models - Validação

**Local**: `src/settings_model.py`

**Melhorias**:

- Adicionar validadores customizados
- Usar `Field` para valores com defaults
- Adicionar `model_config` para configurações

---

## ESTÁGIO 6: Limpezas Finais

### 6.1 Remover imports não utilizados

Verificar e remover imports não usados em todos os arquivos.

### 6.2 Type Hints incompletos

Completar type hints em métodos que ainda têm `-> None` faltando ou parâmetros sem tipo.

### 6.3 Documentação

Adicionar docstrings a métodos públicos.

---

## Resumo de Ações por Estágio

| Estágio | Ação                                              | Complexidade |
| ------- | ------------------------------------------------- | ------------ |
| 1       | Remover código comentado (device_monitor, app.py) | Baixa        |
| 1       | Remover prints de debug                           | Baixa        |
| 1       | Remover arquivo enums.py                          | Baixa        |
| 1       | Remover base64 do cache_loader                    | Média        |
| 2       | Corrigir tray_action em device_monitor            | Média        |
| 2       | Corrigir up()/down() em grid.py                   | Baixa        |
| 2       | Corrigir left()/right() bounds                    | Baixa        |
| 3       | **Tipagem settings_model**                        | Média        |
| 3       | **Corrigir tray_icon atribuição duplicada**       | Baixa        |
| 3       | **Melhorar action_manager type hints**            | Baixa        |
| 3       | **Limpar command_executor**                       | Baixa        |
| 3       | **Revisar device_monitor protocols**              | Alta         |
| 3       | Testar sistema de ícones tray                     | Alta         |
| 3       | Converter ícones base64 para arquivo              | Média        |
| 4       | Remover QThread não usado                         | Baixa        |
| 4       | Limpar classe Signals                             | Média        |
| 4       | Melhorar validação Pydantic                       | Média        |
| 5       | Limpezas finais                                   | Baixa        |

---

## Notas de Implementação

1. **settings.json** contém caminhos absolutos em `icons_directory` que podem variar por ambiente
2. **Tray icons** precisam existir fisicamente em `icons/` para o sistema funcionar
3. **Testes** devem ser feitos com dispositivo real conectado para validar fluxo add/remove
4. **Logging** já está configurado em `src/log.py` - usar `logger.info()` ao invés de `print()`

---

## Arquivos com Problemas de Tipagem Identificados

| Arquivo               | Problema                                        |
| --------------------- | ----------------------------------------------- |
| `settings_model.py`   | Campos opcionais sem default, icon não opcional |
| `tray_icon.py`        | Atribuição duplicada de `self.settings`         |
| `device_monitor.py`   | Protocols incompletos, causam LSP errors        |
| `command_executor.py` | `*_` desnecessário                              |
| `cache_loader.py`     | Retornos sem tipo, uso de str em vez de Path    |
| `context_menu.py`     | Atributos dinâmicos sem tipo                    |
| `action_manager.py`   | `method` sem tipo explícito                     |
| `instance.py`         | `close()` desnecessário                         |
