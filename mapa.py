import cv2
import numpy as np
import os

CAMINHO_MAPA = os.path.join("imgs", "mapa.png")

CORES_ALVO = {
    "VERMELHO (Início)": [0, 0, 255],
    "AZUL (Digitar ID)": [255, 0, 0],
    "CIANO (Pesquisar)": [255, 255, 0],
    "VERDE (Anexar)":    [0, 255, 0],
    "PRETO (Fechar)":    [0, 0, 0]
}

def verificar_pontos():
    if not os.path.exists(CAMINHO_MAPA):
        print("Arquivo mapa.png não encontrado.")
        return

    img = cv2.imread(CAMINHO_MAPA)
    print(f"Lendo: {CAMINHO_MAPA}")
    print("-" * 30)

    for nome, cor_bgr in CORES_ALVO.items():
        cor_np = np.array(cor_bgr, dtype="uint8")
        mask = cv2.inRange(img, cor_np, cor_np)
        pontos = cv2.findNonZero(mask)

        if pontos is not None:
            x, y = pontos[0][0]
            print(f"[OK] {nome} encontrado em X={x}, Y={y}")
        else:
            print(f"[X] {nome} NÃO encontrado. Verifique a cor no Paint.")

if __name__ == "__main__":
    verificar_pontos()