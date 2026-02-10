import cv2
import pytesseract
import pyautogui
import numpy as np
from PIL import Image

class VisaoComputacional:
    def __init__(self, tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def localizar_imagem(self, caminho_imagem, confianca=0.7):
        """ Localiza imagem na tela com tolerância a falhas. """
        try:
            return pyautogui.locateOnScreen(caminho_imagem, confidence=confianca, grayscale=True)
        except:
            return None

    def _tratar_imagem_para_ocr(self, img_pil, zoom=3):
        """ Aumenta e binariza a imagem para leitura perfeita. """
        img_np = np.array(img_pil)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Upscale para letras pequenas
        h, w = gray.shape
        img_resized = cv2.resize(gray, (w * zoom, h * zoom), interpolation=cv2.INTER_LINEAR)
        
        # Limiarização (Preto no Branco)
        _, thresh = cv2.threshold(img_resized, 150, 255, cv2.THRESH_BINARY)
        return thresh

    def ler_texto(self, region=None):
        """ Captura e lê o texto da tela ou de uma região. """
        screenshot = pyautogui.screenshot(region=region)
        img_tratada = self._tratar_imagem_para_ocr(screenshot)
        texto = pytesseract.image_to_string(img_tratada, config='--psm 6 --oem 3 -l por')
        return texto.strip().upper()
