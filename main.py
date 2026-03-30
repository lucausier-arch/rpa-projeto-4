import pandas as pd
from playwright.sync_api import sync_playwright
import time
import os

# Configurações de Caminhos
TXT_FILE = "dados_brutos.txt"
EXCEL_FILE = "data/candidatos.xlsx"
URL_FORMS = "https://seu_link_do_forms"
FOLDER_CORRECAO = "correcao" # <--- Nova pasta da sua função

def preparar_dados():
    """FASE 1: Preparação de Dados"""
    try:
        # Criar pastas se não existirem
        for folder in ["data", "prints", FOLDER_CORRECAO]:
            if not os.path.exists(folder): os.makedirs(folder)

        df_txt = pd.read_csv(TXT_FILE, sep=';', encoding='utf-8')
        
        if 'Status' not in df_txt.columns:
            df_txt['Status'] = 'Pendente'
        if 'Evidência' not in df_txt.columns:
            df_txt['Evidência'] = '-'
            
        df_txt.to_excel(EXCEL_FILE, index=False)
        return True
    except Exception as e:
        print(f"❌ Erro na Fase 1: {e}")
        return False

def executar_automacao():
    """FASE 2: Loop de Processamento"""
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"❌ Erro ao carregar Excel: {e}")
        return

    # Lista de 'afazeres' para a função de correção
    lista_para_correcao = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        for index, row in df.iterrows():
            # Pular se já finalizado
            if row['Status'] == 'Finalizado':
                continue

            # 1. Limpar e Validar CPF
            cpf_limpo = str(row['CPF']).replace('.', '').replace('-', '')
            
            if len(cpf_limpo) != 11:
                # --- FUNÇÃO DE CORREÇÃO ---
                print(f"⚠️ Dado inválido: {row['Nome']}. Enviando para lista de correção.")
                df.at[index, 'Status'] = 'Erro: CPF Inválido'
                
                # Adiciona o registro inteiro para o humano revisar depois
                lista_para_correcao.append(row)
                continue 

            # 2. Processo no Formulário
            try:
                page.goto(URL_FORMS)
                page.fill('input[aria-label="Nome"]', str(row['Nome']))
                page.fill('input[aria-label="CPF"]', cpf_limpo)
                page.fill('input[aria-label="Cargo"]', str(row['Cargo']))
                
                page.click('text=Enviar')
                
                # 3. Evidência e Atualização
                screenshot_path = f"prints/confirmacao_{cpf_limpo}.png"
                page.screenshot(path=screenshot_path)
                
                df.at[index, 'Status'] = 'Finalizado'
                df.at[index, 'Evidência'] = screenshot_path
                
            except Exception as error:
                # Tratamento de Erro Global do Loop (ErrorHandler)
                print(f"❌ Erro de Sistema para {row['Nome']}: {error}")
                df.at[index, 'Status'] = 'Erro no Sistema'

            # Salvar Excel (Segurança contra interrupção)
            df.to_excel(EXCEL_FILE, index=False)

        # --- FINALIZAÇÃO: Exportar Lista de Afazeres ---
        if lista_para_correcao:
            df_revisao = pd.DataFrame(lista_para_correcao)
            nome_arquivo = f"revisar_candidatos_{int(time.time())}.xlsx"
            df_revisao.to_excel(os.path.join(FOLDER_CORRECAO, nome_arquivo), index=False)
            print(f"📋 Lista de correção gerada em /{FOLDER_CORRECAO}")

        browser.close()

if __name__ == "__main__":
    if preparar_dados():
        executar_automacao()
        print("🏁 Automação concluída!")