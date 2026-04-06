import pandas as pd  # Biblioteca para manipulação de tabelas e arquivos Excel/CSV
from playwright.sync_api import sync_playwright  # Ferramenta para automação de navegador (Web RPA)
import time  # Utilizado para pausas controladas (sleep)
import os  # Para manipulação de pastas e caminhos de arquivos no Windows
from datetime import datetime  # Para gerar carimbos de data e hora nos logs

# --- 1. CONFIGURAÇÕES ---
# Dicionário que armazena os valores base e hora extra por cargo (Regra de Negócio)
TABELA_CARGOS = {
    "dev junior": {"base": 4000.00, "extra": 25.00},
    "dev pleno":  {"base": 8000.00, "extra": 50.00},
    "dev senior": {"base": 13000.00, "extra": 81.25},
    "tech lead":  {"base": 17000.00, "extra": 106.25}
}

# URL do formulário que o robô deve preencher
URL_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSc7ChD8xBzZsUNd3pz_3sxn5xlq4cSrjZZrXRHDv8YXdgQslA/viewform?usp=header"

# --- FUNÇÃO DE LOG ---
def registrar_log(mensagem):
    """Gera um registro com data e hora no terminal e em um arquivo txt."""
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')  # Formata data/hora atual
    linha = f"[{data_hora}] {mensagem}\n"  # Monta a linha do log
    if not os.path.exists("logs"): os.makedirs("logs")  # Cria a pasta logs se não existir
    with open("logs/execucao.txt", "a", encoding="utf-8") as f:  # Abre o arquivo em modo 'append' (anexar)
        f.write(linha)  # Escreve a mensagem no arquivo
    print(mensagem)  # Exibe a mensagem no console do VS Code

def calcular_salario_final(cargo, horas):
    """Calcula o salário somando horas extras (acima de 160h) com adicional de 50%."""
    cargo_key = cargo.lower().strip()  # Padroniza o texto do cargo para evitar erro de digitação
    dados = TABELA_CARGOS.get(cargo_key, {"base": 0, "extra": 0})  # Busca os valores no dicionário
    base = dados["base"]  # Salário fixo
    valor_hora_extra = dados["extra"] * 1.5   # Aplica o adicional de 50% sobre o valor da hora extra
    # Se horas > 160, calcula o extra e soma ao base. Se não, retorna apenas o base.
    return round(base + ((horas - 160) * valor_hora_extra) if horas > 160 else base, 2)

