import pandas as pd  
from playwright.sync_api import sync_playwright  
import time  
import os  
from datetime import datetime  

# --- CONFIGURAÇÕES ---
TABELA_CARGOS = {
    "dev junior": {"base": 4000.00, "extra": 25.00},
    "dev pleno":  {"base": 8000.00, "extra": 50.00},
    "dev senior": {"base": 13000.00, "extra": 81.25},
    "tech lead":  {"base": 17000.00, "extra": 106.25}
}

URL_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSc7ChD8xBzZsUNd3pz_3sxn5xlq4cSrjZZrXRHDv8YXdgQslA/viewform?usp=header"

def registrar_log(mensagem):
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linha = f"[{data_hora}] {mensagem}\n"
    if not os.path.exists("logs"): os.makedirs("logs")
    with open("logs/execucao.txt", "a", encoding="utf-8") as f:
        f.write(linha)
    print(mensagem)

def calcular_salario_final(cargo, horas):
    cargo_key = cargo.lower().strip()
    dados = TABELA_CARGOS.get(cargo_key, {"base": 0, "extra": 0})
    base = dados["base"]
    valor_hora_extra = dados["extra"] * 1.5 
    return round(base + ((horas - 160) * valor_hora_extra) if horas > 160 else base, 2)

def criar_pasta_versao():
    """Gera o nome da próxima pasta de versão (finalizados1, 2, 3...) dentro de data/saida"""
    contador = 1
    while True:
        nome_pasta = os.path.join('data/saida', f'finalizados{contador}')
        if not os.path.exists(nome_pasta):
            os.makedirs(nome_pasta)
            return nome_pasta
        contador += 1

def iniciar_robo():
    # Cria as pastas base necessárias
    for p in ['data/entrada', 'data/saida', 'prints', 'logs']:
        if not os.path.exists(p): os.makedirs(p)

    caminho_input = os.path.join('data/entrada', 'dados_brutos.txt')
    registrar_log("🚀 Iniciando processamento do robô.")

    try:
        df = pd.read_csv(caminho_input, sep=';', encoding='utf-8-sig')
    except Exception as e:
        registrar_log(f"❌ Erro fatal ao ler arquivo: {e}")
        return

    # Listas para triagem interna
    lista_correcao, resultados_finais, lista_injustificados = [], [], []

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

            # --- 1. VALIDAÇÃO DE CADASTRO (Vai para o precisa_corrigir da execução) ---
            motivo_erro = None
            if len(cpf_limpo) != 11: motivo_erro = "CPF inválido"
            elif "@" not in email: motivo_erro = "Email sem @"
            elif cargo.lower() not in TABELA_CARGOS: motivo_erro = f"Cargo '{cargo}' não cadastrado"

            if motivo_erro:
                registrar_log(f"⚠️ Erro de Cadastro: {nome} | Motivo: {motivo_erro}")
                linha_erro = linha.to_dict()
                linha_erro['Motivo_Erro'] = motivo_erro
                lista_correcao.append(linha_erro)
                continue

            # --- 2. VALIDAÇÃO DE CARGA HORÁRIA (Vai para injustificados) ---
            if horas < 160:
                registrar_log(f"📉 Injustificado: {nome} ({horas}h).")
                linha_injusto = linha.to_dict()
                linha_injusto['Horas_Faltantes'] = 160 - horas
                lista_injustificados.append(linha_injusto)
                continue

            # --- 3. PROCESSAMENTO DE SUCESSO ---
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

                # Print de Auditoria ANTES de enviar
                time.sleep(0.5)
                page.screenshot(path=f"prints/conferencia_{cpf_limpo}.png")

                # Envio
                page.locator('//span[text()="Enviar"] | //span[text()="Submit"]').click()
                page.wait_for_load_state("networkidle")
                
                registrar_log(f"✅ Sucesso: {nome} enviado.")
                
                linha_sucesso = linha.to_dict()
                salario_formatado = f"R$ {salario_final:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
                linha_sucesso['Salario_Final'] = salario_formatado
                resultados_finais.append(linha_sucesso)

            except Exception as e:
                registrar_log(f"❌ Erro no formulário para {nome}: {e}")

        browser.close()

    # --- SALVAMENTO LOCALIZADO ---
    pasta_final = criar_pasta_versao() # Ex: data/saida/finalizadosX

    # Arquivo de Erros de Cadastro (Agora DENTRO da pasta da execução)
    if lista_correcao:
        pd.DataFrame(lista_correcao).to_excel(os.path.join(pasta_final, "precisa_corrigir.xlsx"), index=False)
    
    # Arquivo de Baixa Carga Horária
    if lista_injustificados:
        pd.DataFrame(lista_injustificados).to_excel(os.path.join(pasta_final, "injustificados.xlsx"), index=False)

    # Arquivo de Sucessos
    if resultados_finais:
        pd.DataFrame(resultados_finais).to_excel(os.path.join(pasta_final, "candidatos_finalizados.xlsx"), index=False)
    
    registrar_log(f"🏁 Processo finalizado. Tudo salvo em: {pasta_final}")

if __name__ == "__main__":
    iniciar_robo()