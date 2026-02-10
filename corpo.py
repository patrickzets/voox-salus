import time
import os
import json
import pyautogui
import pyperclip
import pygetwindow as gw # Necessário para manipular a janela

class ControladorSalus:
    def __init__(self, tesseract_path):
        self.mapa = {}
        self.carregar_mapa()
        
        self.sequencia = [
            "01_inicio", "02_limpar", "03_aba", "04_digitar", "05_lupa",
            "06_selecionar", "08_setinha", "09_pedidos", "10_carregar", 
            "11_anexar", "12_fechar"
        ]

    def carregar_mapa(self):
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_json = os.path.join(dir_atual, "config_mapa.json")
        try:
            with open(caminho_json, "r") as f:
                self.mapa = json.load(f)
        except:
            print("Configuração do mapa não encontrada.")

    def focar_janela(self, log_func):
        """ Traz a janela 'Pedidos remoto' para a frente """
        try:
            # Busca janelas que contenham o nome exato ou parcial
            janelas = gw.getWindowsWithTitle('Pedidos remoto')
            if janelas:
                janela = janelas[0]
                if janela.isMinimized:
                    janela.restore()
                janela.activate()
                janela.maximize()
                time.sleep(1.0) # Tempo para estabilizar a imagem
                return True
            else:
                log_func("⚠️ Janela 'Pedidos remoto' não encontrada!", "erro")
                return False
        except Exception as e:
            log_func(f"❌ Erro ao focar janela: {str(e)}", "erro")
            return False

    def processar_por_arquivos(self, pasta, callback_log, modo_biovida):
        # Primeiro traz a tela para frente antes de qualquer loop
        if not self.focar_janela(callback_log):
            return # Para a execução se a janela não estiver aberta

        arquivos = [f for f in os.listdir(pasta) if f.lower().endswith('.pdf')]
        for arquivo in arquivos:
            id_paciente = arquivo.replace(".pdf", "")
            if modo_biovida and "-" in id_paciente:
                id_paciente = id_paciente.split("-")[-1]
            
            caminho = os.path.join(pasta, arquivo)
            callback_log(f"Processando: {id_paciente}")
            
            resultado = self.executar_passos(id_paciente, caminho)
            yield (id_paciente, resultado)

    def executar_passos(self, id_val, caminho_arquivo):
        for passo in self.sequencia:
            if passo not in self.mapa: continue
            
            x, y = self.mapa[passo]['x'], self.mapa[passo]['y']

            if passo == "04_digitar":
                pyautogui.click(x, y)
                time.sleep(0.5)
                pyautogui.doubleClick(x, y)
                time.sleep(0.8)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyautogui.write(id_val, interval=0.1)
                time.sleep(0.5)
            
            elif passo == "11_anexar":
                pyautogui.click(x, y)
                time.sleep(2.0)
                pyperclip.copy(caminho_arquivo)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1.0)
                pyautogui.press('enter')
                time.sleep(4.0)
            
            elif passo == "05_lupa":
                pyautogui.click(x, y)
                time.sleep(4.0)

            elif passo == "06_selecionar":
                pyautogui.doubleClick(x, y)
                time.sleep(3.0)

            else:
                pyautogui.click(x, y)
                time.sleep(1.0)

        return "SUCESSO"
