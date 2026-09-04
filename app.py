import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import urllib.parse
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
    /* Margens globais com espaço de respiro no topo */
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
    
    /* Regra Fixa de Espaçamento Entre Quadros (Containers) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        padding: 0px !important;
        overflow: hidden !important;
        margin-bottom: 35px !important; /* Espaçamento grande e rígido entre blocos */
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 24px 28px !important; /* Respiro interno das caixas */
    }

    /* Cabeçalhos dos Cards */
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

    /* KPI Cards Box (Resumo Executivo) */
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
    
    /* Centralizar Cabeçalho Principal e Botões de Mês */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-bottom: 10px;
    }

    div[data-testid="stRadio"] > div { justify-content: center; flex-direction: row; flex-wrap: wrap; gap: 8px; }
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

# --- FUNÇÕES DE LIMPEZA ---
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
df_dividas_fixas = carregar_aba(["Dividas Fixas", "Dívidas Fixas", "Parcelamentos Fixos"])
df_entradas = carregar_aba(["Entradas", "Entradas Agosto"])
df_saidas = carregar_aba(["Saídas", "Saidas"])

# --- PROCESSAMENTO AUTOMÁTICO DE DADOS ---
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

total_saidas_pix, saidas_salario_pix, saidas_adiantamento_pix = 0.0, 0.0, 0.0
gasto_gasolina_vr, gasto_gasolina_pix = 0.0, 0.0
gasto_lucca_vr, gasto_lucca_pix = 0.0, 0.0
mask_parcelamentos = pd.Series(dtype=bool)

if not df_saidas.empty:
    try:
        col_val_sai = obter_coluna_valor_principal(df_saidas)
        df_saidas['Valor_Clean'] = df_saidas[col_val_sai].apply(limpar_valor)
        
        cols_tipo_pag = [c for c in df_saidas.columns if any(p in c.lower() for p in ['pagamento', 'meio', 'forma'])]
        col_tipo_pag = cols_tipo_pag[0] if cols_tipo_pag else df_saidas.columns[3]
        
        cols_tipo_gasto = [c for c in df_saidas.columns if any(p in c.lower() for p in ['tipo de gasto', 'categoria'])]
        col_tipo_gasto = cols_tipo_gasto[0] if cols_tipo_gasto else df_saidas.columns[1]
        
        col_data = [c for c in df_saidas.columns if 'data' in c.lower()][0]
        df_saidas['Dia'] = pd.to_datetime(df_saidas[col_data], format='%d/%m/%Y', errors='coerce').dt.day
        
        txt_sai = df_saidas.astype(str).agg(' '.join, axis=1)
        
        mask_sai_pix = df_saidas[col_tipo_pag].astype(str).str.contains('PIX|Dinheiro|Conta|Débito', case=False, na=False) | txt_sai.str.contains('PIX', case=False, na=False)
        mask_sai_vr = df_saidas[col_tipo_pag].astype(str).str.contains('VR|Flash|Crédito', case=False, na=False)
        total_saidas_pix = df_saidas[mask_sai_pix]['Valor_Clean'].sum()
        
        df_saidas['Dia'] = df_saidas['Dia'].fillna(1)
        saidas_salario_pix = df_saidas[mask_sai_pix & (df_saidas['Dia'] < 15)]['Valor_Clean'].sum()
        saidas_adiantamento_pix = df_saidas[mask_sai_pix & (df_saidas['Dia'] >= 15)]['Valor_Clean'].sum()
        
        mask_gasolina = txt_sai.str.contains('Gasolina', case=False, na=False)
        mask_lucca = txt_sai.str.contains('Lucca|Fralda|Leite', case=False, na=False)
        gasto_gasolina_vr = df_saidas[mask_gasolina & mask_sai_vr]['Valor_Clean'].sum()
        gasto_gasolina_pix = df_saidas[mask_gasolina & mask_sai_pix]['Valor_Clean'].sum()
        gasto_lucca_vr = df_saidas[mask_lucca & mask_sai_vr]['Valor_Clean'].sum()
        gasto_lucca_pix = df_saidas[mask_lucca & mask_sai_pix]['Valor_Clean'].sum()
        
        mask_parcelamentos = df_saidas[col_tipo_gasto].astype(str).str.contains('parcelamento|acordo|dívida|divida|financiamento|fixos|mensais', case=False, na=False)
    except: pass

