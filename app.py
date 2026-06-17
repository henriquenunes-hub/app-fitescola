import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
import io
import os

# -------------------------------------------------------------------------
# 1. BASE DE DADOS INTERNA (TABELAS FITESCOLA DO UTILIZADOR)
# -------------------------------------------------------------------------
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
# 2. SUBCLASSE CUSTOMIZADA DO FPDF PARA INCLUIR RODAPÉ AUTOMÁTICO
# -------------------------------------------------------------------------
class PDF_Relatorio(FPDF):
    def __init__(self, nome_professor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_professor = nome_professor

    def footer(self):
        # Posicionar a 15 mm do fundo da página
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(127, 140, 141) # Cinzento discreto
        # Linha separadora do rodapé
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
        # Texto do rodapé: Professor responsável e paginação automática
        texto_rodape = f"Relatório gerado por EduTwin | Professor Responsável: {self.nome_professor}"
        self.cell(0, 10, texto_rodape, 0, 0, 'L')
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

# -------------------------------------------------------------------------
# 3. FUNÇÕES DE LÓGICA E PROCESSAMENTO
# -------------------------------------------------------------------------
def avaliar_teste(valor, idade, genero, teste):
    try:
        val = float(str(valor).replace(',', '.'))
    except:
        return "N/A", "Sem dados válidos enviados."

    df_ref = ref_fem if genero.upper() in ['F', 'FEMININO', 'RAPARIGA'] else ref_masc
    idade_busca = max(9, min(20, int(idade)))
    linha = df_ref[df_ref['Idade'] == idade_busca].iloc[0]
    
    zs = linha[f"{teste}_ZS"]
    pa = linha[f"{teste}_PA"]
    
    if teste in ["VEL", "AGI"]:
        if val <= pa:
            return "PA", "Parabéns! Estás num nível de excelência e elite atlética. Continua focado."
        elif val <= zs:
            return "ZS", "Estás no bom caminho! Mantém a regularidade e consistência nos teus treinos."
        else:
            return "AZS", "Precisas de melhorar. Foca no treino dinâmico de velocidade e coordenação motora."
    else:
        if val >= pa:
            return "PA", "Parabéns! Estás num nível de excelência e elite atlética. Continua focado."
        elif val >= zs:
            return "ZS", "Estás no bom caminho! Mantém a regularidade e condicionamento físico geral."
        else:
            return "AZS", "Precisas de melhorar. Requer mais empenho, prática e dedicação regular nas aulas."

def criar_pdf(aluno, resultados, data_teste, nome_professor):
    # Usar a nossa classe costumizada que injeta o rodapé automaticamente
    pdf = PDF_Relatorio(nome_professor=nome_professor)
    pdf.add_page()
    
    # Cabeçalho decorativo azul
    pdf.set_fill_color(41, 128, 185)
    pdf.rect(0, 0, 210, 42, 'F')
    
    # --- LOGÓTIPO DA ESCOLA (Canto Superior Esquerdo) ---
    if os.path.exists("logo_escola.png"):
        pdf.image("logo_escola.png", x=12, y=6, h=14)
    elif os.path.exists("logo_escola.jpg"):
        pdf.image("logo_escola.jpg", x=12, y=6, h=14)
        
    # --- LOGÓTIPO DO FITESCOLA (Canto Superior Direito) ---
    if os.path.exists("logo_fitescola.png"):
        pdf.image("logo_fitescola.png", x=170, y=6, h=14)
    elif os.path.exists("logo_fitescola.jpg"):
        pdf.image("logo_fitescola.jpg", x=170, y=6, h=14)

    # Títulos do cabeçalho
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_y(10)
    pdf.cell(0, 8, "RELATÓRIO DE CONDIÇÃO FÍSICA", ln=True, align='C')
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(0, 6, "Avaliação da Aptidão Física Escolar", ln=True, align='C')
    
    # Reposicionar o cursor abaixo da faixa azul do cabeçalho
    pdf.set_y(48)
    
    # Dados do Aluno e Data do Teste
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(130, 7, f"Nome: {aluno['Nome']}", ln=False)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(60, 7, f"Data do Teste: {data_teste}", ln=True, align='R')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(60, 7, f"Idade: {aluno['Idade']} anos", ln=False)
    pdf.cell(60, 7, f"Género: {aluno['Género']}", ln=False)
    pdf.cell(70, 7, f"Contacto: {aluno['Email']}", ln=True, align='R')
    pdf.ln(4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Tabela de Resultados - Definição exata de larguras (Soma = 190mm)
    w_teste = 45
    w_resultado = 25
    w_classif = 45
    w_feedback = 75
    
    # Cabeçalho da Tabela
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(w_teste, 8, "Teste Efetuado", 1, 0, 'C')
    pdf.cell(w_resultado, 8, "Resultado", 1, 0, 'C')
    pdf.cell(w_classif, 8, "Classificação", 1, 0, 'C')
    pdf.cell(w_feedback, 8, "Feedback Pedagógico", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 9)
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
            
            if classe == "PA":
                txt_classe = "Perfil Atlético"
            elif classe == "ZS":
                txt_classe = "Zona Saudável"
            else:
                txt_classe = "Abaixo Zona Saudável"
            
            # Cálculo de Altura Dinâmica para Moldar o Texto
            linhas_necessarias = len(pdf.multi_cell(w_feedback, 5, fb, split_only=True))
            altura_linha = max(8, linhas_necessarias * 5)
            
            x_atual = pdf.get_x()
            y_atual = pdf.get_y()
            
            pdf.cell(w_teste, altura_linha, nome_exibicao, 1, 0, 'L')
            pdf.cell(w_resultado, altura_linha, str(res_aluno), 1, 0, 'C')
            
            if classe == "PA":
                pdf.set_text_color(39, 174, 96)
            elif classe == "ZS":
                pdf.set_text_color(41, 128, 185)
            else:
                pdf.set_text_color(192, 41, 43)
                
            pdf.cell(w_classif, altura_linha, txt_classe, 1, 0, 'C')
            pdf.set_text_color(0, 0, 0)
            
            pdf.set_xy(x_atual + w_teste + w_resultado + w_classif, y_atual)
            pdf.multi_cell(w_feedback, altura_linha / linhas_necessarias, fb, 1, 'L')
            pdf.set_xy(x_atual, y_atual + altura_linha)
            
    pdf.ln(8)
    
    # Bloco de Sugestões Gerais de Melhoria
    pdf.set_fill_color(245, 247, 250)
    pdf.rect(10, pdf.get_y(), 190, 32, 'F')
    pdf.set_font("Arial", 'B', 10.5)
    pdf.cell(0, 6, "Recomendações Gerais do teu Professor:", ln=True)
    pdf.set_font("Arial", '', 9.5)
    pdf.multi_cell(0, 5, "- Para zonas 'Abaixo da Zona Saudável': foca-te em treinar essa capacidade 2 a 3 vezes por semana (ex: corrida contínua para o Vaivém, ou pranchas/flexões controladas para a força).\n- Se estás na 'Zona Saudável' ou 'Perfil Atlético': Continua ativo na escola e nos treinos para manteres a tua excelente saúde funcional!")
    
    return pdf.output(dest='S').encode('latin-1')

# -------------------------------------------------------------------------
# 4. INTERFACE STREAMLIT
# -------------------------------------------------------------------------
st.title("🏋️‍♂️ EduTwin: Portal Interativo FitEscola")
st.markdown("Ferramenta avançada para gestão de aptidão física escolar.")

# Bloco de Configuração de Metadados e Customização do Professor
st.sidebar.header("⚙️ Definições do Relatório")
nome_prof = st.sidebar.text_input("Nome do Professor (Rodapé):", value="O teu Nome Completo")
data_escolhida = st.sidebar.date_input("Data de Realização dos Testes:", datetime.today())
data_formatada = data_escolhida.strftime("%d/%m/%Y")

# Alertas sobre Logótipos na barra lateral
st.sidebar.markdown("---")
st.sidebar.subheader("🖼️ Logótipos no Cabeçalho")
if not (os.path.exists("logo_escola.png") or os.path.exists("logo_escola.jpg")):
    st.sidebar.warning("⚠️ 'logo_escola.png' não encontrado no GitHub. O cabeçalho ficará apenas com texto à esquerda.")
else:
    st.sidebar.success("✔️ Logótipo da Escola detetado.")

if not (os.path.exists("logo_fitescola.png") or os.path.exists("logo_fitescola.jpg")):
    st.sidebar.warning("⚠️ 'logo_fitescola.png' não encontrado no GitHub. O cabeçalho ficará apenas com texto à direita.")
else:
    st.sidebar.success("✔️ Logótipo do FitEscola detetado.")

with st.expander("📌 Estrutura Obrigatória do Google Sheets"):
    st.write("O teu arquivo de dados deve conter exatamente estas colunas:")
    st.code("Nome, Idade, Género, Email, Vaivém (Percursos), Abdominais (Rep.), Flexões (Rep.), Imp. Horizontal (cm), Velocidade 40m (s), Senta e Alcança (cm), Agilidade (s)")

link_sheets = st.text_input("Insere aqui o link do teu Google Sheets (Publicado como CSV):", 
                            placeholder="https://docs.google.com/spreadsheets/d/.../pub?output=csv")

if link_sheets:
    try:
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
            
            lista_pdfs = {}
            
            for index, aluno in df_alunos.iterrows():
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
                
                # Passamos a data e o nome do professor dinamicamente para cada PDF criado
                pdf_bytes = criar_pdf(aluno, res_aluno, data_formatada, nome_prof)
                nome_limpo = str(aluno['Nome']).replace(" ", "_")
                lista_pdfs[f"Relatorio_{nome_limpo}.pdf"] = pdf_bytes
            
            st.balloons()
            st.success(f"Foram processados {len(lista_pdfs)} alunos!")
            
            st.write("### ⬇️ Descarregar Relatórios Individuais")
            for nome_arq, dados_arq in lista_pdfs.items():
                st.download_button(label=f"📥 {nome_arq}", data=dados_arq, file_name=nome_arq, mime='application/pdf')
                
    except Exception as e:
        st.error(f"Erro ao ler os dados. Detalhe do erro: {e}")
