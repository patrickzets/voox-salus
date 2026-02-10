import os
import sys
from corpo import ControladorSalus

# --- CONFIGURAÇÃO DE AMBIENTE ---

# 1. Caminho Dinâmico (Resolve o problema do File Not Found)
DIRETORIO_PROJETO = os.path.dirname(os.path.abspath(__file__))
CAMINHO_IMAGEM_ANCORA = os.path.join(DIRETORIO_PROJETO, 'ref_id_paciente.png')

# 2. Caminho do Tesseract (Confira se é este mesmo no seu PC)
CAMINHO_TESSERACT = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def main():
    print("--- INICIANDO ROBO SALUS (Versão OCR) ---")
    print(f"Diretório base: {DIRETORIO_PROJETO}")

    # Verificação de segurança
    if not os.path.exists(CAMINHO_IMAGEM_ANCORA):
        print(f"\n[ERRO FATAL] A imagem de referência não existe em:\n{CAMINHO_IMAGEM_ANCORA}")
        print("Por favor, coloque o print 'ref_id_paciente.png' nesta pasta.")
        return

    # Inicializa o controlador
    bot = ControladorSalus(CAMINHO_TESSERACT)

    # 1. Escaneamento
    try:
        pacientes = bot.escanear_grid(CAMINHO_IMAGEM_ANCORA)
        print(f"\nForam detectados {len(pacientes)} pacientes na tela.")
    except Exception as e:
        print(f"Erro durante o scan: {e}")
        return

    if not pacientes:
        print("Nenhum paciente lido. Verifique se a tela do Salus está visível.")
        return

    # 2. Processamento
    for p in pacientes:
        print(f"ID: {p.id} | Status: {p.status}")

        if "CANCELAD" in p.status: # Pega CANCELADO ou CANCELADA
            print(f"   [IGNORAR] Paciente {p.id} está cancelado.")
            continue
        
        elif "ANDAMENT" in p.status: # Pega EM ANDAMENTO
            print(f"   [AÇÃO] Processando paciente {p.id}...")
            
            # ATENÇÃO: Descomente a linha abaixo para o mouse clicar de verdade!
            # bot.abrir_paciente(p, 0) # O X é recalculado lá dentro
            
        else:
            print(f"   [AVISO] Status '{p.status}' não mapeado.")

    print("\n--- Fim da execução ---")

if __name__ == "__main__":
    main()