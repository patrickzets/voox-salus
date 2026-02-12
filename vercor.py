import os
import re
import time
import csv
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional

import pyautogui
import keyboard

# =========================
# CONFIGURAÇÕES
# =========================

@dataclass
class ClickPoints:
    # 1) Pesquisa
    search_field: Tuple[int, int]

    # 2) Sequência rápida até abrir o anexo
    click_1: Tuple[int, int]
    click_2: Tuple[int, int]
    open_attach_dialog_click: Tuple[int, int]  # <-- este é o "click antes de anexar" (abrir janela)

    # (Opcional) clicar no campo "Nome do arquivo" do seletor (se não estiver focando sozinho)
    file_dialog_filename_field: Optional[Tuple[int, int]]

    # (Opcional) depois que o arquivo entra, clique final no sistema (ex.: confirmar/anexar)
    confirm_click: Optional[Tuple[int, int]]


# Delays: mouse rápido, mas com 8s antes do anexo
DELAYS = {
    "between_clicks_fast": 0.10,
    "after_search_enter": 0.50,
    "wait_before_attach_seconds": 8.0,   # <-- seu requisito
    "after_file_path_enter": 0.80,
    "between_files": 0.40
}

# Padrão no nome do arquivo: "ANTES-12345"
ID_PATTERN = re.compile(r"(?P<attach>\d+)\-(?P<search>\d{5})")

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01


# =========================
# UTILITÁRIOS
# =========================

def safe_abort_check():
    if keyboard.is_pressed("esc"):
        raise KeyboardInterrupt("Abortado pelo usuário (ESC).")

def click(pt: Tuple[int, int], delay: float = 0.1):
    safe_abort_check()
    pyautogui.click(pt[0], pt[1])
    time.sleep(delay)

def type_text(text: str):
    safe_abort_check()
    pyautogui.write(text, interval=0.01)

def press_enter():
    safe_abort_check()
    pyautogui.press("enter")

def find_ids_from_filename(filename: str) -> Tuple[str, str]:
    base = os.path.basename(filename)
    m = ID_PATTERN.search(base)
    if not m:
        raise ValueError(f"Nome fora do padrão 'NUMEROS-12345': {base}")
    return m.group("attach"), m.group("search")

def list_files(folder: str) -> List[str]:
    return [
        os.path.join(folder, n)
        for n in sorted(os.listdir(folder))
        if os.path.isfile(os.path.join(folder, n))
    ]


# =========================
# CAPTURA DE COORDENADAS
# =========================

POINT_KEYS = [
    ("search_field", "CAMPO DE PESQUISA (digita os 5 dígitos depois do traço). Posicione e aperte F8"),
    ("click_1", "1º click após pesquisar. Posicione e aperte F8"),
    ("click_2", "2º click. Posicione e aperte F8"),
    ("open_attach_dialog_click", "CLICK QUE ABRE A JANELA DE ANEXAR (antes de anexar). Posicione e aperte F8"),
    ("file_dialog_filename_field", "CAMPO 'Nome do arquivo' no seletor (opcional, mas recomendado). Posicione e aperte F8"),
    ("confirm_click", "CLICK FINAL no sistema (opcional: confirmar/salvar). Posicione e aperte F8"),
]

def capture_points() -> ClickPoints:
    print("\n=== CAPTURA DE COORDENADAS ===")
    print("Abra o sistema/app na tela certa. Aperte ESC para abortar.\n")

    pts: Dict[str, Tuple[int, int]] = {}

    for key, msg in POINT_KEYS:
        print(msg)
        while True:
            safe_abort_check()
            if keyboard.is_pressed("f8"):
                x, y = pyautogui.position()
                pts[key] = (x, y)
                print(f"  -> Capturado {key}: {pts[key]}\n")
                time.sleep(0.35)  # debounce
                break
            time.sleep(0.02)

    return ClickPoints(
        search_field=pts["search_field"],
        click_1=pts["click_1"],
        click_2=pts["click_2"],
        open_attach_dialog_click=pts["open_attach_dialog_click"],
        file_dialog_filename_field=pts.get("file_dialog_filename_field"),
        confirm_click=pts.get("confirm_click"),
    )


