import customtkinter as ctk
import threading
import os
from tkinter import filedialog, messagebox
from robo import SalusRobot

class AppSalus(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Automação Salus - Patrick")
        self.geometry("600x450")
        self.stop_event = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        self.lbl_arquivo = ctk.CTkLabel(self, text="Nenhum arquivo selecionado")
        self.lbl_arquivo.pack(pady=20)

        self.btn_arquivo = ctk.CTkButton(self, text="Selecionar PDF", command=self.selecionar_arquivo)
        self.btn_arquivo.pack(pady=10)

        self.txt_log = ctk.CTkTextbox(self, width=500, height=200)
        self.txt_log.pack(pady=10)

        self.btn_iniciar = ctk.CTkButton(self, text="INICIAR", command=self.iniciar_thread, fg_color="green")
        self.btn_iniciar.pack(pady=10)

        self.btn_parar = ctk.CTkButton(self, text="PARAR", command=self.parar_processo, fg_color="red", state="disabled")
        self.btn_parar.pack(pady=5)

    def log(self, mensagem):
        self.txt_log.insert("end", mensagem + "\n")
        self.txt_log.see("end")

    def selecionar_arquivo(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filename:
            self.arquivo_atual = filename
            self.lbl_arquivo.configure(text=os.path.basename(filename))

    def iniciar_thread(self):
        if not hasattr(self, 'arquivo_atual'):
            messagebox.showwarning("Aviso", "Selecione um arquivo PDF primeiro.")
            return
            
        self.stop_event.clear()
        self.btn_iniciar.configure(state="disabled")
        self.btn_parar.configure(state="normal")
        threading.Thread(target=self.rodar_processo, daemon=True).start()

    def parar_processo(self):
        self.stop_event.set()
        self.log("Parando processo...")

    def rodar_processo(self):
        bot = SalusRobot(self.log, self.stop_event)
        
        nome_arquivo = os.path.basename(self.arquivo_atual)
        id_paciente = "".join(filter(str.isdigit, nome_arquivo))
        
        sucesso, msg = bot.executar_sequencia(id_paciente, self.arquivo_atual, "SALUS")
        
        self.log(f"Fim: {msg}")
        self.btn_iniciar.configure(state="normal")
        self.btn_parar.configure(state="disabled")

if __name__ == "__main__":
    app = AppSalus()
    app.mainloop()