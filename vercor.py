import os
import time
import csv
from datetime import datetime
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# ================= CONFIG =================
SITE_URL = "https://SEU-SITE-AQUI.com"   # <-- TROQUE AQUI

IDS_TXT_PATH = "ids.txt"                # arquivo com 1 ID por linha
DOWNLOAD_DIR = os.path.abspath("downloads")
LOG_CSV = "log_resultados.csv"
LOG_TXT = "log_resultados.txt"

WAIT = 20
# =========================================


# ======= SELETORES (dos seus prints) =======
ID_INPUT = (By.NAME, "requisicao")

# Se o botão de consultar tiver seletor melhor no seu site, troque aqui.
# Esse é genérico: pega o primeiro botão clicável do formulário, costuma funcionar.
CONSULT_BTN = (By.CSS_SELECTOR, "form button, form input[type='submit'], button, input[type='submit']")

LIBERADO_BADGE = (
    By.CSS_SELECTOR,
    'span.new.badge.badge-verde[data-badge-caption="Liberado"]'
)

DOWNLOAD_LINK = (By.CSS_SELECTOR, "a.btn-download-exame")
# ==========================================


def ler_ids_txt(path: str) -> list[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Não achei o arquivo: {path}")

    ids = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            v = line.strip()
            if not v or v.startswith("#"):
                continue
            ids.append(v)
    return ids


def criar_driver(download_dir: str) -> webdriver.Chrome:
    os.makedirs(download_dir, exist_ok=True)

    options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 900)
    return driver


def cookies_para_requests(driver: webdriver.Chrome) -> requests.Session:
    s = requests.Session()
    for c in driver.get_cookies():
        s.cookies.set(c["name"], c["value"])
    return s


def esta_liberado(wait: WebDriverWait) -> bool:
    try:
        wait.until(EC.visibility_of_element_located(LIBERADO_BADGE))
        return True
    except TimeoutException:
        return False


def baixar_pdf(session: requests.Session, url: str, out_path: str) -> None:
    # baixa e grava em arquivo
    with session.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 128):
                if chunk:
                    f.write(chunk)


def append_log_txt(path: str, msg: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def ensure_csv_header(path: str) -> None:
    if os.path.exists(path):
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "id", "status", "pdf_salvo_em", "url_pdf", "erro"])


def append_log_csv(path: str, row: list[str]) -> None:
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(row)


def executar():
    ids = ler_ids_txt(IDS_TXT_PATH)
    if not ids:
        print("⚠️ ids.txt está vazio.")
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ensure_csv_header(LOG_CSV)

    driver = criar_driver(DOWNLOAD_DIR)
    wait = WebDriverWait(driver, WAIT)

    try:
        driver.get(SITE_URL)

        for i, doc_id in enumerate(ids, start=1):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{i}/{len(ids)}] ID: {doc_id}")

            try:
                # preencher ID
                campo = wait.until(EC.element_to_be_clickable(ID_INPUT))
                campo.clear()
                campo.send_keys(doc_id)

                # consultar
                wait.until(EC.element_to_be_clickable(CONSULT_BTN)).click()

                # pequena pausa pro resultado aparecer
                time.sleep(0.8)

                if not esta_liberado(wait):
                    status = "NAO_LIBERADO"
                    msg = f"{ts} | {doc_id} | {status}"
                    print("⏭️ Não liberado.")
                    append_log_txt(LOG_TXT, msg)
                    append_log_csv(LOG_CSV, [ts, doc_id, status, "", "", ""])
                    continue

                # liberado -> pegar link do pdf
                link = wait.until(EC.presence_of_element_located(DOWNLOAD_LINK))
                url_pdf = link.get_attribute("href")

                if not url_pdf:
                    status = "LIBERADO_SEM_LINK"
                    msg = f"{ts} | {doc_id} | {status}"
                    print("⚠️ Liberado, mas sem href no link.")
                    append_log_txt(LOG_TXT, msg)
                    append_log_csv(LOG_CSV, [ts, doc_id, status, "", "", "href vazio"])
                    continue

                # salvar como ID.pdf
                out_path = os.path.join(DOWNLOAD_DIR, f"{doc_id}.pdf")

                # se já existir, não baixa de novo
                if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                    status = "JA_EXISTE"
                    msg = f"{ts} | {doc_id} | {status} | {out_path}"
                    print("↩️ Já existe, pulando download.")
                    append_log_txt(LOG_TXT, msg)
                    append_log_csv(LOG_CSV, [ts, doc_id, status, out_path, url_pdf, ""])
                    continue

                sess = cookies_para_requests(driver)
                baixar_pdf(sess, url_pdf, out_path)

                status = "LIBERADO_BAIXADO"
                msg = f"{ts} | {doc_id} | {status} | {out_path}"
                print("✅ Baixado:", out_path)

                append_log_txt(LOG_TXT, msg)
                append_log_csv(LOG_CSV, [ts, doc_id, status, out_path, url_pdf, ""])

                time.sleep(0.5)

            except Exception as e:
                status = "ERRO"
                err = str(e)
                msg = f"{ts} | {doc_id} | {status} | {err}"
                print("❌ Erro:", err)
                append_log_txt(LOG_TXT, msg)
                append_log_csv(LOG_CSV, [ts, doc_id, status, "", "", err])

    finally:
        driver.quit()


if __name__ == "__main__":
    executar()