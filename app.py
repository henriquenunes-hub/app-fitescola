import streamlit as st
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Circle

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(page_title="EduTwin - Relatório FitEscola", layout="centered")

# --- Estrutura de Referência Protegida (Sem Erros de Sintaxe) ---
dados_masc = {
    "Vaivém (Percursos)": {"ZS": 45, "AZS": 35},
    "Abdominais (Rep.)": {"ZS": 25, "AZS": 20},
    "Flexões (Rep.)": {"ZS": 15, "AZS": 12},
    "Imp. Horizontal (cm)": {"ZS": 160, "AZS": 140},
    "Velocidade 40m (s)": {"ZS": 6.2, "AZS": 6.8},
    "Senta e Alcança (cm)": {"ZS": 22, "AZS": 18}
}

# ==============================================================================
# 2. FUNÇÃO AUXILIAR: CRIAÇÃO DO INDICADOR VISUAL COMPACTO
# ==============================================================================
def obter_grafico_posicionamento(classificacao):
    """
    Gera um componente gráfico inline extremamente compacto (altura: 18pt)
    para evitar que as linhas da tabela expandam verticalmente.
    """
    d = Drawing(100, 18)
    
    # Barra de progresso dividida: Vermelho Claro (AZS) e Verde Claro (ZS)
    d.add(Rect(0, 3, 42, 7, fillColor=colors.HexColor("#FEE2E2"), strokeColor=None))
    d.add(Rect(42, 3, 58, 7, fillColor=colors.HexColor("#DCFCE7"), strokeColor=None))
    
    # Rótulos textuais miniaturizados nas extremidades
    d.add(String(2, 12, "AZS", fontSize=6, fontName="Helvetica-Bold", fillColor=colors.HexColor("#991B1B")))
    d.add(String(45, 12, "ZS", fontSize=6, fontName="Helvetica-Bold", fillColor=colors.HexColor("#166534")))
    
    # Posicionamento dinâmico dos marcadores (círculos)
    if classificacao == "Abaixo Zona Saudável":
        d.add(Circle(21, 6, 3, fillColor=colors.HexColor("#EF4444"), strokeColor=colors.white, strokeWidth=0.5))
    elif classificacao == "Zona Saudável":
        d.add(Circle(71, 6, 3, fillColor=colors.HexColor("#22C55E"), strokeColor=colors.white, strokeWidth=0.5))
    elif classificacao == "Misto":
        # Caso especial para o Senta e Alcança (um membro em cada zona)
        d.add(Circle(21, 6, 3, fillColor=colors.HexColor("#EF4444"), strokeColor=colors.white, strokeWidth=0.5))
        d.add(Circle(71, 6, 3, fillColor=colors.HexColor("#22C55E"), strokeColor=colors.white, strokeWidth=0.5))
        
    return d

# ==============================================================================
# 3. CAMADA DE FUNDO (CANVAS): CABEÇALHO E RODAPÉ FIXOS
# ==============================================================================
def desenhar_decoracoes_pagina(canvas, doc):
    """
    Desenha os elementos decorativos fixos diretamente no canvas.
    Desta forma, o rodapé não ocupa espaço no fluxo de layout da página.
    """
    canvas.saveState()
    
    # Linha decorativa superior (Azul Escuro)
    canvas.setStrokeColor(colors.HexColor("#1A365D"))
    canvas.setLineWidth(1)
    canvas.line(20, A4[1] - 30, A4[0] - 20, A4[1] - 30)
    
    # Texto do Rodapé (Esquerda)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#4A5568"))
    canvas.drawString(20, 20, "Relatório gerado por EduTwin | Professor Responsável: O teu Nome Completo")
    
    # Número de Página Fixo (Direita) - Sabendo que cabe tudo numa página
    canvas.drawRightString(A4[0] - 20, 20, "Página 1 de 1")
    
    canvas.restoreState()

