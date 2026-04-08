# 🤖 RPA - Automação de Processamento de Folha de Pagamento (Versão 2.0)

Este projeto de **RPA (Robotic Process Automation)** foi desenvolvido em Python para automatizar o fluxo completo de processamento salarial. O robô saneia dados brutos, valida informações, calcula salários com regras de horas extras e realiza o input automatizado em sistemas web, com foco total em **rastreabilidade e auditoria**.

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para configurar o ambiente e executar o robô na sua máquina.

### 1. Clonar o Repositório
Abra o terminal na pasta desejada e clone o projeto:
```bash
git clone [https://github.com/lucausier-arch/rpa-projeto-4.git](https://github.com/lucausier-arch/rpa-projeto-4.git)
cd rpa-projeto-4

# Criar o ambiente
python -m venv .venv

# Ativar no Windows:
.venv\Scripts\activate

# Ativar no Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt

playwright install chromium

python main.py

git pull origin main

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

pip list

## 📋 Funcionalidades Principais

* **Extração e Saneamento:** Leitura de arquivos `.txt` via Pandas com tratamento de codificação e remoção de ruídos.
* **Triagem Inteligente de Dados:**
    * **Validação Cadastral:** Filtra CPFs inválidos e e-mails fora do padrão.
    * **Análise de Performance:** Identifica automaticamente funcionários que não atingiram a jornada mínima de 160h (**Injustificados**).
* **Motor de Cálculo Financeiro:** Aplicação automática de **50% de adicional** sobre horas extras (acima de 160h) com base na tabela de cargos.
* **Automação Web com Auditoria:** * Preenchimento via **Playwright**.
    * **Screenshot de Conferência:** Captura de tela realizada *antes* do envio para garantir a integridade dos dados inseridos.
* **Versionamento de Saída:** Cada execução gera uma nova pasta numerada, impedindo a sobreposição de dados.

## ⚙️ Regras de Negócio (Tabela de Cargos)

| Cargo | Salário Base | Valor Hora Extra (c/ 50% Adicional) |
| :--- | :--- | :--- |
| **Dev Junior** | R$ 4.000,00 | R$ 37,50 |
| **Dev Pleno** | R$ 8.000,00 | R$ 75,00 |
| **Dev Senior** | R$ 13.000,00 | R$ 121,87 |
| **Tech Lead** | R$ 17.000,00 | R$ 159,37 |

## 📂 Estrutura do Projeto (Arquitetura)

```text
rpa-projeto-4/
├── data/
│   ├── entrada/       # Arquivo dados_brutos.txt (Input)
│   └── saida/         # Pastas versionadas (finalizados1, finalizados2...)
│       └── finalizadosX/
│           ├── candidatos_finalizados.xlsx (Sucessos)
│           ├── injustificados.xlsx         (Carga horária baixa)
│           └── precisa_corrigir.xlsx       (Erros cadastrais)
├── logs/              # Histórico técnico de execução (.txt)
├── prints/            # Evidências de auditoria (conferencia_CPF.png)
├── diagram.puml       # Modelagem UML do fluxo
├── main.py            # Script principal do robô
└── requirements.txt   # Dependências (Pandas, Playwright, Openpyxl)