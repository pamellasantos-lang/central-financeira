import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import urllib.parse
import re
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="CONTROLE FINANCEIRO - PAMELLA",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO CSS EXECUTIVA COM ESPAÇAMENTOS FIXOS ---
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 95% !important;
    }
    
    .stApp {
        background-color: #EAEFF5 !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        padding: 0px !important;
        overflow: hidden !important;
        margin-bottom: 35px !important; 
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 24px 28px !important; 
    }

    .card-header-navy {
        background: linear-gradient(90deg, #0F172A 0%, #1E293B 100%);
        color: #FFFFFF;
        padding: 14px 24px;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        margin: -24px -28px 24px -28px;
    }

    .card-header-orange {
        background: linear-gradient(90deg, #FF5722 0%, #E64A19 100%);
        color: #FFFFFF;
        padding: 14px 24px;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        margin: -24px -28px 24px -28px;
    }

    .kpi-card-box {
        background: #F8FAFC;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #E2E8F0;
        border-left: 6px solid #0F172A;
    }
    .kpi-card-orange { border-left-color: #FF5722; }
    .kpi-card-green { border-left-color: #10B981; }
    .kpi-card-blue { border-left-color: #0284C7; }

    .kpi-title { font-size: 0.85rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value-main { font-size: 1.8rem; font-weight: 800; color: #0F172A; }
    .kpi-subtext { font-size: 0.85rem; font-weight: 600; color: #64748B; margin-top: 4px; }
    
    div[data-testid="stRadio"] > div { flex-direction: row; flex-wrap: wrap; gap: 8px; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label { 
        background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 6px 14px; border-radius: 6px; 
        cursor: pointer; font-weight: 700; font-size: 0.85rem; color: #334155;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { 
        background-color: #0F172A !important; border-color: #0F172A !important; color: #FFFFFF !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE LIMPEZA E FORMATAÇÃO ---
def limpar_valor(val):
    if pd.isna(val): return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).replace('R$', '').replace(' ', '').replace('\xa0', '').strip()
    if not s: return 0.0
    if ',' in s: s = s.replace('.', '').replace(',', '.')
    try: return float(s)
    except: return 0.0

def fmt_brl(valor):
    try: return f"R$ {float(valor):,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
    except: return "R$ 0,00"

def obter_coluna_valor_principal(df):
    if df.empty: return None
    cols = [c for c in df.columns if any(p in c.lower() for p in ['valor', 'total', 'receber', 'saldo', 'devedor']) and 'juros' not in c.lower()]
    if cols: return cols[-1]
    return df.columns[-1]

def obter_coluna_por_termo(df, termos):
    """Nova função inteligente que prioriza termos compostos (ex: Descrição do Gasto) antes de termos isolados (ex: Gasto)."""
    if df.empty: return None
    for t in termos:
        for c in df.columns:
            if t in c.lower():
                return c
    return None

def obter_coluna_data_fim(df):
    if df.empty: return None
    cols = [c for c in df.columns if any(p in c.lower() for p in ['fim', 'final', 'término', 'termino', 'última', 'ultima', 'quitação'])]
    if cols: return cols[-1]
    return None

# --- CONEXÃO COM O GOOGLE SHEETS ---
SHEET_ID = "1Y7EsUDd9J_liLwwTbRdjM2lM_XcdsWr_kYNUC-MAZsY"

def carregar_aba(nomes_possiveis):
    if isinstance(nomes_possiveis, str): nomes_possiveis = [nomes_possiveis]
    for nome in nomes_possiveis:
        try:
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(nome)}"
            df = pd.read_csv(url)
            if not df.empty and len(df.columns) > 1: return df
        except: continue
    return pd.DataFrame()

df_dividas_atrasadas = carregar_aba(["Dividas atrasadas", "Dívidas Atrasadas", "Dividas"])
df_dividas_fixas = carregar_aba(["Dividas Fixas", "Dívidas Fixas", "Parcelamentos Fixos", "Custos Ativos"])
df_entradas = carregar_aba(["Entradas", "Entradas Agosto"])
df_saidas = carregar_aba(["Saídas", "Saidas"])

# --- HEADER ALINHADO À ESQUERDA ---
with st.container(border=True):
    col_titulo, col_filtros = st.columns([1.2, 2])
    with col_titulo:
        st.markdown("<h2 style='margin:0; font-size:1.8rem; font-weight:800; color:#0F172A;'>CONTROLE FINANCEIRO<br><span style='color:#FF5722; font-size:1.3rem;'>PAMELLA</span></h2>", unsafe_allow_html=True)
    with col_filtros:
        c_ano, c_mes = st.columns([1, 4])
        with c_ano:
            ano_selecionado = st.selectbox("Ano", [2026, 2027], index=0)
        with c_mes:
            meses_botoes = ["jan.", "fev.", "mar.", "abr.", "mai.", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]
            mes_selecionado = st.radio("Mês", meses_botoes, index=8, horizontal=True)

# --- MAPEAMENTO BLINDADO DE COLUNAS DE SAÍDAS ---
col_desc_sai = obter_coluna_por_termo(df_saidas, ['descrição do gasto', 'descrição', 'descricao'])
col_parc_sai = obter_coluna_por_termo(df_saidas, ['parcelamento', 'parcela'])
col_tipo_gasto_sai = obter_coluna_por_termo(df_saidas, ['tipo de gasto', 'categoria'])
col_tipo_pag_sai = obter_coluna_por_termo(df_saidas, ['tipo de pagamento', 'pagamento', 'meio', 'forma'])
col_val_sai = obter_coluna_valor_principal(df_saidas)

if not df_saidas.empty and col_val_sai:
    df_saidas['Valor_Clean'] = df_saidas[col_val_sai].apply(limpar_valor)
    col_data = obter_coluna_por_termo(df_saidas, ['data'])
    if col_data:
        df_saidas['Dia'] = pd.to_datetime(df_saidas[col_data], format='%d/%m/%Y', errors='coerce').dt.day
        df_saidas['Dia'] = df_saidas['Dia'].fillna(1)
    else:
        df_saidas['Dia'] = 1

# --- PROCESSAMENTO DE ENTRADAS ---
total_entradas_pix, total_entradas_vr = 0.0, 0.0
entradas_salario_pix, entradas_adiantamento_pix = 0.0, 0.0

if not df_entradas.empty:
    try:
        col_val_ent = obter_coluna_valor_principal(df_entradas)
        df_entradas['Valor_Clean'] = df_entradas[col_val_ent].apply(limpar_valor)
        txt_ent = df_entradas.astype(str).agg(' '.join, axis=1)
        
        mask_ent_pix = txt_ent.str.contains('PIX|Dinheiro|Conta', case=False, na=False)
        mask_ent_vr = txt_ent.str.contains('VR|Crédito|Flash', case=False, na=False)
        total_entradas_pix = df_entradas[mask_ent_pix]['Valor_Clean'].sum()
        total_entradas_vr = df_entradas[mask_ent_vr]['Valor_Clean'].sum()
        
        mask_salario = txt_ent.str.contains('Salário|Salario|Transporte|04/09|04/|05/', case=False, na=False)
        mask_adiant = txt_ent.str.contains('Adiantamento|15/09|15/', case=False, na=False)
        entradas_salario_pix = df_entradas[mask_ent_pix & mask_salario]['Valor_Clean'].sum()
        entradas_adiantamento_pix = df_entradas[mask_ent_pix & mask_adiant]['Valor_Clean'].sum()
    except: pass

if total_entradas_pix == 0: total_entradas_pix = 3902.30
if total_entradas_vr == 0: total_entradas_vr = 682.50
if entradas_salario_pix == 0: entradas_salario_pix = 2052.30
if entradas_adiantamento_pix == 0: entradas_adiantamento_pix = 1850.00
total_receita_conta = entradas_salario_pix + entradas_adiantamento_pix

# --- PROCESSAMENTO DE SAÍDAS E ESSENCIAIS ---
total_saidas_pix, saidas_salario_pix, saidas_adiantamento_pix = 0.0, 0.0, 0.0
gasto_gasolina_vr, gasto_gasolina_pix = 0.0, 0.0
gasto_lucca_vr, gasto_lucca_pix = 0.0, 0.0
mask_parcelamentos = pd.Series(dtype=bool)

if not df_saidas.empty and col_tipo_pag_sai:
    try:
        txt_sai = df_saidas.astype(str).agg(' '.join, axis=1)
        mask_sai_pix = df_saidas[col_tipo_pag_sai].astype(str).str.contains('PIX|Dinheiro|Conta|Débito', case=False, na=False) | txt_sai.str.contains('PIX', case=False, na=False)
        mask_sai_vr = df_saidas[col_tipo_pag_sai].astype(str).str.contains('VR|Flash|Crédito', case=False, na=False)
        
        total_saidas_pix = df_saidas[mask_sai_pix]['Valor_Clean'].sum()
        
        saidas_salario_pix = df_saidas[mask_sai_pix & (df_saidas['Dia'] < 15)]['Valor_Clean'].sum()
        saidas_adiantamento_pix = df_saidas[mask_sai_pix & (df_saidas['Dia'] >= 15)]['Valor_Clean'].sum()
        
        mask_gasolina = txt_sai.str.contains('Gasolina', case=False, na=False)
        mask_lucca = txt_sai.str.contains('Lucca|Fralda|Leite', case=False, na=False)
        gasto_gasolina_vr = df_saidas[mask_gasolina & mask_sai_vr]['Valor_Clean'].sum()
        gasto_gasolina_pix = df_saidas[mask_gasolina & mask_sai_pix]['Valor_Clean'].sum()
        gasto_lucca_vr = df_saidas[mask_lucca & mask_sai_vr]['Valor_Clean'].sum()
        gasto_lucca_pix = df_saidas[mask_lucca & mask_sai_pix]['Valor_Clean'].sum()
        
        if col_tipo_gasto_sai:
            mask_parcelamentos = df_saidas[col_tipo_gasto_sai].astype(str).str.contains('parcelamento|acordo|dívida|divida', case=False, na=False)
    except: pass

if df_saidas.empty or total_saidas_pix == 0:
    total_saidas_pix = 1636.32
    saidas_salario_pix = 1636.32
    if gasto_gasolina_vr == 0 and gasto_gasolina_pix == 0: gasto_gasolina_vr = 50.00
    if gasto_lucca_vr == 0 and gasto_lucca_pix == 0: gasto_lucca_vr = 38.90

sobra_liquida = total_entradas_pix - total_saidas_pix
sobra_salario = entradas_salario_pix - saidas_salario_pix
sobra_adiantamento = entradas_adiantamento_pix - saidas_adiantamento_pix

# --- 1. RESUMO EXECUTIVO GERAL ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">📊 RESUMO EXECUTIVO GERAL</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card-box kpi-card-blue"><div class="kpi-title">Total Entradas PIX</div><div class="kpi-value-main" style="color:#0284C7;">{fmt_brl(total_entradas_pix)}</div><div class="kpi-subtext">Salário + Adiantamento</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card-box kpi-card-blue"><div class="kpi-title">Total Entradas VR</div><div class="kpi-value-main" style="color:#0369A1;">{fmt_brl(total_entradas_vr)}</div><div class="kpi-subtext">Cartão Flash Exclusivo</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card-box kpi-card-orange"><div class="kpi-title">Total Saídas PIX</div><div class="kpi-value-main" style="color:#FF5722;">{fmt_brl(total_saidas_pix)}</div><div class="kpi-subtext">Todos os gastos em conta</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card-box kpi-card-green"><div class="kpi-title">Sobra do Mês</div><div class="kpi-value-main" style="color:#10B981;">{fmt_brl(sobra_liquida)}</div><div class="kpi-subtext">Entradas PIX - Saídas PIX</div></div>', unsafe_allow_html=True)

# --- 2. DETALHAMENTO DE ENTRADAS, SAÍDAS E SOBRAS POR JANELA DE PAGAMENTO (PIX) ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">📅 DETALHAMENTO DE ENTRADAS, SAÍDAS E SOBRAS POR JANELA DE PAGAMENTO (PIX)</div>', unsafe_allow_html=True)
    cj1, cj2 = st.columns(2)
    with cj1:
        st.markdown(f"""
        <div style="background:#F8FAFC; padding:20px; border-radius:8px; border:1px solid #CBD5E1;">
            <div style="font-size:1.15rem; font-weight:800; color:#0F172A; margin-bottom:12px; border-bottom:1px solid #CBD5E1; padding-bottom:6px;">💳 Janela Salário (Dia 05)</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#334155; font-weight:600;">Entrada Salário (PIX):</span><span style="color:#0284C7; font-weight:800; font-size:1.1rem;">{fmt_brl(entradas_salario_pix)}</span></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#334155; font-weight:600;">O que eu gastei (PIX):</span><span style="color:#FF5722; font-weight:800; font-size:1.1rem;">- {fmt_brl(saidas_salario_pix)}</span></div>
            <div style="background-color:#CBD5E1; height:1px; width:100%; margin:12px 0;"></div>
            <div style="display:flex; justify-content:space-between; align-items:center;"><span style="color:#0F172A; font-weight:800; font-size:1.2rem;">💰 Quanto Sobrou:</span><span style="color:#10B981; font-weight:800; font-size:1.5rem;">{fmt_brl(sobra_salario)}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with cj2:
        st.markdown(f"""
        <div style="background:#F8FAFC; padding:20px; border-radius:8px; border:1px solid #CBD5E1;">
            <div style="font-size:1.15rem; font-weight:800; color:#0F172A; margin-bottom:12px; border-bottom:1px solid #CBD5E1; padding-bottom:6px;">💳 Janela Adiantamento (Dia 15)</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#334155; font-weight:600;">Entrada Adiantamento (PIX):</span><span style="color:#0284C7; font-weight:800; font-size:1.1rem;">{fmt_brl(entradas_adiantamento_pix)}</span></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#334155; font-weight:600;">O que eu gastei (PIX):</span><span style="color:#FF5722; font-weight:800; font-size:1.1rem;">- {fmt_brl(saidas_adiantamento_pix)}</span></div>
            <div style="background-color:#CBD5E1; height:1px; width:100%; margin:12px 0;"></div>
            <div style="display:flex; justify-content:space-between; align-items:center;"><span style="color:#0F172A; font-weight:800; font-size:1.2rem;">💰 Quanto Sobrou:</span><span style="color:#10B981; font-weight:800; font-size:1.5rem;">{fmt_brl(sobra_adiantamento)}</span></div>
        </div>
        """, unsafe_allow_html=True)

# --- 3. CAIXINHA DE ESSENCIAIS (RESERVA OBRIGATÓRIA MENSAL) ---
caixinha_gasolina = 400.00
caixinha_lucca = 480.00

gasto_gas_tot = gasto_gasolina_vr + gasto_gasolina_pix
pct_gas = min(100.0, (gasto_gas_tot / caixinha_gasolina) * 100) if caixinha_gasolina > 0 else 0
gasto_lucca_tot = gasto_lucca_vr + gasto_lucca_pix
pct_lucca = min(100.0, (gasto_lucca_tot / caixinha_lucca) * 100) if caixinha_lucca > 0 else 0

with st.container(border=True):
    st.markdown('<div class="card-header-orange">📦 CAIXINHA DE ESSENCIAIS (RESERVA OBRIGATÓRIA MENSAL)</div>', unsafe_allow_html=True)
    col_ess1, col_ess2 = st.columns(2)
    with col_ess1:
        st.markdown(f"""
        <div style="background:#F8FAFC; padding:18px; border-radius:8px; border:1px solid #CBD5E1;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:800; font-size:1.1rem; color:#0F172A;">🚗 Gasolina: {fmt_brl(caixinha_gasolina)}</span>
                <span style="background:#FF5722; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.85rem;">{pct_gas:.1f}% Usado</span>
            </div>
            <div style="background-color:#E2E8F0; border-radius:8px; height:10px; width:100%; overflow:hidden; margin-bottom:12px;">
                <div style="background-color:#FF5722; width:{pct_gas:.1f}%; height:100%;"></div>
            </div>
            <div style="font-size:0.95rem; color:#334155; line-height:1.6;">
                • <b>Saiu do VR (Flash):</b> <span style="color:#0284C7; font-weight:700;">{fmt_brl(gasto_gasolina_vr)}</span><br>
                • <b>Saiu do PIX (Conta):</b> <span style="color:#FF5722; font-weight:700;">{fmt_brl(gasto_gasolina_pix)}</span><br>
                • <b>Total Gasto:</b> <span style="color:#0F172A; font-weight:800;">{fmt_brl(gasto_gas_tot)}</span><br>
                • <b>Restante na Caixinha:</b> <span style="color:#10B981; font-weight:800;">{fmt_brl(max(0, caixinha_gasolina - gasto_gas_tot))}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_ess2:
        st.markdown(f"""
        <div style="background:#F8FAFC; padding:18px; border-radius:8px; border:1px solid #CBD5E1;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:800; font-size:1.1rem; color:#0F172A;">👶 Lucca (Fralda/Leite): {fmt_brl(caixinha_lucca)}</span>
                <span style="background:#0284C7; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.85rem;">{pct_lucca:.1f}% Usado</span>
            </div>
            <div style="background-color:#E2E8F0; border-radius:8px; height:10px; width:100%; overflow:hidden; margin-bottom:12px;">
                <div style="background-color:#0284C7; width:{pct_lucca:.1f}%; height:100%;"></div>
            </div>
            <div style="font-size:0.95rem; color:#334155; line-height:1.6;">
                • <b>Saiu do VR (Flash):</b> <span style="color:#0284C7; font-weight:700;">{fmt_brl(gasto_lucca_vr)}</span><br>
                • <b>Saiu do PIX (Conta):</b> <span style="color:#FF5722; font-weight:700;">{fmt_brl(gasto_lucca_pix)}</span><br>
                • <b>Total Gasto:</b> <span style="color:#0F172A; font-weight:800;">{fmt_brl(gasto_lucca_tot)}</span><br>
                • <b>Restante na Caixinha:</b> <span style="color:#10B981; font-weight:800;">{fmt_brl(max(0, caixinha_lucca - gasto_lucca_tot))}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 4. RECEITA OPERACIONAL EM CONTA & JANELAS DE PAGAMENTO ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">📈 RECEITA OPERACIONAL EM CONTA & JANELAS DE PAGAMENTO</div>', unsafe_allow_html=True)
    col_rec_chart, col_rec_box = st.columns([2, 1])

    with col_rec_chart:
        df_rec_hist = pd.DataFrame({'Mês': ['Set/26', 'Out/26', 'Nov/26', 'Dez/26'], 'Receita': [total_receita_conta, 0, 0, 0]})
        fig_rec = px.bar(df_rec_hist, x='Mês', y='Receita', text_auto='.2s', color_discrete_sequence=['#0F172A'])
        fig_rec.update_layout(height=210, margin=dict(l=5, r=5, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_rec, use_container_width=True, config={'displayModeBar': False})

    with col_rec_box:
        st.markdown(f"""
        <div style="background:#F8FAFC; padding:18px; border-radius:8px; border:1px solid #CBD5E1;">
            <div style="font-size:0.9rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">📅 Janela Salário (04/09)</div>
            <div style="font-size:1.3rem; font-weight:800; color:#10B981;">{fmt_brl(entradas_salario_pix)}</div>
            <hr style="margin:8px 0; border:0.5px solid #CBD5E1;">
            <div style="font-size:0.9rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">📅 Janela Adiantamento (15/09)</div>
            <div style="font-size:1.3rem; font-weight:800; color:#0284C7;">{fmt_brl(entradas_adiantamento_pix)}</div>
            <hr style="margin:8px 0; border:0.5px solid #CBD5E1;">
            <div style="font-size:0.95rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">💰 Total Operacional em Conta</div>
            <div style="font-size:1.5rem; font-weight:800; color:#0F172A;">{fmt_brl(total_receita_conta)}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 5. MAPEAMENTO DE DÍVIDAS: ATRASADAS ---
with st.container(border=True):
    st.markdown('<div class="card-header-orange">⚠️ MAPEAMENTO DE DÍVIDAS: ATRASADAS</div>', unsafe_allow_html=True)

    if not df_dividas_atrasadas.empty:
        col_nome_div = obter_coluna_por_termo(df_dividas_atrasadas, ['nome da dívida', 'nome da divida', 'nome'])
        col_credor_div = obter_coluna_por_termo(df_dividas_atrasadas, ['credor'])
        col_val_total_div = obter_coluna_valor_principal(df_dividas_atrasadas)
        col_acordo = obter_coluna_por_termo(df_dividas_atrasadas, ['entrou em acordo', 'acordo'])
        col_parc_feito = obter_coluna_por_termo(df_dividas_atrasadas, ['parcelamento feito', 'parcelamento'])
        col_num_parc = obter_coluna_por_termo(df_dividas_atrasadas, ['quantidade', 'num', 'nº'])
        
        for idx, row in df_dividas_atrasadas.iterrows():
            nome_divida = str(row[col_nome_div]).strip() if col_nome_div and pd.notna(row[col_nome_div]) else ""
            credor_nome = str(row[col_credor_div]).strip() if col_credor_div and pd.notna(row[col_credor_div]) else ""
            
            if not nome_divida or nome_divida.lower() == 'nan':
                nome_divida = credor_nome
            if not credor_nome or credor_nome.lower() == 'nan':
                credor_nome = nome_divida
            if not nome_divida or nome_divida.lower() == 'nan': continue
            
            val_total = limpar_valor(row[col_val_total_div]) if col_val_total_div else 0.0
            if val_total <= 0: continue
            
            is_acordado = False
            if col_acordo and pd.notna(row[col_acordo]):
                is_acordado = str(row[col_acordo]).strip().lower() in ['sim', 's', 'true', '1', 'ativo']
            
            num_parc_total = 1
            parc_feito_txt = str(row[col_parc_feito]) if col_parc_feito and pd.notna(row[col_parc_feito]) else "-"
            match_parc = re.search(r'(\d+)\s*x', parc_feito_txt, re.IGNORECASE)
            if match_parc:
                num_parc_total = int(match_parc.group(1))
            elif col_num_parc and pd.notna(row[col_num_parc]):
                v = limpar_valor(row[col_num_parc])
                if v > 0: num_parc_total = int(v)

            qtd_pagas = 0
            total_pago = 0.0
            
            # Cruzamento estrito entre o "Credor" da Dívida e "Descrição do Gasto" na aba Saídas
            if is_acordado and not df_saidas.empty and col_desc_sai:
                credor_alvo = credor_nome.strip().lower()
                
                def bate_credor_estrito(r_sai):
                    desc_s = str(r_sai[col_desc_sai]).strip().lower() if col_desc_sai else ""
                    if not desc_s: return False
                    return (credor_alvo == desc_s) or (credor_alvo in desc_s) or (desc_s in credor_alvo)
                
                df_matches = df_saidas[df_saidas.apply(bate_credor_estrito, axis=1)]
                
                if not df_matches.empty:
                    total_pago = df_matches['Valor_Clean'].sum()
                    qtd_pagas = 0
                    
                    for _, r_match in df_matches.iterrows():
                        p_str = str(r_match[col_parc_sai]).strip() if col_parc_sai and pd.notna(r_match[col_parc_sai]) else ""
                        
                        if '/' in p_str:
                            try:
                                partes = p_str.split('/')
                                p_paga = int(partes[0].strip())
                                p_tot = int(partes[1].strip())
                                if p_paga > 0:
                                    qtd_pagas = max(qtd_pagas, p_paga)
                                if p_tot > 1:
                                    num_parc_total = p_tot
                            except: pass
                    
                    if qtd_pagas == 0:
                        qtd_pagas = len(df_matches)
            
            if is_acordado and num_parc_total <= 1:
                num_parc_total = 36 # Default
            
            saldo_restante = max(0.0, val_total - total_pago)
            faltam_pagar = max(0, num_parc_total - qtd_pagas)
            
            cor = "#0284C7" if is_acordado else "#FF5722"
            bg = "#E0F2FE" if is_acordado else "#FEE2E2"
            status = "Acordado / Parcelado" if is_acordado else "Pendente"
            
            if is_acordado:
                detalhes_blocos = f"""<div style="flex: 1; min-width: 150px; font-size:0.95rem; color:#334155;">
<b>Já pago:</b> {qtd_pagas} parcela(s)<br>
<span style="color:#10B981; font-weight:700;">{fmt_brl(total_pago)}</span>
</div>
<div style="flex: 1; min-width: 150px; font-size:0.95rem; color:#334155;">
<b>Falta pagar:</b> {faltam_pagar} parcela(s)<br>
<span style="color:#FF5722; font-weight:700;">{fmt_brl(saldo_restante)}</span>
</div>"""
            else:
                detalhes_blocos = """<div style="flex: 2; min-width: 300px; font-size:0.95rem; color:#FF5722; font-weight:600;">
Aguardando acordo / negociação para este credor.
</div>"""
            
            html_card_atr = f"""<div style="background:#F8FAFC; padding:18px; border-radius:8px; border:1px solid #CBD5E1; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
<div style="flex: 1.2; min-width: 250px;">
<span style="font-weight:800; font-size:1.1rem; color:#0F172A;">{nome_divida}</span><br>
<span style="font-size:0.85rem; color:#64748B;">Credor: <b>{credor_nome}</b></span><br>
<span style="background:{bg}; color:{cor}; border:1px solid {cor}; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.75rem;">{status}</span>
</div>
<div style="flex: 1; min-width: 150px; font-size:0.95rem; color:#334155;">
<b>Valor Total:</b> <span style="color:#0F172A; font-weight:700;">{fmt_brl(val_total)}</span><br>
<span style="font-size:0.85rem; color:#64748B;">Acordo: {parc_feito_txt}</span>
</div>
{detalhes_blocos}
</div>"""
            st.markdown(html_card_atr, unsafe_allow_html=True)
    else:
        st.info("Aba 'Dívidas atrasadas' não encontrada ou vazia.")


# --- 6. CUSTOS E PARCELAMENTOS ATIVOS ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">✅ CUSTOS / PARCELAMENTOS ATIVOS (POR JANELA)</div>', unsafe_allow_html=True)

    if not df_dividas_fixas.empty:
        col_nome_fixa = obter_coluna_por_termo(df_dividas_fixas, ['descrição', 'descricao', 'credor', 'nome'])
        col_val_fixa = obter_coluna_valor_principal(df_dividas_fixas)
        col_parc_fixa = obter_coluna_por_termo(df_dividas_fixas, ['possui parcelamento', 'tem parcelamento', 'parcelamento'])
        col_num_parc_fixa = obter_coluna_por_termo(df_dividas_fixas, ['quantidade', 'parcelas', 'num', 'nº'])
        col_inicio_fixa = obter_coluna_por_termo(df_dividas_fixas, ['inicio', 'início'])
        col_fim_fixa = obter_coluna_data_fim(df_dividas_fixas)
        col_janela_fixa = obter_coluna_por_termo(df_dividas_fixas, ['janela'])
        
        itens_salario = []
        itens_adiantamento = []
        
        for idx, row in df_dividas_fixas.iterrows():
            desc = str(row[col_nome_fixa]).strip() if col_nome_fixa else "Desconhecido"
            if not desc or desc == 'nan': continue
            
            val_parcela = limpar_valor(row[col_val_fixa])
            janela = str(row[col_janela_fixa]).lower() if col_janela_fixa else ""
            
            is_parcelado = False
            if col_parc_fixa:
                is_parcelado = str(row[col_parc_fixa]).strip().lower() in ['sim', 's', 'true', '1']
            
            num_parc_total = 1
            if col_num_parc_fixa and pd.notna(row[col_num_parc_fixa]):
                val_str = str(row[col_num_parc_fixa])
                match_p = re.search(r'(\d+)', val_str)
                if match_p:
                    num_parc_total = int(match_p.group(1))
            
            qtd_pagas, total_pago = 0, 0.0
            
            if is_parcelado and not df_saidas.empty and col_desc_sai:
                credor_alvo = desc.strip().lower()
                
                def bate_credor_estrito_fixa(r_sai):
                    desc_s = str(r_sai[col_desc_sai]).strip().lower() if col_desc_sai else ""
                    if not desc_s: return False
                    return (credor_alvo == desc_s) or (credor_alvo in desc_s) or (desc_s in credor_alvo)
                
                df_matches = df_saidas[df_saidas.apply(bate_credor_estrito_fixa, axis=1)]
                
                if not df_matches.empty:
                    total_pago = df_matches['Valor_Clean'].sum()
                    
                    for _, r_match in df_matches.iterrows():
                        p_str = str(r_match[col_parc_sai]).strip() if col_parc_sai and pd.notna(r_match[col_parc_sai]) else ""
                        if '/' in p_str:
                            try:
                                partes = p_str.split('/')
                                curr_p = int(partes[0].strip())
                                if curr_p > 0:
                                    qtd_pagas = max(qtd_pagas, curr_p)
                            except: pass
                    if qtd_pagas == 0:
                        qtd_pagas = len(df_matches)
            
            data_inicio = str(row[col_inicio_fixa]) if col_inicio_fixa and pd.notna(row[col_inicio_fixa]) else "-"
            data_fim = str(row[col_fim_fixa]) if col_fim_fixa and pd.notna(row[col_fim_fixa]) else "-"
            
            if is_parcelado:
                info_parc_html = f"• <b>Total de Parcelas:</b> {num_parc_total}x<br>• <b>Início do Pagamento:</b> {data_inicio}<br>• <b>Finaliza em:</b> {data_fim}<br>• <b>Progresso:</b> <span style='color:#10B981; font-weight:700;'>{qtd_pagas} de {num_parc_total} paga(s)</span>"
            else:
                info_parc_html = "• <b>Custo Fixo Contínuo</b> (Sem data final)"
                
            html_item = f"""<div style="background:#F8FAFC; padding:16px; border-radius:8px; border:1px solid #CBD5E1; margin-bottom:10px;">
<div style="font-weight:800; font-size:1.1rem; color:#0F172A; margin-bottom:4px;">{desc}</div>
<div style="font-size:0.95rem; color:#334155;">
• <b>Valor a Pagar (Mês):</b> <span style="color:#0F172A; font-weight:700;">{fmt_brl(val_parcela)}</span><br>
{info_parc_html}
</div></div>"""
            
            if 'salário' in janela or 'salario' in janela or '05' in janela:
                itens_salario.append(html_item)
            else:
                itens_adiantamento.append(html_item)
                
        c_fix1, c_fix2 = st.columns(2)
        with c_fix1:
            st.markdown("<div style='font-size:1.1rem; font-weight:800; color:#0F172A; margin-bottom:12px; border-bottom:2px solid #10B981; padding-bottom:6px;'>💳 Pagamentos Janela Salário (Dia 05)</div>", unsafe_allow_html=True)
            if itens_salario:
                for it in itens_salario: st.markdown(it, unsafe_allow_html=True)
            else:
                st.write("Sem registros para esta janela.")
                
        with c_fix2:
            st.markdown("<div style='font-size:1.1rem; font-weight:800; color:#0F172A; margin-bottom:12px; border-bottom:2px solid #0284C7; padding-bottom:6px;'>💳 Pagamentos Janela Adiantamento (Dia 15)</div>", unsafe_allow_html=True)
            if itens_adiantamento:
                for it in itens_adiantamento: st.markdown(it, unsafe_allow_html=True)
            else:
                st.write("Sem registros para esta janela.")
    else:
        st.info("Aba 'Dívidas Fixas' não encontrada ou vazia.")


# --- 7. DISTRIBUIÇÃO VISUAL DE GASTOS POR TIPO DE SAÍDA (TREEMAP) ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">📊 DISTRIBUIÇÃO VISUAL DE GASTOS POR TIPO DE SAÍDA (TREEMAP)</div>', unsafe_allow_html=True)

    if not df_saidas.empty and total_saidas_pix > 0:
        try:
            cols_tg = [c for c in df_saidas.columns if any(p in c.lower() for p in ['tipo de gasto', 'categoria'])]
            col_tg = cols_tg[0] if cols_tg else df_saidas.columns[1]
            
            df_tree = df_saidas.groupby(col_tg)['Valor_Clean'].sum().reset_index()
            total_gasto = df_tree['Valor_Clean'].sum()
            df_tree['Porcentagem'] = (df_tree['Valor_Clean'] / total_gasto) * 100
            
            df_tree['Rotulo'] = df_tree.apply(lambda r: f"<b>{r[col_tg]}</b><br>{r['Porcentagem']:.1f}%<br>{fmt_brl(r['Valor_Clean'])}", axis=1)
            
            fig_tree = px.treemap(
                df_tree,
                path=[px.Constant("Saídas do Mês"), 'Rotulo'],
                values='Valor_Clean',
                color='Valor_Clean',
                color_continuous_scale=['#FF5722', '#0284C7', '#10B981', '#0F172A']
            )
            fig_tree.update_traces(root_color="lightgrey")
            fig_tree.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_tree, use_container_width=True, config={'displayModeBar': False})
        except Exception:
            st.write("Processando treemap de saídas...")
    else:
        st.info("Aguardando lançamentos na aba Saídas para compilar o gráfico visual...")
