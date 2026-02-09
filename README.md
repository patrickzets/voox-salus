# 🧬 Voox Salus Automation

![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

> **Automação Inteligente baseada em Visão Computacional para o sistema Salus.**

O **Voox Salus** é um robô de automação de processos (RPA) desenvolvido para otimizar o fluxo de trabalho em laboratórios de DNA. Ele automatiza a tarefa repetitiva e propensa a erros de anexar resultados em PDF aos pedidos de pacientes no sistema Salus (ambiente remoto/Citrix), garantindo precisão milimétrica e segurança de dados.

---

## 🚀 Funcionalidades Principais

* **🖥️ Interface Gráfica Moderna (GUI):** Desenvolvida com `CustomTkinter`, oferece um painel de controle intuitivo, modo escuro nativo e logs em tempo real.
* **👁️ Navegação por Visão Computacional (Color Mapping):** Diferente de bots tradicionais que quebram com mudanças de resolução, o Voox Salus utiliza um sistema exclusivo de **Mapeamento por Cores (OpenCV)**. Ele "enxerga" pontos específicos na tela, tornando a automação resiliente a pequenas mudanças visuais.
* **⚡ Injeção de Dados via Clipboard:** Utiliza a área de transferência do Windows para colar dados instantaneamente, evitando erros de digitação (typos) comuns em conexões remotas lentas.
* **🛑 Controle Total (Kill Switch):** Botão de "PARAR" instantâneo que interrompe a execução de forma segura via Threading Events.
* **📝 Log Detalhado:** Acompanhamento passo-a-passo de cada ação do robô diretamente na interface.

---

## 🛡️ Protocolos de Segurança & Confiabilidade

A segurança foi prioridade zero no desenvolvimento deste bot, dado o ambiente sensível de dados médicos.

### 1. Sanitização de Input (`Integer Safety`)
O sistema possui um filtro rigoroso (`extrair_id`) que remove qualquer caractere não numérico do nome do arquivo antes do processamento. Isso impede ataques de injeção ou erros de "Type Mismatch" no banco de dados do Salus (erro *Not a valid integer*).

### 2. Validação Visual (`Mouse Drag`)
O robô não teleporta o mouse. Ele move o cursor com uma duração perceptível (`duration=0.5s`). Isso permite que o operador humano veja exatamente onde o robô pretende clicar antes da ação, servindo como uma camada extra de verificação visual.

### 3. Smart Waits (Pausas Inteligentes)
Em vez de clicar cegamente, o robô possui "tempos de respiração" calibrados para o *lag* natural de conexões remotas (Citrix/RDP), garantindo que os campos estejam carregados antes da interação.

### 4. Limpeza de Campos
Antes de inserir qualquer dado (ID ou Caminho do Arquivo), o robô executa rotinas de limpeza (`Double Click` + `Backspace`), garantindo que não haja resíduos de dados de operações anteriores.

---

## 🎨 Como Funciona o Mapeamento (Color Map)

O robô utiliza um arquivo `mapa.png` como guia. Cada cor representa uma ação específica, permitindo alterar o fluxo sem mexer no código.

| Cor (Visual) | Código RGB | Ação Executada | Contexto |
| :--- | :--- | :--- | :--- |
| 🔴 **Vermelho** | `255, 0, 0` | **Clique Simples** | Navegação inicial / Botões padrão |
| 🔵 **Azul** | `0, 0, 255` | **Digitação Segura** | Campo de ID do Paciente (Sanitizado) |
| 💠 **Ciano** | `0, 255, 255` | **Clique + Espera** | Botão Pesquisar (Aguarda carregamento) |
| 🟢 **Verde** | `0, 255, 0` | **Upload de Arquivo** | Botão Anexar/Clips (Cola caminho do PDF) |
| ⚪ **Branco** | `255, 255, 255` | **Clique Simples** | Confirmação de Biometria |
| ⚫ **Preto** | `0, 0, 0` | **Clique Final** | Fechar aba/janela |

---

## 🛠️ Instalação e Uso

### Pré-requisitos
* Python 3.10 ou superior
* Acesso ao sistema Salus (Maximizado)

### 1. Clone o repositório
```bash
git clone [https://github.com/patrickzets/voox-salus.git](https://github.com/patrickzets/voox-salus.git)
cd voox-salus
