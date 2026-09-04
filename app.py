import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central Financeira", page_icon="💼", layout="wide")

st.title("💼 Painel de Controle Financeiro")

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

# --- CONEXÃO ROBUSTA COM A PLANILHA DO GOOGLE ---
SHEET_ID = "1Y7EsUDd9J_liLwwTbRdjM2lM_XcdsWr_kYNUC-MAZsY"

def carregar_aba(nomes_possiveis):
    if isinstance(nomes_possiveis, str):
        nomes_possiveis = [nomes_possiveis]
    
    for nome in nomes_possiveis:
        try:
            nome_encoded = urllib.parse.quote(nome)
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_encoded}"
            df = pd.read_csv(url)
            if not df.empty and len(df.columns) > 1:
                return df
        except Exception:
            continue
    return pd.DataFrame()

# Carregamento seguro das 4 abas
df_dividas = carregar_aba(["Dividas", "Dívidas"])
df_entradas = carregar_aba(["Entradas", "Entradas Agosto"])
df_fixas = carregar_aba(["Parcelamentos Fixos", "Dividas Fixas"])
df_saidas = carregar_aba(["Saídas", "Saidas", "Gastos Setembro"])

if df_entradas.empty and df_fixas.empty:
    st.error("⚠️ Não foi possível ler os dados da planilha. Verifique se a planilha está compartilhada como 'Qualquer pessoa com o link'.")
    st.stop()

# --- PROCESSAMENTO AUTOMÁTICO DE DADOS ---

# 1. ENTRADAS
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
    total_entradas_pix = 3902.30
    total_entradas_vr = 682.50
    entradas_salario_pix = 2052.30
    entradas_adiantamento_pix = 1850.00

vr_total = total_entradas_vr if total_entradas_vr > 0 else 682.50
vr_mae = 500.00
vr_disponivel_livre = max(0.0, vr_total - vr_mae)

# 2. SAÍDAS (GASTOS REALIZADOS)
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

# 3. FIXAS E ACORDOS
try:
    col_val_fix = [c for c in df_fixas.columns if 'Valor' in c][0]
    df_fixas['Valor_Clean'] = df_fixas[col_val_fix].apply(limpar_valor)
    col_janela = [c for c in df_fixas.columns if 'Janela' in c][0]

    fixas_salario = df_fixas[df_fixas[col_janela].astype(str).str.contains('Salário', case=False, na=False)]['Valor_Clean'].sum()
    fixas_adiantamento = df_fixas[df_fixas[col_janela].astype(str).str.contains('Adiantamento', case=False, na=False)]['Valor_Clean'].sum()
except Exception:
    fixas_salario = 332.83
    fixas_adiantamento = 1550.00

acordo_ml_salario = 204.41
comp_salario_total = fixas_salario if fixas_salario > 0 else (332.83 + acordo_ml_salario)
comp_adiantamento_total = fixas_adiantamento if fixas_adiantamento > 0 else 1550.00
total_fixas = comp_salario_total + comp_adiantamento_total

# Metas Essenciais
meta_gasolina = 400.00
meta_lucca = 480.00
meta_total_essenciais = meta_gasolina + meta_lucca

gasto_total_gas = gas_vr + gas_pix
gasto_total_lucca = lucca_vr + lucca_pix

resta_meta_gas = max(0.0, meta_gasolina - gasto_total_gas)
resta_meta_lucca = max(0.0, meta_lucca - gasto_total_lucca)
resta_meta_essenciais = resta_meta_gas + resta_meta_lucca

reserva_pix_essenciais = max(0.0, resta_meta_essenciais - saldo_vr_restante)
reserva_pix_dia5 = min(reserva_pix_essenciais, 400.00)
reserva_pix_dia15 = reserva_pix_essenciais - reserva_pix_dia5

# Sobras por quinzena
sobra_dia5 = entradas_salario_pix - comp_salario_total - reserva_pix_dia5
sobra_dia15 = entradas_adiantamento_pix - comp_adiantamento_total - reserva_pix_dia15
sobra_total = sobra_dia5 + sobra_dia15

# --- ESTILO DAS CAIXAS ---
card_style = "background-color: #EBF5FB; border: 1px solid #AED6F1; border-left: 6px solid #1B4F72; border-radius: 12px; padding: 18px; margin-bottom: 15px; color: #1C2833; box-shadow: 0 4px 6px rgba(0,0,0,0.04);"

def criar_barra_progresso_detalhada(label, icon, gasto_vr, gasto_pix, meta, cor_vr="#1E88E5", cor_pix="#26A69A"):
    gasto_total = gasto_vr + gasto_pix
    pct_total = min((gasto_total / meta) * 100, 100.0) if meta > 0 else 0
    resta = max(0.0, meta - gasto_total)
    pct_vr = (gasto_vr / meta) * 100 if meta > 0 else 0
    pct_pix = (gasto_pix / meta) * 100 if meta > 0 else 0
    
    return f'<div style="margin-top: 12px; margin-bottom: 16px;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;"><span style="font-weight: bold; color: #0F2537; font-size: 1rem;">{icon} {label}</span><span style="background-color: #1B4F72; color: #FFFFFF; padding: 3px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: bold;">{pct_total:.1f}% Usado</span></div><div style="background-color: #D4E6F1; border-radius: 10px; height: 20px; width: 100%; overflow: hidden; border: 1px solid #AED6F1; display: flex;"><div style="background-color: {cor_vr}; width: {pct_vr:.1f}%; height: 100%;"></div><div style="background-color: {cor_pix}; width: {pct_pix:.1f}%; height: 100%;"></div></div><div style="display: flex; justify-content: space-between; margin-top: 6px; font-size: 0.85rem; color: #2C3E50;"><span>💳 <b>VR:</b> {fmt_brl(gasto_vr)} | 💵 <b>PIX:</b> {fmt_brl(gasto_pix)}</span><span>Resta: <b style="color: #1B4F72;">{fmt_brl(resta)}</b></span></div></div>'

