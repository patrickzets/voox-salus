import time
import os
import json
import pyautogui
import pyperclip
import sys

class ControladorSalus:
    def __init__(self, tesseract_path=None):
        self.mapa = {}
        self.carregar_mapa()
        
        # A sequência principal NÃO inclui o alerta, ele é um "extra"
        self.sequencia = [
            "01_inicio", "02_limpar", "03_aba", "04_digitar", "05_lupa",
            "06_selecionar", # AQUI ENTRA A GUARDA DEPOIS DISSO
            "08_setinha", "09_pedidos", "10_carregar", 
            "11_anexar", "12_fechar"
        ]

    def carregar_mapa(self):
        try:
            with open("config_mapa.json", "r") as f:
                self.mapa = json.load(f)
            print("Mapa carregado.")
        except:
            print("ERRO: Rode o calibrador.py!")

    def processar_por_arquivos(self, pasta, callback_log, modo_biovida):
        if not os.path.exists(pasta): return
        arquivos = [f for f in os.listdir(pasta) if f.lower().endswith('.pdf')]
        
        for arquivo in arquivos:
            id_paciente = arquivo.replace(".pdf", "")
            if modo_biovida and "-" in id_paciente:
                id_paciente = id_paciente.split("-")[-1]
            
            caminho = os.path.join(pasta, arquivo)
            callback_log(f"Iniciando ID: {id_paciente}...", "info")
            
            res = self.executar_sequencia_completa(id_paciente, caminho, callback_log)
            yield (id_paciente, res)
            time.sleep(1)

    def executar_sequencia_completa(self, id_val, caminho_arquivo, log_func):
        for passo in self.sequencia:
            if passo not in self.mapa:
                log_func(f"Passo {passo} ausente no mapa!", "erro")
                return f"ERRO CONFIG {passo}"

            dados = self.mapa[passo]
            x, y = dados['x'], dados['y']

            # --- AÇÕES ESPECÍFICAS ---

            if passo == "04_digitar":
                pyautogui.click(x, y); time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'a'); pyautogui.press('backspace')
                pyautogui.write(id_val); time.sleep(0.3)

            elif passo == "05_lupa":
                pyautogui.click(x, y)
                time.sleep(3.0) # Espera busca

            elif passo == "06_selecionar":
                 # Duplo clique para abrir
                 pyautogui.doubleClick(x, y)
                 log_func("Paciente aberto. Verificando alertas...", "info")
                 time.sleep(2.5) # Espera a janela (paciente OU alerta) aparecer
                 
                 # === AQUI ESTÁ A GUARDA (VERIFICAÇÃO DO ALERTA) ===
                 # Tenta clicar no botão "Sair" do alerta (Rosa)
                 if self.tentar_clicar_opcional("00_alerta_sair"):
                     log_func("⚠️ Alerta detectado e fechado.", "aviso")
                     time.sleep(1.5) # Espera o alerta sumir e a tela de trás focar
                 # Se não achar o alerta, ele simplesmente segue para o próximo passo (08_setinha)
                 # ==================================================

            elif passo == "11_anexar":
                pyautogui.click(x, y); time.sleep(1.5)
                pyperclip.copy(caminho_arquivo)
                pyautogui.hotkey('ctrl', 'v'); time.sleep(0.5)
                pyautogui.press('enter'); time.sleep(3.0)

            else:
                # Cliques normais (Inicio, Aba, Seta, Pedidos, etc)
                pyautogui.click(x, y)
                time.sleep(0.8)

        return "SUCESSO"

    def tentar_clicar_opcional(self, nome_passo):
        """
        Tenta clicar numa cor se ela existir no mapa.
        Não gera erro se não existir. Retorna True se clicou.
        """
        if nome_passo in self.mapa:
            x, y = self.mapa[nome_passo]['x'], self.mapa[nome_passo]['y']
            # Move primeiro para garantir o foco, depois clica
            pyautogui.moveTo(x, y) 
            pyautogui.click()
            return True
        return False
