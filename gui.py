import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import datetime
import csv

class VooxFinalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voox Salus 2026") # Data ajustada
        self.geometry("900x700")
        self.configure(fg_color="#0B0B0F")
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color="#121216")
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="OPERADOR").pack(pady=(20,0))
        self.combo_user = ctk.CTkComboBox(self.sidebar, values=["Patrick", "Admin"])
        self.combo_user.pack(padx=20, pady=10)
        
        self.radio_var = ctk.IntVar(value=0)
        ctk.CTkRadioButton(self.sidebar, text="Biocroma", variable=self.radio_var, value=0).pack(pady=10)
        ctk.CTkRadioButton(self.sidebar, text="Biovida", variable=self.radio_var, value=1).pack(pady=10)

        # Main
        self.txt_log = ctk.CTkTextbox(self, fg_color="#0F0F12", text_color="#00FF00")
        self.txt_log.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.entry_path = ctk.CTkEntry(self, placeholder_text="Pasta dos PDFs...")
        self.entry_path.pack(fill="x", padx=20)
        
        ctk.CTkButton(self, text="INICIAR", command=self.start).pack(pady=20)

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        from corpo import ControladorSalus
        tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        bot = ControladorSalus(tesseract)
        
        pasta = self.entry_path.get()
        modo = "BIOVIDA" if self.radio_var.get() == 1 else "BIOCROMA"
        user = self.combo_user.get()

        for id_p, res in bot.processar_por_arquivos(pasta, self.log, self.radio_var.get() == 1):
            self.log(f"ID {id_p}: {res}")
            self.save_csv(user, id_p, modo, res)

    def log(self, msg, tipo="info"):
        self.txt_log.insert("end", f">> {msg}\n")
        self.txt_log.see("end")

    def save_csv(self, user, id_p, modo, res):
        file = "Relatorio_Auditoria.csv"
        agora = datetime.datetime.now()
        row = [agora.strftime("%d/%m/%Y"), agora.strftime("%H:%M:%S"), user, id_p, modo, res]
        with open(file, "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(row)

if __name__ == "__main__":
    app = VooxFinalApp()
    app.mainloop()
