import os

# Configurações de Caminho
DIRETORIO_SISTEMA = r"C:\Salus_RPA_System"
DIR_LOGS = os.path.join(DIRETORIO_SISTEMA, "Logs")
DIR_RELATORIOS = os.path.join(DIRETORIO_SISTEMA, "Relatorios")
DIR_PRINTS_ERRO = os.path.join(DIR_LOGS, "Prints_Erro")

# Limite (em segundos) para alertar sobre duração longa de executar_sequencia
LIMITE_TEMPO_SEQUENCIA_SEGUNDOS = 120.0

# Lista de Operadores para a Interface
LISTA_OPERADORES = [
    "Selecione o Operador",
    "teste 2",
    "testee",
    "teste 4",
    "teste 1",
    "Admin/Teste"
]
