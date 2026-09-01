import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central Financeira", page_icon="💼", layout="wide")

# --- ESTILIZAÇÃO CSS (Azul Claro, Branco e Preto) ---
st.markdown("""
<style>
    /* Estilo do fundo da página */
    .stApp {
        background-color: #F0F8FF; /* Azul bem claro */
        color: #000000;
    }
    
    /* Estilização nativa dos Containers (Caixas/Cards) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #E0E0E0 !important;
        border-left: 6px solid #87CEFA !important; /* Borda lateral azul claro */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        padding: 15px !important;
    }

    /* Ajuste de cor de títulos e textos */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #000000 !important;
    }

    /* Customização da Barra de Progresso */
    .stProgress > div > div > div > div {
        background-color: #1E90FF !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("💼 Painel de Controle - Setembro")

# --- DADOS E METAS (Setembro 2026) ---
pix_dia5 = 2200.00
pix_dia15 = 1850.00
total_pix = pix_dia5 + pix_dia15

vr_total = 682.50
vr_mae = 500.00
vr_disponivel_livre = vr_total - vr_mae

# Fixas (Regra de Setembro: Carro dobrado)
fixas_dia5 = 250.00 + 1300.00 # Mãe + Carro Agosto
fixas_dia15 = 250.00 + 1300.00 # Mãe + Carro Setembro
total_fixas = fixas_dia5 + fixas_dia15

# Reservas Essenciais (Gasto em PIX)
meta_gasolina = 400.00
meta_lucca = 480.00
reserva_pix_total = (meta_gasolina + meta_lucca) - vr_disponivel_livre
reserva_pix_dia5 = 450.00
reserva_pix_dia15 = reserva_pix_total - reserva_pix_dia5

# Sobra Livre
sobra_dia5 = pix_dia5 - fixas_dia5 - reserva_pix_dia5
sobra_dia15 = pix_dia15 - fixas_dia15 - reserva_pix_dia15
sobra_total = sobra_dia5 + sobra_dia15

# --- SEÇÃO 1: RESUMO DO CAIXA ---
st.markdown("### 📊 Visão Geral do Mês (Valores em Conta)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.caption("Entradas (PIX)")
        st.subheader(f"R$ {total_pix:,.2f}".replace(',','_').replace('.',',').replace('_','.'))
        st.write("Dias 05 e 15")

with col2:
    with st.container(border=True):
        st.caption("Despesas Fixas")
        st.subheader(f"R$ {total_fixas:,.2f}".replace(',','_').replace('.',',').replace('_','.'))
        st.write("Carro (x2) + Mãe")

with col3:
    with st.container(border=True):
        st.caption("Reserva Essenciais")
        st.subheader(f"R$ {reserva_pix_total:,.2f}".replace(',','_').replace('.',',').replace('_','.'))
        st.write("Valor retido do PIX")

with col4:
    with st.container(border=True):
        st.caption("Livre p/ Dívidas")
        st.subheader(f"R$ {sobra_total:,.2f}".replace(',','_').replace('.',',').replace('_','.'))
        st.write("Sobra Real no Mês")

st.divider()

# --- SEÇÃO 2: PLANEJAMENTO POR QUINZENA ---
st.markdown("### 📅 O Que Fazer em Cada Pagamento")
col_q1, col_q2 = st.columns(2)

with col_q1:
    with st.container(border=True):
        st.markdown("#### Ação no Dia 05 (Recebe R$ 2.200)")
        st.write(f"1. Pague as Fixas: **R$ {fixas_dia5:,.2f}**")
        st.write(f"2. Guarde para Essenciais: **R$ {reserva_pix_dia5:,.2f}**")
        st.divider()
        st.write(f"**Sobra no dia 05:** R$ {sobra_dia5:,.2f}")

with col_q2:
    with st.container(border=True):
        st.markdown("#### Ação no Dia 15 (Recebe R$ 1.850)")
        st.write(f"1. Pague as Fixas: **R$ {fixas_dia15:,.2f}**")
        st.write(f"2. Guarde para Essenciais: **R$ {reserva_pix_dia15:,.2f}**")
        st.divider()
        st.write(f"**Sobra no dia 15:** R$ {sobra_dia15:,.2f}")

st.divider()

# --- SEÇÃO 3: CONTROLE DO VR E METAS ---
st.markdown("### 💳 Controle de Flash (VR) e Metas")
col_m1, col_m2 = st.columns(2)

gasto_gas = 50.00
gasto_lucca = 89.90

with col_m1:
    with st.container(border=True):
        st.markdown("#### Visão do Flash (VR)")
        st.write(f"• **Total Recebido:** R$ {vr_total:,.2f}")
        st.write(f"• **Repasse Mãe:** R$ {vr_mae:,.2f}")
        st.write(f"• **Seu Saldo Livre (Gasolina/Lucca):** R$ {vr_disponivel_livre:,.2f}")

with col_m2:
    with st.container(border=True):
        st.markdown("#### Termômetro de Essenciais")
        
        st.markdown("**🚗 Gasolina**")
        st.progress(min(gasto_gas / meta_gasolina, 1.0))
        st.caption(f"Gasto: R$ {gasto_gas:.2f} de R$ {meta_gasolina:.2f} | **Resta: R$ {meta_gasolina - gasto_gas:.2f}**")
        
        st.markdown("**👶 Lucca (Fralda/Leite)**")
        st.progress(min(gasto_lucca / meta_lucca, 1.0))
        st.caption(f"Gasto: R$ {gasto_lucca:.2f} de R$ {meta_lucca:.2f} | **Resta: R$ {meta_lucca - gasto_lucca:.2f}**")
