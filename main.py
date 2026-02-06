import customtkinter
import tkinter
from tkinter import filedialog, messagebox
import threading
import os
from datetime import datetime

import config
from robo import SalusRobot

customtkinter.set_appearance_mode("Light") 
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Automação Salus v1.0")
        self.geometry("800x900")
        
        # Configuração de Expansão da Janela Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Faz a caixa de log crescer verticalmente
        self.configure(fg_color="#F2F2F2")

        self.stop_event = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        # --- 1. HEADER (TÍTULO) ---
        self.lbl_titulo = customtkinter.CTkLabel(
            self, text="SISTEMA DE ANEXOS SALUS", 
            font=("Segoe UI", 28, "bold"), text_color="#1F4E79"
        )
        self.lbl_titulo.grid(row=0, column=0, pady=(30, 20), sticky="n")

        # --- 2. CARD DE CONFIGURAÇÃO (ENTRADAS) ---
        self.frame_cfg = customtkinter.CTkFrame(
            self, fg_color="white", corner_radius=15, 
            border_width=1, border_color="#DBDBDB"
        )
        self.frame_cfg.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        # Pesos internos do Card
        self.frame_cfg.grid_columnconfigure(1, weight=1)

        # Entradas de Pastas
        self.entry_src = self.create_row(0, "Pasta Origem:", self.select_src)
        self.entry_dst = self.create_row(1, "Pasta Destino:", self.select_dst)

        # Operador (Alinhado com as pastas)
        lbl_op = customtkinter.CTkLabel(self.frame_cfg, text="Operador:", font=("Arial", 13, "bold"), text_color="#333")
        lbl_op.grid(row=2, column=0, padx=(20, 10), pady=15, sticky="w")
        
        self.menu_op = customtkinter.CTkOptionMenu(
            self.frame_cfg, values=config.LISTA_OPERADORES, 
            fg_color="#1F4E79", button_color="#143452", width=250
        )
        self.menu_op.grid(row=2, column=1, padx=(0, 20), pady=15, sticky="w")

        # Seletor de Modo (Biocroma/Biovida)
        self.frame_modo = customtkinter.CTkFrame(self.frame_cfg, fg_color="transparent")
        self.frame_modo.grid(row=3, column=0, columnspan=2, pady=(5, 20))
        
        self.modo_var = tkinter.IntVar(value=0)
        customtkinter.CTkRadioButton(
            self.frame_modo, text="BIOCROMA", variable=self.modo_var, value=0,
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=30)
        
        customtkinter.CTkRadioButton(
            self.frame_modo, text="BIOVIDA", variable=self.modo_var, value=1,
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=30)

        # --- 3. ÁREA DE LOGS (OCUPA O ESPAÇO DISPONÍVEL) ---
        self.txt_box = customtkinter.CTkTextbox(
            self, fg_color="white", border_width=1, border_color="#DBDBDB", 
            corner_radius=10, font=("Consolas", 12)
        )
        self.txt_box.grid(row=2, column=0, padx=40, pady=20, sticky="nsew")
        self.txt_box.insert("0.0", ">> Aguardando seleção de pastas...\n")

        # --- 4. PROGRESSO E STATUS ---
        self.prog = customtkinter.CTkProgressBar(self, progress_color="#1F4E79", height=12)
        self.prog.grid(row=3, column=0, padx=50, pady=(10, 0), sticky="ew")
        self.prog.set(0)

        self.lbl_status = customtkinter.CTkLabel(self, text="Status: Pronto", font=("Arial", 12, "italic"))
        self.lbl_status.grid(row=4, column=0, pady=(5, 20))

        # --- 5. BOTÃO INICIAR ---
        self.btn_start = customtkinter.CTkButton(
            self, text="INICIAR PROCESSO", font=("Segoe UI", 20, "bold"),
            fg_color="#27AE60", hover_color="#219150", height=60, width=350,
            command=self.start_thread, corner_radius=10
        )
        self.btn_start.grid(row=5, column=0, pady=(0, 40))

    def create_row(self, row, text, cmd):
        """Helper para criar linhas de seleção de pasta alinhadas"""
        btn = customtkinter.CTkButton(
            self.frame_cfg, text=text, command=cmd, 
            width=140, height=32, fg_color="#1F4E79", font=("Arial", 12, "bold")
        )
        btn.grid(row=row, column=0, padx=(20, 10), pady=12, sticky="w")

        ent = customtkinter.CTkEntry(
            self.frame_cfg, placeholder_text="Selecione o caminho...", 
            height=35, fg_color="#FAFAFA"
        )
        ent.grid(row=row, column=1, padx=(0, 20), pady=12, sticky="ew")
        return ent

    # --- LÓGICA DE INTERAÇÃO ---
    def select_src(self): 
        d = filedialog.askdirectory()
        if d: 
            self.entry_src.delete(0, "end")
            self.entry_src.insert(0, d)
            self.log(f"Origem definida: {d}")

    def select_dst(self): 
        d = filedialog.askdirectory()
        if d: 
            self.entry_dst.delete(0, "end")
            self.entry_dst.insert(0, d)
            self.log(f"Destino definido: {d}")

    def log(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        self.txt_box.insert("end", f"[{ts}] {msg}\n")
        self.txt_box.see("end")

    def start_thread(self):
        if not self.entry_src.get() or not self.entry_dst.get():
            messagebox.showwarning("Atenção", "Selecione as pastas de origem e destino!")
            return
        
        self.btn_start.configure(state="disabled", text="EXECUTANDO...")
        threading.Thread(target=self.run_process, daemon=True).start()

    def run_process(self):
        src, dst = self.entry_src.get(), self.entry_dst.get()
        op = self.menu_op.get()
        modo = "BIOVIDA" if self.modo_var.get() == 1 else "BIOCROMA"
        files = [f for f in os.listdir(src) if f.lower().endswith('.pdf')]
        
        if not files:
            self.log("Nenhum arquivo PDF encontrado na pasta de origem.")
            self.btn_start.configure(state="normal", text="INICIAR PROCESSO")
            return

        # Modo Simulação
        simulacao = (op == "Admin/Teste")
        if simulacao: self.log("!!! MODO SIMULAÇÃO ATIVADO !!!")
        
        bot = SalusRobot(self.log, self.stop_event, simulacao=simulacao)
        
        for i, f in enumerate(files):
            id_v = bot.extrair_id(f, modo) #
            self.lbl_status.configure(text=f"Processando: {f}")
            
            ok, msg = bot.executar_sequencia(id_v, os.path.join(src, f), modo) #
            
            if ok and not simulacao:
                try:
                    bot.mover_arquivo(os.path.join(src, f), dst)
                    self.log(f"Sucesso: {f} movido.")
                except Exception as e:
                    self.log(f"Erro ao mover {f}: {e}")
            elif not ok:
                self.log(f"Falha em {f}: {msg}")
            
            self.prog.set((i+1)/len(files))

        self.log("Processamento concluído.")
        self.lbl_status.configure(text="Status: Concluído")
        self.btn_start.configure(state="normal", text="INICIAR PROCESSO")
        messagebox.showinfo("Fim", "Todos os arquivos foram processados!")

if __name__ == "__main__":
    app = App()
    app.mainloop()