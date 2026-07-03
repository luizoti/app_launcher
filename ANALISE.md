# Análise do Projeto: App Launcher

**Versão:** 1.3.0  
**Linguagem:** Python 3.10.8  
**Framework GUI:** PySide6 6.6  
**Plataforma-alvo:** Linux (aarch64)

---

## Visão Geral

App Launcher é um lançador de aplicações desktop com foco em controle por joystick/gamepad. Permite mapear botões de qualquer joystick ou teclado para navegar pela interface, lançar aplicações e alternar visibilidade da janela. Ideal para HTPCs (Home Theater PCs) e setups RetroPie.

---

## Arquitetura

```
main.py
├── src/
│   ├── instance.py              # Singleton via PID file
│   ├── settings.py              # Config merge (JSON + defaults) + Pydantic
│   ├── default_settings.py      # Defaults: apps, mappings, window, tray, menu
│   ├── command_executor.py      # Execução segura de comandos
│   ├── log.py                   # RotatingFileHandler
│   ├── utils.py                 # check_running_processes (não usado)
│   ├── enums.py                 # actions_map (não usado ativamente)
│   ├── gui/
│   │   ├── app.py               # AppMainWindow
│   │   ├── action_manager.py    # Signal dispatch por nome
│   │   ├── centralized_resolution.py  # Centraliza janela na tela
│   │   ├── icons/
│   │   │   ├── __init__.py
│   │   │   ├── cache_loader.py  # Cache de ícones (disco + resources)
│   │   │   └── rc_icons.py      # Recursos Qt empacotados
│   │   └── components/
│   │       ├── grid.py           # Grid navegável (directional)
│   │       ├── custom_button.py  # Botão com hover/focus
│   │       ├── tray_icon.py      # System tray com status
│   │       ├── context_menu.py   # Hide/Show + Exit
│   │       └── device_monitor.py # evdev + pyudev, hotplug, button mapping
│   └── types/
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── settings.py       # Pydantic models
│       └── protocols/
│           ├── __init__.py
│           ├── device.py         # Protocols: InputDeviceEvDev, InputDevicePyDev, InputEvent
│           └── command.py        # Protocols: CommandValidator, ProcessRunner, EnvironmentCleaner
└── tests/
    ├── test_command_executor.py      # Testes de validação, env, execução
    └── test_check_running_process.py # Testes utils (frágil)
```

---

## Funcionalidades

### 1. Navegação por Joystick/Gamepad

- Mapeamento de botões → ações: `up`, `down`, `left`, `right`, `enter`, `toggle_view`, `close`
- Leitura de eventos via `evdev` com `read_loop()` em `QThreadPool`
- Suporte a eventos `EV_KEY` (botões) e `EV_ABS` (hat/d-pad)
- Mapeamentos configuráveis por dispositivo em `settings.json`

### 2. Grid de Aplicações

- Organização em grid com `more_itertools.batched`
- Navegação direcional com wrapping entre linhas/colunas
- Botão `CustomButton` com hover/focus effects visuais
- Label informativa que muda conforme o app focalizado

### 3. Hotplug (udev)

- `pyudev.MonitorObserver` detecta conexão/desconexão de dispositivos
- Inicia automaticamente workers para novos dispositivos mapeados
- Atualiza ícone da bandeja conforme status

### 4. System Tray

- Ícone na bandeja com 3 estados: `connected`, `disconnected`, `standby`
- Clique no tray → toggle visibilidade da janela
- Menu de contexto: Hide/Show, Exit

### 5. Modos de Janela

- `borderless` — sem decorações, sempre no topo
- `maximized` — maximizada, sempre no topo
- `fullscreen` — tela cheia, sempre no topo
- Ciclagem via tecla **Tab**

### 6. Instância Única

- PID file em `~/.config/app_launcher.pid`
- Verifica se o PID armazenado ainda está ativo via `psutil`
- Bloqueia execução de segunda instância

### 7. Execução Segura de Comandos

- `CommandValidator`: valida argumentos, bloqueia:
  - Shell commands: `sh`, `bash`, `zsh`, `fish`, `dash`
  - Elevation commands: `sudo`, `su`, `doas`, `pkexec`, `gksu`, `kdesu`
  - Execução como root (UID 0)
- `EnvironmentCleaner`: remove variáveis de ambiente problemáticas (`LD_LIBRARY_PATH`, `QT_PLUGIN_PATH`, `PYTHONPATH`, etc.)
- `ProcessRunner`: executa via `subprocess.Popen` com `shell=False`

---

