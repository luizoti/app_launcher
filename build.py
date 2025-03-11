#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys


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
    # Obtém o diretório absoluto do script (supondo que main.py esteja no mesmo diretório)
    script_dir = os.path.abspath(os.path.dirname(__file__))
    main_py = os.path.join(script_dir, "main.py")

    # Caminho absoluto para o executável do pyinstaller
    pyinstaller_path = "/home/luiz/.asdf/installs/python/3.10.0/bin/pyinstaller"

    # Comando de compilação com pyinstaller usando caminhos absolutos
    command = [
        pyinstaller_path,
        "--onefile",
        "--hidden-import=requests",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=systemd.journal",
        main_py
    ]

    print("Executando pyinstaller...")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("Erro durante a compilação:", e)
        sys.exit(1)

    # Caminho absoluto para o binário compilado
    binary_path = os.path.join(script_dir, "dist", "main")
    if not os.path.exists(binary_path):
        print(f"Binário compilado não encontrado em {binary_path}")
        sys.exit(1)

    # Backup de scripts existentes em /usr/bin (autostart e/ou autostart.sh)
    usr_bin_paths = ["/usr/bin/autostart", "/usr/bin/autostart.sh"]
    backup_if_exists(usr_bin_paths)

    # Copia o binário compilado para /usr/bin com o nome "autostart"
    usr_autostart = "/usr/bin/autostart"
    try:
        shutil.copy(binary_path, usr_autostart)
        os.chmod(usr_autostart, 0o755)
        print(f"Binário copiado para {usr_autostart}")
    except Exception as e:
        print("Erro ao copiar binário para /usr/bin:", e)
        sys.exit(1)

    # Prepara o destino final: /opt/retropie/configs/all/autostart
    final_dest = "/opt/retropie/configs/all/autostart"
    final_dir = os.path.dirname(final_dest)
    os.makedirs(final_dir, exist_ok=True)

    # Se houver script existente no destino final, faz backup
    backup_if_exists([final_dest, final_dest + ".sh"])

    # Cria um link simbólico do autostart em /usr/bin para o destino final
    try:
        os.symlink(usr_autostart, final_dest)
        print(f"Link simbólico criado de {usr_autostart} para {final_dest}")
    except Exception as e:
        print("Erro ao criar link simbólico:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
