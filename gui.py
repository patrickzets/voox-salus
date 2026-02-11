import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import datetime
import csv

# --- DEFINIÇÃO DA PALETA VOOX PREMIMUM ---
C_PRI = "#1F2A44"      # Navy Limpo (Sidebar)
C_SEC = "#5E81AC"      # Steel Blue (Secundária/Busca)
C_ACC = "#F4A261"      # Pêssego (Acento/CTA)
C_BG = "#F7FAFC"       # Fundo Off-white
C_CARD = "#FFFFFF"     # Cards Brancos

# --- TOKENS DE CONTRASTE ---
C_TEXT_MAIN = "#2D3748"
C_TEXT_SEC = "#718096"
C_BORDER = "#E2E8F0"

ctk.set_appearance_mode("Light")

class VooxFinalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voox Salus 2026 - Automação Senior")
        self.geometry("1150x850")
        self.configure(fg_color=C_BG)
        self.txt_log = ctk.CTkTextbox(self.main, height=240, fg_color="#FDFDFD", 
                              text_color=C_TEXT_MAIN, border_width=1, 
                              border_color=C_BORDER, corner_radius=10, 
                              font=("Consolas", 12),
                              state="disabled") # <--- ADICIONE ISSO AQUI
        # Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ===================================================
        # 1. SIDEBAR (NAVY)
        # ===================================================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=C_PRI)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="VOOX", font=("Inter", 38, "bold"), text_color="#FFFFFF").pack(pady=(50,0))
        ctk.CTkLabel(self.sidebar, text="SALUS AUTOMAÇÃO", font=("Inter", 12, "bold"), text_color=C_ACC).pack(pady=(0,50))

        # Controles da Sidebar
        self.config_sidebar_ui()

        # ===================================================
        # 2. ÁREA PRINCIPAL
        # ===================================================
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=45, pady=40)
        self.main.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.main, text="Painel de Controle", font=("Inter", 28, "bold"), text_color=C_TEXT_MAIN).pack(anchor="w", pady=(0,25))

        # CARD DE PASTAS (SUPERFÍCIE BRANCA)
        self.card = ctk.CTkFrame(self.main, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        self.card.pack(fill="x", pady=10)

        self.create_path_row(self.card, "DIRETÓRIO DE ENTRADA (PDFs)", "entry_in")
        self.create_path_row(self.card, "DIRETÓRIO DE SAÍDA", "entry_out")

        # LOG DE ATIVIDADES
        ctk.CTkLabel(self.main, text="RELATÓRIO DE EXECUÇÃO", font=("Inter", 11, "bold"), text_color=C_TEXT_SEC).pack(anchor="w", padx=5, pady=(25,8))
        self.txt_log = ctk.CTkTextbox(self.main, height=240, fg_color="#FDFDFD", text_color=C_TEXT_MAIN, 
                                      border_width=1, border_color=C_BORDER, corner_radius=10, font=("Consolas", 12))
        self.txt_log.pack(fill="both", pady=0)

        # BOTÃO MASTER (CTA PÊSSEGO)
        self.btn_run = ctk.CTkButton(self.main, text="INICIAR PROCESSAMENTO", height=65, 
                                     font=("Inter", 16, "bold"), corner_radius=10,
                                     fg_color=C_ACC, text_color="#FFFFFF", 
                                     hover_color="#E76F51", command=self.start)
        self.btn_run.pack(fill="x", pady=30)

    def config_sidebar_ui(self):
        # Operador
        ctk.CTkLabel(self.sidebar, text="OPERADOR", font=("Inter", 10, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=35, pady=(20,5))
        self.combo_user = ctk.CTkComboBox(self.sidebar, values=["Patrick", "Pedro", "Admin"], 
                                         fg_color="#2D3748", button_color="#2D3748", 
                                         border_color="#4A5568", text_color="#FFFFFF", corner_radius=8, width=210)
        self.combo_user.pack(padx=20, pady=5)
        self.combo_user.set("Patrick")

        # Sistema
        ctk.CTkLabel(self.sidebar, text="SISTEMA", font=("Inter", 10, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=35, pady=(30,5))
        self.radio_var = ctk.IntVar(value=0)
        
        rb_style = {"text_color": "#FFFFFF", "fg_color": C_ACC, "hover_color": "#E76F51", "font": ("Inter", 13)}
        ctk.CTkRadioButton(self.sidebar, text="Biocroma", variable=self.radio_var, value=0, **rb_style).pack(padx=35, pady=12, anchor="w")
        ctk.CTkRadioButton(self.sidebar, text="Biovida", variable=self.radio_var, value=1, **rb_style).pack(padx=35, pady=12, anchor="w")

    def create_path_row(self, parent, label, attr):
        ctk.CTkLabel(parent, text=label, font=("Inter", 10, "bold"), text_color=C_TEXT_SEC).pack(anchor="w", padx=25, pady=(20,0))
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(5,20))
        
        entry = ctk.CTkEntry(frame, placeholder_text="Caminho do diretório...", height=40, 
                             fg_color=C_BG, border_color=C_BORDER, text_color=C_TEXT_MAIN)
        entry.pack(side="left", fill="x", expand=True, padx=(0,10))
        setattr(self, attr, entry)
        
        ctk.CTkButton(frame, text="Buscar", width=100, height=40, corner_radius=8,
                      fg_color=C_SEC, hover_color="#46678F", 
                      command=lambda: self.buscar(entry)).pack(side="right")

    def buscar(self, entry_widget):
        p = filedialog.askdirectory()
        if p:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, p)

    def log(self, msg, tipo="info"):
        self.txt_log.configure(state="normal")
        time_now = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert("end", f"[{time_now}] {msg}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def start(self):
        if not self.entry_in.get() or not self.entry_out.get(): return
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        from corpo import ControladorSalus
        self.btn_run.configure(state="disabled", text="EXECUTANDO...")
        
        bot = ControladorSalus(None)
        pasta_in = self.entry_in.get()
        pasta_out = self.entry_out.get()
        user = self.combo_user.get()
        modo = "BIOVIDA" if self.radio_var.get() == 1 else "BIOCROMA"
        
        caminho_csv = os.path.join(pasta_out, "Relatorio_Auditoria.csv")
        if not os.path.exists(caminho_csv):
            with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
                csv.writer(f, delimiter=";").writerow(["DATA", "HORA", "OPERADOR", "ID", "MODO", "STATUS"])

        for id_p, res in bot.processar_por_arquivos(pasta_in, pasta_out, self.log, self.radio_var.get()==1):
            agora = datetime.datetime.now()
            with open(caminho_csv, "a", newline="", encoding="utf-8") as f:
                csv.writer(f, delimiter=";").writerow([agora.strftime("%d/%m/%Y"), agora.strftime("%H:%M:%S"), user, id_p, modo, res])
        
        self.btn_run.configure(state="normal", text="INICIAR PROCESSAMENTO")
        self.log("Ciclo de auditoria finalizado.")

if __name__ == "__main__":
    app = VooxFinalApp()
    app.mainloop()