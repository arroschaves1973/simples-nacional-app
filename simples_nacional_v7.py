
import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from PIL import Image

st.set_page_config(
    page_title="Simples Nacional 2025 - Brandão Contabilidade",
    page_icon="💼",
    layout="wide"
)

st.image("logo_brandao.png", width=160)
st.title("Simulador e Auditoria - Simples Nacional 2025")
st.markdown("Cálculo com Fator R, comparativo entre anexos, retenções e análise de tendência.")

st.sidebar.header("📌 Dados da Receita")
receita_12m = st.sidebar.number_input("Receita Bruta últimos 12 meses (R$)", 0.0, format="%.2f")
receita_mes = st.sidebar.number_input("Receita do mês atual (R$)", 0.0, format="%.2f")

st.sidebar.header("📌 Folha de Pagamento")
salarios = st.sidebar.number_input("Salários pagos (R$)", 0.0, format="%.2f")
fgts = st.sidebar.number_input("FGTS (R$)", 0.0, format="%.2f")
decimo = st.sidebar.number_input("13º proporcional (R$)", 0.0, format="%.2f")
folha_total = salarios + fgts + decimo

fator_r = folha_total / receita_12m if receita_12m > 0 else 0
anexo_atual = "Anexo III" if fator_r >= 0.28 else "Anexo V"
aliquota_iii = 0.06
aliquota_v = 0.15
das_iii = receita_mes * aliquota_iii
das_v = receita_mes * aliquota_v
das_final = das_iii if fator_r >= 0.28 else das_v

# Cards comparativos
col1, col2, col3 = st.columns(3)
col1.metric("Fator R", f"{fator_r:.2%}")
col2.metric("Anexo Atual", anexo_atual)
col3.metric("DAS Estimado", f"R$ {das_final:,.2f}")

# Comparativo entre Anexos
st.markdown("### ⚖️ Comparativo entre Anexo III e V")
st.write(f"🔹 **Anexo III (6%)** → DAS: R$ {das_iii:,.2f}")
st.write(f"🔸 **Anexo V (15%)** → DAS: R$ {das_v:,.2f}")

if fator_r < 0.28:
    st.warning("⚠️ Fator R abaixo de 28%. Considerado Anexo V.")
else:
    st.success("✅ Fator R acima de 28%. Aplicado Anexo III.")

# Histórico visual (simulado para exemplo)
st.markdown("### 📈 Evolução do Fator R (simulação)")
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
valores_fator = np.clip(np.random.normal(fator_r, 0.04, 12), 0, 1)

fig, ax = plt.subplots()
ax.plot(meses, valores_fator, marker='o')
ax.axhline(0.28, color='gray', linestyle='--', label='Limite 28%')
ax.set_ylabel("Fator R")
ax.set_ylim(0, 1)
ax.legend()
st.pyplot(fig)

# Rodapé
st.markdown("---")
st.markdown("**Brandão Contabilidade**  
📍 Rua Santa Catarina, 1010 - Centro - Sidrolândia - MS  
📧 adm@brandaocontador.com.br  
📞 (67) 3272-3266 / (67) 99601-1356")
st.markdown("[💬 WhatsApp](https://wa.me/5567996011356)")
