import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import io

# -------------------------------------------------------------------------
# 1. BASE DE DADOS INTERNA (TABELAS FITESCOLA DO UTILIZADOR)
# -------------------------------------------------------------------------
# Estrutura extraída do arquivo enviado pelo professor

dados_fem = {
    "Idade": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "VV_ZS": [13, 16, 20, 22, 25, 27, 29, 32, 35, 37, 37, 37],
    "VV_PA": [32, 35, 39, 43, 45, 47, 48, 50, 51, 50, 50, 50],
    "ABD_ZS": [9, 12, 15, 18, 18, 18, 18, 18, 18, 18, 18, 18],
    "ABD_PA": [39, 39, 46, 53, 57, 59, 62, 63, 65, 66, 66, 66],
    "FLX_ZS": [6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
    "FLX_PA": [14, 15, 15, 15, 16, 16, 17, 18, 19, 19, 19, 19],
    "IMP_ZS": [108.4, 110.8, 113.3, 115.8, 118.1, 121.8, 123.0, 126.0, 129.5, 131.9, 131.9, 131.9],
    "IMP_PA": [170.9, 172.4, 173.8, 175.3, 176.4, 179.6, 179.0, 180.4, 183.4, 184.2, 184.2, 184.2],
    "VEL_ZS": [8.55, 8.23, 7.97, 7.77, 7.62, 7.52, 7.49, 7.51, 7.58, 7.72, 7.72, 7.72],
    "VEL_PA": [7.51, 7.23, 7.00, 6.82, 6.69, 6.61, 6.58, 6.60, 6.67, 6.79, 6.79, 6.79],
    "SA_ZS": [22.9, 22.9, 25.4, 25.4, 25.4, 25.4, 30.5, 30.5, 30.5, 30.5, 30.5, 30.5],
    "SA_PA": [31.2, 31.2, 31.4, 32.1, 33.3, 34.6, 35.3, 35.6, 36.0, 36.3, 36.3, 36.3],
    "AGI_ZS": [13.20, 13.10, 13.00, 12.90, 12.80, 12.70, 12.70, 12.60, 12.60, 12.60, 12.60, 12.60],
    "AGI_PA": [11.73, 11.67, 11.61, 11.55, 11.50, 11.40, 11.40, 11.30, 11.40, 11.40, 11.40, 11.40]
}

dados_masc = {
    "Idade": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "VV_ZS": [13, 16, 20, 23, 28, 36, 42, 47, 50, 53, 53, 53],
    "VV_PA": [47, 50, 54, 59, 67, 77, 85, 91, 94, 96, 96, 96],
    "ABD_ZS": [9, 12, 15, 18, 21, 24, 24, 24, 24, 24, 24, 24],
    "ABD_PA": [47, 47, 54, 60, 66, 71, 71, 71, 71, 71, 71, 71],
    "FLX_ZS": [6, 7, 8, 10, 12, 14, 16, 18, 18, 18, 18, 18],
    "FLX_PA": [17, 21, 21, 21, 22, 24, 27, 29, 32, 34, 34, 34],
    "IMP_ZS": [102.1, 110.2, 119.0, 128.4, 135.4, 151.5, 165.4, 175.9, 184.2, 203.2, 203.2, 203.2],
    "IMP_PA": [160.0, 170.2, 180.4, 190.6, 197.3, 213.3, 224.4, 231.8, 239.0, 251.7, 251.7, 251.7],
    "VEL_ZS": [8.27, 7.94, 7.63, 7.33, 7.04, 6.76, 6.49, 6.24, 6.00, 5.77, 5.77, 5.77],
    "VEL_PA": [7.19, 6.92, 6.66, 6.41, 6.18, 5.97, 5.77, 5.59, 5.42, 5.27, 5.27, 5.27],
    "SA_ZS": [20.3, 20.3, 20.3, 20.3, 20.3, 20.3, 20.3, 20.3, 20.3, 20.3, 20.3, 20.3],
    "SA_PA": [29.3, 29.3, 28.9, 28.8, 29.2, 30.4, 31.9, 33.5, 34.5, 35.0, 35.0, 35.0],
    "AGI_ZS": [13.10, 12.80, 12.50, 12.20, 12.00, 11.70, 11.20, 10.90, 10.40, 10.40, 10.40, 10.40],
    "AGI_PA": [11.98, 11.65, 11.38, 11.11, 10.90, 10.60, 10.20, 9.90, 9.90, 9.49, 9.49, 9.49]
}

ref_fem = pd.DataFrame(dados_fem)
ref_masc = pd.DataFrame(dados_masc)

# -------------------------------------------------------------------------
# 2. FUNÇÕES DE LOGICA E PROCESSAMENTO
# -------------------------------------------------------------------------
def avaliar_teste(valor, idade, genero, teste):
    try:
        val = float(str(valor).replace(',', '.'))
    except:
        return "N/A", "Sem dados válidos."

    df_ref = ref_fem if genero.upper() in ['F', 'FEMININO', 'RAPARIGA'] else ref_masc
    
    # Encontrar a linha da idade correspondente (limitar entre 9 e 20)
    idade_busca = max(9, min(20, int(idade)))
    linha = df_ref[df_ref['Idade'] == idade_busca].iloc[0]
    
    zs = linha[f"{teste}_ZS"]
    pa = linha[f"{teste}_PA"]
    
    # Testes onde MENOS tempo/resultado é MELHOR (Velocidade e Agilidade)
    if teste in ["VEL", "AGI"]:
        if val <= pa:
            return "PA", "Parabéns! Nível de elite atlética."
        elif val <= zs:
            return "ZS", "Estás no bom caminho! Mantém o teu nível."
        else:
            return "AZS", "Precisas de melhorar. Foca no treino de velocidade/coordenação."
    # Testes onde MAIS é MELHOR (Vaivém, Abdominais, Flexões, Impulsão, Senta e Alcança)
    else:
        if val >= pa:
            return "PA", "Parabéns! Nível de elite atlética."
        elif val >= zs:
            return "ZS", "Estás no bom caminho! Mantém a tua condição física."
        else:
            return "AZS", "Precisas de melhorar. Requer mais prática e dedicação regular."

def criar_pdf(aluno, resultados):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho decorativo
    pdf.set_fill_color(41, 128, 185) # Azul pedagógico
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, "RELATÓRIO DE CONDICÃO FÍSICA - FITESCOLA", ln=True, align='C')
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(0, 10, "EduTwin - Apoio Inteligente à Educação Física", ln=True, align='C')
    pdf.ln(15)
    
    # Dados do Aluno
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 7, f"Nome: {aluno['Nome']}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(70, 7, f"Idade: {aluno['Idade']} anos", ln=False)
    pdf.cell(70, 7, f"Género: {aluno['Género']}", ln=True)
    pdf.cell(0, 7, f"Contacto: {aluno['Email']}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Tabela de Resultados
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(45, 8, "Teste Efetuado", 1, 0, 'C')
    pdf.cell(30, 8, "Resultado", 1, 0, 'C')
    pdf.cell(40, 8, "Classificação", 1, 0, 'C')
    pdf.cell(75, 8, "Feedback Pedagógico", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    mapa_testes = {
        "Vaivém (Percursos)": "VV", "Abdominais (Rep.)": "ABD", 
        "Flexões (Rep.)": "FLX", "Imp. Horizontal (cm)": "IMP",
        "Velocidade 40m (s)": "VEL", "Senta e Alcança (cm)": "SA", 
        "Agilidade (s)": "AGI"
    }
    
    for nome_exibicao, sigla in mapa_testes.items():
        if nome_exibicao in aluno:
            res_aluno = aluno[nome_exibicao]
            classe, fb = resultados[sigla]
            
            pdf.cell(45, 8, nome_exibicao, 1, 0, 'L')
            pdf.cell(30, 8, str(res_aluno), 1, 0, 'C')
            
            # Cores para a classificação
            if classe == "PA":
                pdf.set_text_color(39, 174, 96) # Verde
                txt_classe = "Perfil Atlético"
            elif classe == "ZS":
                pdf.set_text_color(41, 128, 185) # Azul
                txt_classe = "Zona Saudável"
            else:
                pdf.set_text_color(192, 41, 43) # Vermelho
                txt_classe = "Abaixo Zona Saudável"
                
            pdf.cell(40, 8, txt_classe, 1, 0, 'C')
            pdf.set_text_color(0, 0, 0)
            pdf.cell(75, 8, fb, 1, 1, 'L')
            
    pdf.ln(10)
    
    # Bloco de Sugestões Gerais de Melhoria
    pdf.set_fill_color(245, 247, 250)
    pdf.rect(10, pdf.get_y(), 190, 35, 'F')
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 6, "Recomendações Gerais do teu Professor:", ln=True)
    pdf.set_font("Arial", '', 9.5)
    pdf.multi_cell(0, 5, "- Para zonas 'Abaixo da Zona Saudável': foca-te em treinar essa capacidade 2 a 3 vezes por semana (ex: corrida contínua para o Vaivém, ou pranchas/flexões controladas para a força).\n- Se estás na 'Zona Saudável' ou 'Perfil Atlético': Continua ativo na escola e nos treinos para manteres a tua excelente saúde funcional!")
    
    return pdf.output(dest='S').encode('latin-1')

# -------------------------------------------------------------------------
# 3. INTERFACE STREAMLIT
# -------------------------------------------------------------------------
st.title("🏋️‍♂️ EduTwin: Portal Interativo FitEscola")
st.markdown("Bem-vindo, colega! Esta ferramenta processa os dados do teu Google Sheets e gera instantaneamente relatórios pedagógicos em PDF.")

# Instruções de Formato para o Sheets
with st.expander("📌 Como deve ser a estrutura do teu Google Sheets? (Clica para ver)"):
    st.write("O teu arquivo de dados dos alunos deve conter exatamente estas colunas:")
    st.code("Nome, Idade, Género, Email, Vaivém (Percursos), Abdominais (Rep.), Flexões (Rep.), Imp. Horizontal (cm), Velocidade 40m (s), Senta e Alcança (cm), Agilidade (s)")

# Input do link
link_sheets = st.text_input("Insere aqui o link do teu Google Sheets (Publicado como CSV):", 
                            placeholder="https://docs.google.com/spreadsheets/d/.../pub?output=csv")

if link_sheets:
    try:
        # Tenta ler o link direto transformando em formato de exportação de CSV caso o utilizador ponha o link normal
        if "edit?usp=sharing" in link_sheets:
            link_csv = link_sheets.replace("edit?usp=sharing", "export?format=csv")
        elif "pubhtml" in link_sheets:
            link_csv = link_sheets.replace("pubhtml", "pub?output=csv")
        else:
            link_csv = link_sheets
            
        df_alunos = pd.read_csv(link_csv)
        st.success("🎉 Dados dos alunos carregados com sucesso!")
        st.dataframe(df_alunos)
        
        st.subheader("📊 Processamento em Massa")
        if st.button("Analisar Aptidão Física & Gerar PDFs"):
            
            # Dicionário para armazenar ficheiros criados
            lista_pdfs = {}
            
            for index, aluno in df_alunos.iterrows():
                # Evitar linhas em branco
                if pd.isna(aluno['Nome']):
                    continue
                    
                res_aluno = {}
                res_aluno["VV"] = avaliar_teste(aluno.get("Vaivém (Percursos)", 0), aluno['Idade'], aluno['Género'], "VV")
                res_aluno["ABD"] = avaliar_teste(aluno.get("Abdominais (Rep.)", 0), aluno['Idade'], aluno['Género'], "ABD")
                res_aluno["FLX"] = avaliar_teste(aluno.get("Flexões (Rep.)", 0), aluno['Idade'], aluno['Género'], "FLX")
                res_aluno["IMP"] = avaliar_teste(aluno.get("Imp. Horizontal (cm)", 0), aluno['Idade'], aluno['Género'], "IMP")
                res_aluno["VEL"] = avaliar_teste(aluno.get("Velocidade 40m (s)", 0), aluno['Idade'], aluno['Género'], "VEL")
                res_aluno["SA"] = avaliar_teste(aluno.get("Senta e Alcança (cm)", 0), aluno['Idade'], aluno['Género'], "SA")
                res_aluno["AGI"] = avaliar_teste(aluno.get("Agilidade (s)", 0), aluno['Idade'], aluno['Género'], "AGI")
                
                # Gerar o binário do PDF
                pdf_bytes = criar_pdf(aluno, res_aluno)
                nome_limpo = str(aluno['Nome']).replace(" ", "_")
                lista_pdfs[f"Relatorio_{nome_limpo}.pdf"] = pdf_bytes
            
            st.balloons()
            st.success(f"Foram processados {len(lista_pdfs)} alunos!")
            
            # Disponibilizar downloads individuais na interface
            st.write("### ⬇️ Descarregar Relatórios Individuais")
            for nome_arq, dados_arq in lista_pdfs.items():
                st.download_button(label=f"📥 {nome_arq}", data=dados_arq, file_name=nome_arq, mime='application/pdf')
                
    except Exception as e:
        st.error(f"Erro ao ler os dados. Confirma se o teu Google Sheets está publicado corretamente na web. Detalhe do erro: {e}")
