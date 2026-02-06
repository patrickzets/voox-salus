README FEITA COM IA POIS TENGO PREGUIÇA DE DIGITAR TUDO ISSO!!!!!!!


# 🧬 Salus RPA - Automação de Anexos (DNA)

Este projeto é uma solução de **RPA (Robotic Process Automation)** desenvolvida para otimizar o processo de anexação de documentos escaneados no sistema **Salus Biocroma/Biovida**. O robô automatiza a busca de pacientes, validação de status e upload de arquivos PDF.

## 🚀 Funcionalidades

- **Interface Gráfica (GUI):** Desenvolvida com `CustomTkinter` para uma experiência de usuário moderna e intuitiva.
- **Modos de Operação:** - **Biocroma:** Sequência completa de 12 passos.
  - **Biovida:** Lógica de extração de ID (pós-hífen) e salto de etapas iniciais.
- **Lupa Móvel (OCR):** Utiliza `Tesseract OCR` para ler a tela e garantir que o robô não selecione pacientes com status "CANCELADO".
- **Modo Simulação:** Operador `Admin/Teste` permite validar a detecção de imagens sem realizar cliques reais.
- **Gestão de Arquivos:** Processamento em lote com movimentação automática de arquivos concluídos.

## 🛠️ Tecnologias Utilizadas

- [Python 3.10+](https://www.python.org/)
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - Automação de interface.
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Interface visual.
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Reconhecimento óptico de caracteres.
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Relatórios em Excel.

## 📋 Pré-requisitos

1. **Tesseract OCR:** É necessário ter o Tesseract instalado em `C:\Program Files\Tesseract-OCR`.
2. **Escala do Windows:** O monitor deve estar configurado com **100% de escala** para precisão das coordenadas.
3. **Pasta de Imagens:** Os gatilhos visuais devem estar na pasta `imgs/`.

## 📦 Instalação e Uso

1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/SEU_REPO.git](https://github.com/SEU_USUARIO/SEU_REPO.git)
