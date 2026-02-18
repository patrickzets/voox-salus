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
SITE_URL = "https://biocroma.neovita.net.br"   # base
PAGINA_PEDIDOS = "https://biocroma.neovita.net.br/app/pedidos-paternidade"

IDS_TXT_PATH = "ids.txt"
DOWNLOAD_DIR = r"C:\Automacao\PDFs"

LOG_CSV = "log_resultados.csv"
LOG_TXT = "log_resultados.txt"

WAIT = 20
TEMPO_PARA_LOGIN = 20   # <<< TEMPO PRA VOCÊ LOGAR
# =========================================


# ===== MENU =====
MENU_PEDIDOS = (
    By.CSS_SELECTOR,
    'a[href="https://biocroma.neovita.net.br/app/pedidos-paternidade"]'
)

# ===== FILTRO / BUSCA =====
FILTRO_BTN = (By.CSS_SELECTOR, "a.modal-trigger.btn-acao")
MODAL = (By.ID, "modal")

ID_INPUT = (By.NAME, "requisicao")

LIBERADO_BADGE = (
    By.CSS_SELECTOR,
    'span.new.badge.badge-verde[data-badge-caption="Liberado"]'
)

DOWNLOAD_LINK = (By.CSS_SELECTOR, "a.btn-download-exame")
# =========================


def ler_ids_txt(path: str) -> list[str]:
    ids = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            v = line.strip()
            if v and not v.startswith("#"):
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

    d = webdriver.Chrome(options=options)
    d.set_window_size(1200, 900)

    return d


def cookies_para_requests(driver: webdriver.Chrome) -> requests.Session:
    s = requests.Session()
    for c in driver.get_cookies():
        s.cookies.set(c["name"], c["value"])
    return s


def ensure_csv_header(path: str) -> None:
    if os.path.exists(path):
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            ["timestamp", "id", "status", "pdf_salvo_em", "url_pdf", "erro"]
        )


def log_txt(msg: str) -> None:
    with open(LOG_TXT, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def log_csv(row: list[str]) -> None:
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)


def baixar_pdf(sess: requests.Session, url: str, out_path: str) -> None:
    with sess.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()

        with open(out_path, "wb") as f:
            for chunk in r.iter_content(1024 * 128):
                if chunk:
                    f.write(chunk)


def esta_liberado(wait: WebDriverWait) -> bool:
    try:
        wait.until(EC.visibility_of_element_located(LIBERADO_BADGE))
        return True
    except TimeoutException:
        return False


def abrir_filtro(wait: WebDriverWait, driver: webdriver.Chrome) -> None:

    try:
        m = driver.find_element(*MODAL)
        if m.is_displayed():
            return
    except:
        pass

    wait.until(EC.element_to_be_clickable(FILTRO_BTN)).click()
    wait.until(EC.visibility_of_element_located(MODAL))
    time.sleep(0.3)


def executar():

    ids = ler_ids_txt(IDS_TXT_PATH)
    ensure_csv_header(LOG_CSV)

    driver = criar_driver(DOWNLOAD_DIR)
    wait = WebDriverWait(driver, WAIT)

    try:
        # 1) Abre site
        driver.get(SITE_URL)

        print(f"⏳ Você tem {TEMPO_PARA_LOGIN}s para fazer login manualmente...")
        time.sleep(TEMPO_PARA_LOGIN)

        # 2) Clicar no menu uma vez
        wait.until(EC.element_to_be_clickable(MENU_PEDIDOS)).click()

        wait.until(lambda d: d.current_url.startswith(PAGINA_PEDIDOS))

        # 3) Processar IDs
        for i, doc_id in enumerate(ids, 1):

            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"\n[{i}/{len(ids)}] Requisição: {doc_id}")

            try:
                abrir_filtro(wait, driver)

                campo = wait.until(EC.element_to_be_clickable(ID_INPUT))
                campo.clear()
                campo.send_keys(doc_id)
                campo.send_keys("\n")

                time.sleep(1)

                if not esta_liberado(wait):

                    status = "NAO_LIBERADO"
                    print("⏭️ Não liberado.")

                    log_txt(f"{ts} | {doc_id} | {status}")
                    log_csv([ts, doc_id, status, "", "", ""])

                    continue

                link = wait.until(EC.presence_of_element_located(DOWNLOAD_LINK))
                url_pdf = link.get_attribute("href") or ""

                if not url_pdf:

                    status = "LIBERADO_SEM_LINK"
                    print("⚠️ Sem link.")

                    log_txt(f"{ts} | {doc_id} | {status}")
                    log_csv([ts, doc_id, status, "", "", "href vazio"])

                    continue

                out_path = os.path.join(DOWNLOAD_DIR, f"{doc_id}.pdf")

                if os.path.exists(out_path):

                    status = "JA_EXISTE"
                    print("↩️ Já existe.")

                    log_txt(f"{ts} | {doc_id} | {status}")
                    log_csv([ts, doc_id, status, out_path, url_pdf, ""])

                    continue

                sess = cookies_para_requests(driver)

                baixar_pdf(sess, url_pdf, out_path)

                status = "LIBERADO_BAIXADO"

                print("✅ Baixado:", out_path)

                log_txt(f"{ts} | {doc_id} | {status}")
                log_csv([ts, doc_id, status, out_path, url_pdf, ""])

            except Exception as e:

                err = str(e)

                print("❌ Erro:", err)

                log_txt(f"{ts} | {doc_id} | ERRO | {err}")
                log_csv([ts, doc_id, "ERRO", "", "", err])

    finally:
        driver.quit()


if __name__ == "__main__":
    executar()