import cv2
import numpy as np
import pyautogui
import time
import os
import sys
import pygetwindow as gw
import pyperclip

class SalusRobot:
    def __init__(self, logger_func, stop_event, simulacao=False):
        self.log = logger_func
        self.stop_event = stop_event
        self.simulacao = simulacao
        
        if getattr(sys, 'frozen', False):
            self.caminho_mapa = os.path.join(sys._MEIPASS, "imgs", "mapa.png")
        else:
            self.caminho_mapa = os.path.join("imgs", "mapa.png")

        self.mapa_img = None
        self._posicoes_cache = {}
        self._carregar_mapa()

        self.cores = {
            "passo_01":        ([0, 0, 255], "click"),
            "passo_02":        ([39, 127, 255], "click"),
            "passo_03":        ([0, 255, 255], "click"),
            "passo_04":        ([255, 0, 0], "type_id"),
            "passo_pesquisar": ([255, 255, 0], "click"),
            "passo_05":        ([164, 73, 163], "click"),
            "biometria":       ([255, 255, 255], "click"),
            "passo_07":        ([127, 127, 127], "click"),
            "passo_08":        ([21, 0, 136], "click"),
            "passo_09":        ([201, 174, 255], "click"),
            "passo_11":        ([0, 255, 0], "type_file"),
            "passo_12":        ([0, 0, 0], "click")
        }
        
        self.sequencia = [
            "passo_01", "passo_02", "passo_03", "passo_04",
            "passo_pesquisar", "passo_05", "biometria",
            "passo_07", "passo_08", "passo_09", "passo_11", "passo_12"
        ]

    def _carregar_mapa(self):
        if not os.path.exists(self.caminho_mapa):
            self.log("Erro: mapa.png não encontrado")
            self.mapa_img = None
            return

        self.mapa_img = cv2.imread(self.caminho_mapa)
        if self.mapa_img is None:
            self.log("Erro: falha ao carregar mapa.png")

    def encontrar_cor(self, cor_bgr):
        if self.mapa_img is None:
            return None

        cor_key = tuple(cor_bgr)
        if cor_key in self._posicoes_cache:
            return self._posicoes_cache[cor_key]

        cor_np = np.array(cor_key, dtype="uint8")
        mask = cv2.inRange(self.mapa_img, cor_np, cor_np)
        pontos = cv2.findNonZero(mask)

        if pontos is not None:
            pos = pontos[0][0]
            self._posicoes_cache[cor_key] = pos
            return pos
        self._posicoes_cache[cor_key] = None
        return None

    def executar_acao(self, x, y, tipo, valor=None):
        if self.stop_event.is_set(): return False
        
        pyautogui.moveTo(x, y, duration=0.5)
        
        if tipo == "click":
            pyautogui.click()
            time.sleep(1.0)
            
        elif tipo == "type_id":
            pyautogui.doubleClick()
            pyautogui.press('backspace')
            time.sleep(0.5)
            pyautogui.write(valor, interval=0.1)
            time.sleep(0.5)
            
        elif tipo == "type_file":
            pyautogui.click()
            time.sleep(2.0)
            pyperclip.copy(valor)
            pyautogui.hotkey('alt', 'n')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(5.0)

        return True

    def executar_sequencia(self, id_val, caminho_completo, modo):
        try:
            janelas = gw.getWindowsWithTitle('Pedido de Exames (Remoto)')
            if janelas:
                salus = janelas[0]
                salus.activate()
                salus.maximize()
                time.sleep(1.0)
        except Exception:
            pass

        for nome_passo in self.sequencia:
            if self.stop_event.is_set(): return False, "Parada manual"
            
            cor_alvo, acao = self.cores[nome_passo]
            pos = self.encontrar_cor(cor_alvo)
            
            if pos:
                x, y = pos
                valor_texto = id_val if acao == "type_id" else caminho_completo if acao == "type_file" else None
                self.executar_acao(x, y, acao, valor_texto)
                
                if nome_passo == "passo_pesquisar":
                    time.sleep(3.0)
            else:
                self.log(f"Aviso: Cor do passo {nome_passo} não encontrada")
        
        return True, "Sucesso"

    def janela_disponivel(self, titulo="Pedido de Exames (Remoto)"):
        try:
            return bool(gw.getWindowsWithTitle(titulo))
        except Exception:
            return False
