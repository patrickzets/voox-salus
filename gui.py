import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import datetime
import csv

# --- PALETA VOOX 2026 (NAVY + PEACH) ---
C_PRI = "#1F2A44"      # Navy Limpo (Sidebar)
C_SEC = "#5E81AC"      # Steel Blue (Botões de Busca)
C_ACC = "#F4A261"      # Pêssego (Botão INICIAR)
C_BG = "#F7FAFC"       # Fundo Off-white
C_CARD = "#FFFFFF"     # Cards Brancos

# --- TOKENS DE TEXTO E BORDA ---
C_TEXT_MAIN = "#2D3748"
C_TEXT_SEC = "#718096"
C_BORDER = "#E2E8F0"

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class VooxFinalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voox Salus 2026 - Automação Senior")
        self.geometry("1150x850")
        self.configure(fg_color=C_BG)
        
        # Configuração do Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ===================================================
        # 1. SIDEBAR (COR PRIMÁRIA - NAVY)
        # ===================================================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=C_PRI)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo e Títulos
        ctk.CTkLabel(self.sidebar, text="VOOX", font=("Inter", 38, "bold"), text_color="#FFFFFF").pack(pady=(50,0))
        ctk.CTkLabel(self.sidebar, text="SALUS AUTOMATION", font=("Inter", 12, "bold"), text_color=C_ACC).pack(pady=(0,50))

        # --- Controles da Sidebar ---
        
        # Seleção de Operador
        ctk.CTkLabel(self.sidebar, text="OPERADOR", font=("Inter", 10, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=35, pady=(20,5))
        self.combo_user = ctk.CTkComboBox(self.sidebar, values=["Patrick", "Admin", "Operador 01"], 
                                         fg_color="#2D3748", button_color="#2D3748", 
                                         border_color="#4A5568", text_color="#FFFFFF", 
                                         dropdown_fg_color="#2D3748", corner_radius=8, width=210)
        self.combo_user.pack(padx=20, pady=5)
        self.combo_user.set("Patrick")

        # Seleção de Sistema (Radio Buttons)
        ctk.CTkLabel(self.sidebar, text="SISTEMA", font=("Inter", 10, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=35, pady=(30,5))
        self.radio_var = ctk.IntVar(value=0)
        
        # Estilo dos Radio Buttons
        rb_style = {"text_color": "#FFFFFF", "fg_color": C_ACC, "hover_color": "#E76F51", "font": ("Inter", 13)}
        ctk.CTkRadioButton(self.sidebar, text="Biocroma", variable=self.radio_var, value=0, **rb_style).pack(padx=35, pady=12, anchor="w")
        ctk.CTkRadioButton(self.sidebar, text="Biovida", variable=self.radio_var, value=1, **rb_style).pack(padx=35, pady=12, anchor="w")

        # ===================================================
        # 2. ÁREA PRINCIPAL
        # ===================================================
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=45, pady=40)
        self.main.grid_columnconfigure(0, weight=1)

        # Título Principal
        ctk.CTkLabel(self.main, text="Painel de Controle", font=("Inter", 28, "bold"), text_color=C_TEXT_MAIN).pack(anchor="w", pady=(0,25))

        # CARD BRANCO (Configuração de Pastas)
        self.card = ctk.CTkFrame(self.main, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        self.card.pack(fill="x", pady=10)

        # Cria as linhas de seleção de pasta
        self.create_path_row(self.card, "DIRETÓRIO DE ENTRADA (PDFs)", "entry_in")
        self.create_path_row(self.card, "DIRETÓRIO DE SAÍDA (RELATÓRIOS)", "entry_out")

        # ÁREA DE LOG (BLOQUEADA PARA USUÁRIO)
        ctk.CTkLabel(self.main, text="RELATÓRIO DE EXECUÇÃO", font=("Inter", 11, "bold"), text_color=C_TEXT_SEC).pack(anchor="w", padx=5, pady=(25,8))
        
        # AQUI ESTÁ O BLOQUEIO: state="disabled"
        self.txt_log = ctk.CTkTextbox(self.main, height=380, fg_color="#FDFDFD", text_color=C_TEXT_MAIN, 
                                      border_width=1, border_color=C_BORDER, corner_radius=10, 
                                      font=("Consolas", 12), state="disabled")
        self.txt_log.pack(fill="both", pady=0)

        # BOTÃO INICIAR (COR PÊSSEGO)
        self.btn_run = ctk.CTkButton(self.main, text="INICIAR PROCESSAMENTO", height=65, 
                                     font=("Inter", 16, "bold"), corner_radius=10,
                                     fg_color=C_ACC, text_color="#FFFFFF", 
                                     hover_color="#E76F51", command=self.start)
        self.btn_run.pack(fill="x", pady=30)

    def create_path_row(self, parent, label, attr_name):
        """ Cria uma linha padronizada com Label + Entry + Botão Buscar """
        ctk.CTkLabel(parent, text=label, font=("Inter", 10, "bold"), text_color=C_TEXT_SEC).pack(anchor="w", padx=25, pady=(20,0))
        
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(5,20))
        
        # Campo de Texto
        entry = ctk.CTkEntry(frame, placeholder_text="Selecione o caminho da pasta...", height=40, 
                             fg_color=C_BG, border_color=C_BORDER, text_color=C_TEXT_MAIN)
        entry.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        # Guarda a referência do entry no self (ex: self.entry_in)
        setattr(self, attr_name, entry)
        
        # Botão Buscar (Cor Secundária)
        ctk.CTkButton(frame, text="Buscar", width=100, height=40, corner_radius=8,
                      fg_color=C_SEC, hover_color="#46678F", 
                      command=lambda: self.buscar(entry)).pack(side="right")

    def buscar(self, entry_widget):
        p = filedialog.askdirectory()
        if p:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, p)

    def log(self, msg, tipo="info"):
        """ Escreve no log mesmo estando bloqueado para o usuário """
        self.txt_log.configure(state="normal")  # 1. Destranca
        
        time_now = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert("end", f"[{time_now}] {msg}\n")
        self.txt_log.see("end") # Rola para o final
        
        self.txt_log.configure(state="disabled") # 2. Tranca de novo

    def start(self):
        # Validação simples para não travar
        if not self.entry_in.get() or not self.entry_out.get():
            self.log("⚠️ ERRO: Selecione as pastas de Entrada e Saída antes de iniciar!", "erro")
            return
            
        # Inicia em Thread para não congelar a janela
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        try:
            from corpo import ControladorSalus
        except ImportError:
            self.log("❌ ERRO CRÍTICO: Arquivo 'corpo.py' não encontrado na mesma pasta!", "erro")
            return

        self.btn_run.configure(state="disabled", text="EXECUTANDO... AGUARDE")
        
        # Tesseract (ajuste se necessário, mas geralmente o corpo.py lida com isso)
        # Se o seu corpo.py pede o caminho no init, passamos aqui.
        bot = ControladorSalus(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        
        pasta_in = self.entry_in.get()
        pasta_out = self.entry_out.get()
        user = self.combo_user.get()
        modo = "BIOVIDA" if self.radio_var.get() == 1 else "BIOCROMA"
        
        caminho_csv = os.path.join(pasta_out, "Relatorio_Auditoria.csv")
        
        # Cria cabeçalho se arquivo não existir
        if not os.path.exists(caminho_csv):
            try:
                with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
                    csv.writer(f, delimiter=";").writerow(["DATA", "HORA", "OPERADOR", "ID", "MODO", "STATUS"])
            except Exception as e:
                self.log(f"Erro ao criar CSV: {e}")

        # Loop de processamento
        try:
            # Chama o gerador do corpo.py
            is_biovida = (self.radio_var.get() == 1)
            for id_p, res in bot.processar_por_arquivos(pasta_in, pasta_out, self.log, is_biovida):
                
                # Salva no CSV a cada paciente
                agora = datetime.datetime.now()
                try:
                    with open(caminho_csv, "a", newline="", encoding="utf-8") as f:
                        csv.writer(f, delimiter=";").writerow([agora.strftime("%d/%m/%Y"), agora.strftime("%H:%M:%S"), user, id_p, modo, res])
                except Exception as e:
                    self.log(f"Erro ao salvar no CSV: {e}")
                    
        except Exception as e:
            self.log(f"❌ Erro durante a execução: {str(e)}")
        
        self.btn_run.configure(state="normal", text="INICIAR PROCESSAMENTO")
        self.log("✅ Ciclo finalizado.")

if __name__ == "__main__":
    app = VooxFinalApp()
    app.mainloop()
