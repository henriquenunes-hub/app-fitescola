import streamlit as st
import pandas as pd
import io
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Componentes do ReportLab para o layout profissional de 1 página
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Circle

# ==============================================================================
# CONFIGURAÇÃO SEGURA VIA STREAMLIT SECRETS (MAPEADA COM A SUA ESTRUTURA TOML)
# ==============================================================================
try:
    SMTP_SERVER = st.secrets["email"]["smtp_server"]
    SMTP_PORT = int(st.secrets["email"]["smtp_port"])
    SMTP_USER = st.secrets["email"]["remetente"]
    SMTP_PASS = st.secrets["email"]["password"]
    url_ficheiro = st.secrets["dados"]["link_dados"]
except KeyError as e:
    st.error(f"❌ Erro de Configuração: Verifique se o seu menu 'Secrets' tem exatamente a estrutura correta. Falta a chave: {e}")
    st.stop()

# ==============================================================================
# 1. CONFIGURAÇÃO DA INTERFACE E SIDEBAR ORIGINAL
# ==============================================================================
st.set_page_config(page_title="EduTwin - Relatório FitEscola", layout="wide")

st.sidebar.header("📋 Configurações do Relatório")
nome_professor = st.sidebar.text_input("Nome do Professor Responsável", "O teu Nome Completo")
data_teste = st.sidebar.date_input("Data da Avaliação")

st.sidebar.markdown("---")
st.sidebar.header("✉️ Estado do Sistema")
st.sidebar.success("Servidor de E-mail: Autenticado via Secrets")

# ==============================================================================
# 2. DICIONÁRIO DE FEEDBACKS PEDAGÓGICOS (BATERIA FITESCOLA)
# ==============================================================================
feedbacks_referencia = {
    "Vaivém": {
        "AZS": "A tua capacidade cardiorespiratória está abaixo do recomendado. É aconselhável fazeres exercícios de corrida ou caminhada 3 a 5 vezes por semana.",
        "ZS": "Muito bem, estás na zona saudável! Para manteres uma boa aptidão aeróbia deves fazer exercícios aeróbios 3 a 5 vezes por semana.",
        "PA": "Atingiste o Perfil Atlético na aptidão aeróbia. Agora estás entre os melhores. Procura otimizar os teus atributos físicos, mantendo uma atividade física regular."
    },
    "Abdominais": {
        "AZS": "A tua força do tronco está abaixo do recomendado. É aconselhável fazeres exercícios de força para fortalecimento da zona abdominal, 2 a 3 vezes por semana, como pranchas.",
        "ZS": "Muito bem, estás na zona saudável na força do tronco! Para manteres uma boa resistência abdominal, deves continuar a fazer exercícios de fortalecimento.",
        "PA": "Atingiste o Perfil Atlético na força do tronco! Agora estás entre os melhores. Procura otimizar a estabilidade da tua zona central (core)."
    },
    "Flexões": {
        "AZS": "A tua força dos membros superiores está abaixo do recomendado. É aconselhável fazeres exercícios de força para os membros superiores 2 a 3 vezes por semana.",
        "ZS": "Muito bem, estás na zona saudável nos membros superiores! Mantém o plano.",
        "PA": "Atingiste o Perfil Atlético nos membros superiores! Parabéns pelo teu excelente desempenho físico."
    },
    "Imp_Horizontal": {
        "AZS": "A tua força explosiva dos membros inferiores está abaixo do recomendado. É aconselhável fazeres exercícios de saltos (multissaltos), 2 a 3 vezes por semana.",
        "ZS": "Muito bem, estás na zona saudável na força explosiva!",
        "PA": "Atingiste o Perfil Atlético na força explosiva! O teu rendimento neuromuscular está excelente."
    },
    "Velocidade": {
        "AZS": "A tua velocidade está abaixo do recomendado. É aconselhável fazeres exercícios de coordenação e de técnica de corrida, 2 a 3 vezes por semana.",
        "ZS": "Muito bem, estás na zona saudável na velocidade!",
        "PA": "Atingiste o Perfil Atlético na velocidade! Agora estás entre os melhores. Procura otimizar a tua explosão."
    },
    "Flexibilidade": {
        "AZS": "A tua flexibilidade dos membros inferiores está abaixo do recomendado. É aconselhável fazeres exercícios de flexibilidade para os membros inferiores diariamente para diminuir o risco de lesões.",
        "ZS": "Muito bem, estás na zona saudável! Para manteres uma boa flexibilidade deves fazer exercícios de alongamentos 2 a 3 vezes por semana.",
        "PA": "Atingiste o Perfil Atlético na flexibilidade! Parabéns pela excelente amplitude de movimento e proteção articular."
    }
}