def iniciar_robo():
    # Cria as pastas necessárias para o projeto não dar erro de 'Caminho não encontrado'
    for p in ['data/entrada', 'data/saida', 'correcao', 'prints', 'logs']:
        if not os.path.exists(p): os.makedirs(p)

    caminho_input = os.path.join('data/entrada', 'dados_brutos.txt')  # Define o caminho do arquivo TXT
    registrar_log("🚀 Iniciando processamento do robô.")

    try:
        # Lê o arquivo TXT usando o separador ';' e corrige caracteres especiais (utf-8-sig)
        df = pd.read_csv(caminho_input, sep=';', encoding='utf-8-sig')
    except Exception as e:
        registrar_log(f"❌ Erro fatal ao ler arquivo: {e}")  # Reporta erro se o arquivo não existir ou estiver aberto
        return

    lista_correcao, resultados_finais = [], []  # Listas para armazenar sucessos e erros separadamente

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Abre o Chrome (headless=False permite que você veja ele trabalhando)
        page = browser.new_page()  # Cria uma nova aba no navegador

        # Loop que percorre cada linha da tabela carregada do TXT
        for index, linha in df.iterrows():
            nome = str(linha['Nome']).strip()  # Pega o nome e remove espaços extras
            cargo = str(linha['Cargo']).strip()  # Pega o cargo
            email = str(linha['Email']).strip()  # Pega o email
            pix = str(linha['ChavePIX']).strip()  # Pega a chave PIX
            cpf_limpo = str(linha['CPF']).replace('.', '').replace('-', '').strip()  # Limpa pontos e traços do CPF
            
            try:
                # Tenta converter as horas para número, removendo o 'h' se existir
                horas = float(str(linha['HorasTrabalhadas']).replace('h', '').strip())
            except:
                horas = 0.0  # Se falhar (campo vazio), define como 0

            # --- BLOCO DE VALIDAÇÕES ---
            motivo_erro = None
            if len(cpf_limpo) != 11: motivo_erro = "CPF inválido"  # CPF deve ter 11 dígitos
            elif "@" not in email: motivo_erro = "Email sem @"  # Verificação simples de email
            elif cargo.lower() not in TABELA_CARGOS: motivo_erro = f"Cargo '{cargo}' não cadastrado"

            if motivo_erro:
                registrar_log(f"⚠️ Rejeitado: {nome} | Motivo: {motivo_erro}")
                linha_erro = linha.to_dict()  # Transforma a linha em dicionário
                linha_erro['Motivo_Erro'] = motivo_erro  # Adiciona o motivo do erro
                lista_correcao.append(linha_erro)  # Guarda na lista de correção
                continue  # Pula para o próximo funcionário sem preencher o site

            salario_final = calcular_salario_final(cargo, horas)  # Chama a função de cálculo

            try:
                # --- AUTOMAÇÃO NO NAVEGADOR ---
                page.goto(URL_FORMULARIO)  # Acessa o site
                page.get_by_label("Nome completo").fill(nome)  # Preenche Nome
                page.get_by_label("cpf").fill(cpf_limpo)  # Preenche CPF (apenas números)
                page.get_by_label(cargo, exact=False).click()  # Clica no Cargo correto (Radio Button)
                page.get_by_label("email de contato").fill(email)  # Preenche Email
                page.get_by_label("chave pix").fill(pix)  # Preenche PIX
                page.get_by_label("horas trabalhadas").fill(str(horas))  # Preenche Horas
                page.get_by_label("Salário Final Calculado").fill(str(salario_final))  # Preenche Salário (Número puro)

                time.sleep(1)  # Pausa de segurança
                # Clica no botão de enviar (tenta localizar por texto em Português ou Inglês)
                page.locator('//span[text()="Enviar"] | //span[text()="Submit"]').click()
                page.wait_for_load_state("networkidle")  # Espera a página carregar após o envio
                
                registrar_log(f"✅ Sucesso: {nome} processado e enviado.")
                page.screenshot(path=f"prints/sucesso_{cpf_limpo}.png")  # Tira print do comprovante
                
                linha_sucesso = linha.to_dict()  # Prepara os dados para a planilha de saída
                
                # --- FORMATAÇÃO DE MOEDA (PADRÃO BRASILEIRO) ---
                # Exemplo: 4750.0 -> "R$ 4.750,00"
                salario_formatado = f"R$ {salario_final:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
                linha_sucesso['Salario_Final'] = salario_formatado  # Adiciona o salário formatado
                
                resultados_finais.append(linha_sucesso)  # Guarda na lista de finalizados

            except Exception as e:
                registrar_log(f"❌ Erro no formulário para {nome}: {e}")

        browser.close()  # Fecha o navegador ao fim do loop

    # --- SALVAMENTO DOS RESULTADOS ---
    if lista_correcao: 
        # Cria um arquivo Excel com os erros encontrados
        pd.DataFrame(lista_correcao).to_excel("correcao/precisa_corrigir.xlsx", index=False)
    
    if resultados_finais: 
        # Cria o arquivo final de sucesso com os salários formatados em R$
        pd.DataFrame(resultados_finais).to_excel("data/saida/candidatos_finalizados.xlsx", index=False)
    
    registrar_log("🏁 Robô finalizou todas as tarefas.")

# Garante que o robô só comece a rodar se este arquivo for o principal sendo executado
if __name__ == "__main__":
    iniciar_robo()