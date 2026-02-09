import customtkinter as ctk
import threading
import os
from tkinter import filedialog, messagebox
from robo import SalusRobot

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class AppSalus(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voox Salus - Automação")
        
        largura_janela = 480
        altura_janela = 400
        
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        
        self.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
        self.minsize(400, 300)
        
        self.stop_event = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.lbl_arquivo = ctk.CTkLabel(self.main_frame, text="Selecione o PDF...", wraplength=400)
        self.lbl_arquivo.pack(pady=(10, 5))

        self.btn_arquivo = ctk.CTkButton(self.main_frame, text="📂 Escolher Arquivo", command=self.selecionar_arquivo)
        self.btn_arquivo.pack(pady=5)

        self.txt_log = ctk.CTkTextbox(self.main_frame, width=400, height=120)
        self.txt_log.pack(pady=10)

        self.frame_botoes = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_botoes.pack(pady=10)

        self.btn_iniciar = ctk.CTkButton(self.frame_botoes, text="▶ INICIAR", command=self.iniciar_thread, fg_color="green", width=140)
        self.btn_iniciar.pack(side="left", padx=5)

        self.btn_parar = ctk.CTkButton(self.frame_botoes, text="⏹ PARAR", command=self.parar_processo, fg_color="red", state="disabled", width=140)
        self.btn_parar.pack(side="right", padx=5)
        
        self.lbl_version = ctk.CTkLabel(self.main_frame, text="v1.0 - Patrick", font=("Arial", 10), text_color="gray")
        self.lbl_version.pack(side="bottom", pady=5)

    def log(self, mensagem):
        self.txt_log.insert("end", mensagem + "\n")
        self.txt_log.see("end")

    def selecionar_arquivo(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filename:
            self.arquivo_atual = filename
            self.lbl_arquivo.configure(text=f"📄 {os.path.basename(filename)}")

    def iniciar_thread(self):
        if not hasattr(self, 'arquivo_atual'):
            messagebox.showwarning("Atenção", "Por favor, selecione um arquivo PDF primeiro.")
            return
            
        self.stop_event.clear()
        self.btn_iniciar.configure(state="disabled")
        self.btn_arquivo.configure(state="disabled")
        self.btn_parar.configure(state="normal")
        threading.Thread(target=self.rodar_processo, daemon=True).start()

    def parar_processo(self):
        self.stop_event.set()
        self.log("🛑 Parando processo...")

    def rodar_processo(self):
        bot = SalusRobot(self.log, self.stop_event)
        
        if hasattr(self, 'arquivo_atual'):
            nome_arquivo = os.path.basename(self.arquivo_atual)
            id_paciente = "".join(filter(str.isdigit, nome_arquivo))
            
            try:
                sucesso, msg = bot.executar_sequencia(id_paciente, self.arquivo_atual, "SALUS")
                if sucesso:
                    messagebox.showinfo("Su
