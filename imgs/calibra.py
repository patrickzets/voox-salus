import cv2
import numpy as np
import json
import os
import sys

# Descobre o caminho da pasta onde o script está salvo
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# --- CONFIGURAÇÃO DAS CORES (BGR) ---
PASSOS_CONFIG = {
    "01_inicio":    {"arquivo": "mapa.png", "cor_bgr": [255, 0, 0]},
    "02_limpar":    {"arquivo": "mapa_2.png", "cor_bgr": [255, 127, 39]},
    "03_aba":       {"arquivo": "mapa_3.png", "cor_bgr": [255, 255, 0]},
    "04_digitar":   {"arquivo": "mapa_2.png", "cor_bgr": [0, 0, 255]},
    "05_lupa":      {"arquivo": "mapa_2.png", "cor_bgr": [0, 255, 255]},
    "06_selecionar":{"arquivo": "mapa_2.png", "cor_bgr": [163, 73, 164]},
    "00_alerta_sair":{"arquivo": "mapa_alerta.png", "cor_bgr": [255, 0, 255]},
    "08_setinha":   {"arquivo": "mapa.png", "cor_bgr": [127, 127, 127]},
    "09_pedidos":   {"arquivo": "mapa_4.png", "cor_bgr": [136, 0, 21]},
    "10_carregar":  {"arquivo": "mapa_5.png", "cor_bgr": [255, 174, 201]},
    "11_anexar":    {"arquivo": "mapa_6.png", "cor_bgr": [0, 255, 0]},
    "12_fechar":    {"arquivo": "mapa_5.png", "cor_bgr": [0, 0, 0]}
}

def encontrar_centro(img, cor_bgr):
    lower = np.array([max(0, c - 10) for c in cor_bgr])
    upper = np.array([min(255, c + 10) for c in cor_bgr])
    mask = cv2.inRange(img, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0:
            return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    return None

def gerar_mapa():
    mapa_coords = {}
    print("--- INICIANDO CALIBRAÇÃO ---")

    for passo, dados in PASSOS_CONFIG.items():
        # Monta o caminho completo usando o diretório do script
        caminho_imagem = os.path.join(DIRETORIO_ATUAL, dados["arquivo"])
        
        if os.path.exists(caminho_imagem):
            img = cv2.imread(caminho_imagem)
            centro = encontrar_centro(img, dados["cor_bgr"])
            if centro:
                mapa_coords[passo] = {"x": centro[0], "y": centro[1]}
                print(f"✅ {passo}: OK")
            else:
                print(f"⚠️ {passo}: Cor não achada em {dados['arquivo']}")
        else:
            print(f"❌ {passo}: Arquivo '{dados['arquivo']}' não existe em {DIRETORIO_ATUAL}!")
    
    # Salva o JSON na mesma pasta das imagens
    caminho_json = os.path.join(DIRETORIO_ATUAL, "config_mapa.json")
    with open(caminho_json, "w") as f:
        json.dump(mapa_coords, f, indent=4)
        print(f"\nMapa salvo em: {caminho_json}")

if __name__ == "__main__":
    gerar_mapa()
