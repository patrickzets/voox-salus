import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk 
import threading
import time
import os
import sys

# --- CONFIGURAÇÃO DE CORES (Cyberpunk / Voox) ---
COR_FUNDO_APP = "#0B0B0F"
COR_SIDEBAR = "#121216"
COR_CARD = "#18181B"
COR_BORDA_CARD = "#27272A"
COR_ACCENT = "#7C3AED"        # Roxo
COR_ACCENT_HOVER = "#6D28D9"
COR_TEXTO_PRINCIPAL = "#E5E7EB"
COR_TEXTO_SECUNDARIO = "#9CA3AF"
COR_SUCESSO = "#10B981"

# --- FONTES ---
FONT_TITLE_HERO = ("Roboto", 24, "bold")
FONT_HEADER = ("Roboto", 16, "bold")
FONT_BODY = ("Roboto", 12)
FONT_TERMINAL = ("Consolas", 12)

ctk.set_appearance_mode("Dark")

class VooxUltraApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title("Voox Salus Automation Platform")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.configure(fg_color=COR_FUNDO_APP)
        
        # Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ===================================================
        # 1. SIDEBAR (Lateral Esquerda)
        # ===================================================
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # LOGO
        # Tenta carregar logo_voox.png, se não der, usa texto.
        try:
            if os.path.exists("logo_voox.png"):
                img_pil = Image.open("logo_voox.png")
                self.logo_img = ctk.CTkImage(img_pil, size=(180, 60))
                self.lbl_logo = ctk.CTkLabel(self.sidebar, text="", image=self.logo_img)
            else:
                raise FileNotFoundError
        except:
            self.lbl_logo = ctk.CTkLabel(self.sidebar, text="VOOX\nAUTOMATION", font=FONT_TITLE_HERO, text_color=COR_ACCENT)
        
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(40, 20))

        # Divisor
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COR_BORDA_CARD).grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # MODO DE OPERAÇÃO
        ctk.CTkLabel(self.sidebar, text="AMBIENTE", font=("Roboto", 11, "bold"), text_color=COR_TEXTO_SECUNDARIO).grid(row=2, column=0, padx=20, pady=(20, 10), sticky="w")

        self.radio_var = ctk.IntVar(value=0)
        rb_style = {"font": FONT_HEADER, "text_color": COR_TEXTO_PRINCIPAL, "fg_color": COR_ACCENT, "hover_color": COR_ACCENT_HOVER}
        
        ctk.CTkRadioButton(self.sidebar, text="Biocroma", variable=self.radio_var, value=0, **rb_style).grid(row=3, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkRadioButton(self.sidebar, text="Biovida", variable=self.radio_var, value=1, **rb_style).grid(row=4, column=0, padx=20, pady=10, sticky="nw")

        # VERSÃO
        ctk.CTkLabel(self.sidebar, text="v2.1.0 Stable", font=("Consolas", 10), text_color=COR_TEXTO_SECUNDARIO).grid(row=5, column=0, padx=20, pady=20, sticky="w")

        # ===================================================
        # 2. ÁREA PRINCIPAL
        # ===================================================
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color=COR_FUNDO_APP)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(2, weight=1)

        # Cabeçalho
        self.frame_head = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.frame_head.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="ew")
        ctk.CTkLabel(self.frame_head, text="Painel de Controle", font=FONT_TITLE_HERO, text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        # CARD CONFIG (Entradas)
        self.card_conf = ctk.CTkFrame(self.main_area, fg_color=COR_CARD, corner_radius=10, border_width=1, border_color=COR_BORDA_CARD)
        self.card_conf.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        self.card_conf.grid_columnconfigure(1, weight=1)

        # Inputs
        self.criar_input(self.card_conf, "PASTA ENTRADA", 0, "entry_in")
        self.criar_input(self.card_conf, "PASTA SAÍDA", 1, "entry_out")

        # TERMINAL
        self.card_log = ctk.CTkFrame(self.main_area, fg_color=COR_CARD, corner_radius=10, border_width=1, border_color=COR_BORDA_CARD)
        self.card_log.grid(row=2, column=0, padx=40, pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.card_log, text="TERMINAL DO SISTEMA", font=("Roboto", 10, "bold"), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=15, pady=(10,5))
        
        self.txt_log = ctk.CTkTextbox(self.card_log, font=FONT_TERMINAL, fg_color="#0F0F12", text_color=COR_TEXTO_PRINCIPAL)
        self.txt_log.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.txt_log.insert("0.0", ">> Voox Automation Pronto.\n")
        self.txt_log.configure(state="disabled")

        # BOTÃO INICIAR
        self.btn_start = ctk.CTkButton(self.main_area, text="INICIAR PROCESSO", font=FONT_HEADER, height=50, fg_color=COR_ACCENT, hover_color=COR_ACCENT_HOVER, command=self.iniciar)
        self.btn_start.grid(row=3, column=0, padx=40, pady=(0, 40), sticky="ew")

        # Barra de Progresso
        self.prog = ctk.CTkProgressBar(self.main_area, height=4, progress_color=COR_ACCENT, fg_color=COR_BORDA_CARD)
        self.prog.grid(row=4, column=0, sticky="ew")
        self.prog.set(0)

    def criar_input(self, parent, texto, row, var_name):
        ctk.CTkLabel(parent, text=texto, font=("Roboto", 11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=row, column=0, padx=20, pady=20, sticky="w")
        entry = ctk.CTkEntry(parent, height=35, fg_color=COR_SIDEBAR, border_color=COR_BORDA_CARD, text_color="white")
        entry.grid(row=row, column=1, padx=10, pady=20, sticky="ew")
        setattr(self, var_name, entry)
        ctk.CTkButton(parent, text="Buscar", width=80, fg_color=COR_BORDA_CARD, hover_color=COR_SIDEBAR, command=lambda: self.buscar(entry)).grid(row=row, column=2, padx=20, pady=20)

    def buscar(self, entry):
        p = filedialog.askdirectory()
        if p:
            entry.delete(0, "end")
            entry.insert(0, p)

    def log(self, msg):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f">> {msg}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def iniciar(self):
        if not self.entry_in.get():
            self.log("[ERRO] Selecione a pasta de entrada!")
            return
        
        self.btn_start.configure(state="disabled", text="EXECUTANDO...")
        self.prog.start()
        threading.Thread(target=self.rodar_robo, daemon=True).start()

    def rodar_robo(self):
        try:
            self.log("Carregando módulos...")
            # Importação atrasada para evitar erro circular ou de carga
            import sys
            
            # Tenta importar o controlador
            try:
                from corpo import ControladorSalus
            except ImportError:
                self.log("[CRÍTICO] Arquivo 'corpo.py' não encontrado na pasta.")
                return

            modo = "Biocroma" if self.radio_var.get() == 0 else "Biovida"
            self.log(f"Iniciando: {modo}")

            diretorio_atual = os.path.dirname(os.path.abspath(__file__))
            img_ancora = os.path.join(diretorio_atual, 'ref_id_paciente.png')
            caminho_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            if not os.path.exists(img_ancora):
                self.log(f"[ERRO] Imagem âncora não encontrada em:\n{img_ancora}")
                return

            bot = ControladorSalus(caminho_tesseract)
            self.log("Escaneando tela (Não mexa no mouse)...")
            time.sleep(1)

            pacientes = bot.escanear_grid(img_ancora)
            self.prog.stop()

            if not pacientes:
                self.log("[AVISO] Nenhum paciente encontrado na tela visível.")
                self.prog.set(0)
            else:
                self.log(f"Encontrados: {len(pacientes)} registros.")
                passo = 1/len(pacientes)
                prog_atual = 0

                for p in pacientes:
                    if "CANCELADO" in p.status:
                        self.log(f"ID {p.id}: Cancelado (Ignorado).")
                    elif "ANDAMENTO" in p.status:
                        self.log(f"ID {p.id}: Em Andamento -> Processando...")
                        # bot.abrir_paciente(p, 0) # Descomente para ação real
                        time.sleep(0.5)
                    else:
                        self.log(f"ID {p.id}: Status {p.status} (Desconhecido).")
                    
                    prog_atual += passo
                    self.prog.set(prog_atual)
            
            self.log("Processo Finalizado.")

        except Exception as e:
            self.log(f"[ERRO GERAL] {e}")
        finally:
            self.prog.stop()
            self.prog.set(1)
            self.btn_start.configure(state="normal", text="INICIAR PROCESSO")

if __name__ == "__main__":
    app = VooxUltraApp()
    app.mainloop()