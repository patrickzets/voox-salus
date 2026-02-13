import os
import time
import pyautogui
import pyperclip

PASTA = "pdfs_gerados"

pyautogui.FAILSAFE = True


def ler_pdfs(pasta):
    lista = []

    for arquivo in os.listdir(pasta):

        if arquivo.lower().endswith(".pdf"):

            nome_sem_ext = os.path.splitext(arquivo)[0]
            caminho_pdf = os.path.join(pasta, arquivo)

            if "-" in nome_sem_ext:
                parte1, parte2 = nome_sem_ext.split("-", 1)
            else:
                print("Formato inválido:", nome_sem_ext)
                continue

            lista.append((parte1, parte2, caminho_pdf))

    return lista


itens = ler_pdfs(PASTA)

print("PDFs encontrados:", len(itens))
time.sleep(3)


for parte1, parte2, caminho_pdf in itens:

    print("Processando:", parte1, "-", parte2)

    # ===================================
    # 🔹 1) PESQUISAR (parte depois do -)
    # ===================================

    # pyautogui.click(x_pesquisa, y_pesquisa)
    # pyautogui.write(parte2)
    # pyautogui.press("enter")
    # time.sleep(2)

    # ===================================
    # 🔹 2) DIGITAR ID PARA ANEXAR (parte antes do -)
    # ===================================

    # pyautogui.click(x_id, y_id)
    # pyautogui.write(parte1)
    # time.sleep(1)

    # ===================================
    # 🔹 3) ANEXAR ARQUIVO
    # ===================================

    # pyautogui.click(x_botao_anexar, y_botao_anexar)
    # time.sleep(3)  # esperar abrir janela

    pyperclip.copy(caminho_pdf)
    time.sleep(0.5)

    # pyautogui.click(x_campo_caminho, y_campo_caminho)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")

    time.sleep(3)

    # ===================================
    # 🔹 4) CLICAR PARA VOLTAR / RECOMEÇAR
    # ===================================

    # pyautogui.click(x_voltar, y_voltar)
    # time.sleep(3)

    print("Concluído:", parte1)
    time.sleep(2)


print("Todos os PDFs processados.")