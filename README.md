# RPA - Automação de Folha de Pagamento

Projeto de automação desenvolvido em Python para o curso "Python to Automation".
O robô realiza a leitura de dados brutos, validação de CPF, cálculo de salário com horas extras e preenchimento automatizado no Google Forms.


# 🤖 RPA - Automação de Processamento de Folha de Pagamento

Este projeto de **RPA (Robotic Process Automation)** foi desenvolvido em Python para automatizar o fluxo de processamento salarial. O robô realiza a leitura de dados brutos de arquivos `.txt`, valida informações sensíveis, calcula salários com regras de horas extras e realiza o input automatizado em sistemas web via Google Forms.

## 📋 Funcionalidades

* **Extração de Dados:** Leitura de arquivos semi-estruturados (`.txt`) usando Pandas.
* **Saneamento e Validação:** * Limpeza de CPF (remoção de caracteres especiais).
    * Validação de formato de e-mail e consistência de cargos.
* **Motor de Cálculo:** Cálculo de salário base com adicional de **50% de hora extra** para jornadas acima de 160h mensais.
* **Automação Web:** Preenchimento de formulário Google Forms utilizando **Playwright**.
* **Gestão de Evidências:** * Captura de screenshots (`.png`) de cada envio.
    * Geração de Logs detalhados de execução (`logs/execucao.txt`).
* **Output Estruturado:** Exportação de planilhas Excel (`.xlsx`) com valores formatados em moeda brasileira (**R$ 1.234,56**).

## ⚙️ Regras de Negócio (Tabela de Cargos)

| Cargo | Salário Base | Valor Hora Extra (50% Adicional) |
| :--- | :--- | :--- |
| Dev Junior | R$ 4.000,00 | R$ 37,50 |
| Dev Pleno | R$ 8.000,00 | R$ 75,00 |
| Dev Senior | R$ 13.000,00 | R$ 121,87 |
| Tech Lead | R$ 17.000,00 | R$ 159,37 |

## 📂 Estrutura do Projeto

```text
PROJETO_4_RPA/
├── data/
│   ├── entrada/       # Arquivo dados_brutos.txt (Input)
│   └── saida/         # Planilha candidatos_finalizados.xlsx (Sucesso)
├── correcao/          # Planilha precisa_corrigir.xlsx (Erros de validação)
├── prints/            # Comprovantes de envio (Screenshots)
├── logs/              # Histórico de execução (.txt)
├── main.py            # Script principal do robô
└── requirements.txt   # Dependências do projeto (Pandas, Playwright, Openpyxl)

## Instalação 

git clone [https://github.com/lucausier-arch/PROJETO_4_RPA.git](https://github.com/lucausier-arch/PROJETO_4_RPA.git)
cd PROJETO_4_RPA
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

## 🛠️ Tecnologias Utilizadas

Python 3.12+
Pandas: Tratamento de dados.
Playwright: Automação Web.
Openpyxl: Geração de relatórios Excel.
PlantUML: Documentação de processos.

## 🚀 Como Rodar

1. Clone o repositório.
2. Crie o ambiente virtual: `python -m venv venv`.
3. Ative o ambiente: `.\venv\Scripts\activate`.
4. Instale as dependências: `pip install -r requirements.txt`.
5. Instale o navegador do Playwright: `playwright install`.
6. Execute o robô: `python main.py`.

## 📂 Estrutura

- `data/input`: Arquivos de entrada (.txt).
- `data/output`: Planilhas processadas com sucesso.
- `correcao`: Registros com erros de validação.
- `prints`: Comprovantes de envio.
