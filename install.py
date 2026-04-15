#!/usr/bin/env python3
"""Script de instalação e build para o AppLauncher."""

import argparse
import os
import pwd
import shutil
import subprocess
import sys


def compile_resources():
    """Compila icons.qrc para rc_icons.py se necessário."""
    script_dir = os.path.abspath(os.path.dirname(__file__))
    qrc_path = os.path.join(script_dir, "src", "gui", "icons", "icons.qrc")
    output_path = os.path.join(script_dir, "src", "gui", "icons", "rc_icons.py")

    if not os.path.exists(qrc_path):
        print(f"QRC não encontrado em {qrc_path}, pulando compilação de recursos.")
        return

    needs_compile = not os.path.exists(output_path) or os.path.getmtime(
        qrc_path
    ) > os.path.getmtime(output_path)

    if needs_compile:
        print("Compilando recursos Qt (.qrc -> .py)...")
        try:
            subprocess.run(
                ["pyside6-rcc", "-o", output_path, qrc_path],
                check=True,
                cwd=script_dir,
            )
            print("Recursos compilados com sucesso.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao compilar recursos: {e}")
            sys.exit(1)
    else:
        print("Recursos já estão atualizados, pulando.")


def get_user_home(uid=1000):
    try:
        return pwd.getpwuid(uid).pw_dir
    except KeyError:
        print(f"Não foi possível encontrar usuário com UID {uid}")
        sys.exit(1)


def backup_file(filepath):
    if os.path.exists(filepath) or os.path.islink(filepath):
        backup_path = filepath + ".bak"
        print(f"Realizando backup de {filepath} para {backup_path}")
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.move(filepath, backup_path)
        except Exception as e:
            print(f"Erro ao fazer backup de {filepath}: {e}")
            return False
    return True


def build():
    """Compila o app com PyInstaller via uv."""
    print("=== Build do AppLauncher ===\n")

    compile_resources()

    script_dir = os.path.abspath(os.path.dirname(__file__))
    main_py = os.path.join(script_dir, "main.py")

    if not os.path.exists(main_py):
        print(f"Erro: main.py não encontrado em {script_dir}")
        sys.exit(1)

    hidden_imports = [
        "requests",
        "PySide6.QtWidgets",
        "PySide6.QtGui",
        "PySide6.QtCore",
        "PySide6.QtOpenGL",
        "systemd.journal",
        "src.gui.icons.rc_icons",
    ]

    icons_dir = os.path.join(script_dir, "icons")
    rc_icons = os.path.join(script_dir, "src", "gui", "icons", "rc_icons.py")

    datas = []
    if os.path.exists(icons_dir):
        datas.append((icons_dir, "icons"))
    if os.path.exists(rc_icons):
        datas.append((rc_icons, "src/gui/icons/rc_icons.py"))

    command = [
        "uv",
        "run",
        "pyinstaller",
        "--onefile",
        "--clean",
        "--name=app_launcher",
    ]

    for imp in hidden_imports:
        command.extend(["--hidden-import", imp])

    for data in datas:
        command.extend(["--add-data", f"{data[0]}:{data[1]}"])

    command.append(main_py)

    print("Executando PyInstaller via uv...")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("Erro durante a compilação:", e)
        sys.exit(1)

    binary_path = os.path.join(script_dir, "dist", "app_launcher")
    if not os.path.exists(binary_path):
        print(f"Binário compilado não encontrado em {binary_path}")
        sys.exit(1)

    print(f"Binário compilado com sucesso em: {binary_path}")
    return binary_path


def install():
    """Instala binário em ~/.local/bin/."""
    print("=== Instalação do AppLauncher ===\n")

    user_home = get_user_home(1000)
    target_dir = os.path.join(user_home, ".local", "bin")
    target_bin = os.path.join(target_dir, "app_launcher")

    os.makedirs(target_dir, exist_ok=True)

    script_dir = os.path.abspath(os.path.dirname(__file__))
    source_bin = os.path.join(script_dir, "dist", "app_launcher")

    if not os.path.exists(source_bin):
        print("Binário não encontrado. Execute 'install.py build' primeiro.")
        print(f"Procurando em: {source_bin}")
        sys.exit(1)

    if os.path.exists(target_bin):
        backup_file(target_bin)

    try:
        shutil.copy(source_bin, target_bin)
        os.chmod(target_bin, 0o755)
        print(f"Binário copiado para {target_bin}")
    except Exception as e:
        print("Erro ao copiar binário para destino:", e)
        sys.exit(1)

    print(f"Instalação concluída em: {target_bin}")


def autostart():
    """Cria arquivo XDG autostart em ~/.config/autostart/."""
    print("=== Configuração de Autostart ===\n")

    user_home = get_user_home(1000)
    target_bin = os.path.join(user_home, ".local", "bin", "app_launcher")
    autostart_dir = os.path.join(user_home, ".config", "autostart")
    autostart_file = os.path.join(autostart_dir, "app_launcher.desktop")

    if not os.path.exists(target_bin):
        print(f"Erro: binário não encontrado em {target_bin}")
        print("Execute 'install.py install' primeiro.")
        sys.exit(1)

    os.makedirs(autostart_dir, exist_ok=True)

    desktop_entry = f"""[Desktop Entry]
Type=Application
Name=AppLauncher
Exec={target_bin}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""

    if os.path.exists(autostart_file):
        backup_file(autostart_file)

    try:
        with open(autostart_file, "w") as f:
            f.write(desktop_entry)
        os.chmod(autostart_file, 0o644)
        print(f"Arquivo de autostart criado: {autostart_file}")
    except Exception as e:
        print("Erro ao criar arquivo de autostart:", e)
        sys.exit(1)

    print("Autostart configurado com XDG (sem sudo)")


def remove():
    """Remove binário e configuração de autostart."""
    print("=== Remoção do AppLauncher ===\n")

    user_home = get_user_home(1000)

    print("--- Removendo binário instalado ---")
    target_bin = os.path.join(user_home, ".local", "bin", "app_launcher")
    bin_backup = os.path.join(user_home, ".local", "bin", "app_launcher.bak")

    if os.path.exists(target_bin):
        os.remove(target_bin)
        print(f"Removido: {target_bin}")
    else:
        print(f"Não encontrado: {target_bin}")

    if os.path.exists(bin_backup):
        os.remove(bin_backup)
        print(f"Removido backup: {bin_backup}")

    print("\n--- Removendo configuração de autostart ---")
    autostart_file = os.path.join(
        user_home, ".config", "autostart", "app_launcher.desktop"
    )
    autostart_backup = autostart_file + ".bak"

    if os.path.exists(autostart_file):
        os.remove(autostart_file)
        print(f"Removido: {autostart_file}")
    else:
        print(f"Não encontrado: {autostart_file}")

    if os.path.exists(autostart_backup):
        os.remove(autostart_backup)
        print(f"Removido backup: {autostart_backup}")

    print("\n=== Remoção concluída ===")


def main():
    parser = argparse.ArgumentParser(
        description="Script de instalação e build para o AppLauncher"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=["build", "install", "autostart", "remove", "all"],
        help="Comando a executar (padrão: all)",
    )
    args = parser.parse_args()

    if args.command == "all":
        print("=== Instalação completa do AppLauncher ===\n")
        build()
        print()
        install()
        print()
        autostart()
        print("\n=== Instalação concluída ===")
    elif args.command == "build":
        build()
    elif args.command == "install":
        install()
    elif args.command == "autostart":
        autostart()
    elif args.command == "remove":
        remove()


if __name__ == "__main__":
    main()
