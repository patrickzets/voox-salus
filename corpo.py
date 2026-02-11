import time
import os
import json
import pyautogui
import pyperclip
import pygetwindow as gw

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

    def focar_janela_robusta(self, log_func):
        try:
            titulos = gw.getAllTitles()
            alvo = None
            for t in titulos:
                if "pedidos remoto" in t.lower():
                    alvo = t
                    break
            
            if alvo:
                janela = gw.getWindowsWithTitle(alvo)[0]
                if janela.isMinimized: janela.restore()
                janela.activate()
                janela.maximize()
                time.sleep(1.5)
                return True
            else:
                log_func("⚠️ Janela 'Pedidos remoto' não encontrada.", "erro")
                return False
        except:
            return True

    def verificar_digitacao(self, id_esperado, x, y, log_func):
        """ Verifica se o ID foi realmente preenchido no campo """
        max_tentativas = 2
        for tentativa in range(max_tentativas):
            pyautogui.click(x, y)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            conteudo_campo = pyperclip.paste().strip()
            
            if conteudo_campo == id_esperado:
                return True
            else:
                log_func(f"⚠️ Tentativa {tentativa+1}: ID incorreto no campo. Re-digitando...", "aviso")
                pyautogui.press('backspace')
                pyautogui.write(id_esperado, interval=0.1)
                time.sleep(0.5)
        
        return False

    def processar_por_arquivos(self, pasta_in, pasta_out, callback_log, modo_biovida):
        if not self.focar_janela_robusta(callback_log): return 

        arquivos = [f for f in os.listdir(pasta_in) if f.lower().endswith('.pdf')]
        for arquivo in arquivos:
            id_paciente = arquivo.replace(".pdf", "")
            if modo_biovida and "-" in id_paciente:
                id_paciente = id_paciente.split("-")[-1]
            
            caminho_in = os.path.join(pasta_in, arquivo)
            callback_log(f"Processando ID: {id_paciente}")
            
            resultado = self.executar_passos(id_paciente, caminho_in, callback_log)
            yield (id_paciente, resultado)

    def executar_passos(self, id_val, caminho_arquivo, log_func):
        for passo in self.sequencia:
            if passo not in self.mapa: continue
            x, y = self.mapa[passo]['x'], self.mapa[passo]['y']

            if passo == "04_digitar":
                # Digita Inicial
                pyautogui.click(x, y)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyautogui.write(id_val, interval=0.1)
                
                # Validação de Segurança
                if not self.verificar_digitacao(id_val, x, y, log_func):
                    log_func(f"❌ Falha crítica: Não foi possível preencher o ID {id_val}", "erro")
                    return "ERRO DIGITAÇÃO"
            
            elif passo == "05_lupa":
                pyautogui.click(x, y)
                time.sleep(4.5)

            elif passo == "06_selecionar":
                pyautogui.doubleClick(x, y)
                time.sleep(3.5)

            elif passo == "11_anexar":
                pyautogui.click(x, y); time.sleep(2.0)
                pyperclip.copy(caminho_arquivo)
                pyautogui.hotkey('ctrl', 'v'); time.sleep(1.0); pyautogui.press('enter')
                time.sleep(5.0)

            else:
                pyautogui.click(x, y); time.sleep(1.0)

        return "SUCESSO"