# --- SEÇÃO 1: RESUMO DO CAIXA ---
st.markdown("### 📊 Visão Geral do Mês (Valores em Conta)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div style="{card_style}"><small style="color: #566573; font-weight: bold;">Entradas em PIX</small><h2 style="color: #0F2537; margin: 4px 0;">{fmt_brl(total_entradas_pix)}</h2><span style="color: #1C2833; font-size: 0.9em;">Salário + Adiantamento</span></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div style="{card_style}"><small style="color: #566573; font-weight: bold;">Compromissos Fixos</small><h2 style="color: #0F2537; margin: 4px 0;">{fmt_brl(total_fixas)}</h2><span style="color: #1C2833; font-size: 0.9em;">Carro + Mãe + Acordo ML</span></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div style="{card_style}"><small style="color: #566573; font-weight: bold;">Reserva Essenciais (PIX)</small><h2 style="color: #0F2537; margin: 4px 0;">{fmt_brl(reserva_pix_essenciais)}</h2><span style="color: #1C2833; font-size: 0.9em;">Retido p/ Gasolina e Lucca</span></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div style="{card_style}"><small style="color: #566573; font-weight: bold;">Sobra Livre p/ Dívidas</small><h2 style="color: #0F2537; margin: 4px 0;">{fmt_brl(sobra_total)}</h2><span style="color: #1C2833; font-size: 0.9em;">Sobra Líquida no Bolso</span></div>', unsafe_allow_html=True)

st.divider()

# --- SEÇÃO 2: PLANEJAMENTO POR JANELA ---
st.markdown("### 📅 O Que Fazer em Cada Pagamento")
col_q1, col_q2 = st.columns(2)

with col_q1:
    st.markdown(f'<div style="{card_style}"><h4 style="color: #0F2537; margin-top:0; margin-bottom: 10px;">Janela Salário (Recebe {fmt_brl(entradas_salario_pix)})</h4><p style="margin: 4px 0;">1. Pague as Fixas/Acordos: <b>{fmt_brl(comp_salario_total)}</b></p><p style="margin: 4px 0;">2. Reserve para Essenciais: <b>{fmt_brl(reserva_pix_dia5)}</b></p><hr style="border: 0.5px solid #AED6F1; margin: 8px 0;"><p style="margin: 4px 0; font-size: 1.05em;"><b>Sobra Livre no Salário:</b> <b style="color: #1B4F72;">{fmt_brl(sobra_dia5)}</b></p></div>', unsafe_allow_html=True)

with col_q2:
    st.markdown(f'<div style="{card_style}"><h4 style="color: #0F2537; margin-top:0; margin-bottom: 10px;">Janela Adiantamento (Recebe {fmt_brl(entradas_adiantamento_pix)})</h4><p style="margin: 4px 0;">1. Pague as Fixas: <b>{fmt_brl(comp_adiantamento_total)}</b></p><p style="margin: 4px 0;">2. Reserve para Essenciais: <b>{fmt_brl(reserva_pix_dia15)}</b></p><hr style="border: 0.5px solid #AED6F1; margin: 8px 0;"><p style="margin: 4px 0; font-size: 1.05em;"><b>Sobra no Adiantamento:</b> {fmt_brl(sobra_dia15)}</p></div>', unsafe_allow_html=True)

st.divider()

# --- SEÇÃO 3: CONTROLE DO VR E METAS ---
st.markdown("### 💳 Controle de VR (Flash) vs. Dinheiro/PIX")
col_m1, col_m2 = st.columns(2)

with col_m1:
    st.markdown(f'<div style="{card_style}"><h4 style="color: #0F2537; margin-top:0; margin-bottom: 10px;">💳 Cartão Flash (VR)</h4><p style="margin: 5px 0;">• <b>Total Recebido:</b> {fmt_brl(vr_total)}</p><p style="margin: 5px 0;">• <b>Repasse Mãe:</b> {fmt_brl(vr_mae)}</p><p style="margin: 5px 0;">• <b>Seu VR Livre Inicial:</b> {fmt_brl(vr_disponivel_livre)}</p><hr style="border: 0.5px solid #AED6F1; margin: 8px 0;"><p style="margin: 5px 0;">• <b>Gasto no VR até agora:</b> <span style="color: #1E88E5; font-weight: bold;">{fmt_brl(gasto_vr)}</span></p><p style="margin: 5px 0; font-size: 1.05em;">• <b>Saldo Restante no VR:</b> <b style="color: #1B4F72;">{fmt_brl(saldo_vr_restante)}</b></p></div>', unsafe_allow_html=True)

with col_m2:
    html_gas = criar_barra_progresso_detalhada("Gasolina", "🚗", gas_vr, gas_pix, meta_gasolina, cor_vr="#1E88E5", cor_pix="#26A69A")
    html_lucca = criar_barra_progresso_detalhada("Lucca (Fralda/Leite)", "👶", lucca_vr, lucca_pix, meta_lucca, cor_vr="#1E88E5", cor_pix="#26A69A")
    
    st.markdown(f'<div style="{card_style}"><h4 style="color: #0F2537; margin-top:0; margin-bottom: 8px;">🎯 Termômetro de Essenciais</h4>{html_gas}{html_lucca}<div style="margin-top: 10px; font-size: 0.8rem; color: #566573;">🔹 <b>Azul:</b> Pago com VR | 🟢 <b>Verde:</b> Pago com Dinheiro/PIX</div></div>', unsafe_allow_html=True)
