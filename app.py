import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central Financeira", page_icon="💼", layout="wide")
st.title("💼 Central Financeira Pessoal")

# --- DADOS E METAS MENSAL ---
mes_atual = datetime.now().month
ano_atual = datetime.now().year

# Entradas Previstas
pix_dia5 = 2200.00
pix_dia15 = 1850.00
total_pix = pix_dia5 + pix_dia15

vr_total = 682.50
vr_mae = 500.00
vr_disponivel = vr_total - vr_mae # R$ 182,50

# Regra de Contas Fixas
if mes_atual == 9 and ano_atual == 2026:
    fixas_dia5 = 1550.00 # Mãe R$ 250 + Carro (Agosto) R$ 1.300
    fixas_dia15 = 1550.00 # Mãe R$ 250 + Carro (Setembro) R$ 1.300
    st.info("⚠️ **Regra de Setembro Ativa:** Pagamento de 2 parcelas do carro (Agosto em atraso + Setembro).")
else:
    fixas_dia5 = 250.00
    fixas_dia15 = 1550.00

total_fixas = fixas_dia5 + fixas_dia15

# Metas Essenciais
meta_gasolina = 400.00
meta_lucca = 480.00 # Fralda R$ 320 + Leite R$ 160
total_essenciais = meta_gasolina + meta_lucca # R$ 880,00

# Quanto do essenciais precisa ser pago via PIX (descontando o VR livre)
reserva_pix_total = total_essenciais - vr_disponivel # R$ 697,50

# Divisão Sugerida de Reserva por Quinzena
reserva_pix_dia5 = 450.00
reserva_pix_dia15 = reserva_pix_total - reserva_pix_dia5 # R$ 247,50

# Sobras por Quinzena pós Fixas e Reservas Essenciais
sobra_dia5 = pix_dia5 - fixas_dia5 - reserva_pix_dia5 # R$ 200,00
sobra_dia15 = pix_dia15 - fixas_dia15 - reserva_pix_dia15 # R$ 52,50
sobra_total_mes = sobra_dia5 + sobra_dia15 # R$ 252,50

# --- PAINEL PRINCIPAL ---
st.markdown("### 📊 Visão Geral de Setembro")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Entradas (PIX)", f"R$ {total_pix:,.2f}".replace(',','_').replace('.',',').replace('_','.'))
c2.metric("Contas Fixas", f"R$ {total_fixas:,.2f}".replace(',','_').replace('.',',').replace('_','.'))
c3.metric("Reserva Essenciais (PIX)", f"R$ {reserva_pix_total:,.2f}".replace(',','_').replace('.',',').replace('_','.'))
c4.metric("Sobra Livre p/ Dívidas", f"R$ {sobra_total_mes:,.2f}".replace(',','_').replace('.',',').replace('_','.'), delta="Livre no Mês")

st.divider()

# --- BLOCO DE RESERVAS ESSENCIAIS ---
st.markdown("### 🛒 Planejamento de Reservas Essenciais")
st.write("Valores exatos que você precisa carimbar/separar para **Gasolina, Fraldas e Leite** em cada pagamento:")

col_res1, col_res2, col_res3 = st.columns(3)

with col_res1:
    st.subheader("🎯 Metas do Mês")
    st.write(f"• **Gasolina:** R$ {meta_gasolina:.2f}")
    st.write(f"• **Lucca (Fraldas + Leite):** R$ {meta_lucca:.2f}")
    st.write(f"• **Total Essencial:** R$ {total_essenciais:.2f}")
    st.caption(f"💡 R$ {vr_disponivel:.2f} é coberto pelo VR Flash. Os outros R$ {reserva_pix_total:.2f} saem do PIX.")

with col_res2:
    st.subheader("📅 Reserva no Dia 05")
    st.metric("Guardar do Pagamento 05", f"R$ {reserva_pix_dia5:.2f}")
    st.write(f"• Entram: R$ {pix_dia5:.2f}")
    st.write(f"• Paga Fixas (Carro+Mãe): R$ {fixas_dia5:.2f}")
    st.write(f"• **Sobra Livre no Dia 05:** R$ {sobra_dia5:.2f}")

with col_res3:
    st.subheader("📅 Reserva no Dia 15")
    st.metric("Guardar do Adiantamento 15", f"R$ {reserva_pix_dia15:.2f}")
    st.write(f"• Entram: R$ {pix_dia15:.2f}")
    st.write(f"• Paga Fixas (Carro+Mãe): R$ {fixas_dia15:.2f}")
    st.write(f"• **Sobra Livre no Dia 15:** R$ {sobra_dia15:.2f}")

st.divider()

# --- TERMÔMETRO DE GASTOS REALIZADOS ---
st.markdown("### 📉 Acompanhamento em Tempo Real")
# Simulando dados da planilha
gastos_registrados = pd.DataFrame({
    'Data': ['01/09/2026', '01/09/2026'],
    'Tipo': ['VR (Flash)', 'VR (Flash)'],
    'Descrição': ['Gasolina', 'Fraldas'],
    'Valor (R$)': [50.00, 89.90]
})

gasto_gas = gastos_registrados[gastos_registrados['Descrição'] == 'Gasolina']['Valor (R$)'].sum()
gasto_lucca = gastos_registrados[gastos_registrados['Descrição'].isin(['Fraldas', 'Leite'])]['Valor (R$)'].sum()

g1, g2 = st.columns(2)
with g1:
    st.markdown("**🚗 Gasolina**")
    st.progress(min(gasto_gas / meta_gasolina, 1.0))
    st.caption(f"Gasto: R$ {gasto_gas:.2f} de R$ {meta_gasolina:.2f} | **Resta: R$ {meta_gasolina - gasto_gas:.2f}**")

with g2:
    st.markdown("**👶 Lucca (Fralda/Leite)**")
    st.progress(min(gasto_lucca / meta_lucca, 1.0))
    st.caption(f"Gasto: R$ {gasto_lucca:.2f} de R$ {meta_lucca:.2f} | **Resta: R$ {meta_lucca - gasto_lucca:.2f}**")
