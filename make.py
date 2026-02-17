import os
import pwd
import shutil
import subprocess
import sys


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
            # Se o backup já existir, removemos para evitar erro no move
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.move(filepath, backup_path)
        except Exception as e:
            print(f"Erro ao fazer backup de {filepath}: {e}")
            sys.exit(1)

def backup_if_exists(paths):
    for path in paths:
        backup_file(path)

def main():
    user_home = get_user_home(1000)
    target_dir = os.path.join(user_home, ".local", "bin")
    os.makedirs(target_dir, exist_ok=True)
    target_bin = os.path.join(target_dir, "app_launcher")

    script_dir = os.path.abspath(os.path.dirname(__file__))
    main_py = os.path.join(script_dir, "main.py")

    # Lista expandida de hidden imports para evitar erros comuns de Qt no Linux
    hidden_imports = [
        "requests",
        "PySide6.QtWidgets",
        "PySide6.QtGui",
        "PySide6.QtCore",
        "PySide6.QtOpenGL",  # Frequentemente necessário para renderização UI
        "systemd.journal",
    ]

    # Comando usando 'uv run' garante que usamos o binário correto do PyInstaller
    # e as bibliotecas do nosso .venv sem precisar ativar o shell manualmente.
    command = [
        "uv", "run", "pyinstaller",
        "--onefile",
        "--clean", # Limpa o cache para evitar conflitos de build anterior
        "--name=app_launcher",
    ]

    # Adiciona os hidden imports dinamicamente
    for imp in hidden_imports:
        command.extend(["--hidden-import", imp])

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

    backup_if_exists([target_bin])

    try:
        shutil.copy(binary_path, target_bin)
        os.chmod(target_bin, 0o755)
        print(f"Binário copiado para {target_bin}")
    except Exception as e:
        print("Erro ao copiar binário para destino:", e)
        sys.exit(1)

    # Configuração de Autostart (RetroPie)
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