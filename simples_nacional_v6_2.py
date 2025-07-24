
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora Simples Nacional 2025", layout="wide")

st.title("📊 Calculadora Simples Nacional 2025")

st.markdown("Simule o cálculo do DAS com base em **Receita Bruta**, **Fator R**, **Anexo** e **retenções legais**.")
st.markdown("Preencha os valores mensais e veja os resultados mês a mês conforme o Simples Nacional atualizado para 2025.")

# Entradas fixas
st.sidebar.header("🔧 Dados Acumulados Anteriores")
rbt12_inicial = st.sidebar.number_input("Receita Bruta dos 12 meses anteriores a Jan/2025 (R$)", min_value=0.0, step=100.0)
folha12_inicial = st.sidebar.number_input("Folha de Pagamento dos 12 meses anteriores a Jan/2025 (R$)", min_value=0.0, step=100.0)

meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# Entrada de dados mês a mês
st.subheader("🧾 Lançamento Mensal")

data = []
for mes in meses:
    with st.expander(f"Mês: {mes}"):
        receita_total = st.number_input(f"{mes} - Receita Bruta Total (R$)", key=f"rt_{mes}", min_value=0.0)
        receita_serv = st.number_input(f"{mes} - Receita de Serviços (R$)", key=f"rs_{mes}", min_value=0.0)
        receita_com = st.number_input(f"{mes} - Receita de Comércio (R$)", key=f"rc_{mes}", min_value=0.0)
        ret_iss = st.selectbox(f"{mes} - Houve retenção de ISS?", ["Não", "Sim"], key=f"ri_{mes}")
        val_iss = st.number_input(f"{mes} - Valor ISS Retido (R$)", key=f"vi_{mes}", min_value=0.0)
        mono = st.selectbox(f"{mes} - Produtos Monofásicos?", ["Não", "Sim"], key=f"pm_{mes}")
        st_field = st.selectbox(f"{mes} - Substituição Tributária?", ["Não", "Sim"], key=f"st_{mes}")
        prolab = st.number_input(f"{mes} - Pró-labore (R$)", key=f"pl_{mes}", min_value=0.0)
        salarios = st.number_input(f"{mes} - Salários pagos (R$)", key=f"sp_{mes}", min_value=0.0)
        inss = st.number_input(f"{mes} - INSS empregado (R$)", key=f"inss_{mes}", min_value=0.0)
        fgts = st.number_input(f"{mes} - FGTS (R$)", key=f"fgts_{mes}", min_value=0.0)
        decimo = st.number_input(f"{mes} - 13º proporcional (R$)", key=f"dec_{mes}", min_value=0.0)

        data.append({
            "Mês": mes,
            "Receita Bruta Total": receita_total,
            "Receita de Serviços": receita_serv,
            "Receita de Comércio": receita_com,
            "Retenção ISS": ret_iss,
            "Valor ISS Retido": val_iss,
            "Monofásico": mono,
            "Substituição Tributária": st_field,
            "Pró-labore": prolab,
            "Salários": salarios,
            "INSS empregado": inss,
            "FGTS": fgts,
            "13º": decimo
        })

# Processamento
st.subheader("📋 Relatório Consolidado")

df = pd.DataFrame(data)
df["Folha Mês"] = df[["Pró-labore", "Salários", "INSS empregado", "FGTS", "13º"]].sum(axis=1)

# Calcular RBT12 e Folha12 acumulados mês a mês
df["RBT12"] = rbt12_inicial + df["Receita Bruta Total"].cumsum()
df["Folha12"] = folha12_inicial + df["Folha Mês"].cumsum()

df["Fator R (%)"] = df.apply(lambda row: round((row["Folha12"] / row["RBT12"] * 100) if row["RBT12"] > 0 else 0, 2), axis=1)
df["Tipo Receita"] = df["Receita de Serviços"].apply(lambda x: "Serviço" if x > 0 else "Comércio")

def aplicar_anexo(row):
    if row["Tipo Receita"] == "Serviço":
        return "III" if row["Fator R (%)"] >= 28 else "V"
    else:
        return "I"

def aliquota(row):
    if row["Tipo Receita"] == "Serviço":
        return 0.06 if row["Fator R (%)"] >= 28 else 0.15
    else:
        return 0.06

df["Anexo"] = df.apply(aplicar_anexo, axis=1)
df["Alíquota (%)"] = df.apply(lambda r: round(aliquota(r) * 100, 2), axis=1)
df["DAS Bruto (R$)"] = df["Receita Bruta Total"] * df["Alíquota (%)"] / 100
df["DAS Final (R$)"] = df.apply(lambda r: r["DAS Bruto (R$)"] - r["Valor ISS Retido"] if r["Retenção ISS"] == "Sim" else r["DAS Bruto (R$)"], axis=1)


# Cálculo de alíquota nominal, dedução e efetiva
faixas = {
    "I": [(180000.00, 0.04, 0.00), (360000.00, 0.073, 5940.00), (720000.00, 0.095, 13860.00),
          (1800000.00, 0.107, 22500.00), (3600000.00, 0.143, 87300.00), (4800000.00, 0.19, 378000.00)],
    "III": [(180000.00, 0.06, 0.00), (360000.00, 0.112, 9360.00), (720000.00, 0.135, 17640.00),
            (1800000.00, 0.16, 35640.00), (3600000.00, 0.21, 125640.00), (4800000.00, 0.33, 648000.00)],
    "V": [(180000.00, 0.15, 0.00), (360000.00, 0.18, 4500.00), (720000.00, 0.195, 9900.00),
          (1800000.00, 0.205, 17100.00), (3600000.00, 0.23, 62100.00), (4800000.00, 0.305, 540000.00)]
}

