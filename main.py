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
        )
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=(5, 10))

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
            sucesso, msg = bot.executar_sequencia(id_paciente, caminho_completo, sistema)
            
            if sucesso:
                self.log(f"✅ {arquivo}: Sucesso! Movendo para concluídos...")
                acao_texto = "Copiando" if self.copiar_arquivos.get() else "Movendo"
                self.log(f"✅ {arquivo}: Sucesso! {acao_texto} para concluídos...")
                try:
                    shutil.move(caminho_completo, os.path.join(self.pasta_destino, arquivo))
                    destino = os.path.join(self.pasta_destino, arquivo)
                    if self.copiar_arquivos.get():
                        shutil.copy2(caminho_completo, destino)
                    else:
                        shutil.move(caminho_completo, destino)
                except Exception as e:
                    self.log(f"⚠️ Erro ao mover arquivo: {e}")
                    self.log(f"⚠️ Erro ao finalizar arquivo: {e}")
            else:
                self.log(f"❌ {arquivo}: Falhou ({msg}). Mantendo na origem.")

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