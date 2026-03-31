# RPA - Automação de Folha de Pagamento

Projeto de automação desenvolvido em Python para o curso "Python to Automation".
O robô realiza a leitura de dados brutos, validação de CPF, cálculo de salário com horas extras e preenchimento automatizado no Google Forms.

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
