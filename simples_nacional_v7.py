
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

st.set_page_config(
    page_title="Simples Nacional 2025 - Brandão Contabilidade",
    page_icon="💼",
    layout="wide"
)

# Logo
st.image("logo_brandao.png", width=160)

# Título
st.title("Simulador e Auditoria - Simples Nacional 2025")
st.markdown("Calcule de forma prática e segura o DAS, Fator R, comparativos entre anexos e retenções aplicáveis.")

# Entradas - Receita
st.sidebar.header("📌 Receita Bruta")
receita_12m = st.sidebar.number_input("Receita Bruta acumulada (últimos 12 meses)", 0.0, format="%.2f")
receita_mes = st.sidebar.number_input("Receita Bruta do mês atual", 0.0, format="%.2f")

# Entradas - Folha
st.sidebar.header("📌 Folha de Pagamento")
salarios = st.sidebar.number_input("Salários pagos no mês", 0.0, format="%.2f")
fgts = st.sidebar.number_input("FGTS do mês", 0.0, format="%.2f")
decimo = st.sidebar.number_input("13º proporcional", 0.0, format="%.2f")

# Cálculos
folha_total = salarios + fgts + decimo
fator_r = folha_total / receita_12m if receita_12m > 0 else 0
anexo = "III" if fator_r >= 0.28 else "V"
aliquota = 0.06 if anexo == "III" else 0.15
das_estimado = receita_mes * aliquota

# Apresentação
col1, col2, col3 = st.columns(3)
col1.metric("Fator R", f"{fator_r:.2%}")
col2.metric("Anexo aplicável", f"Anexo {anexo}")
col3.metric("DAS estimado", f"R$ {das_estimado:,.2f}")

# Comparativo
st.markdown("### 📊 Comparativo entre Anexo III e V")
st.write(f"🔹 Anexo III (6%): R$ {receita_mes * 0.06:,.2f}")
st.write(f"🔸 Anexo V (15%): R$ {receita_mes * 0.15:,.2f}")

if fator_r >= 0.28:
    st.success("✅ Aplicado Anexo III com base no Fator R.")
else:
    st.warning("⚠️ Aplicado Anexo V. Fator R abaixo de 28%.")

# Gráfico - Histórico simulado
st.markdown("### 📈 Histórico simulado do Fator R")
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
valores_simulados = np.clip(np.random.normal(fator_r, 0.03, 12), 0, 1)

fig, ax = plt.subplots()
ax.plot(meses, valores_simulados, marker='o', color='blue')
ax.axhline(0.28, color='red', linestyle='--', label='Limite 28%')
ax.set_ylim(0, 1)
ax.set_ylabel("Fator R")
ax.legend()
st.pyplot(fig)

# Rodapé com string multilinha segura
rodape = """**Brandão Contabilidade**  
📍 Rua Santa Catarina, 1010 - Centro - Sidrolândia - MS  
📧 adm@brandaocontador.com.br  
📞 (67) 3272-3266 / (67) 99601-1356"""
st.markdown(rodape)
st.markdown("[💬 Fale conosco no WhatsApp](https://wa.me/5567996011356)")
