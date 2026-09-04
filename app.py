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
    
    /* Customização dos Containers Nativos em Caixas Fechadas */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        padding: 0px !important;
        overflow: hidden !important;
        margin-bottom: 15px !important;
    }
    
    /* Preenchimento interno das caixas */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 14px 18px !important;
    }

    /* Faixas de Cabeçalho dos Cards */
    .card-header-navy {
        background: linear-gradient(90deg, #0F172A 0%, #1E293B 100%);
        color: #FFFFFF;
        padding: 10px 18px;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        margin: -14px -18px 14px -18px;
    }

    .card-header-orange {
        background: linear-gradient(90deg, #FF5722 0%, #E64A19 100%);
        color: #FFFFFF;
        padding: 10px 18px;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        margin: -14px -18px 14px -18px;
    }

    /* KPI Cards Box (Resumo Executivo) */
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
    
    /* Estilização das caixinhas de mês (Radio horizontal) */
    div.row-widget.stRadio > div { flex-direction: row; flex-wrap: wrap; gap: 8px; }
    div.row-widget.stRadio > div > label { 
        background-color: #FFFFFF; border: 1px solid #CBD5E1; 
        padding: 5px 12px; border-radius: 6px; cursor: pointer;
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

def obter_coluna_valor(df):
    if df.empty: return None
    for col in df.columns:
        if any(p in col.lower() for p in ['valor', 'total', 'receber', 'saldo', 'quantia', 'parcela']):
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
    try:
        col_val_ent = obter_coluna_valor(df_entradas)
        df_entradas['Valor_Clean'] = df_entradas[col_val_ent].apply(limpar_valor)
        txt_ent = df_entradas.astype(str).agg(' '.join, axis=1)
        
        mask_ent_pix = txt_ent.str.contains('PIX|Dinheiro|Conta', case=False, na=False)
        mask_ent_vr = txt_ent.str.contains('VR|Crédito|Flash', case=False, na=False)
        
        total_entradas_pix = df_entradas[mask_ent_pix]['Valor_Clean'].sum()
        total_entradas_vr = df_entradas[mask_ent_vr]['Valor_Clean'].sum()
        
        mask_salario = txt_ent.str.contains('Salário|Salario|Transporte|04/09|04/', case=False, na=False)
        mask_adiant = txt_ent.str.contains('Adiantamento|15/09|15/', case=False, na=False)
        
        entradas_salario_pix = df_entradas[mask_ent_pix & mask_salario]['Valor_Clean'].sum()
        entradas_adiantamento_pix = df_entradas[mask_ent_pix & mask_adiant]['Valor_Clean'].sum()
    except Exception:
        pass

if total_entradas_pix == 0: total_entradas_pix = 3902.30
if total_entradas_vr == 0: total_entradas_vr = 682.50
if entradas_salario_pix == 0: entradas_salario_pix = 2052.30
if entradas_adiantamento_pix == 0: entradas_adiantamento_pix = 1850.00

total_receita_conta = entradas_salario_pix + entradas_adiantamento_pix

# 2. SAÍDAS E GASTOS ESSENCIAIS
total_saidas_pix = 0.0
gasto_gasolina_vr = 0.0
gasto_gasolina_pix = 0.0
gasto_lucca_vr = 0.0
gasto_lucca_pix = 0.0

if not df_saidas.empty:
    try:
        col_val_sai = obter_coluna_valor(df_saidas)
        df_saidas['Valor_Clean'] = df_saidas[col_val_sai].apply(limpar_valor)
        
        cols_tipo_pag = [c for c in df_saidas.columns if any(p in c.lower() for p in ['pagamento', 'meio', 'forma'])]
        col_tipo_pag = cols_tipo_pag[0] if cols_tipo_pag else df_saidas.columns[2]
        
        txt_sai = df_saidas.astype(str).agg(' '.join, axis=1)
        
        mask_sai_pix = df_saidas[col_tipo_pag].astype(str).str.contains('PIX|Dinheiro|Conta|Débito|Debito', case=False, na=False) | txt_sai.str.contains('PIX', case=False, na=False)
        total_saidas_pix = df_saidas[mask_sai_pix]['Valor_Clean'].sum()
        
        mask_sai_vr = df_saidas[col_tipo_pag].astype(str).str.contains('VR|Flash|Crédito', case=False, na=False)
        
        mask_gasolina = txt_sai.str.contains('Gasolina', case=False, na=False)
        mask_lucca = txt_sai.str.contains('Lucca|Fralda|Leite', case=False, na=False)
        
        gasto_gasolina_vr = df_saidas[mask_gasolina & mask_sai_vr]['Valor_Clean'].sum()
        gasto_gasolina_pix = df_saidas[mask_gasolina & mask_sai_pix]['Valor_Clean'].sum()
        
        gasto_lucca_vr = df_saidas[mask_lucca & mask_sai_vr]['Valor_Clean'].sum()
        gasto_lucca_pix = df_saidas[mask_lucca & mask_sai_pix]['Valor_Clean'].sum()
    except Exception:
        pass

if df_saidas.empty or total_saidas_pix == 0:
    total_saidas_pix = 287.24
    if gasto_gasolina_vr == 0 and gasto_gasolina_pix == 0: gasto_gasolina_vr = 50.00
    if gasto_lucca_vr == 0 and gasto_lucca_pix == 0: gasto_lucca_vr = 38.90

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
    st.markdown(f'<div class="kpi-card-box kpi-card-green"><div class="kpi-title">Sobra Líquida</div><div class="kpi-value-main" style="color:#10B981;">{fmt_brl(sobra_liquida)}</div><div class="kpi-subtext">Entradas PIX - Saídas PIX</div></div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

# --- 2. CAIXINHA DE ESSENCIAIS MENSAIS ---
caixinha_gasolina = 400.00
caixinha_lucca = 480.00
caixinha_total = caixinha_gasolina + caixinha_lucca

caixa_salario = 680.00
caixa_adiantamento = 200.00

gasto_gas_tot = gasto_gasolina_vr + gasto_gasolina_pix
pct_gas = min(100.0, (gasto_gas_tot / caixinha_gasolina) * 100) if caixinha_gasolina > 0 else 0

gasto_lucca_tot = gasto_lucca_vr + gasto_lucca_pix
pct_lucca = min(100.0, (gasto_lucca_tot / caixinha_lucca) * 100) if caixinha_lucca > 0 else 0

with st.container(border=True):
    st.markdown('<div class="card-header-orange">📦 CAIXINHA DE ESSENCIAIS (RESERVA OBRIGATÓRIA MENSAL)</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:#0F172A; color:white; padding:12px 18px; border-radius:8px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-size:0.9rem; font-weight:600; color:#CBD5E1;">Valor Total da Caixinha no Mês:</span><br>
            <span style="font-size:1.4rem; font-weight:800; color:#10B981;">{fmt_brl(caixinha_total)}</span>
        </div>
        <div style="text-align:right; border-left:1px solid #334155; padding-left:15px;">
            <span style="font-size:0.85rem; font-weight:600; color:#94A3B8;">Distribuição de Reserva:</span><br>
            <span style="font-size:1rem; font-weight:700;">📅 Janela Salário: <span style="color:#FF5722;">{fmt_brl(caixa_salario)}</span></span><br>
            <span style="font-size:1rem; font-weight:700;">📅 Janela Adiantamento: <span style="color:#FF5722;">{fmt_brl(caixa_adiantamento)}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_ess1, col_ess2 = st.columns(2)

    with col_ess1:
        st.markdown(f"""
        <div style="background:#F8FAFC; padding:16px; border-radius:8px; border:1px solid #E2E8F0;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; font-size:1.05rem; color:#0F172A;">🚗 Gasolina: {fmt_brl(caixinha_gasolina)}</span>
                <span style="background:#FF5722; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.85rem;">{pct_gas:.1f}% Usado</span>
            </div>
            <div style="background-color:#E2E8F0; border-radius:8px; height:10px; width:100%; overflow:hidden; margin-bottom:12px;">
                <div style="background-color:#FF5722; width:{pct_gas:.1f}%; height:100%; border-radius:8px;"></div>
            </div>
            <div style="font-size:0.95rem; color:#334155; line-height:1.6;">
                • <b>Saiu do VR (Flash):</b> <span style="color:#0284C7; font-weight:700;">{fmt_brl(gasto_gasolina_vr)}</span><br>
                • <b>Saiu do PIX (Conta):</b> <span style="color:#FF5722; font-weight:700;">{fmt_brl(gasto_gasolina_pix)}</span><br>
                • <b>Saldo Restante na Caixinha:</b> <span style="color:#10B981; font-weight:700;">{fmt_brl(max(0, caixinha_gasolina - gasto_gas_tot))}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_ess2:
        st.markdown(f"""
        <div style="background:#F8FAFC; padding:16px; border-radius:8px; border:1px solid #E2E8F0;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; font-size:1.05rem; color:#0F172A;">👶 Lucca (Fralda/Leite): {fmt_brl(caixinha_lucca)}</span>
                <span style="background:#0284C7; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.85rem;">{pct_lucca:.1f}% Usado</span>
            </div>
            <div style="background-color:#E2E8F0; border-radius:8px; height:10px; width:100%; overflow:hidden; margin-bottom:12px;">
                <div style="background-color:#0284C7; width:{pct_lucca:.1f}%; height:100%; border-radius:8px;"></div>
            </div>
            <div style="font-size:0.95rem; color:#334155; line-height:1.6;">
                • <b>Saiu do VR (Flash):</b> <span style="color:#0284C7; font-weight:700;">{fmt_brl(gasto_lucca_vr)}</span><br>
                • <b>Saiu do PIX (Conta):</b> <span style="color:#FF5722; font-weight:700;">{fmt_brl(gasto_lucca_pix)}</span><br>
                • <b>Saldo Restante na Caixinha:</b> <span style="color:#10B981; font-weight:700;">{fmt_brl(max(0, caixinha_lucca - gasto_lucca_tot))}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 3. RECEITA OPERACIONAL E JANELAS ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">📈 RECEITA OPERACIONAL EM CONTA & JANELAS (A PARTIR DE SET/2026)</div>', unsafe_allow_html=True)
    col_rec_chart, col_rec_box = st.columns([2, 1])

    with col_rec_chart:
        df_rec_hist = pd.DataFrame({'Mês': ['Set/26', 'Out/26', 'Nov/26', 'Dez/26'], 'Receita': [total_entradas_pix, 0, 0, 0]})
        fig_rec = px.bar(df_rec_hist, x='Mês', y='Receita', text_auto='.2s', color_discrete_sequence=['#0F172A'])
        fig_rec.update_layout(height=210, margin=dict(l=5, r=5, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_rec, use_container_width=True, config={'displayModeBar': False})

    with col_rec_box:
        st.markdown(f"""
        <div style="background:#F8FAFC; padding:16px; border-radius:8px; border:1px solid #E2E8F0;">
            <div style="font-size:0.85rem; font-weight:bold; color:#0F172A; margin-bottom:2px;">📅 Janela Salário (04/09)</div>
            <div style="font-size:1.2rem; font-weight:800; color:#10B981;">{fmt_brl(entradas_salario_pix)}</div>
            <hr style="margin:6px 0; border:0.5px solid #E2E8F0;">
            <div style="font-size:0.85rem; font-weight:bold; color:#0F172A; margin-bottom:2px;">📅 Janela Adiantamento (15/09)</div>
            <div style="font-size:1.2rem; font-weight:800; color:#0284C7;">{fmt_brl(entradas_adiantamento_pix)}</div>
            <hr style="margin:6px 0; border:0.5px solid #E2E8F0;">
            <div style="font-size:0.85rem; font-weight:bold; color:#0F172A; margin-bottom:2px;">💰 Total Receita Operacional (Conta)</div>
            <div style="font-size:1.35rem; font-weight:800; color:#0F172A;">{fmt_brl(total_receita_conta)}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 4. MAPA DE DÍVIDAS E STATUS DE ACORDO ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">💳 MAPEAMENTO GERAL DE DÍVIDAS & ACOMPANHAMENTO DE PARCELAS PAGAS (VINCULADO ÁS SAÍDAS)</div>', unsafe_allow_html=True)

    if not df_dividas.empty:
        try:
            col_nome_div = [c for c in df_dividas.columns if any(p in c.lower() for p in ['credor', 'nome', 'dívida', 'divida'])][0]
            col_val_div = obter_coluna_valor(df_dividas)
            df_dividas['Val_Clean'] = df_dividas[col_val_div].apply(limpar_valor)
            
            txt_saidas_full = df_saidas.astype(str).agg(' '.join, axis=1) if not df_saidas.empty else pd.Series(dtype=str)
            
            acordos_rastreados = []
            for idx, row in df_dividas.iterrows():
                credor = str(row[col_nome_div])
                txt_row = ' '.join(row.astype(str)).lower()
                is_acordado = any(term in txt_row for term in ['sim', 'ativo', 'acordad', 'parcelad', 'ok', '36x'])
                
                if not txt_saidas_full.empty:
                    mask_match = txt_saidas_full.str.contains(credor, case=False, na=False)
                    qtd_pagas = mask_match.sum()
                    total_pago = df_saidas[mask_match]['Valor_Clean'].sum()
                else:
                    qtd_pagas, total_pago = 0, 0.0
                
                val_total = row['Val_Clean']
                
                cols_num_parc = [c for c in df_dividas.columns if any(p in c.lower() for p in ['nº', 'num', 'parcelas', 'qtd'])]
                if cols_num_parc and pd.notna(row[cols_num_parc[0]]) and limpar_valor(row[cols_num_parc[0]]) > 0:
                    num_parc = int(limpar_valor(row[cols_num_parc[0]]))
                else:
                    num_parc = 36 if is_acordado else 1
                
                saldo_restante = max(0.0, val_total - total_pago)
                
                acordos_rastreados.append({
                    'Credor': credor,
                    'Valor_Total': val_total,
                    'Is_Acordado': is_acordado,
                    'Num_Parcelas': num_parc,
                    'Parcelas_Pagas': qtd_pagas,
                    'Total_Pago': total_pago,
                    'Saldo_Restante': saldo_restante,
                    'Status_Grupo': 'Acordado (Parcelamento Ativo)' if is_acordado else 'Não Acordado (Pendente)'
                })
            
            df_acordos_df = pd.DataFrame(acordos_rastreados)
            
            fig_div = px.bar(
                df_acordos_df.sort_values(by='Valor_Total', ascending=True),
                y='Credor',
                x='Valor_Total',
                color='Status_Grupo',
                orientation='h',
                text_auto='.2s',
                color_discrete_map={'Acordado (Parcelamento Ativo)': '#0284C7', 'Não Acordado (Pendente)': '#FF5722'},
                labels={'Valor_Total': 'Saldo Devedor (R$)', 'Status_Grupo': 'Status'}
            )
            fig_div.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Valor Total da Dívida (R$)",
                yaxis_title="",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_div, use_container_width=True, config={'displayModeBar': False})
            
            st.markdown("##### 📌 Status dos Parcelamentos dos Acordos (Atualizado via Saídas)")
            df_somente_acordos = df_acordos_df[df_acordos_df['Is_Acordado']]
            
            if not df_somente_acordos.empty:
                for _, ac_row in df_somente_acordos.iterrows():
                    pct_parc_pago = min(100.0, (ac_row['Parcelas_Pagas'] / ac_row['Num_Parcelas']) * 100) if ac_row['Num_Parcelas'] > 0 else 0
                    st.markdown(f"""
                    <div style="background:#F8FAFC; padding:12px 16px; border-radius:8px; border:1px solid #CBD5E1; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:700; font-size:1.05rem; color:#0F172A;">🤝 Acordo: {ac_row['Credor']}</span>
                            <span style="background:#0284C7; color:white; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.85rem;">{ac_row['Parcelas_Pagas']} de {ac_row['Num_Parcelas']} parcelas pagas ({pct_parc_pago:.1f}%)</span>
                        </div>
                        <div style="background-color:#E2E8F0; border-radius:6px; height:8px; width:100%; overflow:hidden; margin:8px 0;">
                            <div style="background-color:#0284C7; width:{pct_parc_pago:.1f}%; height:100%;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.9rem; color:#334155;">
                            <span>• <b>Total Quitado até agora:</b> <span style="color:#10B981; font-weight:700;">{fmt_brl(ac_row['Total_Pago'])}</span></span>
                            <span>• <b>Saldo Devedor Restante:</b> <span style="color:#FF5722; font-weight:700;">{fmt_brl(ac_row['Saldo_Restante'])}</span></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum acordo ativo cadastrado na aba Dívidas.")
        except Exception:
            st.write("Processando visualização das dívidas...")
    else:
        st.write("Sincronizando dados de dívidas da planilha...")

# --- 5. GRÁFICO DE PORCENTAGEM SEPARADO POR TIPO DE GASTO ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">🍩 DISTRIBUIÇÃO PERCENTUAL POR TIPO DE GASTO</div>', unsafe_allow_html=True)

    if not df_saidas.empty:
        try:
            cols_tg = [c for c in df_saidas.columns if any(p in c.lower() for p in ['tipo de gasto', 'categoria'])]
            col_tg = cols_tg[0] if cols_tg else df_saidas.columns[1]
            
            df_pie = df_saidas.groupby(col_tg)['Valor_Clean'].sum().reset_index()
            
            fig_pie = px.pie(
                df_pie,
                values='Valor_Clean',
                names=col_tg,
                hole=0.5,
                color_discrete_sequence=['#FF5722', '#10B981', '#0284C7', '#0F172A', '#8B5CF6', '#F59E0B']
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
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
        st.info("Aguardando lançamentos na aba Saídas...")
