
import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image

st.set_page_config(page_title="Simples Nacional 2025 - Brandão Contabilidade", layout="wide")

col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo_brandao.png", width=180)
with col2:
    st.title("Simples Nacional 2025")
    st.markdown("### Brandão Contabilidade | Simulador com auditoria, retenções e Fator R")

st.markdown("---")

st.sidebar.header("📌 Dados de Entrada")
receita_12m = st.sidebar.number_input("Receita bruta acumulada (últimos 12 meses)", min_value=0.0, format="%.2f")
folha_12m = st.sidebar.number_input("Folha de pagamento acumulada (últimos 12 meses)", min_value=0.0, format="%.2f")
receita_mes = st.sidebar.number_input("Receita bruta do mês atual", min_value=0.0, format="%.2f")
retencao_iss = st.sidebar.checkbox("Houve retenção de ISS no mês?")
valor_retido = 0.0
if retencao_iss:
    valor_retido = st.sidebar.number_input("Valor retido de ISS", min_value=0.0, format="%.2f")

fator_r = folha_12m / receita_12m if receita_12m > 0 else 0
anexo = "Anexo III" if fator_r >= 0.28 else "Anexo V"
aliquota = 0.06 if anexo == "Anexo III" else 0.15
das = receita_mes * aliquota - valor_retido

st.markdown("### 🧮 Resultado do Cálculo")
col1, col2, col3 = st.columns(3)
col1.metric("Fator R", f"{fator_r:.2%}")
col2.metric("Anexo aplicável", anexo)
col3.metric("DAS estimado", f"R$ {das:,.2f}")

st.markdown("### 📊 Gráfico - Comparação do Fator R")
fig, ax = plt.subplots()
ax.bar(["Fator R"], [fator_r], color="green" if fator_r >= 0.28 else "red")
ax.axhline(0.28, color="gray", linestyle="--", label="Limite Anexo III")
ax.set_ylim(0, 1)
ax.set_title("Fator R")
st.pyplot(fig)

st.markdown("### 📋 Auditoria do Cálculo")
df = pd.DataFrame({
    "Descrição": [
        "Receita bruta 12 meses", "Folha 12 meses", "Fator R",
        "Anexo aplicável", "Alíquota", "Receita mês atual",
        "Retenção ISS", "DAS estimado"
    ],
    "Valor": [
        receita_12m, folha_12m, f"{fator_r:.2%}",
        anexo, f"{aliquota*100:.2f}%", receita_mes,
        f"R$ {valor_retido:,.2f}" if retencao_iss else "Não houve",
        f"R$ {das:,.2f}"
    ]
})

st.dataframe(df)

# Gerar Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name="Auditoria")
st.download_button("📥 Baixar Excel", excel_buffer.getvalue(), file_name="Relatorio_Simples_Nacional.xlsx")

# Logo e contato no final
st.markdown("---")
st.markdown("#### Brandão Contabilidade")
st.markdown("📍 Rua Santa Catarina, 1010 - Centro - Sidrolândia - MS")
st.markdown("📧 adm@brandaocontador.com.br | 📞 (67) 3272-3266 / (67) 99601-1356")
st.markdown("[💬 Fale conosco no WhatsApp](https://wa.me/5567996011356)")
