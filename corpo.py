import time
import os
import json
import pyautogui
import pyperclip
from interface import VisaoComputacional

class ControladorSalus:
    def __init__(self, tesseract_path):
        self.visao = VisaoComputacional(tesseract_path)
        self.mapa = {}
        self.carregar_mapa()
        
        # Sequência exata de execução
        self.sequencia = [
            "01_inicio", "02_limpar", "03_aba", "04_digitar", "05_lupa",
            "06_selecionar", "08_setinha", "09_pedidos", "10_carregar", 
            "11_anexar", "12_fechar"
        ]

    def carregar_mapa(self):
        # Busca o JSON na pasta do script para evitar erro de caminho
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_json = os.path.join(dir_atual, "config_mapa.json")
        try:
            with open(caminho_json, "r") as f:
                self.mapa = json.load(f)
        except:
            print("⚠️ Erro: config_mapa.json não encontrado.")

    def processar_por_arquivos(self, pasta, callback_log, modo_biovida):
        if not os.path.exists(pasta): return
        arquivos = [f for f in os.listdir(pasta) if f.lower().endswith('.pdf')]
        
        for arquivo in arquivos:
            id_paciente = arquivo.replace(".pdf", "")
            if modo_biovida and "-" in id_paciente:
                id_paciente = id_paciente.split("-")[-1]
            
            caminho_pdf = os.path.join(pasta, arquivo)
            callback_log(f"Iniciando ID: {id_paciente}...", "info")
            
            res = self.executar_sequencia(id_paciente, caminho_pdf, callback_log)
            yield (id_paciente, res)

    def executar_sequencia(self, id_val, caminho_arquivo, log):
        for passo in self.sequencia:
            if passo not in self.mapa: continue
            
            x, y = self.mapa[passo]['x'], self.mapa[passo]['y']

            if passo == "04_digitar":
                pyautogui.click(x, y)
                pyautogui.hotkey('ctrl', 'a'); pyautogui.press('backspace')
                pyautogui.write(id_val); time.sleep(0.5)
            elif passo == "05_lupa":
                pyautogui.click(x, y); time.sleep(4.0)
            elif passo == "06_selecionar":
                pyautogui.doubleClick(x, y); time.sleep(3.0)
                # --- GUARDA DE ALERTA ---
                if self.checar_alerta_ocr():
                    log("⚠️ Alerta detectado. Fechando...", "aviso")
                    if "00_alerta_sair" in self.mapa:
                        pyautogui.click(self.mapa["00_alerta_sair"]['x'], self.mapa["00_alerta_sair"]['y'])
                        time.sleep(1.5)
            elif passo == "11_anexar":
                pyautogui.click(x, y); time.sleep(1.5)
                pyperclip.copy(caminho_arquivo)
                pyautogui.hotkey('ctrl', 'v'); time.sleep(0.5); pyautogui.press('enter')
                time.sleep(5.0) # Tempo de upload
            else:
                pyautogui.click(x, y); time.sleep(0.8)

        return "SUCESSO"

    def checar_alerta_ocr(self):
        """ Verifica se palavras de alerta estão na tela """
        texto = self.visao.ler_texto()
        perigo = ["BIOMETRIA", "AVISO", "ATENCAO", "ERRO", "ALERTA", "PENDENCIA"]
        return any(p in texto for p in perigo)
