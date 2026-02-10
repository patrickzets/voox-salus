import cv2
import os

# Altere para o nome do arquivo que está dando erro
NOME_ARQUIVO = "mapa.png" 
DIRETORIO = r"c:/Users/patri/OneDrive/Desktop/Voox/voox-salus/imgs/"
CAMINHO = os.path.join(DIRETORIO, NOME_ARQUIVO)

def check_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = image[y, x]
        print(f"📍 Coordenada: ({x}, {y}) | COR BGR PARA O CODIGO: [{pixel[0]}, {pixel[1]}, {pixel[2]}]")

image = cv2.imread(CAMINHO)
if image is None:
    print("Erro: Arquivo não encontrado!")
else:
    cv2.namedWindow("Identificador de Cores - Clique na bolinha")
    cv2.setMouseCallback("Identificador de Cores - Clique na bolinha", check_color)
    cv2.imshow("Identificador de Cores - Clique na bolinha", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
