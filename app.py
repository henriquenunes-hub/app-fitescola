import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
import io
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Forçar o Matplotlib a correr em segundo plano sem interface gráfica
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# -------------------------------------------------------------------------
# 1. BASE DE DADOS INTERNA (TABELAS FITESCOLA)
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
# 2. SUBCLASSE DO FPDF
# -------------------------------------------------------------------------
class PDF_Relatorio(FPDF):
    def __init__(self, nome_professor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_professor = nome_professor

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(127, 140, 141)
        self.line(10, self.get_y() - 2, 287, self.get_y() - 2)
        texto_rodape = f"Relatório gerado por EduTwin | Professor Responsável: {self.nome_professor}"
        self.cell(0, 10, texto_rodape, 0, 0, 'L')
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

# -------------------------------------------------------------------------
# 3. FUNÇÕES DE LÓGICA, PROGRESSÃO VISUAL E ENVIO
# -------------------------------------------------------------------------
def avaliar_teste(valor, idade, genero, teste):
    try:
        val = float(str(valor).replace(',', '.'))
    except:
        return "N/A", "Sem dados válidos.", 0, 0, 0

    df_ref = ref_fem if genero.upper() in ['F', 'FEMININO', 'RAPARIGA'] else ref_masc
    idade_busca = max(9, min(20, int(idade)))
    linha = df_ref[df_ref['Idade'] == idade_busca].iloc[0]
    
    zs = linha[f"{teste}_ZS"]
    pa = linha[f"{teste}_PA"]
    
    if teste in ["VEL", "AGI"]:
        if val <= pa:
            return "PA", "Excelente! Nível de elite atlética. Apresentas uma velocidade de reação e execução motora fantásticas. Continua focado nos treinos explosivos.", val, zs, pa
        elif val <= zs:
            return "ZS", "Bom trabalho! Estás na Zona Saudável. A tua coordenação e tempos de resposta estão equilibrados para garantir uma boa saúde funcional. Mantém a regularidade.", val, zs, pa
        else:
            return "AZS", "Abaixo da Zona Saudável. Precisas de estimular a tua agilidade e velocidade. Recomenda-se a prática de jogos desportivos dinâmicos e exercícios de mudanças de direção.", val, zs, pa
    else:
        if val >= pa:
            return "PA", "Incrível! Superaste a marca do Perfil Atlético. Revelas uma excelente aptidão muscular/cardiorrespiratória. Continua a desafiar os teus limites!", val, zs, pa
        elif val >= zs:
            return "ZS", "Parabéns! Garantes a presença na Zona Saudável. Tens uma base física sólida que protege o teu bem-estar e o teu rendimento escolar. Continua assim!", val, zs, pa
        else:
            return "AZS", "Abaixo da Zona Saudável. Esta capacidade requer mais empenho e foco. Tenta praticar exercícios de força controlada ou corrida contínua 2 a 3 vezes por semana.", val, zs, pa

def gerar_grafico_linha(val_aluno, zs, pa, teste_sigla, genero):
    """Gera um gráfico horizontal limpo, com a cabeça do rapaz perfeitamente destacada."""
    fig, ax = plt.subplots(figsize=(4.5, 0.7))
    
    inverter = teste_sigla in ["VEL", "AGI"]
    if inverter:
        valores_eixo = [pa, zs, val_aluno]
        min_x = min(valores_eixo) * 0.85
        max_x = max(valores_eixo) * 1.15
        ax.set_xlim(max_x, min_x)
    else:
        valores_eixo = [zs, pa, val_aluno]
        min_x = min(valores_eixo) * 0.7 if min(valores_eixo) > 0 else 0
        max_x = max(valores_eixo) * 1.2
        ax.set_xlim(min_x, max_x)

    # 1. Linha base cinzenta (Centralizada em y=1.0)
    ax.axhline(y=1.0, color='#e2e8f0', linewidth=4, zorder=1)
    
    # 2. Pontos de Referência Normativa (na linha)
    ax.scatter([zs], [1.0], color='#3498db', s=50, zorder=2)
    ax.scatter([pa], [1.0], color='#2ecc71', s=50, zorder=2)
    
    # 3. Identificação exata do género
    gen_str = str(genero).strip().upper()
    is_fem = gen_str in ['F', 'FEMININO', 'RAPARIGA', 'FEM']
    
    cor_aluno = '#e91e63' if is_fem else '#1e3a8a'     # Rosa / Azul Escuro
    cor_borda = '#ad1457' if is_fem else '#172554'
    
    # 4. Desenho Anatómico Calibrado
    if is_fem:
        # Rapariga: Corpo triangular + cabeça padrão
        ax.scatter([val_aluno], [0.90], marker='^', s=130, color=cor_aluno, edgecolor=cor_borda, linewidth=0.8, zorder=3)
        ax.scatter([val_aluno], [1.18], marker='o', s=55, color=cor_aluno, edgecolor=cor_borda, linewidth=0.8, zorder=4)
    else:
        # Rapaz: Corpo quadrado estável + cabeça subida de 1.25 para 1.32 para o encaixe perfeito
        ax.scatter([val_aluno], [0.88], marker='s', s=85, color=cor_aluno, edgecolor=cor_borda, linewidth=0.8, zorder=3)
        ax.scatter([val_aluno], [1.32], marker='o', s=55, color=cor_aluno, edgecolor=cor_borda, linewidth=0.8, zorder=4)
    
    # 5. Textos de Referência no topo (subidos ligeiramente para acompanhar o rapaz)
    ax.text(zs, 1.75, f'ZS:{zs}', color='#2980b9', fontsize=8, ha='center', weight='bold')
    ax.text(pa, 1.75, f'PA:{pa}', color='#27ae60', fontsize=8, ha='center', weight='bold')

    # Ajuste dos limites verticais (teto expandido para 2.3)
    ax.set_ylim(0.4, 2.3)
    
    # Limpeza absoluta de eixos e bordas
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#eceff1')
    ax.tick_params(axis='x', colors='#94a3b8', labelsize=7)
    
    plt.tight_layout()
    filename = f"temp_chart_{teste_sigla}_{val_aluno}.png"
    plt.savefig(filename, dpi=160, transparent=True)
    plt.close(fig)
    return filename
    
def criar_pdf(aluno, resultados, data_teste, nome_professor):
    pdf = PDF_Relatorio(nome_professor=nome_professor, orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    pdf.set_y(10)
    if os.path.exists("logo_escola.png"):
        pdf.image("logo_escola.png", x=10, y=10, h=15)
    if os.path.exists("logo_fitescola.png"):
        pdf.image("logo_fitescola.png", x=257, y=10, h=15)
        
    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 7, "RELATÓRIO DE APTIDÃO FÍSICA INDIVIDUAL", ln=True, align='C')
    pdf.set_font("Arial", 'I', 11)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, "Avaliação de Parâmetros Motores e Funcionais | Bateria FitEscola", ln=True, align='C')
    pdf.ln(8)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(160, 6, f"Nome do Aluno: {aluno['Nome']}", ln=False)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(117, 6, f"Data da Avaliação: {data_teste}", ln=True, align='R')
    
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Arial", '', 10)
    pdf.cell(60, 6, f"Idade: {aluno['Idade']} anos", ln=False)
    pdf.cell(60, 6, f"Género: {aluno['Género']}", ln=False)
    pdf.cell(157, 6, f"Contacto: {aluno['Email']}", ln=True, align='R')
    pdf.ln(3)
    pdf.line(10, pdf.get_y(), 287, pdf.get_y())
    pdf.ln(4)
    
    w_teste = 42
    w_resultado = 20
    w_classif = 38
    w_grafico = 62
    w_feedback = 115
    
    pdf.set_fill_color(248, 250, 252)
    pdf.set_font("Arial", 'B', 9.5)
    pdf.cell(w_teste, 8, "Teste Efetuado", 1, 0, 'C', fill=True)
    pdf.cell(w_resultado, 8, "Resultado", 1, 0, 'C', fill=True)
    pdf.cell(w_classif, 8, "Classificação", 1, 0, 'C', fill=True)
    pdf.cell(w_grafico, 8, "Posicionamento Visual", 1, 0, 'C', fill=True)
    pdf.cell(w_feedback, 8, "Feedback Pedagógico e Recomendações", 1, 1, 'C', fill=True)
    
    pdf.set_font("Arial", '', 9)
    mapa_testes = {
        "Vaivém (Percursos)": "VV", "Abdominais (Rep.)": "ABD", 
        "Flexões (Rep.)": "FLX", "Imp. Horizontal (cm)": "IMP",
        "Velocidade 40m (s)": "VEL", "Senta e Alcança (cm)": "SA", 
        "Agilidade (s)": "AGI"
    }
    
    arquivos_deletar = []
    
    for nome_exibicao, sigla in mapa_testes.items():
        if nome_exibicao in aluno:
            res_aluno = aluno[nome_exibicao]
            classe, fb, val, zs, pa = resultados[sigla]
            
            if classe == "PA":
                txt_classe = "Perfil Atlético"
            elif classe == "ZS":
                txt_classe = "Zona Saudável"
            else:
                txt_classe = "Abaixo Zona Saudável"
            
            linhas_necessarias = len(pdf.multi_cell(w_feedback, 4.5, fb, split_only=True))
            altura_linha = max(14, linhas_necessarias * 4.5)
            
            x_atual = pdf.get_x()
            y_atual = pdf.get_y()
            
            pdf.cell(w_teste, altura_linha, nome_exibicao, 1, 0, 'L')
            pdf.cell(w_resultado, altura_linha, str(res_aluno), 1, 0, 'C')
            
            if classe == "PA":
                pdf.set_text_color(34, 197, 94)
            elif classe == "ZS":
                pdf.set_text_color(59, 130, 246)
            else:
                pdf.set_text_color(239, 68, 68)
            pdf.cell(w_classif, altura_linha, txt_classe, 1, 0, 'C')
            pdf.set_text_color(0, 0, 0)
            
            pdf.cell(w_grafico, altura_linha, "", 1, 0)
            if classe != "N/A":
                img_path = gerar_grafico_linha(val, zs, pa, sigla, aluno['Género'])
                arquivos_deletar.append(img_path)
                pdf.image(img_path, x=x_atual + w_teste + w_resultado + w_classif + 1, y=y_atual + 1, w=w_grafico - 2, h=altura_linha - 2)
            
            pdf.set_xy(x_atual + w_teste + w_resultado + w_classif + w_grafico, y_atual)
            pdf.multi_cell(w_feedback, altura_linha / linhas_necessarias, fb, 1, 'L')
            pdf.set_xy(x_atual, y_atual + altura_linha)
            
    pdf.ln(5)
    
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(10, pdf.get_y(), 277, 18, 'F')
    pdf.set_font("Arial", 'B', 9.5)
    pdf.cell(0, 5, "Orientações de Desenvolvimento Desportivo:", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 4.5, "A silhueta assinalada identifica a tua posição atual face às referências nacionais de saúde. Lembra-te que a aptidão física evolui com o teu compromisso diário e consistência motora nas aulas. Continua focado nos teus objetivos!")
    
    pdf_output = pdf.output(dest='S').encode('latin-1')
    for f in arquivos_deletar:
        if os.path.exists(f):
            os.remove(f)
            
    return pdf_output

