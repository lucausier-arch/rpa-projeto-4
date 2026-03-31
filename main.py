import pandas as pd
from playwright.sync_api import sync_playwright
import time
import os
from datetime import datetime

# --- 1. CONFIGURAÇÕES ---
TABELA_CARGOS = {
    "dev junior": {"base": 4000.00, "extra": 25.00},
    "dev pleno":  {"base": 8000.00, "extra": 50.00},
    "dev senior": {"base": 13000.00, "extra": 81.25},
    "tech lead":  {"base": 17000.00, "extra": 106.25},
    "dev lead":   {"base": 17000.00, "extra": 106.25}
}

URL_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSc7ChD8xBzZsUNd3pz_3sxn5xlq4cSrjZZrXRHDv8YXdgQslA/viewform?usp=header"

# --- NOVA FUNÇÃO DE LOG ---
def registrar_log(mensagem):
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linha = f"[{data_hora}] {mensagem}\n"
    with open("logs/execucao.txt", "a", encoding="utf-8") as f:
        f.write(linha)
    print(mensagem) # Continua mostrando no terminal também

def calcular_salario_final(cargo, horas):
    cargo_key = cargo.lower().strip()
    dados = TABELA_CARGOS.get(cargo_key, {"base": 0, "extra": 0})
    base = dados["base"]
    valor_hora_extra = dados["extra"] * 1.5 
    return round(base + ((horas - 160) * valor_hora_extra) if horas > 160 else base, 2)

def iniciar_robo():
    # Pastas conforme seu print
    for p in ['data/entrada', 'data/saida', 'correcao', 'prints', 'logs']:
        if not os.path.exists(p): os.makedirs(p)

    caminho_input = os.path.join('data/entrada', 'dados_brutos.txt')
    registrar_log("🚀 Iniciando processamento do robô.")

    try:
        df = pd.read_csv(caminho_input, sep=';', encoding='utf-8-sig')
    except Exception as e:
        registrar_log(f"❌ Erro fatal ao ler arquivo: {e}")
        return

    lista_correcao, resultados_finais = [], []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()

        for index, linha in df.iterrows():
            nome = str(linha['Nome']).strip()
            cargo = str(linha['Cargo']).strip()
            email = str(linha['Email']).strip()
            pix = str(linha['ChavePIX']).strip()
            cpf_limpo = str(linha['CPF']).replace('.', '').replace('-', '').strip()
            
            try:
                horas = float(str(linha['HorasTrabalhadas']).replace('h', '').strip())
            except:
                horas = 0.0

            # Validações
            motivo_erro = None
            if len(cpf_limpo) != 11: motivo_erro = "CPF inválido"
            elif "@" not in email: motivo_erro = "Email sem @"
            elif cargo.lower() not in TABELA_CARGOS: motivo_erro = f"Cargo '{cargo}' não cadastrado"

            if motivo_erro:
                registrar_log(f"⚠️ Rejeitado: {nome} | Motivo: {motivo_erro}")
                linha_erro = linha.to_dict()
                linha_erro['Motivo_Erro'] = motivo_erro
                lista_correcao.append(linha_erro)
                continue 

            salario_final = calcular_salario_final(cargo, horas)

            try:
                page.goto(URL_FORMULARIO)
                page.get_by_label("Nome completo").fill(nome)
                page.get_by_label("cpf").fill(cpf_limpo)
                page.get_by_label(cargo, exact=False).click() 
                page.get_by_label("email de contato").fill(email)
                page.get_by_label("chave pix").fill(pix)
                page.get_by_label("horas trabalhadas").fill(str(horas))
                page.get_by_label("Salário Final Calculado").fill(str(salario_final))

                time.sleep(1)
                page.locator('//span[text()="Enviar"] | //span[text()="Submit"]').click()
                page.wait_for_load_state("networkidle")
                
                registrar_log(f"✅ Sucesso: {nome} processado e enviado.")
                page.screenshot(path=f"prints/sucesso_{cpf_limpo}.png")
                
                linha_sucesso = linha.to_dict()
                linha_sucesso['Salario_Final'] = salario_final
                resultados_finais.append(linha_sucesso)

            except Exception as e:
                registrar_log(f"❌ Erro no formulário para {nome}: {e}")

        browser.close()

    # Salvar Planilhas
    if lista_correcao: pd.DataFrame(lista_correcao).to_excel("correcao/precisa_corrigir.xlsx", index=False)
    if resultados_finais: pd.DataFrame(resultados_finais).to_excel("data/saida/candidatos_finalizados.xlsx", index=False)
    
    registrar_log("🏁 Robô finalizou todas as tarefas.")

if __name__ == "__main__":
    iniciar_robo()