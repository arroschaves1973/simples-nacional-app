
import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime

st.set_page_config(
    page_title="Simples Nacional 2025 - Brandão Contabilidade",
    page_icon="💼",
    layout="wide"
)

# Logo e título
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.image("logo_brandao.png", width=160)
with col_titulo:
    st.title("Simulador Simples Nacional 2025")
    st.markdown("**Cálculo detalhado com Fator R, folha de pagamento, retenções e auditoria**")

st.markdown("---")
st.sidebar.header("📌 Receita e Retenção")

receita_12m = st.sidebar.number_input("Receita Bruta dos últimos 12 meses (R$)", min_value=0.0, format="%.2f")
receita_mes = st.sidebar.number_input("Receita Bruta do mês atual (R$)", min_value=0.0, format="%.2f")

retencao_iss = st.sidebar.checkbox("Houve retenção de ISS?")
valor_retido = st.sidebar.number_input("Valor retido de ISS (R$)", min_value=0.0, format="%.2f") if retencao_iss else 0.0

st.sidebar.header("📌 Folha de Pagamento (últimos 12 meses)")
salarios = st.sidebar.number_input("Salários pagos (R$)", min_value=0.0, format="%.2f")
fgts = st.sidebar.number_input("FGTS recolhido (R$)", min_value=0.0, format="%.2f")
inss = st.sidebar.number_input("INSS descontado dos empregados (R$)", min_value=0.0, format="%.2f")
decimo_terceiro = st.sidebar.number_input("13º salário proporcional (R$)", min_value=0.0, format="%.2f")

folha_total = salarios + fgts + decimo_terceiro

fator_r = folha_total / receita_12m if receita_12m > 0 else 0
anexo = "Anexo III" if fator_r >= 0.28 else "Anexo V"
aliquota = 0.06 if anexo == "Anexo III" else 0.15
das = receita_mes * aliquota - valor_retido

# Visualização
col1, col2, col3 = st.columns(3)
col1.metric("📊 Fator R", f"{fator_r:.2%}")
col2.metric("📑 Anexo Aplicável", anexo)
col3.metric("💰 DAS Estimado", f"R$ {das:,.2f}")

st.markdown("### 📋 Relatório Detalhado")
df = pd.DataFrame({
    "Descrição": [
        "Receita bruta 12 meses", "Salários", "FGTS", "13º proporcional",
        "Folha considerada (R$)", "Fator R", "Anexo", "Alíquota", "Receita mês",
        "Retenção de ISS", "DAS estimado"
    ],
    "Valor": [
        receita_12m, salarios, fgts, decimo_terceiro, folha_total,
        f"{fator_r:.2%}", anexo, f"{aliquota*100:.2f}%", receita_mes,
        f"R$ {valor_retido:,.2f}" if retencao_iss else "Não houve",
        f"R$ {das:,.2f}"
    ]
})
st.dataframe(df, use_container_width=True)

# Excel download
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Auditoria")
st.download_button("📥 Baixar Excel com Auditoria", excel_buffer.getvalue(), file_name="Auditoria_SimplesNacional.xlsx")

# Gráfico do Fator R
st.markdown("### 📈 Gráfico do Fator R")
fig, ax = plt.subplots()
ax.bar(["Fator R"], [fator_r], color="green" if fator_r >= 0.28 else "red")
ax.axhline(0.28, color="gray", linestyle="--", label="Limite 28%")
ax.set_ylim(0, 1)
ax.set_ylabel("Proporção")
ax.legend()
st.pyplot(fig)

# Rodapé
st.markdown("---")
st.markdown("**Brandão Contabilidade**  
📍 Rua Santa Catarina, 1010 - Centro - Sidrolândia - MS  
📧 adm@brandaocontador.com.br  
📞 (67) 3272-3266 / (67) 99601-1356")
st.markdown("[💬 Fale conosco no WhatsApp](https://wa.me/5567996011356)")