## Schemas (Pydantic)

| Modelo                | Campos                                                                        |
| --------------------- | ----------------------------------------------------------------------------- |
| `AppsModel`           | `cmd: str \| list[str]`, `enabled: bool`, `icon: str`                         |
| `DeviceMappingsModel` | `buttons: dict[str, str]`, `tray: bool`                                       |
| `IconsModel`          | `connected: str`, `disconnected: str`, `standby: str`                         |
| `WindowModel`         | `apps_per_row`, `button_size`, `fullScreen`, `height`, `width`, `window_mode` |
| `MenuModel`           | `hide: str`, `settings: str`                                                  |
| `WindowMode`          | Enum: `borderless`, `maximized`, `fullscreen`                                 |

---

## Mapeamentos Default de Dispositivos

| Dispositivo                                                  | Botões mapeados                  |
| ------------------------------------------------------------ | -------------------------------- |
| DualSense Wireless Controller                                | 302→enter, 316→toggle_view       |
| Keyszer (virtual) Keyboard                                   | 172→toggle_view, 28→enter        |
| Microsoft X-Box 360 pad                                      | 304→enter, 316→toggle_view       |
| PLAYSTATION(R)3 Controller                                   | 302→enter, 304→toggle_view       |
| Sony Computer Entertainment Game Controller                  | 172→toggle_view, 28→button_enter |
| Wireless Controller                                          | 304→enter, 316→toggle_view       |
| Sony Computer Entertainment Wireless Controller              | 304→enter, 316→toggle_view       |
| Sony Interactive Entertainment DualSense Wireless Controller | 304→enter, 316→toggle_view       |
| Virtual Joystick                                             | 304→enter, 316→toggle_view       |

---

## Dependências

| Pacote            | Versão  | Uso                                   |
| ----------------- | ------- | ------------------------------------- |
| PySide6           | 6.6     | GUI Qt                                |
| evdev             | 1.7.1   | Leitura de eventos de input           |
| pyudev            | 0.24.4  | Hotplug/monitoramento de dispositivos |
| psutil            | 5.8.0   | Gerenciamento de processos            |
| pydantic          | 2.12.5  | Schemas de configuração               |
| pydantic-settings | 2.13.1  | Settings management                   |
| Pillow            | 12.2.0  | Processamento de imagens/ícones       |
| more-itertools    | 11.0.2  | Batching da grid                      |
| setproctitle      | 1.3.6   | Testes (não usado em produção)        |
| pyright           | 1.1.408 | Type checking                         |
| ruff              | 0.15.4  | Linter/formatter                      |
| pytest            | 7.0.0   | Testes                                |
| pyinstaller       | 6.19.0  | Build standalone                      |

---

## Fluxo de Inicialização

1. `main.py` configura logging (debug se não for frozen)
2. Define `QT_QPA_PLATFORM=xcb`
3. Lê PID file → se outra instância ativa, exit(1)
4. Escreve PID atual no arquivo
5. Cria `AppMainWindow`:
   - Carrega settings (JSON + defaults via Pydantic)
   - Aplica modo de janela
   - Cria `AppGrid` com botões para cada app configurado
   - Centraliza na tela
   - Cria `TrayIcon` + `DeviceMonitor`
   - Instala `KeyPressFilter` global
   - Inicia monitor de dispositivos
6. `app.exec()` → loop Qt

---

## Fluxo de Eventos do Dispositivo

```
DeviceMonitor.start_monitor()
  ├── pyudev.MonitorObserver (hotplug)
  │     └── _refresh_devices(device)
  │           ├── action="add"  → create_new_treaded_device() → DeviceEventWorker
  │           └── action="remove" → atualiza connected_devices + tray
  │
  └── _get_devices_on_start()
        └── list_devices() → valida → create_new_treaded_device()

DeviceEventWorker.run()
  └── read_loop() → categorize(event)
        ├── EV_KEY → _get_device_mapping() → action (string)
        ├── EV_ABS → HAT0X/HAT0Y → direction (up/down/left/right)
        └── emit(action) → AppGrid.action_handler() / AppMainWindow.action_handler()
```

---

## Problemas Encontrados

### Bug

1. **`read_pid_file()` type hint inconsistente** (`src/instance.py:26`)  
   Retorna `bool | int`, mas o tipo declarado é `bool | int` — no entanto `bool` em Python é `int`, então `isinstance(retorno, int)` pega ambos. A assinatura é confusa.

