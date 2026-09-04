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

# --- ESTILIZAÇÃO CSS EXECUTIVA ---
st.markdown("""
<style>
    /* Estilo global da página */
    .stApp {
        background-color: #EAEFF5 !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    
    /* Cards BI */
    .bi-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        border: 1px solid #E2E8F0;
    }
    
    .card-header-navy {
        background: linear-gradient(90deg, #0F172A 0%, #1E293B 100%);
        color: #FFFFFF;
        padding: 10px 16px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        margin: -18px -18px 14px -18px;
    }

    .card-header-orange {
        background: linear-gradient(90deg, #FF5722 0%, #E64A19 100%);
        color: #FFFFFF;
        padding: 10px 16px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        margin: -18px -18px 14px -18px;
    }

    /* KPI Cards Box */
    .kpi-card-box {
        background: #FFFFFF;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        border: 1px solid #E2E8F0;
        border-left: 5px solid #0F172A;
    }
    .kpi-card-orange { border-left-color: #FF5722; }
    .kpi-card-green { border-left-color: #10B981; }
    .kpi-card-blue { border-left-color: #0284C7; }

    .kpi-title { font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 4px; }
    .kpi-value-main { font-size: 1.6rem; font-weight: 800; color: #0F172A; }
    .kpi-subtext { font-size: 0.8rem; font-weight: 600; color: #64748B; margin-top: 2px; }
    
    /* Estilização para as caixinhas de mês (Radio horizontal) */
    div.row-widget.stRadio > div { flex-direction: row; flex-wrap: wrap; gap: 10px; }
    div.row-widget.stRadio > div > label { 
        background-color: #FFFFFF; border: 1px solid #CBD5E1; 
        padding: 6px 14px; border-radius: 6px; cursor: pointer;
    }
    div.row-widget.stRadio > div > label[data-checked="true"] {
        background-color: #0F172A; border-color: #0F172A;
    }
    div.row-widget.stRadio > div > label[data-checked="true"] * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE LIMPEZA E BUSCA DINÂMICA ---
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

def obter_coluna(df, palavras_chave):
    if df.empty: return None
    for col in df.columns:
        for p in palavras_chave:
            if p.lower() in col.lower():
                return col
    return df.columns[-1]

# --- CONEXÃO COM A PLANILHA DO GOOGLE ---
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

df_dividas = carregar_aba(["Dividas", "Dívidas"])
df_entradas = carregar_aba(["Entradas", "Entradas Agosto"])
df_saidas = carregar_aba(["Saídas", "Saidas"])
df_fixas = carregar_aba(["Parcelamentos Fixos"])

# --- HEADER: TÍTULO, ANO E MÊS ---
col_titulo, col_filtros = st.columns([1.2, 2])

with col_titulo:
    st.markdown("<h1 style='margin-top:10px; font-size:2.0rem; font-weight:800; color:#0F172A;'>CONTROLE FINANCEIRO<br><span style='color:#FF5722; font-size:1.4rem;'>PAMELLA</span></h1>", unsafe_allow_html=True)

with col_filtros:
    c_ano, c_mes = st.columns([1, 4])
    with c_ano:
        ano_selecionado = st.selectbox("Ano", [2026, 2027], index=0)
    with c_mes:
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        mes_selecionado = st.radio("Mês", meses, index=8, horizontal=True)

st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

# --- PROCESSAMENTO AUTOMÁTICO DE DADOS ---

# 1. ENTRADAS
total_entradas_pix = 0.0
total_entradas_vr = 0.0
entradas_salario_pix = 0.0
entradas_adiantamento_pix = 0.0

if not df_entradas.empty:
    col_val_ent = obter_coluna(df_entradas, ['total', 'valor', 'receber'])
    col_tipo_rec = obter_coluna(df_entradas, ['recebimento', 'meio', 'tipo'])
    col_tipo_ent = obter_coluna(df_entradas, ['tipo de entrada', 'categoria', 'origem'])
    
    df_entradas['Valor_Clean'] = df_entradas[col_val_ent].apply(limpar_valor)
    
    mask_ent_pix = df_entradas[col_tipo_rec].astype(str).str.contains('PIX|Dinheiro|Conta', case=False, na=False)
    mask_ent_vr = df_entradas[col_tipo_rec].astype(str).str.contains('VR|Crédito|Flash', case=False, na=False)
    
    total_entradas_pix = df_entradas[mask_ent_pix]['Valor_Clean'].sum()
    total_entradas_vr = df_entradas[mask_ent_vr]['Valor_Clean'].sum()
    
    mask_salario = df_entradas[col_tipo_ent].astype(str).str.contains('Salário|Transporte', case=False, na=False)
    mask_adiant = df_entradas[col_tipo_ent].astype(str).str.contains('Adiantamento', case=False, na=False)
    
    entradas_salario_pix = df_entradas[mask_ent_pix & mask_salario]['Valor_Clean'].sum()
    entradas_adiantamento_pix = df_entradas[mask_ent_pix & mask_adiant]['Valor_Clean'].sum()

# 2. SAÍDAS E ESSENCIAIS (Busca ampla em todas as colunas de texto)
total_saidas_pix = 0.0
gasto_gasolina_ess = 0.0
gasto_lucca_ess = 0.0

if not df_saidas.empty:
    col_val_sai = obter_coluna(df_saidas, ['valor', 'total'])
    col_tipo_pag = obter_coluna(df_saidas, ['tipo de pagamento', 'pagamento', 'meio'])
    df_saidas['Valor_Clean'] = df_saidas[col_val_sai].apply(limpar_valor)
    
    mask_sai_pix = df_saidas[col_tipo_pag].astype(str).str.contains('PIX|Dinheiro|Conta', case=False, na=False)
    total_saidas_pix = df_saidas[mask_sai_pix]['Valor_Clean'].sum()
    
    cols_txt_sai = [c for c in df_saidas.columns if c != col_val_sai and c != 'Valor_Clean']
    texto_saidas = df_saidas[cols_txt_sai].astype(str).agg(' '.join, axis=1)
    
    gasto_gasolina_ess = df_saidas[texto_saidas.str.contains('Gasolina', case=False, na=False)]['Valor_Clean'].sum()
    gasto_lucca_ess = df_saidas[texto_saidas.str.contains('Lucca|Fralda|Leite', case=False, na=False)]['Valor_Clean'].sum()

sobra_liquida = total_entradas_pix - total_saidas_pix

# --- 1. RESUMO EXECUTIVO ---
st.markdown("### 📊 Resumo Executivo")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<div class="kpi-card-box kpi-card-blue"><div class="kpi-title">Total Entradas PIX</div><div class="kpi-value-main" style="color:#0284C7;">{fmt_brl(total_entradas_pix)}</div><div class="kpi-subtext">Salário + Adiantamento</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card-box kpi-card-blue"><div class="kpi-title">Total Entradas VR</div><div class="kpi-value-main" style="color:#0369A1;">{fmt_brl(total_entradas_vr)}</div><div class="kpi-subtext">Cartão Flash Exclusivo</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card-box kpi-card-orange"><div class="kpi-title">Total Saídas PIX</div><div class="kpi-value-main" style="color:#FF5722;">{fmt_brl(total_saidas_pix)}</div><div class="kpi-subtext">Todos os gastos em conta</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card-box kpi-card-green"><div class="kpi-title">Sobra</div><div class="kpi-value-main" style="color:#10B981;">{fmt_brl(sobra_liquida)}</div><div class="kpi-subtext">Entradas PIX - Saídas PIX</div></div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

# --- 2. QUADRO ESSENCIAIS MENSAIS (UNIFICADO NO MESMO CARD) ---
meta_gasolina = 400.00
meta_lucca = 480.00

pct_gas = min(100.0, (gasto_gasolina_ess / meta_gasolina) * 100) if meta_gasolina > 0 else 0
resta_gas = max(0.0, meta_gasolina - gasto_gasolina_ess)

pct_lucca = min(100.0, (gasto_lucca_ess / meta_lucca) * 100) if meta_lucca > 0 else 0
resta_lucca = max(0.0, meta_lucca - gasto_lucca_ess)

html_essenciais_card = f"""
<div class="bi-card">
    <div class="card-header-orange">👶 ESSENCIAIS MENSAIS (LUCCA & GASOLINA)</div>
    <div style="display: flex; gap: 16px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 280px; background: #F8FAFC; padding: 16px; border-radius: 8px; border: 1px solid #E2E8F0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">🚗 Gasolina (Meta: {fmt_brl(meta_gasolina)})</span>
                <span style="background: #FF5722; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem;">{pct_gas:.1f}% Usado</span>
            </div>
            <div style="background-color: #E2E8F0; border-radius: 8px; height: 10px; width: 100%; overflow: hidden; margin-bottom: 10px;">
                <div style="background-color: #FF5722; width: {pct_gas:.1f}%; height: 100%; border-radius: 8px;"></div>
            </div>
            <div style="font-size: 0.95rem; color: #334155;">
                • <b>Já gastou:</b> <span style="color: #FF5722; font-weight: 700;">{fmt_brl(gasto_gasolina_ess)}</span><br>
                • <b>Resta disponível:</b> <span style="color: #10B981; font-weight: 700;">{fmt_brl(resta_gas)}</span>
            </div>
        </div>
        <div style="flex: 1; min-width: 280px; background: #F8FAFC; padding: 16px; border-radius: 8px; border: 1px solid #E2E8F0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">👶 Lucca (Fralda/Leite) (Meta: {fmt_brl(meta_lucca)})</span>
                <span style="background: #0284C7; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem;">{pct_lucca:.1f}% Usado</span>
            </div>
            <div style="background-color: #E2E8F0; border-radius: 8px; height: 10px; width: 100%; overflow: hidden; margin-bottom: 10px;">
                <div style="background-color: #0284C7; width: {pct_lucca:.1f}%; height: 100%; border-radius: 8px;"></div>
            </div>
            <div style="font-size: 0.95rem; color: #334155;">
                • <b>Já gastou:</b> <span style="color: #0284C7; font-weight: 700;">{fmt_brl(gasto_lucca_ess)}</span><br>
                • <b>Resta disponível:</b> <span style="color: #10B981; font-weight: 700;">{fmt_brl(resta_lucca)}</span>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(html_essenciais_card, unsafe_allow_html=True)

# --- 3. RECEITA OPERACIONAL E JANELAS (A PARTIR DE SETEMBRO/26) ---
st.markdown('<div class="bi-card"><div class="card-header-navy">📈 Receita Operacional em Conta & Janelas (A partir de Set/2026)</div>', unsafe_allow_html=True)
col_rec_chart, col_rec_box = st.columns([2, 1])

with col_rec_chart:
    meses_filtro = ['Set/26', 'Out/26', 'Nov/26', 'Dez/26']
    receitas_hist = [total_entradas_pix, 0, 0, 0] 
    
    df_rec_hist = pd.DataFrame({'Mês': meses_filtro, 'Receita': receitas_hist})
    fig_rec = px.bar(df_rec_hist, x='Mês', y='Receita', text_auto='.2s', color_discrete_sequence=['#0F172A'])
    fig_rec.update_layout(height=210, margin=dict(l=5, r=5, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="")
    st.plotly_chart(fig_rec, use_container_width=True, config={'displayModeBar': False})

with col_rec_box:
    st.markdown(f"""
    <div style="background:#F8FAFC; padding:16px; border-radius:8px; border:1px solid #E2E8F0; margin-top:5px;">
        <div style="font-size:0.9rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">📅 Janela Salário (04/09)</div>
        <div style="font-size:1.3rem; font-weight:800; color:#10B981;">{fmt_brl(entradas_salario_pix)}</div>
        <hr style="margin:8px 0; border:0.5px solid #E2E8F0;">
        <div style="font-size:0.9rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">📅 Janela Adiantamento (15/09)</div>
        <div style="font-size:1.3rem; font-weight:800; color:#0F172A;">{fmt_brl(entradas_adiantamento_pix)}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. MAPA DE DÍVIDAS E STATUS DE ACORDO ---
st.markdown('<div class="bi-card"><div class="card-header-navy">💳 Mapeamento Geral de Dívidas e Status de Acordos de Quitação</div>', unsafe_allow_html=True)

if not df_dividas.empty:
    try:
        col_nome_div = obter_coluna(df_dividas, ['nome', 'dívida', 'divida', 'credor'])
        col_val_div = obter_coluna(df_dividas, ['valor', 'saldo', 'total'])
        df_dividas['Val_Clean'] = df_dividas[col_val_div].apply(limpar_valor)
        
        # Identificação de Status de Acordo / Parcelamento
        cols_status = [c for c in df_dividas.columns if any(p in c.lower() for p in ['acord', 'status', 'parcel', 'situa', 'ativo'])]
        if cols_status:
            col_st = cols_status[0]
            def classificar_status(val):
                s = str(val).lower()
                if any(term in s for term in ['sim', 'ativo', 'acordad', 'parcelad', 'ok']):
                    return 'Acordado (Parcelamento Ativo)'
                return 'Não Acordado (Pendente)'
            df_dividas['Status_Grupo'] = df_dividas[col_st].apply(classificar_status)
        else:
            df_dividas['Status_Grupo'] = 'Não Acordado (Pendente)'
            
        df_div_sorted = df_dividas.sort_values(by='Val_Clean', ascending=True)
        
        color_map = {
            'Acordado (Parcelamento Ativo)': '#0284C7',
            'Não Acordado (Pendente)': '#FF5722'
        }
        
        fig_div = px.bar(
            df_div_sorted,
            y=col_nome_div,
            x='Val_Clean',
            color='Status_Grupo',
            orientation='h',
            text_auto='.2s',
            color_discrete_map=color_map,
            labels={'Val_Clean': 'Saldo Devedor (R$)', 'Status_Grupo': 'Status'}
        )
        fig_div.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Saldo Devedor (R$)",
            yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_div, use_container_width=True, config={'displayModeBar': False})
    except Exception:
        st.write("Processando visualização das dívidas...")
else:
    st.write("Sincronizando dados de dívidas da planilha...")

st.markdown('</div>', unsafe_allow_html=True)

# --- 5. GRÁFICO DE PORCENTAGEM SEPARADO POR TIPO DE GASTO ---
st.markdown('<div class="bi-card"><div class="card-header-navy">🍩 Distribuição Percentual por Tipo de Gasto</div>', unsafe_allow_html=True)

if not df_saidas.empty and total_saidas_pix > 0:
    try:
        col_tg = obter_coluna(df_saidas, ['tipo de gasto', 'categoria', 'tipo'])
        df_pie = df_saidas.groupby(col_tg)['Valor_Clean'].sum().reset_index()
        
        fig_pie = px.pie(
            df_pie,
            values='Valor_Clean',
            names=col_tg,
            hole=0.5,
            color_discrete_sequence=['#FF5722', '#10B981', '#0284C7', '#0F172A', '#8B5CF6', '#F59E0B']
        )
        fig_pie.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    except Exception:
        st.write("Processando distribuição de saídas...")
else:
    df_mock = pd.DataFrame({'Tipo': ['Fixos Essenciais', 'Parcelamentos Fixos', 'Variáveis'], 'Valor': [880.0, 1550.0, 258.57]})
    fig_pie = px.pie(df_mock, values='Valor', names='Tipo', hole=0.5, color_discrete_sequence=['#FF5722', '#0F172A', '#10B981'])
    fig_pie.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

st.markdown('</div>', unsafe_allow_html=True)