def determinar_zona(teste, valor, genero="M"):
    # Verifica se o valor está em falta (NaN ou String vazia)
    if pd.isna(valor) or str(valor).strip().lower() in ['nan', '']:
        return None
        
    try:
        v = float(str(valor).replace(',', '.'))
    except:
        return None
    
    gen = str(genero).strip().upper()
    
    if gen == "F":
        if teste == "Vaivém":
            return "AZS" if v < 37 else ("PA" if v >= 50 else "ZS")
        elif teste == "Abdominais":
            return "AZS" if v < 18 else ("PA" if v >= 66 else "ZS")
        elif teste == "Flexões":
            return "AZS" if v < 7 else ("PA" if v >= 19 else "ZS")
        elif teste == "Imp_Horizontal":
            return "AZS" if v < 132 else ("PA" if v >= 185 else "ZS")
        elif teste == "Velocidade":
            return "AZS" if v > 7.70 else ("PA" if v <= 6.70 else "ZS")
        elif teste in ["Senta_Dir", "Senta_Esq"]:
            return "AZS" if v < 31 else ("PA" if v >= 36.3 else "ZS")
    else:
        if teste == "Vaivém":
            return "AZS" if v < 40 else ("PA" if v >= 77 else "ZS")
        elif teste == "Abdominais":
            return "AZS" if v < 24 else ("PA" if v >= 71 else "ZS")
        elif teste == "Flexões":
            return "AZS" if v < 14 else ("PA" if v >= 24 else "ZS")
        elif teste == "Imp_Horizontal":
            return "AZS" if v < 155 else ("PA" if v >= 214 else "ZS")
        elif teste == "Velocidade":
            return "AZS" if v > 6.50 else ("PA" if v <= 5.97 else "ZS")
        elif teste in ["Senta_Dir", "Senta_Esq"]:
            return "AZS" if v < 22 else ("PA" if v >= 30.4 else "ZS")
            
    return "ZS"

