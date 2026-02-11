import time
import os
import json
import pyautogui
import pyperclip
import pygetwindow as gw
from interface import VisaoComputacional

class ControladorSalus:
    def __init__(self, tesseract_path):
        # Inicializa a visão para ler alertas na tela
        self.visao = VisaoComputacional(tesseract_path)
        
        self.mapa = {}
        self.carregar_mapa()
        
        # Sequência exata dos 12 passos que você definiu
        self.sequencia = [
            "01_inicio", "02_limpar", "03_aba", "04_digitar", "05_lupa",
            "06_selecionar", "08_setinha", "09_pedidos", "10_carregar", 
            "11_anexar", "12_fechar"
        ]

    def carregar_mapa(self):
        """ Carrega o JSON com as coordenadas calibradas """
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_json = os.path.join(dir_atual, "config_mapa.json")
        try:
            with open(caminho_json, "r") as f:
                self.mapa = json.load(f)
        except FileNotFoundError:
            print("❌ ERRO: 'config_mapa.json' não encontrado. Rode o 'calibra.py' primeiro!")

    def focar_janela_robusta(self, log_func):
        """ 
        Tenta trazer a janela do Salus para frente.
        Estratégia: Nome exato -> Nome parcial -> Forçar ativação 
        """
        titulo_alvo = "Pedidos de Exames (Remoto)"
        
        try:
            # 1. Tenta achar a janela
            janelas = gw.getWindowsWithTitle(titulo_alvo)
            alvo = None

            if janelas:
                alvo = janelas[0]
            else:
                # Busca flexível (caso o nome mude um pouco)
                for t in gw.getAllTitles():
                    if "pedidos" in t.lower() and "remoto" in t.lower():
                        alvo = gw.getWindowsWithTitle(t)[0]
                        break
            
            # 2. Se achou, traz para frente
            if alvo:
                if alvo.isMinimized:
                    alvo.restore()
                
                try:
                    alvo.activate()
                except:
                    # Fallback: clica no topo da janela para forçar foco do Windows
                    pyautogui.click(alvo.left + 50, alvo.top + 10)
                
                alvo.maximize()
                # IMPORTANTE: Sistemas remotos demoram para renderizar após maximizar
                time.sleep(2.5) 
                return True
            else:
                log_func("❌ ERRO: Janela 'Pedidos de Exames (Remoto)' não encontrada!", "erro")
                return False
                
        except Exception as e:
            log_func(f"⚠️ Aviso de foco: {str(e)}", "aviso")
            return True # Tenta continuar mesmo assim

    def verificar_digitacao(self, id_esperado, x, y, log_func):
        """ Garante que o ID foi digitado corretamente """
        for tentativa in range(2):
            # Clica e seleciona tudo
            pyautogui.click(x, y)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)
            
            # Verifica clipboard
            conteudo = pyperclip.paste().strip()
            
            if conteudo == id_esperado:
                return True
            else:
                log_func(f"⚠️ ID digitado errado ({conteudo}). Tentando de novo...", "aviso")
                pyautogui.press('backspace')
                pyautogui.write(id_esperado, interval=0.1)
                time.sleep(0.5)
        
        return False

    def checar_alerta_ocr(self):
        """ Lê a tela para ver se tem avisos de bloqueio """
        try:
            texto = self.visao.ler_texto() # Lê a tela toda
            palavras_chave = ["BIOMETRIA", "AVISO", "ATENCAO", "ERRO", "PENDENCIA", "CONFIRMACAO"]
            
            for p in palavras_chave:
                if p in texto:
                    return True
            return False
        except:
            return False

    def processar_por_arquivos(self, pasta_in, pasta_out, callback_log, modo_biovida):
        # 1. Garante que o Salus está na tela
        if not self.focar_janela_robusta(callback_log):
            return 

        # 2. Lista arquivos
        if not os.path.exists(pasta_in):
            callback_log("Pasta de entrada não existe!", "erro")
            return

        arquivos = [f for f in os.listdir(pasta_in) if f.lower().endswith('.pdf')]
        
        for arquivo in arquivos:
            # Tratamento do ID
            id_paciente = arquivo.replace(".pdf", "")
            if modo_biovida and "-" in id_paciente:
                id_paciente = id_paciente.split("-")[-1]
            
            caminho_in = os.path.join(pasta_in, arquivo)
            callback_log(f"Iniciando ID: {id_paciente}")
            
            # Executa a mágica
            resultado = self.executar_passos(id_paciente, caminho_in, callback_log)
            yield (id_paciente, resultado)

    def executar_passos(self, id_val, caminho_arquivo, log_func):
        for passo in self.sequencia:
            # Se o passo não estiver calibrado, pula (ou avisa)
            if passo not in self.mapa: 
                continue
            
            x, y = self.mapa[passo]['x'], self.mapa[passo]['y']

            # --- LÓGICA ESPECÍFICA PARA CADA PASSO ---
            
            if passo == "04_digitar":
                pyautogui.click(x, y)
                time.sleep(0.5)
                pyautogui.doubleClick(x, y) # Garante foco
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyautogui.write(id_val, interval=0.1)
                
                # Validação de Segurança
                if not self.verificar_digitacao(id_val, x, y, log_func):
                    return "ERRO DIGITACAO"

            elif passo == "05_lupa":
                pyautogui.click(x, y)
                time.sleep(4.0) # Espera a busca lenta do sistema

            elif passo == "06_selecionar":
                pyautogui.doubleClick(x, y)
                time.sleep(3.0) # Espera abrir paciente
                
                # --- GUARDA DE ALERTA (OCR) ---
                if self.checar_alerta_ocr():
                    log_func("⚠️ Alerta detectado na tela! Tentando fechar...", "aviso")
                    if "00_alerta_sair" in self.mapa:
                        pyautogui.click(self.mapa["00_alerta_sair"]['x'], self.mapa["00_alerta_sair"]['y'])
                        time.sleep(2.0)
                # ------------------------------

            elif passo == "11_anexar":
                pyautogui.click(x, y)
                time.sleep(2.0) # Espera janela do Windows abrir
                pyperclip.copy(caminho_arquivo)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1.0)
                pyautogui.press('enter')
                time.sleep(5.0) # Espera o upload terminar (Aumente se a internet for lenta)

            else:
                # Cliques normais (Abas, Seta, Pedidos, Carregar, Fechar)
                pyautogui.click(x, y)
                time.sleep(1.0)

        return "SUCESSO"
