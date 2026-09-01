import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central Financeira", page_icon="💼", layout="wide")

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

# --- ESTILO DAS CAIXAS ---
card_style = """
    background-color: #EBF5FB;
    border: 1px solid #AED6F1;
    border-left: 6px solid #1B4F72;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 15px;
    color: #1C2833;
    box-shadow: 0 4px 6px rgba(0,0,0,0.04);
"""

# Função para gerar barras de progresso HTML personalizadas
def criar_barra_progresso(label, icon, gasto, meta, cor_barra="#1E88E5"):
    pct = min((gasto / meta) * 100, 100.0)
    resta = max(0.0, meta - gasto)
    
    gasto_fmt = f"{gasto:,.2f}".replace(',','_').replace('.',',').replace('_','.')
    meta_fmt = f"{meta:,.2f}".replace(',','_').replace('.',',').replace('_','.')
    resta_fmt = f"{resta:,.2f}".replace(',','_').replace('.',',').replace('_','.')
    
    return f"""
    <div style="margin-top: 12px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-weight: bold; color: #0F2537; font-size: 1rem;">{icon} {label}</span>
            <span style="background-color: {cor_barra}; color: #FFFFFF; padding: 3px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: bold;">{pct:.1f}%</span>
        </div>
        <div style="background-color: #D4E6F1; border-radius: 10px; height: 20px; width: 100%; overflow: hidden; border: 1px solid #AED6F1;">
            <div style="background-color: {cor_barra}; width: {pct:.1f}%; height: 100%; border-radius: 8px;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.88rem; color: #4A5568;">
            <span>Gasto: <b>R$ {gasto_fmt}</b> de R$ {meta_fmt}</span>
            <span>Resta: <b style="color: #1B4F72;">R$ {resta_fmt}</b></span>
        </div>
    </div>
    """

# --- SEÇÃO 1: RESUMO DO CAIXA ---
st.markdown("### 📊 Visão Geral do Mês (Valores em Conta)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style="{card_style}">
        <small style="color: #566573; font-weight: bold;">Entradas (PIX)</small>
        <h2 style="color: #0F2537; margin: 4px 0;">R$ {total_pix:,.2f}</h2>
        <span style="color: #1C2833; font-size: 0.9em;">Dias 05 e 15</span>
    </div>
    """.replace(',','_').replace('.',',').replace('_','.'), unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="{card_style}">
        <small style="color: #566573; font-weight: bold;">Despesas Fixas</small>
        <h2 style="color: #0F2537; margin: 4px 0;">R$ {total_fixas:,.2f}</h2>
        <span style="color: #1C2833; font-size: 0.9em;">Carro (x2) + Mãe</span>
    </div>
    """.replace(',','_').replace('.',',').replace('_','.'), unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="{card_style}">
        <small style="color: #566573; font-weight: bold;">Reserva Essenciais</small>
        <h2 style="color: #0F2537; margin: 4px 0;">R$ {reserva_pix_total:,.2f}</h2>
        <span style="color: #1C2833; font-size: 0.9em;">Valor retido do PIX</span>
    </div>
    """.replace(',','_').replace('.',',').replace('_','.'), unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="{card_style}">
        <small style="color: #566573; font-weight: bold;">Livre p/ Dívidas</small>
        <h2 style="color: #0F2537; margin: 4px 0;">R$ {sobra_total:,.2f}</h2>
        <span style="color: #1C2833; font-size: 0.9em;">Sobra Real no Mês</span>
    </div>
    """.replace(',','_').replace('.',',').replace('_','.'), unsafe_allow_html=True)

st.divider()

# --- SEÇÃO 2: PLANEJAMENTO POR QUINZENA ---
st.markdown("### 📅 O Que Fazer em Cada Pagamento")
col_q1, col_q2 = st.columns(2)

with col_q1:
    st.markdown(f"""
    <div style="{card_style}">
        <h4 style="color: #0F2537; margin-top:0; margin-bottom: 10px;">Ação no Dia 05 (Recebe R$ 2.200)</h4>
        <p style="margin: 4px 0;">1. Pague as Fixas: <b>R$ {fixas_dia5:,.2f}</b></p>
        <p style="margin: 4px 0;">2. Guarde para Essenciais: <b>R$ {reserva_pix_dia5:,.2f}</b></p>
        <hr style="border: 0.5px solid #AED6F1; margin: 8px 0;">
        <p style="margin: 4px 0; font-size: 1.05em;"><b>Sobra no dia 05:</b> R$ {sobra_dia5:,.2f}</p>
    </div>
    """.replace(',','_').replace('.',',').replace('_','.'), unsafe_allow_html=True)

with col_q2:
    st.markdown(f"""
    <div style="{card_style}">
        <h4 style="color: #0F2537; margin-top:0; margin-bottom: 10px;">Ação no Dia 15 (Recebe R$ 1.850)</h4>
        <p style="margin: 4px 0;">1. Pague as Fixas: <b>R$ {fixas_dia15:,.2f}</b></p>
        <p style="margin: 4px 0;">2. Guarde para Essenciais: <b>R$ {reserva_pix_dia15:,.2f}</b></p>
        <hr style="border: 0.5px solid #AED6F1; margin: 8px 0;">
        <p style="margin: 4px 0; font-size: 1.05em;"><b>Sobra no dia 15:</b> R$ {sobra_dia15:,.2f}</p>
    </div>
    """.replace(',','_').replace('.',',').replace('_','.'), unsafe_allow_html=True)

st.divider()

# --- SEÇÃO 3: CONTROLE DO VR E METAS ---
st.markdown("### 💳 Controle de Flash (VR) e Metas")
col_m1, col_m2 = st.columns(2)

gasto_gas = 50.00
gasto_lucca = 89.90

with col_m1:
    st.markdown(f"""
    <div style="{card_style}">
        <h4 style="color: #0F2537; margin-top:0; margin-bottom: 10px;">Visão do Flash (VR)</h4>
        <p style="margin: 6px 0;">• <b>Total Recebido:</b> R$ {vr_total:,.2f}</p>
        <p style="margin: 6px 0;">• <b>Repasse Mãe:</b> R$ {vr_mae:,.2f}</p>
        <p style="margin: 6px 0;">• <b>Seu Saldo Livre (Gasolina/Lucca):</b> R$ {vr_disponivel_livre:,.2f}</p>
    </div>
    """.replace(',','_').replace('.',',').replace('_','.'), unsafe_allow_html=True)

with col_m2:
    html_gas = criar_barra_progresso("Gasolina", "🚗", gasto_gas, meta_gasolina, "#1E88E5")
    html_lucca = criar_barra_progresso("Lucca (Fralda/Leite)", "👶", gasto_lucca, meta_lucca, "#00ACC1")
    
    st.markdown(f"""
    <div style="{card_style}">
        <h4 style="color: #0F2537; margin-top:0; margin-bottom: 8px;">Termômetro de Essenciais</h4>
        {html_gas}
        {html_lucca}
    </div>
    """, unsafe_allow_html=True)