# ==============================================================================
# 3. DESIGN GRÁFICO DO POSICIONAMENTO VISUAL (REPORTLAB)
# ==============================================================================
def obter_grafico_posicionamento(zona_dir, zona_esq=None):
    # Se ambos os parâmetros estiverem em falta, não desenha o gráfico
    if zona_dir is None and zona_esq is None:
        return ""
        
    d = Drawing(110, 16)
    d.add(Rect(0, 2, 35, 6, fillColor=colors.HexColor("#FEE2E2"), strokeColor=None))
    d.add(Rect(35, 2, 40, 6, fillColor=colors.HexColor("#DCFCE7"), strokeColor=None))
    d.add(Rect(75, 2, 35, 6, fillColor=colors.HexColor("#DBEAFE"), strokeColor=None))
    
    d.add(String(2, 10, "AZS", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#991B1B")))
    d.add(String(38, 10, "ZS", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#166534")))
    d.add(String(78, 10, "PA", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#1E40AF")))
    
    def obter_x(zona):
        if zona == "AZS": return 17
        if zona == "PA": return 92
        return 55

    if zona_esq is not None:
        if zona_dir is not None:
            d.add(Circle(obter_x(zona_dir), 5, 2.5, fillColor=colors.HexColor("#EF4444") if zona_dir=="AZS" else colors.HexColor("#22C55E"), strokeColor=colors.white, strokeWidth=0.5))
        if zona_esq is not None:
            d.add(Circle(obter_x(zona_esq), 5, 2.5, fillColor=colors.HexColor("#EF4444") if zona_esq=="AZS" else colors.HexColor("#22C55E"), strokeColor=colors.black, strokeWidth=0.5))
    else:
        if zona_dir is not None:
            cor = colors.HexColor("#EF4444") if zona_dir == "AZS" else (colors.HexColor("#3B82F6") if zona_dir == "PA" else colors.HexColor("#22C55E"))
            d.add(Circle(obter_x(zona_dir), 5, 2.5, fillColor=cor, strokeColor=colors.white, strokeWidth=0.5))
    return d

def desenhar_decoracoes_pagina(canvas, doc):
    canvas.saveState()
    
    # --- CABEÇALHO GRÁFICO PROPORCIONAL ---
    if os.path.exists("logo_escola.png"):
        canvas.drawImage("logo_escola.png", 20, A4[1] - 55, width=90, height=25, mask='auto', preserveAspectRatio=True)
        
    if os.path.exists("logo_fitescola.png"):
        canvas.drawImage("logo_fitescola.png", A4[0] - 110, A4[1] - 55, width=90, height=25, mask='auto', preserveAspectRatio=True)

    # Linha divisória decorativa superior
    canvas.setStrokeColor(colors.HexColor("#1A365D"))
    canvas.setLineWidth(1)
    canvas.line(20, A4[1] - 62, A4[0] - 20, A4[1] - 62)
    
    # --- RODAPÉ GRÁFICO ---
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#4A5568"))
    canvas.drawString(20, 20, f"Relatório gerado por EduTwin | Professor Responsável: {nome_professor}")
    canvas.drawRightString(A4[0] - 20, 20, "Página 1 de 1")
    canvas.restoreState()

# ==============================================================================
# 4. MOTOR DO LAYOUT DO PDF (GARANTE 1 PÁGINA COM TRATAMENTO DE NA)
# ==============================================================================
def gerar_pdf_aluno(row):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=20, rightMargin=20, topMargin=75, bottomMargin=35)
    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=14, leading=16, textColor=colors.HexColor("#1A365D"), alignment=1, spaceAfter=2)
    style_subtitle = ParagraphStyle('T2', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.HexColor("#4A5568"), alignment=1, spaceAfter=10)
    style_meta = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=9, leading=13)
    style_th = ParagraphStyle('Th', parent=styles['Normal'], fontSize=8.5, leading=10, textColor=colors.white, fontName="Helvetica-Bold")
    style_td = ParagraphStyle('Td', parent=styles['Normal'], fontSize=8, leading=10.5)
    style_td_center = ParagraphStyle('TdC', parent=style_td, alignment=1)
    style_alerta = ParagraphStyle('Alert', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor("#9B2C2C"), fontName="Helvetica-Bold")
    style_orientacoes = ParagraphStyle('Ori', parent=styles['Normal'], fontSize=8, leading=11)

    story = []
    story.append(Paragraph("RELATÓRIO DE APTIDÃO FÍSICA INDIVIDUAL", style_title))
    story.append(Paragraph("Avaliação de Parâmetros Motores e Funcionais | Bateria FitEscola", style_subtitle))
    
    # Campo "Contacto" totalmente removido daqui
    dados_aluno = [
        [Paragraph(f"<b>Nome do Aluno:</b> {row['Nome']}", style_meta), Paragraph(f"<b>Idade:</b> {row['Idade']} anos", style_meta), Paragraph(f"<b>Género:</b> {row['Género']}", style_meta)],
        [Paragraph(f"<b>Data da Avaliação:</b> {data_teste.strftime('%d/%m/%Y')}", style_meta), "", ""]
    ]
    tabela_meta = Table(dados_aluno, colWidths=[200, 150, 205])
    tabela_meta.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 2), ('TOPPADDING', (0,0), (-1,-1), 2)]))
    story.append(tabela_meta)
    story.append(Spacer(1, 10))
    
    col_widths = [110, 55, 85, 110, 195]
    table_data = [[Paragraph("Teste Efetuado", style_th), Paragraph("Resultado", style_th), Paragraph("Classificação", style_th), Paragraph("Posicionamento Visual", style_th), Paragraph("Feedback Pedagógico e Recomendações", style_th)]]
    
    testes = [
        ("Vaivém (Percursos)", "Vaivém", "Vaivém"),
        ("Abdominais (Rep.)", "Abdominais", "Abdominais"),
        ("Flexões (Rep.)", "Flexões", "Flexões"),
        ("Imp. Horizontal (cm)", "Imp_Horizontal", "Imp_Horizontal"),
        ("Velocidade 40m (s)", "Velocidade", "Velocidade")
    ]
    
    genero_aluno = row.get('Género', 'M')
    
    for nome_exibicao, chave_zona, chave_fb in testes:
        val = row[nome_exibicao]
        zona = determinar_zona(chave_zona, val, genero_aluno)
        
        if zona is None:
            # Deixa as colunas vazias se o teste não foi realizado
            table_data.append([
                Paragraph(nome_exibicao, style_td),
                Paragraph("", style_td_center),
                Paragraph("", style_td_center),
                "", 
                Paragraph("", style_td)
            ])
        else:
            txt_zona = "Abaixo Zona Saudável" if zona=="AZS" else ("Perfil Atlético" if zona=="PA" else "Zona Saudável")
            feedback = feedbacks_referencia[chave_fb][zona]
            table_data.append([
                Paragraph(nome_exibicao, style_td),
                Paragraph(str(val), style_td_center),
                Paragraph(txt_zona, style_td_center),
                obter_grafico_posicionamento(zona),
                Paragraph(feedback, style_td)
            ])
    
    val_dir = row["Senta_Dir"]
    val_esq = row["Senta_Esq"]
    zona_dir = determinar_zona("Senta_Dir", val_dir, genero_aluno)
    zona_esq = determinar_zona("Senta_Esq", val_esq, genero_aluno)
    
    if zona_dir is None and zona_esq is None:
        # Se ambos estiverem em falta, deixa a linha da flexibilidade em branco
        table_data.append([
            Paragraph("Senta e Alcança (cm)", style_td),
            Paragraph("", style_td_center),
            Paragraph("", style_td_center),
            "",
            Paragraph("", style_td)
        ])
    else:
        txt_z_dir = "AZS" if zona_dir=="AZS" else ("PA" if zona_dir=="PA" else "ZS") if zona_dir else "-"
        txt_z_esq = "AZS" if zona_esq=="AZS" else ("PA" if zona_esq=="PA" else "ZS") if zona_esq else "-"
        
        fb_dir = feedbacks_referencia["Flexibilidade"][zona_dir] if zona_dir else "Dados não registados para o membro direito."
        fb_esq = feedbacks_referencia["Flexibilidade"][zona_esq] if zona_esq else "Dados não registados para o membro esquerdo."
        
        res_dir_txt = f"{val_dir} cm" if zona_dir else "-"
        res_esq_txt = f"{val_esq} cm" if zona_esq else "-"
        
        table_data.append([
            Paragraph("Senta e Alcança (cm)", style_td),
            Paragraph(f"<b>Dir:</b> {res_dir_txt}<br/><b>Esq:</b> {res_esq_txt}", style_td_center),
            Paragraph(f"<b>Dir:</b> {txt_z_dir}<br/><b>Esq:</b> {txt_z_esq}", style_td_center),
            obter_grafico_posicionamento(zona_dir, zona_esq),
            Paragraph(f"<b>Membro Dir:</b> {fb_dir}<br/><b>Membro Esq:</b> {fb_esq}", style_td)
        ])
    
    tabela_principal = Table(table_data, colWidths=col_widths)
    tabela_principal.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(tabela_principal)
    story.append(Spacer(1, 6))
    
    # Só exibe o aviso de assimetria se ambos os testes existirem e forem diferentes
    if zona_dir is not None and zona_esq is not None and zona_dir != zona_esq:
        tabela_alerta = Table([[Paragraph("⚠️ Atenção à diferença entre os dois membros! Pode ser sinal de treino mal dirigido ou de um problema de saúde.", style_alerta)]], colWidths=[555])
        tabela_alerta.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFF5F5")), ('BORDER', (0, 0), (-1, -1), 0.5, colors.HexColor("#FEB2B2")), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4), ('LEFTPADDING', (0, 0), (-1, -1), 6)]))
        story.append(tabela_alerta)
        story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Orientações de Desenvolvimento Desportivo:</b>", style_td))
    conteudo_orientacoes = "• A silhueta assinalada identifica a tua posição atual face às referências nacionais de saúde.<br/>• Lembra-te que a aptidão física evolui com o teu compromisso diário e consistência motora nas aulas."
    story.append(Paragraph(conteudo_orientacoes, style_orientacoes))
    
    doc.build(story, onFirstPage=desenhar_decoracoes_pagina, onLaterPages=desenhar_decoracoes_pagina)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# ==============================================================================
