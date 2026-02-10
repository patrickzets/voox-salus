import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import datetime
import csv

# --- PALETA VOOX ---
COR_FUNDO = "#0B0B0F"
COR_SIDEBAR = "#121216"
COR_ACCENT = "#7C3AED" 
COR_TEXTO = "#E5E7EB"

ctk.set_appearance_mode("Dark")

class VooxFinalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voox Salus 2026")
        self.geometry("1000x750")
        self.configure(fg_color=COR_FUNDO)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="VOOX", font=("Roboto", 32, "bold"), text_color=COR_ACCENT).pack(pady=(40,0))
        ctk.CTkLabel(self.sidebar, text="AUTOMATION", font=("Roboto", 12, "bold"), text_color=COR_TEXTO).pack(pady=(0,40))

        # Seletor Operador
        ctk.CTkLabel(self.sidebar, text="OPERADOR", font=("Roboto", 11, "bold")).pack(anchor="w", padx=25, pady=(20,5))
        self.combo_user = ctk.CTkComboBox(self.sidebar, values=["Patrick", "Operador 01", "Admin"], fg_color=COR_ACCENT, button_color=COR_ACCENT, border_color=COR_ACCENT)
        self.combo_user.pack(padx=20, pady=5)
        self.combo_user.set("Patrick")

        # Rádios
        self.radio_var = ctk.IntVar(value=0)
        ctk.CTkRadioButton(self.sidebar, text="Biocroma", variable=self.radio_var, value=0, fg_color=COR_ACCENT).pack(padx=25, pady=10, anchor="w")
        ctk.CTkRadioButton(self.sidebar, text="Biovida", variable=self.radio_var, value=1, fg_color=COR_ACCENT).pack(padx=25, pady=10, anchor="w")

        # Main Area
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main.grid_columnconfigure(0, weight=1)

        self.entry_path = ctk.CTkEntry(self.main, placeholder_text="Pasta dos arquivos...", height=40, fg_color=COR_SIDEBAR, border_color="#333")
        self.entry_path.pack(fill="x", pady=10)
        
        ctk.CTkButton(self.main, text="Selecionar Pasta", command=self.buscar, fg_color=COR_SIDEBAR, border_width=1, border_color=COR_ACCENT, text_color=COR_ACCENT).pack(pady=5)

        self.txt_log = ctk.CTkTextbox(self.main, height=400, fg_color="#0F0F12", border_width=1, border_color="#27272A")
        self.txt_log.pack(fill="both", pady=20)

        self.btn_run = ctk.CTkButton(self.main, text="INICIAR AGORA", height=60, font=("Roboto", 16, "bold"), fg_color=COR_ACCENT, command=self.start)
        self.btn_run.pack(fill="x")

    def buscar(self):
        p = filedialog.askdirectory()
        if p:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, p)

    def log(self, msg, tipo="info"):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f">> {msg}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def start(self):
        if not self.entry_path.get(): return
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        from corpo import ControladorSalus
        bot = ControladorSalus(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        pasta = self.entry_path.get()
        user = self.combo_user.get()
        modo = "BIOVIDA" if self.radio_var.get() == 1 else "BIOCROMA"

        for id_p, res in bot.processar_por_arquivos(pasta, self.log, self.radio_var.get()==1):
            agora = datetime.datetime.now()
            with open("Relatorio_Auditoria.csv", "a", newline="", encoding="utf-8") as f:
                csv.writer(f, delimiter=";").writerow([agora.strftime("%d/%m/%Y"), agora.strftime("%H:%M:%S"), user, id_p, modo, res])
        
        self.log("Processo concluído.")

if __name__ == "__main__":
    app = VooxFinalApp()
    app.mainloop()
