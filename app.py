import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FINANCEIRO | Painel Executivo", page_icon="📈", layout="wide")

# --- CUSTOM CSS (Layout BI executivo idêntico ao modelo) ---
st.markdown("""
<style>
    /* Estilo global da página */
    .stApp {
        background-color: #EAEFF5 !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Sidebar escuro */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* Cards BI */
    .bi-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        border: 1px solid #E2E8F0;
    }
    
    /* Header dos Cards */
    .card-header-orange {
        background: linear-gradient(90deg, #FF5722 0%, #E64A19 100%);
        color: #FFFFFF;
        padding: 8px 14px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        margin: -16px -16px 12px -16px;
    }
    
    .card-header-navy {
        background: linear-gradient(90deg, #0F172A 0%, #1E293B 100%);
        color: #FFFFFF;
        padding: 8px 14px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        margin: -16px -16px 12px -16px;
    }

    /* Banner KPI Fluxo com Setas */
    .kpi-flow-wrapper {
        background: #FFFFFF;
        padding: 14px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        margin-bottom: 15px;
        border: 1px solid #E2E8F0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .kpi-item {
        text-align: center;
    }
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .val-orange { font-size: 1.4rem; font-weight: 800; color: #FF5722; }
    .val-navy { font-size: 1.4rem; font-weight: 800; color: #0F172A; }
    .val-green { font-size: 1.4rem; font-weight: 800; color: #10B981; }
    .val-sub { font-size: 0.8rem; font-weight: 600; color: #475569; }
    .arrow { font-size: 1.4rem; color: #94A3B8; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES DE FORMATAÇÃO ---
def limpar_valor(val):
    if pd.isna(val): return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).replace('R$', '').replace(' ', '').replace('\xa0', '').strip()
    if not s: return 0.0
    if ',' in s: s = s.replace('.', '').replace(',', '.')
    try: return float(s)
    except: return 0.0

def fmt_brl(valor):
    try:
        val = float(valor)
        return f"R$ {val:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
    except:
        return "R$ 0,00"

# --- SIDEBAR E NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>📊 CENTRAL</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📌 Visão Geral")
    st.write("🟢 Dashboard Executivo")
    st.write("💳 Dívidas & Acordos")
    st.write("📅 Planejamento Quinzenal")
    st.write("🛒 Metas de Essenciais")
    st.divider()
    st.caption("Assistente Pessoal v4.0 Executivo")

# --- CONEXÃO COM GOOGLE SHEETS ---
SHEET_ID = "1Y7EsUDd9J_liLwwTbRdjM2lM_XcdsWr_kYNUC-MAZsY"

def carregar_aba(nomes_possiveis):
    if isinstance(nomes_possiveis, str): nomes_possiveis = [nomes_possiveis]
    for nome in nomes_possiveis:
        try:
            nome_encoded = urllib.parse.quote(nome)
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_encoded}"
            df = pd.read_csv(url)
            if not df.empty and len(df.columns) > 1: return df
        except Exception: continue
    return pd.DataFrame()

df_dividas = carregar_aba(["Dividas", "Dívidas"])
df_entradas = carregar_aba(["Entradas", "Entradas Agosto"])
df_fixas = carregar_aba(["Parcelamentos Fixos", "Dividas Fixas"])
df_saidas = carregar_aba(["Saídas", "Saidas", "Gastos Setembro"])

# --- PROCESSAMENTO DOS DADOS DAS 4 ABAS ---
try:
    col_val_ent = [c for c in df_entradas.columns if 'Total' in c or 'Valor' in c][0]
    col_tipo_rec = [c for c in df_entradas.columns if 'Recebimento' in c or 'Tipo' in c][0]
    df_entradas['Valor_Clean'] = df_entradas[col_val_ent].apply(limpar_valor)

    total_entradas_pix = df_entradas[df_entradas[col_tipo_rec].astype(str).str.contains('PIX', case=False, na=False)]['Valor_Clean'].sum()
    total_entradas_vr = df_entradas[df_entradas[col_tipo_rec].astype(str).str.contains('VR|Crédito', case=False, na=False)]['Valor_Clean'].sum()

    col_tipo_ent = [c for c in df_entradas.columns if 'Tipo de Entrada' in c or 'Tipo' in c][0]
    entradas_salario_pix = df_entradas[df_entradas[col_tipo_ent].astype(str).str.contains('Salário|Transporte', case=False, na=False)]['Valor_Clean'].sum()
    entradas_adiantamento_pix = df_entradas[df_entradas[col_tipo_ent].astype(str).str.contains('Adiantamento', case=False, na=False)]['Valor_Clean'].sum()
except Exception:
    total_entradas_pix, total_entradas_vr = 3902.30, 682.50
    entradas_salario_pix, entradas_adiantamento_pix = 2052.30, 1850.00

vr_total = total_entradas_vr if total_entradas_vr > 0 else 682.50
vr_mae = 500.00
vr_disponivel_livre = max(0.0, vr_total - vr_mae)

if not df_saidas.empty:
    try:
        col_val_sai = [c for c in df_saidas.columns if 'Valor' in c][0]
        cols_tipo_all = [c for c in df_saidas.columns if 'Tipo' in c]
        col_tipo_sai = cols_tipo_all[1] if len(cols_tipo_all) > 1 else df_saidas.columns[3]
        df_saidas['Valor_Clean'] = df_saidas[col_val_sai].apply(limpar_valor)
        
        gasto_pix = df_saidas[df_saidas[col_tipo_sai].astype(str).str.contains('PIX', case=False, na=False)]['Valor_Clean'].sum()
        gasto_vr = df_saidas[df_saidas[col_tipo_sai].astype(str).str.contains('VR|Flash', case=False, na=False)]['Valor_Clean'].sum()
        
        col_desc_sai = [c for c in df_saidas.columns if 'Descrição' in c or 'Gasto' in c][0]
        is_gas = df_saidas[col_desc_sai].astype(str).str.contains('Gasolina', case=False, na=False)
        is_lucca = df_saidas[col_desc_sai].astype(str).str.contains('Fralda|Leite', case=False, na=False)
        
        gas_vr = df_saidas[is_gas & df_saidas[col_tipo_sai].astype(str).str.contains('VR|Flash', case=False, na=False)]['Valor_Clean'].sum()
        gas_pix = df_saidas[is_gas & df_saidas[col_tipo_sai].astype(str).str.contains('PIX', case=False, na=False)]['Valor_Clean'].sum()
        
        lucca_vr = df_saidas[is_lucca & df_saidas[col_tipo_sai].astype(str).str.contains('VR|Flash', case=False, na=False)]['Valor_Clean'].sum()
        lucca_pix = df_saidas[is_lucca & df_saidas[col_tipo_sai].astype(str).str.contains('PIX', case=False, na=False)]['Valor_Clean'].sum()
    except Exception:
        gasto_pix, gasto_vr = 82.83, 175.74
        gas_vr, gas_pix = 50.00, 0.0
        lucca_vr, lucca_pix = 38.90, 0.0
else:
    gasto_pix, gasto_vr = 82.83, 175.74
    gas_vr, gas_pix = 50.00, 0.0
    lucca_vr, lucca_pix = 38.90, 0.0

saldo_vr_restante = max(0.0, vr_disponivel_livre - gasto_vr)

try:
    col_val_fix = [c for c in df_fixas.columns if 'Valor' in c][0]
    df_fixas['Valor_Clean'] = df_fixas[col_val_fix].apply(limpar_valor)
    col_janela = [c for c in df_fixas.columns if 'Janela' in c][0]

    fixas_salario = df_fixas[df_fixas[col_janela].astype(str).str.contains('Salário', case=False, na=False)]['Valor_Clean'].sum()
    fixas_adiantamento = df_fixas[df_fixas[col_janela].astype(str).str.contains('Adiantamento', case=False, na=False)]['Valor_Clean'].sum()
except Exception:
    fixas_salario, fixas_adiantamento = 332.83, 1550.00

acordo_ml = 204.41
comp_salario = fixas_salario if fixas_salario > 0 else (332.83 + acordo_ml)
comp_adiantamento = fixas_adiantamento if fixas_adiantamento > 0 else 1550.00
total_despesas_fixas = comp_salario + comp_adiantamento

meta_gas = 400.00
meta_lucca = 480.00
meta_essenciais = meta_gas + meta_lucca

gasto_total_gas = gas_vr + gas_pix
gasto_total_lucca = lucca_vr + lucca_pix
gasto_total_essenciais = gasto_total_gas + gasto_total_lucca

resta_meta_essenciais = max(0.0, meta_essenciais - gasto_total_essenciais)
reserva_pix_essenciais = max(0.0, resta_meta_essenciais - saldo_vr_restante)

sobra_liquida_mes = total_entradas_pix - total_despesas_fixas - reserva_pix_essenciais
pct_sobra = (sobra_liquida_mes / total_entradas_pix) * 100 if total_entradas_pix > 0 else 0

# --- TOPO: TÍTULO FINANCEIRO + FILTRO DE MESES ---
col_head1, col_head2 = st.columns([1, 2])
with col_head1:
    st.markdown("<h1 style='margin:0; font-size:2.2rem; font-weight:800; color:#0F172A;'>FINANCEIRO <span style='color:#FF5722;'>.</span></h1>", unsafe_allow_html=True)

with col_head2:
    st.markdown("""
    <div style="display:flex; gap:6px; justify-content:flex-end; align-items:center; margin-top:10px;">
        <span style="font-size:0.8rem; font-weight:bold; color:#64748B; margin-right:8px;">Mês:</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">jan</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">fev</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">mar</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">abr</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">mai</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">jun</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">jul</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">ago</span>
        <span style="background:#0F172A; color:white; padding:4px 12px; border-radius:6px; font-size:0.8rem; font-weight:bold;">set</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">out</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">nov</span>
        <span style="background:#E2E8F0; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; color:#475569;">dez</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

# --- PRIMEIRA LINHA: FLUXO DE KPIS + MEDIDOR DE META DE ESSENCIAIS ---
col_top_flow, col_top_gauge = st.columns([3, 1])

with col_top_flow:
    st.markdown(f"""
    <div class="kpi-flow-wrapper">
        <div class="kpi-item">
            <div class="kpi-title">Despesa Fixa</div>
            <div class="val-orange">{fmt_brl(total_despesas_fixas)}</div>
            <div class="val-sub">Carro + Mãe + Acordos</div>
        </div>
        <div class="arrow">➔</div>
        <div class="kpi-item">
            <div class="kpi-title">Receita Total PIX</div>
            <div class="val-navy">{fmt_brl(total_entradas_pix)}</div>
            <div class="val-sub">Salário + Adiantamento</div>
        </div>
        <div class="arrow">➔</div>
        <div class="kpi-item">
            <div class="kpi-title">% Sobra Líquida</div>
            <div class="val-green">{pct_sobra:.1f}%</div>
            <div class="val-sub">Margem do Mês</div>
        </div>
        <div class="arrow">➔</div>
        <div class="kpi-item">
            <div class="kpi-title">Sobra Livre Bolso</div>
            <div class="val-green">{fmt_brl(sobra_liquida_mes)}</div>
            <div class="val-sub">Livre para Quitação</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_top_gauge:
    pct_essenciais_usado = min(100.0, (gasto_total_essenciais / meta_essenciais) * 100) if meta_essenciais > 0 else 0
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = gasto_total_essenciais,
        number = {'prefix': "R$ ", 'font': {'size': 18, 'color': '#0F172A'}},
        gauge = {
            'axis': {'range': [None, meta_essenciais], 'tickwidth': 1, 'tickcolor': "#CBD5E1"},
            'bar': {'color': "#FF5722"},
            'bgcolor': "#F1F5F9",
            'bordercolor': "#CBD5E1",
            'steps': [
                {'range': [0, meta_essenciais*0.5], 'color': '#E2E8F0'},
                {'range': [meta_essenciais*0.5, meta_essenciais], 'color': '#CBD5E1'}
            ],
        }
    ))
    fig_gauge.update_layout(height=110, margin=dict(l=10, r=10, t=25, b=5), paper_bgcolor='rgba(0,0,0,0)')
    
    st.markdown('<div class="bi-card"><div class="card-header-orange">🎯 Meta de Essenciais (Gasolina/Lucca)</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# --- SEGUNDA LINHA: DESPESA OPERACIONAL MENSAL VS RECEITA OPERACIONAL MENSAL ---
col_mid_left, col_mid_right = st.columns([1, 1])

with col_mid_left:
    st.markdown('<div class="bi-card"><div class="card-header-orange">📊 Despesa Operacional & Essenciais</div>', unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns([1.2, 1])
    
    with col_chart1:
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        despesas_historico = [2100, 2200, 2150, 2300, 2250, 2400, 2350, 2500, total_despesas_fixas + gasto_total_essenciais, 0, 0, 0]
        df_hist = pd.DataFrame({'Mês': months, 'Despesa': despesas_historico})
        
        fig_bar_exp = px.bar(df_hist, x='Mês', y='Despesa', text_auto='.2s', color_discrete_sequence=['#FF5722'])
        fig_bar_exp.update_layout(height=210, margin=dict(l=5, r=5, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_bar_exp, use_container_width=True, config={'displayModeBar': False})
        
    with col_chart2:
        df_cat = pd.DataFrame({
            'Categoria': ['Carro', 'Lucca', 'Gasolina', 'Mãe', 'Acordos'],
            'Valor': [1300.0, meta_lucca, meta_gas, 500.0, acordo_ml]
        })
        fig_donut_cat = px.pie(df_cat, values='Valor', names='Categoria', hole=0.5, color_discrete_sequence=['#FF5722', '#10B981', '#3B82F6', '#0F172A', '#8B5CF6'])
        fig_donut_cat.update_layout(height=210, margin=dict(l=5, r=5, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_donut_cat, use_container_width=True, config={'displayModeBar': False})
        
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid_right:
    st.markdown('<div class="bi-card"><div class="card-header-navy">📈 Receita Operacional & Janelas</div>', unsafe_allow_html=True)
    
    col_rec1, col_rec2 = st.columns([1.3, 1])
    
    with col_rec1:
        receita_historico = [3800, 3850, 3800, 3900, 3850, 3900, 3900, 3900, total_entradas_pix, 0, 0, 0]
        df_rec = pd.DataFrame({'Mês': months, 'Receita': receita_historico})
        
        fig_bar_rec = px.bar(df_rec, x='Mês', y='Receita', text_auto='.2s', color_discrete_sequence=['#0F172A'])
        fig_bar_rec.update_layout(height=210, margin=dict(l=5, r=5, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_bar_rec, use_container_width=True, config={'displayModeBar': False})
        
    with col_rec2:
        st.markdown(f"""
        <div style="background:#F8FAFC; padding:12px; border-radius:8px; border:1px solid #E2E8F0; margin-top:5px;">
            <div style="font-size:0.75rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">📅 Janela 04/09 (Salário)</div>
            <div style="font-size:1.1rem; font-weight:800; color:#10B981;">{fmt_brl(entradas_salario_pix)}</div>
            <small style="color:#64748B;">Fixas/Acordos: {fmt_brl(comp_salario)}</small>
            <hr style="margin:6px 0; border:0.5px solid #E2E8F0;">
            <div style="font-size:0.75rem; font-weight:bold; color:#0F172A; margin-bottom:4px;">📅 Janela 15/09 (Adiantamento)</div>
            <div style="font-size:1.1rem; font-weight:800; color:#0F172A;">{fmt_brl(entradas_adiantamento_pix)}</div>
            <small style="color:#64748B;">Fixas Carro/Mãe: {fmt_brl(comp_adiantamento)}</small>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- TERCEIRA LINHA: 3 CARDS DA PARTE INFERIOR ---
col_bot1, col_bot2, col_bot3 = st.columns([1, 1.2, 1])

with col_bot1:
    st.markdown('<div class="bi-card"><div class="card-header-navy">💳 Dívidas & Acordos de Quitação</div>', unsafe_allow_html=True)
    if not df_dividas.empty:
        try:
            col_nome_div = [c for c in df_dividas.columns if 'Nome' in c or 'Dívida' in c][0]
            col_val_div = [c for c in df_dividas.columns if 'Valor' in c or 'Saldo' in c][0]
            df_dividas['Val_Clean'] = df_dividas[col_val_div].apply(limpar_valor)
            
            top_dividas = df_dividas.sort_values(by='Val_Clean', ascending=False).head(5)
            fig_div_bar = px.bar(top_dividas, y=col_nome_div, x='Val_Clean', orientation='h', text_auto='.2s', color_discrete_sequence=['#1E293B'])
            fig_div_bar.update_layout(height=200, margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_div_bar, use_container_width=True, config={'displayModeBar': False})
        except:
            st.write("Exibindo saldo de dívidas em processamento...")
    else:
        st.write("Sincronizando tabela de dívidas...")
    st.markdown('</div>', unsafe_allow_html=True)

with col_bot2:
    st.markdown('<div class="bi-card"><div class="card-header-navy">📋 Demonstrativo de Extrato de Saídas</div>', unsafe_allow_html=True)
    if not df_saidas.empty:
        try:
            display_cols = [c for c in df_saidas.columns if 'Valor_Clean' not in c][:4]
            st.dataframe(df_saidas[display_cols].head(5), use_container_width=True, height=190)
        except:
            st.write("Processando extrato de saídas...")
    else:
        st.write("Carregando lançamentos recentes...")
    st.markdown('</div>', unsafe_allow_html=True)

with col_bot3:
    st.markdown('<div class="bi-card"><div class="card-header-navy">🍩 Meio de Pagamento (VR vs PIX)</div>', unsafe_allow_html=True)
    df_meio = pd.DataFrame({
        'Meio': ['VR (Flash)', 'PIX / Dinheiro'],
        'Gasto': [gasto_vr, gasto_pix]
    })
    fig_donut_meio = px.pie(df_meio, values='Gasto', names='Meio', hole=0.6, color_discrete_sequence=['#3B82F6', '#10B981'])
    fig_donut_meio.update_layout(height=200, margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
    st.plotly_chart(fig_donut_meio, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
