import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central Financeira", page_icon="💼", layout="wide")

# --- ESTILIZAÇÃO CSS (Azul Claro, Branco e Preto) ---
st.markdown("""
<style>
    /* Estilo do fundo e texto principal */
    .stApp {
        background-color: #F0F8FF; /* Azul bem claro (AliceBlue) */
        color: #000000;
    }
    
    /* Estilo das caixas (Cards) */
    .card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #87CEFA; /* Detalhe em LightSkyBlue */
        margin-bottom: 20px;
    }
    
    .card-title {
        color: #000000;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .card-value {
        color: #000000;
        font-size: 2rem;
        font-weight: bold;
    }
    
    .card-sub {
        color: #555555;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("💼 Painel de Controle - Setembro")

# --- DADOS E METAS (Setembro 2026) ---
# Entradas
pix_dia5 = 2200.00
pix_dia15 = 1850.00
total_pix = pix_dia5 + pix_dia15

# VR Flash Total
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

# --- SEÇÃO 1: RESUMO DO CAIXA (CAIXAS/CARDS) ---
st.markdown("### 📊 Visão Geral do Mês (Valores em Conta)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Entradas (PIX)</div>
        <div class="card-value">R$ {total_pix:,.2f}</div>
        <div class="card-sub">Dias 05 e 15</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Despesas Fixas</div>
        <div class="card-value">R$ {total_fixas:,.2f}</div>
        <div class="card-sub">Carro (x2) + Mãe</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Reserva Essenciais</div>
        <div class="card-value">R$ {reserva_pix_total:,.2f}</div>
        <div class="card-sub">Valor retido do PIX</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="border-left: 5px solid #000000;">
        <div class="card-title">Livre p/ Dívidas</div>
        <div class="card-value">R$ {sobra_total:,.2f}</div>
        <div class="card-sub">Sobra Real no Mês</div>
    </div>
    """, unsafe_allow_html=True)

# --- SEÇÃO 2: PLANEJAMENTO POR QUINZENA ---
st.markdown("### 📅 O Que Fazer em Cada Pagamento")
col_q1, col_q2 = st.columns(2)

with col_q1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Ação no Dia 05 (Recebe R$ 2.200)</div>
        <p>1. Pague as Fixas: <b>R$ {fixas_dia5:,.2f}</b></p>
        <p>2. Guarde para Essenciais: <b>R$ {reserva_pix_dia5:,.2f}</b></p>
        <hr>
        <p><b>Sobra no dia 05:</b> R$ {sobra_dia5:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col_q2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Ação no Dia 15 (Recebe R$ 1.850)</div>
        <p>1. Pague as Fixas: <b>R$ {fixas_dia15:,.2f}</b></p>
        <p>2. Guarde para Essenciais: <b>R$ {reserva_pix_dia15:,.2f}</b></p>
        <hr>
        <p><b>Sobra no dia 15:</b> R$ {sobra_dia15:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# --- SEÇÃO 3: CONTROLE DO VR E METAS ---
st.markdown("### 💳 Controle de Flash (VR) e Metas")
col_m1, col_m2 = st.columns(2)

# Simulando dados da planilha
gastos_registrados = pd.DataFrame({
    'Descrição': ['Gasolina', 'Fraldas'],
    'Valor (R$)': [50.00, 89.90]
})
gasto_gas = 50.00
gasto_lucca = 89.90

with col_m1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Visão do Flash (VR)</div>
        <p><b>Total Recebido:</b> R$ {vr_total:,.2f}</p>
        <p><b>Repasse Mãe:</b> R$ {vr_mae:,.2f}</p>
        <p><b>Seu Saldo Livre (Gasolina/Lucca):</b> R$ {vr_disponivel_livre:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Termômetro de Essenciais</div>", unsafe_allow_html=True)
    
    st.markdown("**🚗 Gasolina**")
    st.progress(min(gasto_gas / meta_gasolina, 1.0))
    st.caption(f"Gasto: R$ {gasto_gas:.2f} de R$ {meta_gasolina:.2f} | **Resta: R$ {meta_gasolina - gasto_gas:.2f}**")
    
    st.markdown("**👶 Lucca (Fralda/Leite)**")
    st.progress(min(gasto_lucca / meta_lucca, 1.0))
    st.caption(f"Gasto: R$ {gasto_lucca:.2f} de R$ {meta_lucca:.2f} | **Resta: R$ {meta_lucca - gasto_lucca:.2f}**")
    st.markdown('</div>', unsafe_allow_html=True)
