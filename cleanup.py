#!/usr/bin/env python3
"""Script de cleanup para desfazer instalações anteriores do AppLauncher."""

import os
import pwd
import sys


def get_user_home(uid=1000):
    try:
        return pwd.getpwuid(uid).pw_dir
    except KeyError:
        print(f"Não foi possível encontrar usuário com UID {uid}")
        sys.exit(1)


def cleanup_install():
    """Remove binário instalado em ~/.local/bin/"""
    user_home = get_user_home(1000)
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


def cleanup_autostart():
    """Remove symlink e arquivos do RetroPie em /opt/retropie/"""
    autostart_link = "/opt/retropie/configs/all/autostart"
    autostart_backup = "/opt/retropie/configs/all/autostart.bak"
    autostart_script = "/opt/retropie/configs/all/autostart.sh"
    autostart_script_backup = "/opt/retropie/configs/all/autostart.sh.bak"

    if os.path.islink(autostart_link):
        os.remove(autostart_link)
        print(f"Removido symlink: {autostart_link}")
    elif os.path.exists(autostart_link):
        os.remove(autostart_link)
        print(f"Removido: {autostart_link}")
    else:
        print(f"Não encontrado: {autostart_link}")

    if os.path.exists(autostart_backup):
        os.remove(autostart_backup)
        print(f"Removido backup: {autostart_backup}")

    if os.path.exists(autostart_script):
        os.remove(autostart_script)
        print(f"Removido: {autostart_script}")

    if os.path.exists(autostart_script_backup):
        os.remove(autostart_script_backup)
        print(f"Removido backup: {autostart_script_backup}")


def cleanup_all():
    """Executa todos os cleanups."""
    print("=== Cleanup do AppLauncher ===\n")

    print("--- Removendo binário instalado ---")
    cleanup_install()

    print("\n--- Removendo configuração de autostart (RetroPie) ---")
    cleanup_autostart()

    print("\n=== Cleanup concluído ===")


def main():
    cleanup_all()


if __name__ == "__main__":
    main()
