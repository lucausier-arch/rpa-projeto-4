import pandas as pd
from playwright.sync_api import sync_playwright
import time
import os

# --- 1. CONFIGURAÇÕES E REGRAS DE NEGÓCIO ---
TABELA_CARGOS = {
    "dev junior": {"base": 4000.00, "extra": 25.00},
    "dev pleno":  {"base": 8000.00, "extra": 50.00},
    "dev senior": {"base": 13000.00, "extra": 81.25},
    "tech lead":  {"base": 17000.00, "extra": 106.25},
    "dev lead":   {"base": 17000.00, "extra": 106.25}  # Adicionado para evitar erro no seu TXT
}

# COLOQUE O LINK QUE VOCÊ COPIOU DO "ENVIAR" AQUI:
URL_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSc7ChD8xBzZsUNd3pz_3sxn5xlq4cSrjZZrXRHDv8YXdgQslA/viewform?usp=header"

def calcular_salario_final(cargo, horas):
    cargo_key = cargo.lower().strip()
    dados = TABELA_CARGOS.get(cargo_key, {"base": 0, "extra": 0})
    base = dados["base"]
    valor_hora_extra = dados["extra"] * 1.5 
    
    if horas > 160:
        total = base + ((horas - 160) * valor_hora_extra)
    else:
        total = base
    return round(total, 2)

def iniciar_robo():
    # Estrutura de pastas baseada no seu print
    pasta_entrada = os.path.join('data', 'entrada')
    pasta_saida = os.path.join('data', 'saida')
    pasta_correcao = 'correcao'
    pasta_prints = 'prints'

    for p in [pasta_entrada, pasta_saida, pasta_correcao, pasta_prints]:
        if not os.path.exists(p): os.makedirs(p)

    caminho_input = os.path.join(pasta_entrada, 'dados_brutos.txt')
    
    print(f"📖 Lendo arquivo: {caminho_input}")
    
    try:
        # Correção de acentuação (utf-8-sig) conforme solicitado
        df = pd.read_csv(caminho_input, sep=';', encoding='utf-8-sig')
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return

    lista_correcao = []
    resultados_finais = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()

        for index, linha in df.iterrows():
            nome = str(linha['Nome']).strip()
            cargo = str(linha['Cargo']).strip()
            email = str(linha['Email']).strip()
            pix = str(linha['ChavePIX']).strip()
            
            try:
                horas = float(str(linha['HorasTrabalhadas']).replace('h', '').strip())
            except:
                horas = 0.0

            # Validações de Segurança
            cpf_limpo = str(linha['CPF']).replace('.', '').replace('-', '').strip()
            motivo_erro = None

            if len(cpf_limpo) != 11:
                motivo_erro = "CPF inválido"
            elif "@" not in email or ".com" not in email:
                motivo_erro = "Email inválido"
            elif cargo.lower() not in TABELA_CARGOS:
                motivo_erro = f"Cargo '{cargo}' não cadastrado"

            if motivo_erro:
                print(f"⚠️ Rejeitado: {nome} | Motivo: {motivo_erro}")
                dados_erro = linha.to_dict()
                dados_erro['Motivo_Erro'] = motivo_erro
                lista_correcao.append(dados_erro)
                continue 

            salario_final = calcular_salario_final(cargo, horas)

            try:
                page.goto(URL_FORMULARIO)
                
                # Preenchimento
                page.get_by_label("Nome completo").fill(nome)
                page.get_by_label("cpf").fill(cpf_limpo)
                page.get_by_label(cargo, exact=False).click() 
                page.get_by_label("email de contato").fill(email)
                page.get_by_label("chave pix").fill(pix)
                page.get_by_label("horas trabalhadas").fill(str(horas))
                page.get_by_label("Salário Final Calculado").fill(str(salario_final))

                # Correção do Clique: Espera 1s para o Forms validar e clica
                time.sleep(1)
                
                # Tenta clicar em "Enviar" ou "Submit"
                botao_enviar = page.locator('//span[text()="Enviar"] | //span[text()="Submit"]')
                botao_enviar.click()
                
                # Espera confirmação de envio
                page.wait_for_load_state("networkidle")
                
                print(f"✅ Enviado: {nome}")
                page.screenshot(path=f"{pasta_prints}/sucesso_{cpf_limpo}.png")
                
                dados_sucesso = linha.to_dict()
                dados_sucesso['Salario_Final'] = salario_final
                resultados_finais.append(dados_sucesso)

            except Exception as e:
                print(f"❌ Falha no envio de {nome}: {e}")

        browser.close()

    # Geração dos relatórios Excel (Requer openpyxl)
    if lista_correcao:
        pd.DataFrame(lista_correcao).to_excel(f"{pasta_correcao}/precisa_corrigir.xlsx", index=False)
    if resultados_finais:
        pd.DataFrame(resultados_finais).to_excel(f"{pasta_saida}/candidatos_finalizados.xlsx", index=False)

    print("🏁 Processo concluído. Verifique as pastas de saída.")

if __name__ == "__main__":
    iniciar_robo()