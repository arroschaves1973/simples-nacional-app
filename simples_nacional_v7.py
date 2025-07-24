
import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image

st.set_page_config(page_title="Simples Nacional 2025", layout="wide")

st.image("logo_brandao.png", width=300)
st.title("Calculadora Simples Nacional 2025 - Brandão Contabilidade")

st.markdown("Preencha os dados abaixo para calcular o DAS com base no Simples Nacional")

with st.form("formulario"):
    receita = st.number_input("Receita bruta acumulada nos últimos 12 meses (R$)", min_value=0.0, format="%.2f")
    folha = st.number_input("Folha de pagamento dos últimos 12 meses (R$)", min_value=0.0, format="%.2f")
    receita_mes = st.number_input("Receita do mês atual (R$)", min_value=0.0, format="%.2f")
    st.form_submit_button("Calcular")

if receita > 0:
    fator_r = folha / receita
    st.metric("Fator R", f"{fator_r:.2%}")

    if fator_r > 0.28:
        anexo = "Anexo III"
        aliquota = 0.06
    else:
        anexo = "Anexo V"
        aliquota = 0.15

    das = receita_mes * aliquota
    st.success(f"Anexo aplicável: **{anexo}**")
    st.success(f"Alíquota: **{aliquota*100:.2f}%**")
    st.success(f"Valor estimado do DAS: **R$ {das:,.2f}**")

    df = pd.DataFrame({
        "Descrição": ["Receita 12 meses", "Folha 12 meses", "Fator R", "Anexo", "Receita mês", "Alíquota", "DAS"],
        "Valor": [receita, folha, f"{fator_r:.2%}", anexo, receita_mes, f"{aliquota*100:.2f}%", das]
    })

    st.dataframe(df)

    # Download do Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Cálculo Simples Nacional")
    st.download_button("📥 Baixar Excel com Relatório", excel_buffer.getvalue(), file_name="SimplesNacional_2025.xlsx")

    # Gráfico Fator R
    fig, ax = plt.subplots()
    ax.bar(["Fator R"], [fator_r], color="green" if fator_r > 0.28 else "red")
    ax.axhline(0.28, color="gray", linestyle="--", label="Limite 28%")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Proporção")
    ax.set_title("Visualização do Fator R")
    st.pyplot(fig)