# ==============================================================================
# 4. FUNÇÃO PRINCIPAL: GERAÇÃO DO PDF COMPACTO
# ==============================================================================
def gerar_pdf_individual():
    pdf_buffer = io.BytesIO()
    
    # Definição do documento com margens otimizadas de 20 pontos (aprox. 0.7 cm)
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=20,
        rightMargin=20,
        topMargin=35,
        bottomMargin=35
    )
    
    styles = getSampleStyleSheet()
    
    # --- ESTILOS CUSTOMIZADOS (Otimizados para densidade de dados) ---
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1A365D"),
        alignment=1, # Centro
        spaceAfter=2
    )
    
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceAfter=12
    )
    
    style_meta = ParagraphStyle('MetaText', parent=styles['Normal'], fontSize=9, leading=13)
    style_th = ParagraphStyle('TableHeader', parent=styles['Normal'], fontSize=8.5, leading=10, textColor=colors.white, fontName="Helvetica-Bold")
    style_td = ParagraphStyle('TableCell', parent=styles['Normal'], fontSize=8, leading=10.5)
    style_td_center = ParagraphStyle('TableCellCenter', parent=style_td, alignment=1)
    
    style_alerta = ParagraphStyle(
        'AlertText',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#9B2C2C"),
        fontName="Helvetica-Bold"
    )
    
    style_orientacoes = ParagraphStyle('OrientacoesText', parent=styles['Normal'], fontSize=8.5, leading=12)

    story = []
    
    # Cabeçalho Principal
    story.append(Paragraph("RELATÓRIO DE APTIDÃO FÍSICA INDIVIDUAL", style_title))
    story.append(Paragraph("Avaliação de Parâmetros Motores e Funcionais | Bateria FitEscola", style_subtitle))
    
    # Bloco de Metadados do Aluno (Organizado em tabela invisível para poupar espaço)
    dados_aluno = [
        [Paragraph("<b>Nome do Aluno:</b> 1.0", style_meta), 
         Paragraph("<b>Idade:</b> 14.0 anos", style_meta), 
         Paragraph("<b>Género:</b> M", style_meta)],
        [Paragraph("<b>Data da Avaliação:</b> 20/06/2026", style_meta), 
         Paragraph("<b>Contacto:</b> h3nriqu3nun3s@gmail.com", style_meta), 
         ""]
    ]
    tabela_meta = Table(dados_aluno, colWidths=[200, 150, 205])
    tabela_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(tabela_meta)
    story.append(Spacer(1, 10))
    
    # --- MATRIZ DE DADOS DA TABELA DE TESTES ---
    # ColWidths totalizam exatamente 555 pontos (Largura total disponível no A4 com margens de 20)
    col_widths = [105, 65, 95, 105, 185]
    
    table_data = [
        # Linha de Cabeçalho
        [
            Paragraph("Teste Efetuado", style_th),
            Paragraph("Resultado", style_th),
            Paragraph("Classificação", style_th),
            Paragraph("Posicionamento Visual", style_th),
            Paragraph("Feedback Pedagógico e Recomendações", style_th)
        ],
        # Linhas de Dados
        [
            Paragraph("Vaivém (Percursos)", style_td),
            Paragraph("35.0", style_td_center),
            Paragraph("Abaixo Zona Saudável", style_td_center),
            obter_grafico_posicionamento("Abaixo Zona Saudável"),
            Paragraph("A tua capacidade cardiorespiratória está abaixo do recomendado. É aconselhável fazeres exercícios de corrida ou caminhada 3 a 5 vezes por semana.", style_td)
        ],
        [
            Paragraph("Abdominais (Rep.)", style_td),
            Paragraph("23.0", style_td_center),
            Paragraph("Abaixo Zona Saudável", style_td_center),
            obter_grafico_posicionamento("Abaixo Zona Saudável"),
            Paragraph("A tua força do tronco está abaixo do recomendado. É aconselhável fazeres exercícios de força para fortalecimento da zona abdominal, 2 a 3 vezes por semana. Pranchas são uma excelente opção.", style_td)
        ],
        [
            Paragraph("Flexões (Rep.)", style_td),
            Paragraph("13.0", style_td_center),
            Paragraph("Abaixo Zona Saudável", style_td_center),
            obter_grafico_posicionamento("Abaixo Zona Saudável"),
            Paragraph("A tua força dos membros superiores está abaixo do recomendado. É aconselhável fazeres exercícios de força direcionados para os braços e tronco, 2 a 3 vezes por semana.", style_td)
        ],
        [
            Paragraph("Imp. Horizontal (cm)", style_td),
            Paragraph("151.0", style_td_center),
            Paragraph("Abaixo Zona Saudável", style_td_center),
            obter_grafico_posicionamento("Abaixo Zona Saudável"),
            Paragraph("A tua força explosiva dos membros inferiores está abaixo do recomendado. É aconselhável fazeres exercícios de saltos (multissaltos), 2 a 3 vezes por semana.", style_td)
        ],
        [
            Paragraph("Velocidade 40m (s)", style_td),
            Paragraph("6.77", style_td_center),
            Paragraph("Abaixo Zona Saudável", style_td_center),
            obter_grafico_posicionamento("Abaixo Zona Saudável"),
            Paragraph("A tua velocidade está abaixo do recomendado. É aconselhável fazeres exercícios de coordenação rápida e técnica de corrida, 2 a 3 vezes por semana.", style_td)
        ],
        # Linha Otimizada do Senta e Alcança (Junção linear para poupar altura crítica)
        [
            Paragraph("Senta e Alcança (cm)", style_td),
            Paragraph("<b>Dir:</b> 20.2 cm<br/><b>Esq:</b> 25.0 cm", style_td_center),
            Paragraph("<b>Dir:</b> Abaixo ZS<br/><b>Esq:</b> Zona Saudável", style_td_center),
            obter_grafico_posicionamento("Misto"),
            Paragraph("<b>Perna Direita (AZS):</b> Abaixo do recomendado. Alonga diariamente.<br/><b>Perna Esquerda (ZS):</b> Muito bem! Mantém o treino de flexibilidade 2 a 3 vezes por semana.", style_td)
        ]
    ]
    
    tabela_principal = Table(table_data, colWidths=col_widths, repeatRows=1)
    tabela_principal.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Redução agressiva de padding para blindagem contra quebras de página
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(tabela_principal)
    story.append(Spacer(1, 8))
    
    # Caixa de Alerta de Assimetria (Design Compacto Callout)
    texto_alerta = [
        [Paragraph("⚠️ Atenção à diferença entre os dois membros! Pode ser sinal de treino mal dirigido ou de um problema de saúde.", style_alerta)]
    ]
    tabela_alerta = Table(texto_alerta, colWidths=[555])
    tabela_alerta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFF5F5")),
        ('BORDER', (0, 0), (-1, -1), 0.5, colors.HexColor("#FEB2B2")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tabela_alerta)
    story.append(Spacer(1, 10))
    
    # Secção de Orientações Finais
    story.append(Paragraph("<b>Orientações de Desenvolvimento Desportivo:</b>", style_td))
    story.append(Spacer(1, 2))
    
    conteudo_orientacoes = (
        "• A silhueta assinalada identifica a tua posição atual face às referências nacionais de saúde.<br/>"
        "• Lembra-te que a aptidão física evolui com o teu compromisso diário e consistência motora nas aulas.<br/>"
        "• Continua focado nos teus objetivos!"
    )
    story.append(Paragraph(conteudo_orientacoes, style_orientacoes))
    
    # Compilação final injetando o canvas estático para o cabeçalho/rodapé
    doc.build(story, onFirstPage=desenhar_decoracoes_pagina, onLaterPages=desenhar_decoracoes_pagina)
    
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# ==============================================================================
# 5. INTERFACE DO UTILIZADOR (STREAMLIT UI)
# ==============================================================================
st.title("EduTwin - Emissão de Relatório")
st.write("Clique no botão abaixo para descarregar o relatório formatado estritamente numa única página.")

pdf_data = gerar_pdf_individual()

st.download_button(
    label="📥 Descarregar Relatório PDF (1 Página)",
    data=pdf_data,
    file_name="Relatorio_1.0.pdf",
    mime="application/pdf"
)
