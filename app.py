import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Controle Pessoal - Chefe", page_icon="📊", layout="wide")
st.title("📊 Painel de Controle Financeiro")
st.write("Bem-vindo ao seu assistente financeiro pessoal.")

# --- 2. DADOS SIMULADOS (Em breve conectaremos direto no Google Sheets) ---
# Aqui o app vai ler a sua planilha. Por enquanto, coloquei os dados que temos hoje.
mes_atual = datetime.now().month
ano_atual = datetime.now().year

gastos_registrados = pd.DataFrame({
    'Data': ['01/09/2026', '01/09/2026'],
    'Tipo': ['VR (Flash)', 'VR (Flash)'],
    'Descrição': ['Gasolina', 'Fraldas'],
    'Valor (R$)': [50.00, 89.90]
})

# --- 3. REGRAS DE NEGÓCIO E LIMITES ---
# Entradas
entradas_pix = 4050.00  # 2200 (dia 05) + 1850 (dia 15)
vr_total = 682.50
vr_mae = 500.00
vr_disponivel = vr_total - vr_mae # R$ 182.50

# Regra do Carro (Setembro vs Outros Meses)
if mes_atual == 9 and ano_atual == 2026:
    custo_carro = 2600.00 # Agosto atrasado + Setembro
    st.info("⚠️ Aviso: Regra de Setembro ativada (2 parcelas do carro incluídas no cálculo).")
else:
    custo_carro = 1300.00 # Mês normal

custo_mae = 500.00 # 250 (dia 05) + 250 (dia 15)
total_fixas = custo_carro + custo_mae

# Metas Essenciais
meta_gasolina = 400.00
meta_lucca = 480.00 # Fralda 320 + Leite 160

# --- 4. CÁLCULOS DE GASTOS REAIS ---
gasto_gasolina = gastos_registrados[gastos_registrados['Descrição'] == 'Gasolina']['Valor (R$)'].sum()
gasto_lucca = gastos_registrados[gastos_registrados['Descrição'].isin(['Fraldas', 'Leite'])]['Valor (R$)'].sum()
gasto_vr = gastos_registrados[gastos_registrados['Tipo'] == 'VR (Flash)']['Valor (R$)'].sum()

# O que falta gastar das metas (que vai sair do PIX)
falta_gasolina = max(0, meta_gasolina - gasto_gasolina)
falta_lucca = max(0, meta_lucca - gasto_lucca)
reserva_necessaria_pix = (falta_gasolina + falta_lucca) - max(0, vr_disponivel - gasto_vr)

# O Grande Cálculo do Dinheiro Livre
dinheiro_livre = entradas_pix - total_fixas - reserva_necessaria_pix

# --- 5. INTERFACE VISUAL (DASHBOARD) ---
st.markdown("### 💰 Resumo do Caixa (Dinheiro Real)")
col1, col2, col3 = st.columns(3)
col1.metric("Entradas (PIX)", f"R$ {entradas_pix:,.2f}".replace(',','_').replace('.',',').replace('_','.'))
col2.metric("Despesas Fixas", f"R$ {total_fixas:,.2f}".replace(',','_').replace('.',',').replace('_','.'))
col3.metric("Livre para Dívidas", f"R$ {dinheiro_livre:,.2f}".replace(',','_').replace('.',',').replace('_','.'), help="Valor já descontando o carro, a mãe e as metas que faltam de gasolina e bebê.")

st.divider()

st.markdown("### 🎯 Termômetro de Metas Essenciais")
col_g1, col_g2, col_g3 = st.columns(3)

with col_g1:
    st.markdown("**🚗 Gasolina (Meta: R$ 400)**")
    progresso_gas = min(gasto_gasolina / meta_gasolina, 1.0)
    st.progress(progresso_gas)
    st.caption(f"Gasto: R$ {gasto_gasolina:.2f} | Resta: R$ {meta_gasolina - gasto_gasolina:.2f}")

with col_g2:
    st.markdown("**👶 Lucca (Fralda/Leite - Meta: R$ 480)**")
    progresso_lucca = min(gasto_lucca / meta_lucca, 1.0)
    st.progress(progresso_lucca)
    st.caption(f"Gasto: R$ {gasto_lucca:.2f} | Resta: R$ {meta_lucca - gasto_lucca:.2f}")

with col_g3:
    st.markdown("**💳 VR Flash (Limite: R$ 182,50)**")
    progresso_vr = min(gasto_vr / vr_disponivel, 1.0)
    st.progress(progresso_vr)
    st.caption(f"Gasto: R$ {gasto_vr:.2f} | Resta: R$ {vr_disponivel - gasto_vr:.2f}")

st.divider()
st.markdown("*(Nota do Assistente: No próximo passo, vamos conectar este painel direto na sua Planilha do Google para ele ler seus gastos automaticamente!)*")
