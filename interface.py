import cv2
import pytesseract
import pyautogui
import numpy as np
from PIL import Image

class VisaoComputacional:
    def __init__(self, tesseract_cmd):
        # Configura o caminho do executável do Tesseract
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def localizar_na_tela(self, imagem_referencia, confianca=0.8):
        """
        Localiza uma imagem (ex: cabeçalho) na tela.
        Retorna (left, top, width, height) ou None.
        """
        try:
            return pyautogui.locateOnScreen(imagem_referencia, confidence=confianca, grayscale=True)
        except Exception as e:
            print(f"Erro ao localizar {imagem_referencia}: {e}")
            return None

    def _tratar_imagem(self, pil_image):
        """
        Converte imagem PIL para OpenCV, aplica Grayscale e Threshold
        para remover o fundo azul da seleção e isolar o texto.
        """
        img_np = np.array(pil_image)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Threshold: Tudo abaixo de 127 vira preto, acima vira branco.
        # Ajuste o 127 se necessário para lidar com o azul escuro vs claro.
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        return thresh

    def ler_texto_da_regiao(self, region, config_tesseract='--psm 6'):
        """
        Tira print de uma região específica, trata a imagem e extrai texto.
        region: tupla (left, top, width, height)
        """
        screenshot = pyautogui.screenshot(region=region)
        img_tratada = self._tratar_imagem(screenshot)
        
        # Debug visual (opcional: descomente para ver o que o robô vê)
        # cv2.imwrite(f"debug_{region[0]}.png", img_tratada)

        texto = pytesseract.image_to_string(img_tratada, config=config_tesseract)
        return [linha.strip() for linha in texto.split('\n') if linha.strip()]

    def clicar(self, x, y):
        pyautogui.click(x, y)

    def duplo_clique(self, x, y):
        pyautogui.doubleClick(x, y)