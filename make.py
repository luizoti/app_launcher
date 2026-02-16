import os
import pwd
import shutil
import subprocess
import sys


def get_user_home(uid=1000):
    """
    Retorna o diretório home do usuário com UID especificado.
    """
    try:
        return pwd.getpwuid(uid).pw_dir
    except KeyError:
        print(f"Não foi possível encontrar usuário com UID {uid}")
        sys.exit(1)


def backup_file(filepath):
    """
    Se o arquivo (ou link) existir, faz backup renomeando-o com a extensão .bak.
    """
    if os.path.exists(filepath) or os.path.islink(filepath):
        backup_path = filepath + ".bak"
        print(f"Realizando backup de {filepath} para {backup_path}")
        try:
            shutil.move(filepath, backup_path)
        except Exception as e:
            print(f"Erro ao fazer backup de {filepath}: {e}")
            sys.exit(1)


def backup_if_exists(paths):
    """
    Para cada caminho da lista, verifica e faz backup se existir.
    """
    for path in paths:
        backup_file(path)


def main():
    user_home = get_user_home(1000)
    target_dir = os.path.join(user_home, ".local", "bin")
    os.makedirs(target_dir, exist_ok=True)
    target_bin = os.path.join(target_dir, "app_launcher")

    script_dir = os.path.abspath(os.path.dirname(__file__))
    main_py = os.path.join(script_dir, "main.py")

    command = [
        "pyinstaller",
        "--onefile",
        "--hidden-import=requests",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=systemd.journal",
        "--name=app_launcher",
        main_py,
    ]

    print("Executando pyinstaller...")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("Erro durante a compilação:", e)
        sys.exit(1)

    binary_path = os.path.join(script_dir, "dist", "app_launcher")
    if not os.path.exists(binary_path):
        print(f"Binário compilado não encontrado em {binary_path}")
        sys.exit(1)

    backup_if_exists([target_bin])

    try:
        shutil.copy(binary_path, target_bin)
        os.chmod(target_bin, 0o755)
        print(f"Binário copiado para {target_bin}")
    except Exception as e:
        print("Erro ao copiar binário para destino:", e)
        sys.exit(1)

    final_dest = "/opt/retropie/configs/all/autostart"
    final_dir = os.path.dirname(final_dest)
    os.makedirs(final_dir, exist_ok=True)

    backup_if_exists([final_dest, final_dest + ".sh"])

    try:
        if os.path.exists(final_dest) or os.path.islink(final_dest):
            os.remove(final_dest)
        os.symlink(target_bin, final_dest)
        print(f"Link simbólico criado de {target_bin} para {final_dest}")
    except Exception as e:
        print("Erro ao criar link simbólico:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