# 5. DISPARADOR DE CORREIO ELETRÓNICO (SMTPLIB)
# ==============================================================================
def enviar_email_com_pdf(email_destino, nome_aluno, pdf_bytes):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = email_destino
    msg['Subject'] = f"Relatório Individual FitEscola - {nome_aluno}"
    
    corpo = f"Olá {nome_aluno},\n\nSegue em anexo o teu Relatório de Aptidão Física Individual da bateria FitEscola, validado pelo Professor {nome_professor}.\n\nMelhores cumprimentos,\nDireção Pedagógica"
    msg.attach(MIMEText(corpo, 'plain'))
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="Relatorio_{nome_aluno.replace(" ", "_")}.pdf"')
    msg.attach(part)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, email_destino, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return str(e)

# ==============================================================================
# 6. CARREGAMENTO AUTOMÁTICO E DINÂMICO VIA GOOGLE SHEETS URL
# ==============================================================================
st.title("📊 EduTwin - Dashboard de Análise FitEscola")
st.write("O sistema processa automaticamente a folha de dados em nuvem para emitir os PDFs unificados.")

try:
    raw_df = pd.read_csv(url_ficheiro, header=None)
    
    if raw_df.shape[0] > 2 and (str(raw_df.iloc[1, 9]).strip() == "Dta" or "Esq" in str(raw_df.iloc[1].values)):
        df = raw_df.iloc[2:].copy()
        df.columns = [
            'Nome', 'Idade', 'Género', 'Email', 
            'Vaivém (Percursos)', 'Abdominais (Rep.)', 'Flexões (Rep.)', 
            'Imp. Horizontal (cm)', 'Velocidade 40m (s)', 'Senta_Dir', 'Senta_Esq'
        ]
        df = df.dropna(subset=['Nome'])
    else:
        df = pd.read_csv(url_ficheiro)
        if 'Senta_Dir' not in df.columns:
            df.rename(columns={df.columns[-2]: 'Senta_Dir', df.columns[-1]: 'Senta_Esq'}, inplace=True)
            
    df['Nome'] = df['Nome'].astype(str).str.strip()
            
    st.subheader("👀 Pré-visualização dos Alunos Importados")
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖨️ Centro de Exportação PDF")
        aluno_selecionado = st.selectbox("Escolher Aluno para Relatório Individual", df["Nome"].unique())
        
        row_aluno = df[df["Nome"] == aluno_selecionado].iloc[0]
        pdf_bytes = gerar_pdf_aluno(row_aluno)
        
        st.download_button(
            label=f"📥 Descarregar PDF de {aluno_selecionado}",
            data=pdf_bytes,
            file_name=f"Relatorio_{str(aluno_selecionado).replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        
    with col2:
        st.subheader("🚀 Disparo de Correio Eletrónico")
        st.write(f"Estão prontos para processamento **{len(df)} relatórios individuais**.")
        
        if st.button("Enviar E-mails para a Turma Completa"):
            barra_progresso = st.progress(0)
            status_log = st.empty()
            sucessos = 0
            
            for idx, (index, row) in enumerate(df.iterrows()):
                aluno_nome = row['Nome']
                email_aluno = row['Email']
                
                status_log.text(f"A processar relatório de {aluno_nome}...")
                pdf_aluno = gerar_pdf_aluno(row)
                
                status_log.text(f"A enviar e-mail para: {email_aluno}...")
                resultado = enviar_email_com_pdf(email_aluno, aluno_nome, pdf_aluno)
                
                if resultado is True:
                    sucessos += 1
                else:
                    st.error(f"Falha no envio para {aluno_nome}: {resultado}")
                    
                barra_progresso.progress((idx + 1) / len(df))
            
            status_log.empty()
            st.success(f"🎉 Processo concluído! {sucessos} de {len(df)} e-mails enviados com sucesso.")

except Exception as erro:
    st.error(f"❌ Erro ao tentar ler a folha online do Google Sheets. Detalhes: {erro}")