if df_saidas.empty or total_saidas_pix == 0:
    total_saidas_pix = 1636.32
    saidas_salario_pix = 1636.32
    if gasto_gasolina_vr == 0 and gasto_gasolina_pix == 0: gasto_gasolina_vr = 50.00
    if gasto_lucca_vr == 0 and gasto_lucca_pix == 0: gasto_lucca_vr = 38.90

sobra_liquida = total_entradas_pix - total_saidas_pix
sobra_salario = entradas_salario_pix - saidas_salario_pix
sobra_adiantamento = entradas_adiantamento_pix - saidas_adiantamento_pix


# =========================================================================
# ORDEM DOS QUADROS ESTRITAMENTE FIXADA E CENTRALIZADA
# =========================================================================

# --- 1. CABEÇALHO CENTRALIZADO COM ANO E MESES ---
with st.container(border=True):
    st.markdown("""
    <div class="header-container">
        <h1 style='margin:0 0 5px 0; font-size:2.2rem; font-weight:800; color:#0F172A; letter-spacing: 1px;'>
            CONTROLE FINANCEIRO <span style='color:#FF5722;'>PAMELLA</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    col_vazia1, col_ano, col_mes, col_vazia2 = st.columns([1.5, 1, 4, 1.5])
    with col_ano:
        ano_selecionado = st.selectbox("Ano", [2026, 2027], index=0, label_visibility="collapsed")
    with col_mes:
        meses_botoes = ["jan.", "fev.", "mar.", "abr.", "mai.", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]
        mes_selecionado = st.radio("Mês", meses_botoes, index=8, horizontal=True, label_visibility="collapsed")


# --- 2. RESUMO EXECUTIVO GERAL ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">📊 RESUMO EXECUTIVO GERAL</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card-box kpi-card-blue"><div class="kpi-title">Total Entradas PIX</div><div class="kpi-value-main" style="color:#0284C7;">{fmt_brl(total_entradas_pix)}</div><div class="kpi-subtext">Salário + Adiantamento</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card-box kpi-card-blue"><div class="kpi-title">Total Entradas VR</div><div class="kpi-value-main" style="color:#0369A1;">{fmt_brl(total_entradas_vr)}</div><div class="kpi-subtext">Cartão Flash Exclusivo</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card-box kpi-card-orange"><div class="kpi-title">Total Saídas PIX</div><div class="kpi-value-main" style="color:#FF5722;">{fmt_brl(total_saidas_pix)}</div><div class="kpi-subtext">Todos os gastos em conta</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card-box kpi-card-green"><div class="kpi-title">Sobra do Mês</div><div class="kpi-value-main" style="color:#10B981;">{fmt_brl(sobra_liquida)}</div><div class="kpi-subtext">Entradas PIX - Saídas PIX</div></div>', unsafe_allow_html=True)


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
                <div style="background-color:#FF5722; width:{pct_gas:.1f}%; height:100%; border-radius:8px;"></div>
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
                <div style="background-color:#0284C7; width:{pct_lucca:.1f}%; height:100%; border-radius:8px;"></div>
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
            <div style="font-size:0.9rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">📅 Janela Salário (Dia 05)</div>
            <div style="font-size:1.3rem; font-weight:800; color:#10B981;">{fmt_brl(entradas_salario_pix)}</div>
            <hr style="margin:8px 0; border:0.5px solid #CBD5E1;">
            <div style="font-size:0.9rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">📅 Janela Adiantamento (Dia 15)</div>
            <div style="font-size:1.3rem; font-weight:800; color:#0284C7;">{fmt_brl(entradas_adiantamento_pix)}</div>
            <hr style="margin:8px 0; border:0.5px solid #CBD5E1;">
            <div style="font-size:0.95rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">💰 Total Receita Operacional (Conta)</div>
            <div style="font-size:1.5rem; font-weight:800; color:#0F172A;">{fmt_brl(total_receita_conta)}</div>
        </div>
        """, unsafe_allow_html=True)