def obter_aliq_deducao(rbt12, anexo):
    tabela = faixas.get(anexo, [])
    for limite, aliquota, deducao in tabela:
        if rbt12 <= limite:
            return aliquota, deducao
    return tabela[-1][1], tabela[-1][2]

df["Aliq Nominal"], df["Dedução (R$)"] = zip(*df.apply(lambda row: obter_aliq_deducao(row["RBT12"], row["Anexo"]), axis=1))
df["Aliq Efetiva (%)"] = df.apply(lambda r: round(((r["RBT12"] * r["Aliq Nominal"] - r["Dedução (R$)"]) / r["RBT12"]) * 100 if r["RBT12"] > 0 else 0, 2), axis=1)
df["DAS Bruto (R$)"] = df["Receita Bruta Total"] * df["Aliq Efetiva (%)"] / 100
df["DAS Final (R$)"] = df.apply(lambda r: r["DAS Bruto (R$)"] - r["Valor ISS Retido"] if r["Retenção ISS"] == "Sim" else r["DAS Bruto (R$)"], axis=1)

# Exibir tabela final

st.dataframe(df[[
    "Mês", "Receita Bruta Total", "RBT12", "Folha Mês", "Folha12", 
    "Fator R (%)", "Tipo Receita", "Anexo", "Alíquota (%)", 
    "DAS Bruto (R$)", "Valor ISS Retido", "DAS Final (R$)"
]])

# Exportação

import io
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Relatório')

st.download_button(
    label="📥 Baixar Excel com Relatório",
    data=excel_buffer.getvalue(),
    file_name="SimplesNacional_2025.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)



# Geração de PDF com dados dinâmicos
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import io

st.subheader("📄 Exportar Relatório em PDF")

nome_empresa = st.text_input("Nome da Empresa", value="EMPRESA EXEMPLO LTDA")
cnpj_empresa = st.text_input("CNPJ", value="12.345.678/0001-99")
cnaes_empresa = st.text_area("CNAEs Principais", value="33.14-7-99, 25.39-0-01, 43.21-5-00")
responsavel = st.text_input("Responsável Técnico", value="João da Silva - Contador CRC 123456/SP")

if st.button("📤 Gerar PDF do Relatório"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Relatório Consolidado - Simples Nacional 2025", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Empresa:</b> {nome_empresa}", styles["Normal"]))
    story.append(Paragraph(f"<b>CNPJ:</b> {cnpj_empresa}", styles["Normal"]))
    story.append(Paragraph(f"<b>CNAEs Principais:</b> {cnaes_empresa}", styles["Normal"]))
    story.append(Paragraph(f"<b>Data de Geração:</b> {datetime.date.today().strftime('%d/%m/%Y')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Seleção de colunas essenciais
    rel_df = df[[
        "Mês", "Receita Bruta Total", "RBT12", "Folha Mês", "Fator R (%)",
        "Anexo", "Aliq Efetiva (%)", "DAS Final (R$)"
    ]]
    dados = [list(rel_df.columns)] + rel_df.values.tolist()
    tabela = Table(dados, repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
    ]))

    story.append(tabela)
    story.append(Spacer(1, 24))
    story.append(Paragraph("Assinatura do Responsável: ____________________________", styles["Normal"]))
    story.append(Paragraph(responsavel, styles["Italic"]))
    doc.build(story)
    buffer.seek(0)

    st.download_button("📥 Baixar PDF", data=buffer, file_name="Relatorio_SimplesNacional_2025.pdf", mime="application/pdf")


# -----------------------
# 🔍 PAINEL DE AUDITORIA
# -----------------------
st.subheader("🔍 Auditoria de Cálculo - Comparativo Tributário")

# Gerar tabela de auditoria com base no dataframe atual
def gerar_auditoria(df):
    aud = pd.DataFrame()
    aud["Mês"] = df["Mês"]
    aud["Receita Bruta Total"] = df["Receita Bruta Total"]
    aud["RBT12"] = df["RBT12"]
    aud["Folha12"] = df["Folha12"]
    aud["Fator R (%)"] = df["Fator R (%)"]
    aud["Anexo (com Fator R)"] = df["Anexo"]
    aud["Anexo (sem Fator R)"] = df["Anexo"]  # para fins de comparação real, pode ser ajustado
    aud["Aliq Nominal"] = df["Aliq Nominal"]
    aud["Dedução"] = df["Dedução (R$)"]
    aud["Aliq Efetiva (%)"] = df["Aliq Efetiva (%)"]
    aud["DAS c/ Nominal"] = (df["Receita Bruta Total"] * df["Aliq Nominal"]).round(2)
    aud["DAS c/ Efetiva"] = df["DAS Bruto (R$)"].round(2)
    aud["ISS Retido"] = df["Valor ISS Retido"].round(2)
    aud["DAS Final"] = df["DAS Final (R$)"].round(2)
    return aud

auditoria_df = gerar_auditoria(df)
st.dataframe(auditoria_df, use_container_width=True)

# Exportar auditoria
csv_aud = auditoria_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Baixar Auditoria em CSV", data=csv_aud, file_name="auditoria_simples_nacional.csv", mime="text/csv")
