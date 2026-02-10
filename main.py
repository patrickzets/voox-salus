import customtkinter as ctk
import threading
import os
import shutil  # Biblioteca para mover arquivos
from tkinter import filedialog, messagebox
from robo import SalusRobot

# --- CONFIGURAÇÃO DE TEMA PROFISSIONAL (Light Mode Clean) ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class AppSalus(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("Voox Salus | Gerenciador de Automação")
        self.geometry("800x750")
        self.configure(fg_color="#F4F6F8")
        
        # Centralizar
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 750) // 2
        self.geometry(f"+{x}+{y}")
        
        self.stop_event = threading.Event()
        
        # Variáveis de Controle
        self.pasta_origem = ""
        self.pasta_destino = ""
        self.sistema_selecionado = ctk.StringVar(value="BIOCROMA") # Padrão
        self.copiar_arquivos = ctk.BooleanVar(value=False)
        
        self.setup_ui()

    def setup_ui(self):
        # --- CABEÇALHO ---
        self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_header.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(
            self.frame_header, 
            text="VOOX SALUS", 
            font=("Montserrat", 24, "bold"), 
            text_color="#2C3E50"
        ).pack(side="left")
        
        ctk.CTkLabel(
            self.frame_header, 
            text="v2.0 Enterprise", 
            font=("Arial", 12), 
            text_color="gray"
        ).pack(side="left", padx=10, pady=(10,0))

        # --- CARD 1: CONFIGURAÇÕES (Onde escolhe as pastas) ---
        self.card_config = ctk.CTkFrame(self, fg_color="white", corner_radius=15, border_width=1, border_color="#E5E5E5")
        self.card_config.pack(fill="x", padx=30, pady=10)

        # Título do Card
        ctk.CTkLabel(self.card_config, text="CONFIGURAÇÃO DE FLUXO", font=("Arial", 12, "bold"), text_color="#3498DB").pack(anchor="w", padx=20, pady=(15, 5))

        # 1. Seleção de Sistema (Radio Buttons)
        self.frame_radios = ctk.CTkFrame(self.card_config, fg_color="transparent")
        self.frame_radios.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(self.frame_radios, text="Sistema Alvo:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        
        self.radio_biocroma = ctk.CTkRadioButton(
            self.frame_radios, text="BIOCROMA", variable=self.sistema_selecionado, value="BIOCROMA",
            fg_color="#3498DB", hover_color="#2980B9"
        )
        self.radio_biocroma.pack(side="left", padx=10)
        
        self.radio_biovida = ctk.CTkRadioButton(
            self.frame_radios, text="BIOVIDA", variable=self.sistema_selecionado, value="BIOVIDA",
            fg_color="#E67E22", hover_color="#D35400"
        )
        self.radio_biovida.pack(side="left", padx=10)

        # 2. Pasta Origem
        self.criar_seletor_pasta(self.card_config, "Pasta de Arquivos (Origem):", "origem")
        
        # 3. Pasta Destino
        self.criar_seletor_pasta(self.card_config, "Pasta de Finalizados (Destino):", "destino")

        # 4. Opção de cópia
        self.frame_opcoes = ctk.CTkFrame(self.card_config, fg_color="transparent")
        self.frame_opcoes.pack(fill="x", padx=20, pady=(5, 10))
        ctk.CTkCheckBox(
            self.frame_opcoes,
            text="Copiar arquivos em vez de mover",
            variable=self.copiar_arquivos,
            onvalue=True,
            offvalue=False,
            text_color="#2C3E50",
            fg_color="#3498DB",
            hover_color="#2980B9",
        ).pack(anchor="w")
        
        # Espaçamento final do card
        ctk.CTkLabel(self.card_config, text="").pack(pady=5)


        # --- CARD 2: MONITORAMENTO (Logs e Progresso) ---
        self.card_monitor = ctk.CTkFrame(self, fg_color="white", corner_radius=15, border_width=1, border_color="#E5E5E5")
        self.card_monitor.pack(fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(self.card_monitor, text="MONITORAMENTO EM TEMPO REAL", font=("Arial", 12, "bold"), text_color="#27AE60").pack(anchor="w", padx=20, pady=(15, 5))

        # Barra de Progresso
        self.lbl_status_progresso = ctk.CTkLabel(self.card_monitor, text="Aguardando início...", text_color="gray")
        self.lbl_status_progresso.pack(anchor="w", padx=20)
        
        self.progress = ctk.CTkProgressBar(self.card_monitor, height=12, corner_radius=6, progress_color="#27AE60")
        self.progress.pack(fill="x", padx=20, pady=5)
        self.progress.set(0)

        # Log Console
        self.txt_log = ctk.CTkTextbox(
            self.card_monitor, 
            font=("Consolas", 11), 
            fg_color="#F8F9FA", 
            text_color="#2C3E50",
            corner_radius=6,
            border_width=1,
            border_color="#E0E0E0"
        )
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=10)


        # --- RODAPÉ COM BOTOES ---
        self.frame_footer = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_footer.pack(fill="x", padx=30, pady=20)

        self.btn_iniciar = ctk.CTkButton(
            self.frame_footer, 
            text="INICIAR PROCESSAMENTO", 
            command=self.iniciar_thread,
            fg_color="#27AE60", # Verde Profissional
            hover_color="#219150",
            font=("Arial", 14, "bold"),
            height=50
        )
        self.btn_iniciar.pack(fill="x")

        self.btn_parar = ctk.CTkButton(
            self.frame_footer, 
            text="PARAR OPERAÇÃO", 
            command=self.parar_processo,
            fg_color="transparent", 
            text_color="#C0392B",
            hover_color="#FDEDEC",
            border_width=1,
            border_color="#C0392B",
            height=30,
            state="disabled"
        )
        self.btn_parar.pack(pady=10)

    def criar_seletor_pasta(self, parent, label_text, tipo):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(frame, text=label_text, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        
        sub_frame = ctk.CTkFrame(frame, fg_color="transparent")
        sub_frame.pack(fill="x")
        
        entry = ctk.CTkEntry(sub_frame, placeholder_text="Selecione a pasta...", height=35, border_color="#BDC3C7")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        entry.configure(state="disabled") # Apenas leitura
        
        if tipo == "origem": self.entry_origem = entry
        else: self.entry_destino = entry

        btn = ctk.CTkButton(
            sub_frame, 
            text="📂 Escolher", 
            width=80, 
            height=35,
            fg_color="#34495E", 
            hover_color="#2C3E50",
            command=lambda: self.selecionar_pasta(tipo)
        )
        btn.pack(side="right")

    def log(self, mensagem):
        if threading.current_thread() is threading.main_thread():
            self._append_log(mensagem)
        else:
            self.after(0, self._append_log, mensagem)

    def _append_log(self, mensagem):
        self.txt_log.insert("end", f"> {mensagem}\n")
        self.txt_log.see("end")

    def selecionar_pasta(self, tipo):
        pasta = filedialog.askdirectory()
        if pasta:
            if tipo == "origem":
                self.pasta_origem = pasta
                self.entry_origem.configure(state="normal")
                self.entry_origem.delete(0, "end")
                self.entry_origem.insert(0, pasta)
                self.entry_origem.configure(state="disabled")
            else:
                self.pasta_destino = pasta
                self.entry_destino.configure(state="normal")
                self.entry_destino.delete(0, "end")
                self.entry_destino.insert(0, pasta)
                self.entry_destino.configure(state="disabled")

    def iniciar_thread(self):
        # Validações
        if not self.pasta_origem or not self.pasta_destino:
            messagebox.showwarning("Configuração Incompleta", "Por favor, selecione as pastas de Origem e Destino.")
            return
        
        if self.pasta_origem == self.pasta_destino:
            messagebox.showerror("Erro", "A pasta de origem e destino não podem ser a mesma.")
            return

        self.stop_event.clear()
        self.btn_iniciar.configure(state="disabled", text="PROCESSANDO LOTE...")
        self.btn_parar.configure(state="normal")
        
        threading.Thread(target=self.rodar_lote, daemon=True).start()

    def parar_processo(self):
        self.stop_event.set()
        self.log("🛑 Solicitando parada segura...")

    def rodar_lote(self):
        bot = SalusRobot(self.log, self.stop_event)
        sistema = self.sistema_selecionado.get()
        
        self.log(f"--- INICIANDO LOTE ({sistema}) ---")
        self.log(f"Origem: {self.pasta_origem}")
        self.log(f"Destino: {self.pasta_destino}")

        if bot.mapa_img is None:
            self.log("Erro: mapa.png não foi carregado. Verifique o arquivo antes de iniciar o lote.")
            self.after(0, self.reset_botoes)
            return

        if not bot.janela_disponivel():
            self.log("Erro: janela alvo 'Pedido de Exames (Remoto)' não encontrada.")
            self.after(0, self.reset_botoes)
            return

        # Lista apenas arquivos PDF
        arquivos = sorted(
            entry.name
            for entry in os.scandir(self.pasta_origem)
            if entry.is_file() and entry.name.lower().endswith(".pdf")
        )
        total = len(arquivos)
        sucessos = []
        falhas = 0
        
        if total == 0:
            self.log("Nenhum arquivo PDF encontrado na pasta de origem.")
            self.after(0, self.reset_botoes)
            return

        self.log(f"Total de arquivos na fila: {total}")
        
        for index, arquivo in enumerate(arquivos, start=1):
            if self.stop_event.is_set():
                break
            
            # Atualiza Progresso Visual
            progresso = index / total
            self.after(
                0,
                self._atualizar_progresso,
                progresso,
                f"Processando arquivo {index} de {total}: {arquivo}",
            )
            
            caminho_completo = os.path.join(self.pasta_origem, arquivo)
            id_paciente = "".join(filter(str.isdigit, arquivo))
            
            # --- CHAMA O ROBÔ ---
            try:
                sucesso, msg = bot.executar_sequencia(id_paciente, caminho_completo, sistema)
            except Exception as exc:
                sucesso, msg = False, f"Erro inesperado: {exc}"
                erro_inesperado = msg
            
            if sucesso:
                self.log(f"✅ {arquivo}: Sucesso! Marcado para finalizar ao final do lote.")
                sucessos.append(arquivo)
            else:
                self.log(f"❌ {arquivo}: Falhou ({msg}). Mantendo na origem.")
                falhas += 1

        erros_movimentacao = 0
        if sucessos:
            acao_texto = "Copiando" if self.copiar_arquivos.get() else "Movendo"
            self.log(f"{acao_texto} arquivos finalizados em lote...")
            for arquivo in sucessos:
                caminho_completo = os.path.join(self.pasta_origem, arquivo)
                destino = os.path.join(self.pasta_destino, arquivo)
                try:
                    if self.copiar_arquivos.get():
                        shutil.copy2(caminho_completo, destino)
                    else:
                        shutil.move(caminho_completo, destino)
                except Exception as e:
                    erros_movimentacao += 1
                    self.log(f"⚠️ Erro ao finalizar arquivo {arquivo}: {e}")

        sucesso_total = len(sucessos)
        self.log(
            "Resumo final: "
            f"total={total}, sucesso={sucesso_total}, falha={falhas}, "
            f"erros_movimentacao={erros_movimentacao}."
        )

        interrompido = self.stop_event.is_set()
        self.after(0, self._finalizar_lote, total, interrompido)

    def _atualizar_progresso(self, progresso, texto):
        self.progress.set(progresso)
        self.lbl_status_progresso.configure(text=texto)

    def _finalizar_lote(self, total, interrompido):
        self.progress.set(1)
        status_texto = "Operação interrompida." if interrompido else "Lote finalizado."
        self.lbl_status_progresso.configure(text=status_texto)
        self.log("--- FIM DO PROCESSAMENTO ---")
        if interrompido:
            messagebox.showwarning("Relatório", "Processamento interrompido pelo usuário.")
        else:
            messagebox.showinfo("Relatório", f"Processamento finalizado.\nTotal processado: {total}")

        self.reset_botoes()

    def reset_botoes(self):
        self.btn_iniciar.configure(state="normal", text="INICIAR PROCESSAMENTO")
        self.btn_parar.configure(state="disabled")

if __name__ == "__main__":
    app = AppSalus()
    app.mainloop()
