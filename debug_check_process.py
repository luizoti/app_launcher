#!/usr/bin/env python3
"""Debug script — salva lista de processos em log para análise."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psutil

from src.utils import _extract_process_name, _focus_process, check_running_processes

BLOCK_LIST = ["emulationstation", "kodi", "moonlight", "pegasus", "retroarch"]
LOG_FILE = "debug_process.log"


def _dump_candidates(search_terms: list[str]) -> list[str]:
    termos = [t.lower() for t in search_terms]
    lines: list[str] = []
    lines.append(f"{'='*70}")
    lines.append(f"VARRENDO TODOS OS PROCESSOS — busca por: {search_terms}")
    lines.append(f"{'='*70}")

    encontrados = 0
    erros = 0
    total = 0

    for proc in psutil.process_iter(["name", "cmdline", "pid"]):
        total += 1
        try:
            raw_name = proc.info.get("name")
            name = (raw_name or "").lower()
            raw_cmdline = proc.info.get("cmdline")
            cmdline = " ".join(raw_cmdline or []).lower()
            pid = proc.info.get("pid", "?")

            match_info = []
            for term, orig in zip(termos, search_terms):
                reasons = []
                if term in name:
                    reasons.append("name contem termo")
                if name in term:
                    reasons.append("termo contem name (trunc?)")
                if term in cmdline:
                    reasons.append("cmdline contem termo")
                if reasons:
                    match_info.append(f"  >> {orig} -> {', '.join(reasons)}")

            if match_info:
                encontrados += 1
                nome_exib = raw_name or "(None)"
                cmd_exib = " ".join(raw_cmdline or ["(None)"])
                lines.append(f"\n[OK] PID={pid}  name={nome_exib!r}")
                lines.append(f"     cmdline={cmd_exib!r}")
                for m in match_info:
                    lines.append(m)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            erros += 1
        except KeyError as e:
            erros += 1
            lines.append(f"[KEYERROR] proc={proc} — {e}")
        except Exception as e:
            erros += 1
            lines.append(f"[ERRO] proc={proc} — {type(e).__name__}: {e}")

    lines.append(f"\n{'='*40}")
    lines.append(f"Total varridos: {total}")
    lines.append(f"Match encontrados: {encontrados}")
    lines.append(f"Erros ignorados: {erros}")
    lines.append(f"{'='*40}")
    return lines


def _test_check_running_processes(search_terms: list[str]) -> list[str]:
    lines: list[str] = []
    lines.append(f"\n{'='*70}")
    lines.append(f"check_running_processes({search_terms})")
    lines.append(f"{'='*70}")
    result = check_running_processes(search_terms)
    lines.append(f"Resultado: {result}")
    if not result:
        lines.append(">>> ATENCAO: lista vazia — nenhum processo detectado!")
    return lines


def _test_focus_process(name: str) -> list[str]:
    result = _focus_process(name)
    return [f"\n_focus_process({name!r})", f"Resultado: {result}"]


def _test_extract_process_name() -> list[str]:
    cmds = [
        ["x-terminal-emulator", "-e", "emulationstation"],
        ["/usr/bin/moonlight-qt", "stream", "nitro", "app", "Pegasus"],
        "subl",
        "/usr/bin/firefox https://x.com",
    ]
    return [
        f"\n--- _extract_process_name ---",
        *[
            f"_extract_process_name({cmd!r}) = {_extract_process_name(cmd)!r}"
            for cmd in cmds
        ],
    ]


if __name__ == "__main__":
    all_lines: list[str] = []
    all_lines.append(f"DEBUG PROCESS LOG — {datetime.now().isoformat()}")
    all_lines.append("")

    all_lines.extend(_dump_candidates(BLOCK_LIST))
    all_lines.extend(_test_check_running_processes(BLOCK_LIST))
    for name in BLOCK_LIST:
        all_lines.extend(_test_focus_process(name))
    all_lines.extend(_test_extract_process_name())

    text = "\n".join(all_lines) + "\n"
    with open(LOG_FILE, "w") as f:
        f.write(text)
    print(f"Log salvo em: {LOG_FILE}")