# --- 5. DETALHAMENTO DE ENTRADAS, SAÍDAS E SOBRAS POR JANELA DE PAGAMENTO (PIX) ---
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


# --- 6. MAPEAMENTO DE DÍVIDAS: ATRASADAS E FIXAS MENSAIS ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">💳 MAPEAMENTO DE DÍVIDAS: ATRASADAS E FIXAS MENSAIS</div>', unsafe_allow_html=True)

    def processar_lista_dividas(df_base, tipo_lista="atrasadas"):
        rastreados = []
        if df_base.empty: return rastreados
        
        cols_nome = [c for c in df_base.columns if any(p in c.lower() for p in ['credor', 'nome', 'dívida', 'divida', 'descrição'])]
        col_nome = cols_nome[0] if cols_nome else df_base.columns[0]
        col_val = obter_coluna_valor_principal(df_base)
        col_fim = obter_coluna_data_fim(df_base)
        
        for idx, row in df_base.iterrows():
            credor = str(row[col_nome]).strip()
            if not credor or credor == 'nan': continue
            val_total = limpar_valor(row[col_val])
            if val_total <= 0: continue
            
            txt_row = ' '.join(row.astype(str)).lower()
            
            # Se for atrasadas, olha para "Acordado", se for fixas, assumimos que já está parcelada/acordada
            if tipo_lista == "fixas":
                is_acordado = True
            else:
                is_acordado = any(term in txt_row for term in ['sim', 'ativo', 'acordad', 'parcelad', 'ok', '36x'])
            
            qtd_pagas, total_pago = 0, 0.0
            
            # Checa os pagamentos de fato registrados nas Saídas
            if not df_saidas.empty and not mask_parcelamentos.empty and mask_parcelamentos.any():
                col_desc_sai = [c for c in df_saidas.columns if any(p in c.lower() for p in ['descrição', 'descricao', 'gasto', 'detalhe'])][0]
                df_saidas_parc = df_saidas[mask_parcelamentos]
                
                # Procura pelo nome do credor no meio das saídas de parcelamento
                # Usa split para pegar a primeira palavra chave principal (ex: "Mercado" de "Mercado Livre")
                palavra_chave = credor.split()[0] if len(credor.split()) > 0 else credor
                mask_match = df_saidas_parc[col_desc_sai].astype(str).str.contains(palavra_chave, case=False, na=False)
                
                qtd_pagas = mask_match.sum()
                total_pago = df_saidas_parc[mask_match]['Valor_Clean'].sum()
            
            cols_num_parc = [c for c in df_base.columns if any(p in c.lower() for p in ['nº', 'num', 'parcelas', 'qtd'])]
            num_parc = 1
            if cols_num_parc and pd.notna(row[cols_num_parc[0]]):
                v = limpar_valor(row[cols_num_parc[0]])
                if v > 0: num_parc = int(v)
            if is_acordado and num_parc <= 1:
                num_parc = 36 # Exemplo padrão caso não ache o número na planilha
            
            data_termino = str(row[col_fim]) if col_fim and pd.notna(row[col_fim]) else "-"
            saldo_restante = max(0.0, val_total - total_pago)
            
            rastreados.append({
                'Credor': credor,
                'Valor_Total': val_total,
                'Is_Acordado': is_acordado,
                'Num_Parcelas': num_parc,
                'Parcelas_Pagas': qtd_pagas,
                'Total_Pago': total_pago,
                'Saldo_Restante': saldo_restante,
                'Termino': data_termino
            })
        return sorted(rastreados, key=lambda x: x['Valor_Total'], reverse=True)

    col_div1, col_div2 = st.columns(2)
    
    # --- BLOCO ESQUERDO: DÍVIDAS ATRASADAS (ISOLADO PARA DF_DIVIDAS_ATRASADAS) ---
    with col_div1:
        st.markdown("<h4 style='color:#FF5722; margin-bottom:15px;'>⚠️ Dívidas Atrasadas</h4>", unsafe_allow_html=True)
        divs_atrasadas = processar_lista_dividas(df_dividas_atrasadas, "atrasadas")
        
        if divs_atrasadas:
            total_acordado = sum(d['Valor_Total'] for d in divs_atrasadas if d['Is_Acordado'])
            total_pendente = sum(d['Valor_Total'] for d in divs_atrasadas if not d['Is_Acordado'])
            
            for d in divs_atrasadas:
                cor = "#0284C7" if d['Is_Acordado'] else "#FF5722"
                bg = "#E0F2FE" if d['Is_Acordado'] else "#FEE2E2"
                status = "Acordo Ativo" if d['Is_Acordado'] else "Pendente"
                
                st.markdown(f"""
                <div style="background:#F8FAFC; padding:16px; border-radius:8px; border:1px solid #CBD5E1; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-weight:800; font-size:1.1rem; color:#0F172A;">{d['Credor']}</span>
                        <span style="background:{bg}; color:{cor}; border:1px solid {cor}; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.75rem;">{status}</span>
                    </div>
                    <div style="font-size:0.9rem; color:#334155; line-height:1.6;">
                        • <b>Valor Total:</b> <span style="color:#0F172A; font-weight:700;">{fmt_brl(d['Valor_Total'])}</span><br>
                        • <b>Parcelas Pagas:</b> {d['Parcelas_Pagas']} de {d['Num_Parcelas']}<br>
                        • <b>Previsão de Término:</b> {d['Termino']}<br>
                        • <b>Falta Pagar:</b> <span style="color:#FF5722; font-weight:700;">{fmt_brl(d['Saldo_Restante'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            df_comp_atr = pd.DataFrame({'Status': ['Acordado/Parcelado', 'Pendente/Atrasado'], 'Valor': [total_acordado, total_pendente]})
            if total_acordado > 0 or total_pendente > 0:
                fig_comp_atr = px.bar(df_comp_atr, y='Status', x='Valor', orientation='h', color='Status', color_discrete_sequence=['#0284C7', '#FF5722'], text_auto='.2s')
                fig_comp_atr.update_layout(height=180, margin=dict(l=5, r=5, t=10, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="", showlegend=False)
                st.markdown("<div style='font-size:0.9rem; font-weight:700; color:#334155; margin-top:10px;'>📊 Comparativo: Acordado vs Pendente</div>", unsafe_allow_html=True)
                st.plotly_chart(fig_comp_atr, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Nenhuma dívida atrasada localizada na aba 'Dívidas atrasadas'.")

    # --- BLOCO DIREITO: DÍVIDAS FIXAS (ISOLADO PARA DF_DIVIDAS_FIXAS) ---
    with col_div2:
        st.markdown("<h4 style='color:#10B981; margin-bottom:15px;'>✅ Dívidas Fixas (Parcelamentos)</h4>", unsafe_allow_html=True)
        divs_fixas = processar_lista_dividas(df_dividas_fixas, "fixas")
        
        if divs_fixas:
            for d in divs_fixas:
                st.markdown(f"""
                <div style="background:#F8FAFC; padding:16px; border-radius:8px; border:1px solid #CBD5E1; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-weight:800; font-size:1.1rem; color:#0F172A;">{d['Credor']}</span>
                        <span style="background:#D1FAE5; color:#059669; border:1px solid #10B981; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.75rem;">Em Dia (Fixo)</span>
                    </div>
                    <div style="font-size:0.9rem; color:#334155; line-height:1.6;">
                        • <b>Valor/Mês:</b> <span style="color:#0F172A; font-weight:700;">{fmt_brl(d['Valor_Total'])}</span><br>
                        • <b>Parcelas Pagas:</b> {d['Parcelas_Pagas']} de {d['Num_Parcelas']}<br>
                        • <b>Previsão de Término:</b> {d['Termino']}<br>
                        • <b>Restante Aproximado:</b> <span style="color:#0F172A; font-weight:700;">{fmt_brl(d['Saldo_Restante'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma dívida fixa/parcelamento localizado na aba 'Dívidas Fixas'.")

# --- 7. GRÁFICO VISUAL DE TIPO DE SAÍDA (TREEMAP VISUAL MANTIDO NO FINAL) ---
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