# =========================
# ANEXO REAL (SELETOR DE ARQUIVOS)
# =========================

def attach_file_via_dialog(file_path: str, filename_field: Optional[Tuple[int, int]]):
    """
    Pressupõe que a janela de anexar (seletor de arquivos) está aberta e em foco.
    Estratégia: clicar no campo 'Nome do arquivo' (se informado) e digitar caminho completo + Enter.
    """
    safe_abort_check()

    # Garantir caminho absoluto (melhora compatibilidade)
    file_path = os.path.abspath(file_path)

    if filename_field is not None:
        click(filename_field, 0.10)

    # Limpa o campo e cola o caminho
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.05)
    type_text(file_path)
    press_enter()


# =========================
# AUTOMAÇÃO
# =========================

def run(folder: str, points: ClickPoints, log_csv_path: str):
    files = list_files(folder)
    if not files:
        raise RuntimeError("A pasta não tem arquivos.")

    print(f"\nArquivos encontrados: {len(files)}")
    print("Deixe o sistema/app em FOCO (janela ativa).")
    print("ESC aborta. (Failsafe: mover mouse pro canto superior esquerdo também aborta.)\n")
    time.sleep(2)

    with open(log_csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["arquivo", "attach_id", "search_id", "status", "erro"])

        for i, path in enumerate(files, start=1):
            base = os.path.basename(path)
            try:
                attach_id, search_id = find_ids_from_filename(base)

                print(f"[{i}/{len(files)}] {base} | search={search_id} | attach={attach_id}")

                # 1) Pesquisa (5 dígitos) + Enter
                click(points.search_field, DELAYS["between_clicks_fast"])
                pyautogui.hotkey("ctrl", "a")
                type_text(search_id)
                press_enter()
                time.sleep(DELAYS["after_search_enter"])

                # 2) Clica rápido até abrir janela de anexar
                click(points.click_1, DELAYS["between_clicks_fast"])
                click(points.click_2, DELAYS["between_clicks_fast"])

                # Este é o clique "antes de anexar": abre o seletor -> esperar 8s
                click(points.open_attach_dialog_click, DELAYS["between_clicks_fast"])
                time.sleep(DELAYS["wait_before_attach_seconds"])

                # 3) Anexa de verdade (digita o caminho do arquivo no seletor e Enter)
                attach_file_via_dialog(path, points.file_dialog_filename_field)
                time.sleep(DELAYS["after_file_path_enter"])

                # 4) (Opcional) clique final no sistema, se necessário
                if points.confirm_click is not None:
                    click(points.confirm_click, DELAYS["between_clicks_fast"])

                w.writerow([base, attach_id, search_id, "OK", ""])
                time.sleep(DELAYS["between_files"])

            except KeyboardInterrupt as e:
                w.writerow([base, "", "", "ABORTADO", str(e)])
                print("\nAbortado pelo usuário.")
                raise

            except Exception as e:
                w.writerow([base, "", "", "ERRO", str(e)])
                print(f"  !! ERRO: {e}")
                time.sleep(0.5)


# =========================
# ENTRADA
# =========================

def choose_folder_gui() -> str:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        return filedialog.askdirectory(title="Selecione a pasta com os arquivos")
    except Exception:
        return ""

def main():
    print("=== Automação: pesquisar + abrir anexo + anexar arquivo real ===")
    print("Padrão esperado no nome do arquivo: NUMEROS-12345 (5 dígitos após o traço)")
    print("Ex.: 987654-12345.pdf\n")

    folder = choose_folder_gui()
    if not folder:
        folder = input("Cole o caminho da pasta aqui: ").strip().strip('"')

    if not os.path.isdir(folder):
        raise RuntimeError("Pasta inválida.")

    points = capture_points()
    log_path = os.path.join(folder, "log_automacao.csv")

    run(folder, points, log_path)
    print(f"\nConcluído! Log em: {log_path}")

if __name__ == "__main__":
    main()