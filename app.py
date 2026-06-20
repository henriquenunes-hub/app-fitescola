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
# CARREGAMENTO DINÂMICO DE FEEDBACKS PEDAGÓGICOS
# -------------------------------------------------------------------------
def carregar_feedbacks_pedagogicos():
    """Procura automaticamente qualquer CSV de feedbacks no repositório e carrega-o."""
    import glob
    
    # Procura por qualquer ficheiro .csv que contenha "feedback" no nome (independente de maiúsculas)
    ficheiro_csv = None
    for f in glob.glob("*.csv"):
        if "feedback" in f.lower():
            ficheiro_csv = f
            break
            
    # Se não encontrar nenhum por palavra-chave, tenta o nome padrão
    if not ficheiro_csv:
        ficheiro_csv = "feedbacks.csv"
        
    if not os.path.exists(ficheiro_csv):
        return {}
    
    # Tenta ler o ficheiro com múltiplos encodings e separadores (, ou ;)
    for encoding in ['utf-8-sig', 'latin-1', 'utf-8', 'cp1252']:
        for sep in [';', ',']:
            try:
                df = pd.read_csv(ficheiro_csv, sep=sep, encoding=encoding)
                if 'Teste' in df.columns:
                    # Limpa espaços invisíveis nos nomes das colunas (AZS, ZS, PA)
                    df.columns = df.columns.str.strip()
                    # Garante que a coluna 'Teste' está limpa e em minúsculas para o cruzamento
                    df['Teste_Limpo'] = df['Teste'].astype(str).str.strip().str.lower()
                    return df.set_index("Teste_Limpo").to_dict(orient="index")
            except:
                continue
    return {}

# Inicializa o dicionário global diretamente (sem cache para não bloquear)
feedbacks_csv = carregar_feedbacks_pedagogicos()

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
    "IMP_PA":
