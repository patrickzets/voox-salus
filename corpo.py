import time
from interface import VisaoComputacional

class Paciente:
    def __init__(self, id_paciente, status, coordenada_y):
        self.id = id_paciente
        self.status = status.upper()
        self.y = coordenada_y

class ControladorSalus:
    def __init__(self, tesseract_path):
        self.visao = VisaoComputacional(tesseract_path)
        
        # Configurações de Geometria (Ajuste conforme sua tela)
        self.offset_y_dados = 25  # Pixels abaixo do cabeçalho para começar a ler
        self.altura_linha = 20    # Altura aproximada de cada linha do grid
        self.largura_coluna_id = 80
        self.largura_coluna_status = 150
        self.distancia_status_x = 300 # Distância horizontal aprox entre ID e Status

    def escanear_grid(self, img_cabecalho_id):
        print("Buscando âncora visual...")
        localizacao = self.visao.localizar_na_tela(img_cabecalho_id)
        
        if not localizacao:
            print("Cabeçalho 'Id paciente' não encontrado.")
            return []

        x_ancora, y_ancora, w_ancora, h_ancora = localizacao
        
        # Define as regiões de leitura baseadas na âncora encontrada
        y_inicio = y_ancora + h_ancora + 5
        altura_scan = 400 # Ler 400px para baixo (várias linhas)

        regiao_ids = (x_ancora, y_inicio, self.largura_coluna_id, altura_scan)
        
        # A região de status é deslocada para a direita (X + distancia)
        regiao_status = (x_ancora + self.distancia_status_x, y_inicio, self.largura_coluna_status, altura_scan)

        print("Lendo dados da tela (OCR)...")
        lista_ids = self.visao.ler_texto_da_regiao(regiao_ids, config_tesseract='--psm 6 -c tessedit_char_whitelist=0123456789')
        lista_status = self.visao.ler_texto_da_regiao(regiao_status, config_tesseract='--psm 6 --oem 3 -l por')

        return self._correlacionar_dados(lista_ids, lista_status, x_ancora, y_inicio)

    def _correlacionar_dados(self, ids, status, x_base, y_base):
        """
        Junta as duas listas (IDs e Status) em objetos Paciente.
        Assume alinhamento 1:1.
        """
        pacientes = []
        qtd = min(len(ids), len(status))
        
        for i in range(qtd):
            # Calcula onde clicar (centro aproximado da linha)
            y_clique = y_base + (i * self.altura_linha) + (self.altura_linha // 2)
            
            p = Paciente(ids[i], status[i], y_clique)
            pacientes.append(p)
            
        return pacientes

    def executar_acao(self, paciente):
        print(f"Processando ID {paciente.id}...")
        # Exemplo de ação: Duplo clique na linha do paciente
        # O X é fixo na coluna de ID, o Y é calculado
        self.visao.duplo_clique(paciente.y, paciente.y) 
        time.sleep(1) # Espera janela abrir