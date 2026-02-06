import pyautogui
import time
import os
import pytesseract
from PIL import ImageGrab
import sys

class SalusRobot:
    def __init__(self, logger_func, stop_event, simulacao=False):
        """
        Inicializa o robô com as funções de comunicação da interface.
        """
        self.log = logger_func
        self.stop_event = stop_event
        self.simulacao = simulacao
        
        # Configuração de Caminho para Imagens (Suporta script e .exe)
        if getattr(sys, 'frozen', False):
            # Se for executável, as imagens estarão numa pasta temporária
            self.pasta_imgs = os.path.join(sys._MEIPASS, "imgs")
        else:
            self.pasta_imgs = "imgs"
        
        # Caminho do Tesseract (ajuste se necessário no PC do estágio)
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        # Coordenadas da Lupa (Ajuste conforme sua tela)
        self.regiao_central = (300, 200, 800, 600)
        self.x_status, self.y_status = 800, 300
        self.larg_status, self.alt_linha = 120, 30
        self.x_clique_selecao = 500

    def acao(self, tipo, valor, msg=""):
        """
        Executa a ação ou apenas simula no Log se for o modo Admin/Teste.
        """
        if self.simulacao:
            self.log(f"[SIMULAÇÃO] {tipo}: {msg if msg else valor}")
            return True
        
        try:
            if tipo == "CLICK":
                pyautogui.click(valor)
            elif tipo == "WRITE":
                pyautogui.write(valor)
            elif tipo == "PRESS":
                pyautogui.press(valor)
            return True
        except Exception as e:
            self.log(f"Erro na ação {tipo}: {e}")
            return False

    def extrair_id(self, nome_arquivo, modo):
        """
        Extrai o ID do nome do arquivo PDF. 
        Biovida: pega após o hífen. Biocroma: nome inteiro.
        """
        id_bruto = nome_arquivo.replace(".pdf", "").replace(".PDF", "")
        if modo == "BIOVIDA" and "-" in id_bruto:
            # Pega a parte após o hífen, conforme solicitado
            return id_bruto.split("-")[1].strip()
        return id_bruto

    def selecionar_paciente_valido(self):
        """
        Lógica da Lupa Móvel: procura o primeiro paciente não cancelado.
        """
        self.log("Buscando menor ID ativo na tabela...")
        
        # 1. Tenta ordenar a tabela clicando no cabeçalho ID
        caminho_header = os.path.join(self.pasta_imgs, "header_id.png")
        btn_id = pyautogui.locateCenterOnScreen(caminho_header, confidence=0.8)
        
        if btn_id:
            self.acao("CLICK", btn_id, "Ordenando coluna ID")
            time.sleep(1 if self.simulacao else 2)
        
        # 2. Varredura de Status linha por linha
        for i in range(5):
            if self.stop_event.is_set(): return False
            
            y_atual = self.y_status + (i * self.alt_linha)
            # Define o retângulo da célula de status
            bbox = (self.x_status, y_atual, self.x_status + self.larg_status, y_atual + self.alt_linha)
            
            # Tira print da célula e faz o OCR
            img_celula = ImageGrab.grab(bbox=bbox)
            texto = pytesseract.image_to_string(img_celula).upper().strip()
            
            self.log(f"Linha {i+1}: Status lido = '{texto}'")
            
            if "CANCELADO" not in texto and "CANC" not in texto:
                # Se não estiver cancelado, clica na linha para selecionar
                self.acao("CLICK", (self.x_clique_selecao, y_atual), f"Selecionando paciente linha {i+1}")
                time.sleep(1)
                return True
        
        self.log("Nenhum paciente válido encontrado nas primeiras 5 linhas.")
        return False

    def executar_sequencia(self, id_val, caminho_completo, modo):
        """
        Executa a sequência de 12 passos ou o salto do Biovida.
        """
        passos_completo = [f"passo_{str(i).zfill(2)}.png" for i in range(1, 13)]
        
        # Lógica Inicial Diferenciada
        if modo == "BIOVIDA":
            self.log(f"Iniciando Modo Biovida para ID: {id_val}")
            caminho_campo = os.path.join(self.pasta_imgs, "campo_biovida.png")
            campo = pyautogui.locateCenterOnScreen(caminho_campo, confidence=0.8, region=self.regiao_central)
            
            if campo:
                self.acao("CLICK", campo, "Campo de busca Biovida")
                self.acao("WRITE", id_val)
                self.acao("PRESS", 'enter')
                time.sleep(1 if self.simulacao else 3)
                # Pula para o passo 05 (Validação da Tabela)
                sequencia_atual = passos_completo[4:]
            else:
                return False, "Campo de busca Biovida não encontrado."
        else:
            self.log(f"Iniciando Modo Biocroma para ID: {id_val}")
            sequencia_atual = passos_completo

        # Loop da Sequência de Imagens
        for img_nome in sequencia_atual:
            if self.stop_event.is_set():
                return False, "Interrupção pelo usuário."

            self.log(f"Procurando: {img_nome}")
            
            # Aplica região central apenas em passos de busca/decisão inicial
            area = self.regiao_central if "01" in img_nome or "04" in img_nome else None
            caminho_img = os.path.join(self.pasta_imgs, img_nome)
            
            try:
                pos = pyautogui.locateCenterOnScreen(caminho_img, confidence=0.8, region=area, grayscale=True)
            except:
                pos = None

            if pos:
                # Gatilhos Especiais
                if img_nome == "passo_04.png": # Busca Biocroma
                    self.acao("CLICK", pos)
                    self.acao("WRITE", id_val)
                    self.acao("PRESS", 'enter')
                    time.sleep(3)
                
                elif img_nome == "passo_05.png": # Seleção de Paciente
                    if not self.selecionar_paciente_valido():
                        return False, "Paciente cancelado ou inexistente."
                
                elif img_nome == "passo_11.png": # Anexar PDF
                    self.acao("CLICK", pos)
                    time.sleep(1)
                    self.acao("WRITE", caminho_completo)
                    self.acao("PRESS", 'enter')
                    time.sleep(1)
                
                else: # Passos normais de clique
                    self.acao("CLICK", pos)
                    time.sleep(0.5 if self.simulacao else 1)
            else:
                # Se não achou a imagem, o processo trava
                return False, f"Imagem {img_nome} não localizada na tela."

        return True, "Anexo realizado com sucesso."

    def mover_arquivo(self, origem, destino):
        """
        Move o arquivo para a pasta de concluídos.
        """
        if self.simulacao:
            self.log(f"[SIMULAÇÃO] Arquivo seria movido para: {destino}")
            return True
            
        try:
            if not os.path.exists(destino):
                os.makedirs(destino)
            nome_arq = os.path.basename(origem)
            os.rename(origem, os.path.join(destino, nome_arq))
            return True
        except Exception as e:
            self.log(f"Erro ao mover arquivo: {e}")
            return False