2. **`CommandValidator._check_blacklist` duplicação** (`src/command_executor.py:70-77`)  
   `ELEVATION_COMMANDS` é verificado duas vezes: primeiro o `first_arg` sozinho (linha 70), depois `" ".join(args_list[:2])` (linha 74-77). A segunda checagem usa `first_arg in ELEVATION_COMMANDS` de novo (linha 74), que é sempre True se chegou ali, então o segundo bloco é dead code ou redundante.

3. **`DeviceMonitor._check_connection_status` depende de `self.connected_devices`** (`src/gui/components/device_monitor.py:161-171`)  
   O método `_get_connected_device_names()` (linha 173-174) itera sobre `self.connected_devices`, mas essa lista só é populada via `_refresh_devices()` (hotplug), não na inicialização. Se nenhum dispositivo for conectado/desconectado após o start, `_check_connection_status` pode retornar "disconnected" mesmo com dispositivos rodando.

4. **`DeviceEventWorker.run()` sem fallback para tipo não mapeado** (`src/gui/components/device_monitor.py:95-109`)  
   Se `event.type` não for `EV_KEY` nem `EV_ABS`, o evento é ignorado (linha 96-97). Mas se for `EV_KEY` ou `EV_ABS` e o mapping retornar `None`, `emit_action(None)` é chamado.

5. **`KeyPressFilter` global captura todos eventos de tecla** (`src/gui/app.py:30-39`)  
   Instala um event filter que chama `window.keyPressEvent()` para **todo** keypress no aplicativo inteiro. Pode causar comportamento inesperado se outros widgets precisarem de tratamento próprio de teclado.

### Código Morto / Não Utilizado

6. **`src/enums.py` — `actions_map` e `actions_map_reversed`**  
   Definem um mapeamento numérico de ações (1→up, 2→down, ...), mas não são importados nem usados em nenhum lugar do código. O mapeamento real vem do JSON/settings.

7. **`src/utils.py` — `check_running_processes`**  
   Tem TODO indicando que não está em uso e a utilidade não é clara. Não é importado por nenhum módulo.

8. **`WindowModel.fullScreen`** (`src/types/schemas/settings.py:44`)  
   É um campo booleano, mas a lógica real de fullscreen foi substituída pelo enum `WindowMode.FULLSCREEN`. O campo `fullScreen` no JSON nunca é lido/usado pela aplicação.

### Configuração / Dados

9. **`settings.json` — Entradas duplicadas**  
   As chaves `a`, `e`, `f`, `i`, `l2WZ1`, `r`, `t`, `x`, `y`, `z` todas apontam para `x-terminal-emulator -e emulationstation`. São 11 entradas, 9 delas idênticas. Provavelmente resquício de teste/geração.

### Testes

10. **`test_check_running_process.py` — Uso frágil de `setproctitle`**  
    O teste altera o título do próprio processo Python para simular processos rodando. Isso é frágil porque:
    - Pode conflitar com outros testes rodando em paralelo
    - `setproctitle` pode não funcionar em todos os sistemas
    - O teste não limpa o título após execução
    - A asserção compara lista com generator (pode dar falso positivo/negativo)

### Estilo / Manutenção

11. **`settings.py` — Config merge manual** (`src/settings.py:76-125`)  
    O método `from_json()` faz merge manual campo por campo entre defaults e JSON. Poderia usar `model_validate` ou `dict` update recursivo do Pydantic v2.

12. **`settings.py:CONFIG_DIRECTORY` definido em módulo** (`src/settings.py:63`)  
    É definido no escopo do módulo antes da classe `Settings`, chamando `_select_config_directory()` que depende do filesystem. Isso roda na importação, o que pode causar problemas em testes ou ambientes sem filesystem.

13. **Mistura de inglês e português em comentários**  
    `src/settings.py:77` — `"Carrega do JSON, merge com defaults."` em português, enquanto o resto do código está em inglês.

14. **`device_monitor.py` — Tipagem com `cast` excessivo**  
    Uso de `cast()` em vários lugares para tipos que poderiam ser resolvidos com type hints diretos ou genéricos.

---

## Resumo de Métricas

| Item                              | Contagem                     |
| --------------------------------- | ---------------------------- |
| Arquivos Python                   | 25                           |
| Linhas de código (aproximado)     | ~1700                        |
| Testes                            | 2 arquivos, ~15 testes       |
| Dependências                      | 10                           |
| Schemas Pydantic                  | 7                            |
| Dispositivos mapeados (default)   | 9                            |
| Apps configurados (settings.json) | 12 (3 únicos + 9 duplicatas) |
| Modos de janela                   | 3                            |
