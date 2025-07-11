import base64

import psutil
from PyQt5.QtGui import QIcon, QImage, QPixmap


def base64_to_icon(icon=None, connected=False) -> QIcon:
    image = QImage()
    image.loadFromData(base64.b64decode(icon))
    return QIcon(QPixmap.fromImage(image))


def are_processes_running():
    resultados = {}
    programas_para_verificar = ["emulationstation", "retroarch", "kodi"]

    # Converte a lista de programas para minúsculas para garantir consistência
    programas_para_verificar = [p.lower() for p in programas_para_verificar]

    # Itera pelos processos em execução
    for processo in psutil.process_iter(["name"]):
        try:
            nome_processo = processo.info["name"].lower()
            if nome_processo in programas_para_verificar:
                resultados[nome_processo] = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Para os programas não encontrados, retorna False
    for programa in programas_para_verificar:
        if programa not in resultados:
            resultados[programa] = False

    return resultados
