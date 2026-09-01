import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central Financeira", page_icon="💼", layout="wide")

st.title("💼 Painel de Controle - Setembro")

# --- FUNÇÕES DE TRATAMENTO DE DADOS ---
def limpar_valor(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).replace('R$', '').replace(' ', '').replace('\xa0', '').strip()
    if not s:
        return 0.0
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except:
        return 0.0

def fmt_brl(valor):
    try:
        val = float(valor)
        return f"R$ {val:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
    except:
        return "R$ 0,00"

# --- CONEXÃO COM A PLANILHA DO GOOGLE ---
SHEET_ID = "1Y7EsUDd9J_liLwwTbRdjM2lM_XcdsWr_kYNUC-MAZsY"

def carregar_aba(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
    return pd.read_csv(url)

try:
    df_entradas = carregar_aba("Entradas Agosto")
    df_fixas = carregar_aba("Dividas Fixas")
    df_gastos = carregar_aba("Gastos Setembro")
except Exception as e:
    st.error("⚠️ Não foi possível ler a planilha. Verifique se o compartilhamento está como 'Qualquer pessoa com o link'.")
    st.stop()

# --- PROCESSAMENTO AUTOMÁTICO DE DADOS ---
# Processar Entradas em Dinheiro (PIX)
try:
    col_valor_ent = [c for c in df_entradas.columns if 'Receber' in c or 'Valor' in c][0]
    col_tipo_ent = [c for c in df_entradas.columns if 'Tipo' in c or 'Recebimento' in c][0]
    df_entradas['Valor_Clean'] = df_entradas[col_valor_ent].apply(limpar_valor)
    
    # Entradas PIX
    pix_rows = df_entradas[~df_entradas[col_tipo_ent].astype(str).str.contains('VR', case=False, na=False)]
    total_pix = pix_rows['Valor_Clean'].sum()
    if total_pix == 0:
        total_pix = 4050.00
except:
    total_pix = 4050.00

# VR / Flash
vr_total = 682.50
vr_mae = 500.00
vr_disponivel_livre = vr_total - vr_mae

# Processar Gastos da Aba 'Gastos Setembro'
try:
    col_desc_gastos = [c for c in df_gastos.columns if 'Descrição' in c or 'Gasto' in c or 'Tipo' in c][0]
    col_valor_gastos = [c for c in df_gastos.columns if 'Valor' in c][0]
    df_gastos['Valor_Clean'] = df_gastos[col_valor_gastos].apply(limpar_valor)
    
    gasto_gas = df_gastos[df_gastos[col_desc_gastos].astype(str).str.contains('Gasolina', case=False, na=False)]['Valor_Clean'].sum()
    gasto_lucca = df_gastos[df_gastos[col_desc_gastos].astype(str).str.contains('Fralda|Leite', case=False, na=False)]['Valor_Clean'].sum()
except:
    gasto_gas = 50.00
    gasto_lucca = 89.90

# Regras de Setembro (Fixas)
fixas_dia5 = 250.00 + 1300.00
fixas_dia15 = 250.00 + 1300.00
total_fixas = fixas_dia5 + fixas_dia15

# Metas Essenciais
meta_gasolina = 400.00
meta_lucca = 480.00
reserva_pix_total = (meta_gasolina + meta_lucca) - vr_disponivel_livre
reserva_pix_dia5 = 450.00
reserva_pix_dia15 = reserva_pix_total - reserva_pix_dia5

# Sobra Livre
sobra_dia5 = 2200.00 - fixas_dia5 - reserva_pix_dia5
sobra_dia15 = 1850.00 - fixas_dia15 - reserva_pix_dia15
sobra_total = sobra_dia5 + sobra_dia15

# --- ESTILO DAS CAIXAS ---
card_style = "background-color: #EBF5FB; border: 1px solid #AED6F1; border-left: 6px solid #1B4F72; border-radius: 12px; padding: 18px; margin-bottom: 15px; color: #1C2833; box-shadow: 0 4px 6px rgba(0,0,0,0.04);"

def criar_barra_progresso(label, icon, gasto, meta, cor_barra="#1E88E5"):
    pct = min((gasto / meta) * 100, 100.0) if meta > 0 else 0
    resta = max(0.0, meta - gasto)
    gasto_fmt = fmt_brl(gasto)
    meta_fmt = fmt_brl(meta)
    resta_fmt = fmt_brl(resta)
    
    return f'<div style="margin-top: 12px; margin-bottom: 16px;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;"><span style="font-weight: bold; color: #0F2537; font-size: 1rem;">{icon} {label}</span><span style="background-color: {cor_barra}; color: #FFFFFF; padding: 3px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: bold;">{pct:.1f}%</span></div><div style="background-color: #D4E6F1; border-radius: 10px; height: 20px; width: 100%; overflow: hidden; border: 1px solid #AED6F1;"><div style="background-color: {cor_barra}; width: {pct:.1f}%; height: 100%; border-radius: 8px;"></div></div><div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.88rem; color: #4A5568;"><span>Gasto: <b>{gasto_fmt}</b> de {meta_fmt}</span><span>Resta: <b style="color: #1B4F72;">{resta_fmt}</b></span></div></div>'

# --- SEÇÃO 1: RESUMO DO CAIXA ---
st.markdown("### 📊 Visão Geral do Mês (Valores em Conta)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div style="{card_style}"><small style="color: #566573; font-weight: bold;">Entradas (PIX)</small><h2 style="color: #0F2537; margin: 4px 0;">{fmt_brl(total_pix)}</h2><span style="color: #1C2833; font-size: 0.9em;">Dias 05 e 15</span></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div style="{card_style}"><small style="color: #566573; font-weight: bold;">Despesas Fixas</small><h2 style="color: #0F2537; margin: 4px 0;">{fmt_brl(total_fixas)}</h2><span style="color: #1C2833; font-size: 0.9em;">Carro (x2) + Mãe</span></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div style="{card_style}"><small style="color: #566573; font-weight: bold;">Reserva Essenciais</small><h2 style="color: #0F2537; margin: 4px 0;">{fmt_brl(reserva_pix_total)}</h2><span style="color: #1C2833; font-size: 0.9em;">Valor retido do PIX</span></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div style="{card_style}"><small style="color: #566573; font-weight: bold;">Livre p/ Dívidas</small><h2 style="color: #0F2537; margin: 4px 0;">{fmt_brl(sobra_total)}</h2><span style="color: #1C2833; font-size: 0.9em;">Sobra Real no Mês</span></div>', unsafe_allow_html=True)

st.divider()

# --- SEÇÃO 2: PLANEJAMENTO POR QUINZENA ---
st.markdown("### 📅 O Que Fazer em Cada Pagamento")
col_q1, col_q2 = st.columns(2)

with col_q1:
    st.markdown(f'<div style="{card_style}"><h4 style="color: #0F2537; margin-top:0; margin-bottom: 10px;">Ação no Dia 05 (Recebe R$ 2.200)</h4><p style="margin: 4px 0;">1. Pague as Fixas: <b>{fmt_brl(fixas_dia5)}</b></p><p style="margin: 4px 0;">2. Guarde para Essenciais: <b>{fmt_brl(reserva_pix_dia5)}</b></p><hr style="border: 0.5px solid #AED6F1; margin: 8px 0;"><p style="margin: 4px 0; font-size: 1.05em;"><b>Sobra no dia 05:</b> {fmt_brl(sobra_dia5)}</p></div>', unsafe_allow_html=True)

with col_q2:
    st.markdown(f'<div style="{card_style}"><h4 style="color: #0F2537; margin-top:0; margin-bottom: 10px;">Ação no Dia 15 (Recebe R$ 1.850)</h4><p style="margin: 4px 0;">1. Pague as Fixas: <b>{fmt_brl(fixas_dia15)}</b></p><p style="margin: 4px 0;">2. Guarde para Essenciais: <b>{fmt_brl(reserva_pix_dia15)}</b></p><hr style="border: 0.5px solid #AED6F1; margin: 8px 0;"><p style="margin: 4px 0; font-size: 1.05em;"><b>Sobra no dia 15:</b> {fmt_brl(sobra_dia15)}</p></div>', unsafe_allow_html=True)

st.divider()

# --- SEÇÃO 3: CONTROLE DO VR E METAS ---
st.markdown("### 💳 Controle de Flash (VR) e Metas")
col_m1, col_m2 = st.columns(2)

with col_m1:
    st.markdown(f'<div style="{card_style}"><h4 style="color: #0F2537; margin-top:0; margin-bottom: 10px;">Visão do Flash (VR)</h4><p style="margin: 6px 0;">• <b>Total Recebido:</b> {fmt_brl(vr_total)}</p><p style="margin: 6px 0;">• <b>Repasse Mãe:</b> {fmt_brl(vr_mae)}</p><p style="margin: 6px 0;">• <b>Seu Saldo Livre (Gasolina/Lucca):</b> {fmt_brl(vr_disponivel_livre)}</p></div>', unsafe_allow_html=True)

with col_m2:
    html_gas = criar_barra_progresso("Gasolina", "🚗", gasto_gas, meta_gasolina, "#1E88E5")
    html_lucca = criar_barra_progresso("Lucca (Fralda/Leite)", "👶", gasto_lucca, meta_lucca, "#00ACC1")
    
    st.markdown(f'<div style="{card_style}"><h4 style="color: #0F2537; margin-top:0; margin-bottom: 8px;">Termômetro de Essenciais</h4>{html_gas}{html_lucca}</div>', unsafe_allow_html=True)