def disparar_email(email_destino, nome_aluno, pdf_conteudo, nome_arquivo):
    try:
        cfg = st.secrets["email"]
        msg = MIMEMultipart()
        msg['From'] = cfg["remetente"]
        msg['To'] = email_destino
        msg['Subject'] = f"FitEscola: Novo Relatório Analítico de Condição Física - {nome_aluno}"
        
        corpo = f"Olá {nome_aluno},\n\nJunto enviamos em anexo o teu novo relatório de aptidão física do FitEscola.\n\nBons treinos!\n\nCom os melhores cumprimentos,\n{st.session_state.get('nome_prof_global', 'O teu Professor de Educação Física')}"
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        part = MIMEBase('application', "octet-stream")
        part.set_payload(pdf_conteudo)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{nome_arquivo}"')
        msg.attach(part)
        
        server = smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"])
        server.starttls()
        server.login(cfg["remetente"], cfg["password"])
        server.sendmail(cfg["remetente"], email_destino, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.sidebar.error(f"Erro no envio para {email_destino}: {e}")
        return False

# -------------------------------------------------------------------------
# 4. INTERFACE STREAMLIT
# -------------------------------------------------------------------------
st.title("🏋️‍♂️ EduTwin: Portal Interativo FitEscola")
st.markdown("Relatórios em formato de Paisagem com ícones de perfil seguros.")

st.sidebar.header("⚙️ Definições do Relatório")
nome_prof = st.sidebar.text_input("Nome do Professor (Rodapé/E-mail):", value="O teu Nome Completo")
st.session_state['nome_prof_global'] = nome_prof

data_escolhida = st.sidebar.date_input("Data de Realização dos Testes:", datetime.today())
data_formatada = data_escolhida.strftime("%d/%m/%Y")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Estado do Servidor")
if "email" in st.secrets:
    st.sidebar.success("✔️ Servidor de E-mail Conectado.")
else:
    st.sidebar.error("❌ Configura os Secrets de e-mail.")

link_gravado = st.secrets.get("dados", {}).get("link_dados", "")
link_sheets = st.text_input("Link do Google Sheets detetado automaticamente:", 
                            value=link_gravado,
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
        st.success("🎉 Base de dados integrada e sincronizada!")
        st.dataframe(df_alunos)
        
        st.subheader("📊 Processamento e Ações em Massa")
        col1, col2 = st.columns(2)
        
        if 'pack_pdfs' not in st.session_state:
            st.session_state['pack_pdfs'] = {}
            st.session_state['dados_prontos'] = False

        if col1.button("🔄 1. Analisar Dados & Gerar Relatórios"):
            st.session_state['pack_pdfs'] = {}
            with st.spinner("A modelar silhuetas e a exportar PDFs..."):
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
                    
                    pdf_bytes = criar_pdf(aluno, res_aluno, data_formatada, nome_prof)
                    nome_limpo = str(aluno['Nome']).replace(" ", "_")
                    
                    st.session_state['pack_pdfs'][f"Relatorio_{nome_limpo}.pdf"] = {
                        "bytes": pdf_bytes,
                        "email": aluno['Email'],
                        "nome_aluno": aluno['Nome']
                    }
            st.session_state['dados_prontos'] = True
            st.balloons()
            st.success(f"Sucesso! {len(st.session_state['pack_pdfs'])} relatórios gerados.")

        if st.session_state['dados_prontos']:
            if col2.button("📧 2. Disparar E-mails Automatizados"):
                if "email" not in st.secrets:
                    st.error("Credenciais em falta.")
                else:
                    sucessos = 0
                    barra_progresso = st.progress(0)
                    total = len(st.session_state['pack_pdfs'])
                    
                    for i, (nome_arq, info) in enumerate(st.session_state['pack_pdfs'].items()):
                        if disparar_email(info["email"], info["nome_aluno"], info["bytes"], nome_arq):
                            sucessos += 1
                        barra_progresso.progress((i + 1) / total)
                    
                    st.success(f"🚀 Concluído! {sucessos} e-mails enviados.")

            st.write("### ⬇ Cópia de Segurança Local")
            for nome_arq, info in st.session_state['pack_pdfs'].items():
                st.download_button(label=f"📥 {nome_arq}", data=info["bytes"], file_name=nome_arq, mime='application/pdf')
                
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
