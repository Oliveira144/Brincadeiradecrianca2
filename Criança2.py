import streamlit as st
import collections
import random
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Football Studio Analyzer",
    page_icon="🔮",
    layout="wide"
)

# --- Variáveis ---
mapear_emojis = {'V': '🔴', 'A': '🔵', 'E': '🟡'}
nomes = {'V': 'Casa', 'A': 'Visitante', 'E': 'Empate'}

# --- Inicialização ---
if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=50)  # Histórico maior
if 'estatisticas' not in st.session_state:
    st.session_state.estatisticas = {'Casa': 0, 'Visitante': 0, 'Empate': 0}

# --- Função: Detectar Padrão ---
def analisar_padrao(historico):
    """
    Retorna: (padrao_detectado, nivel_manipulacao, cenarios, explicacao)
    """
    if len(historico) < 2:
        return ("Nenhum Padrão", 1, {}, "Insira mais resultados para iniciar.")

    hist = list(historico)[::-1]

    # Inicializa probabilidades básicas
    prob = {'Casa': 33, 'Visitante': 33, 'Empate': 34}
    nivel = 1
    explicacao = "Analisando padrões recentes..."

    # --- Padrões de Empate ---
    if hist[0] == 'E':
        nivel = 4
        prob['Empate'] += 10
        explicacao = "Empate recente detectado. Cassino pode usar para resetar padrões."
    elif 'E' in hist[:4]:
        nivel = 3
        prob['Empate'] += 5
        explicacao = "Empate nos últimos 4 resultados. Pode indicar manipulação estratégica."

    # --- Padrões Sequenciais ---
    seq = 1
    for i in range(1, len(hist)):
        if hist[i] == hist[0]:
            seq += 1
        else:
            break

    if seq >= 3:
        nivel = 5
        lado = 'Casa' if hist[0] == 'V' else 'Visitante'
        prob[lado] += 15
        explicacao = f"Sequência longa ({seq}). Cassino tende a induzir inversão ou continuação."

    # --- Ping-Pong ---
    alternancia = True
    for i in range(min(len(hist), 6) - 1):
        if hist[i] == hist[i+1]:
            alternancia = False
            break
    if alternancia and len(hist) >= 4:
        nivel = max(nivel, 6)
        prob['Casa'] += 5
        prob['Visitante'] += 5
        explicacao = "Padrão de alternância (Ping-Pong). Possível quebra ou continuação."

    # --- Ruído Controlado (nenhum padrão claro) ---
    if nivel == 1:
        explicacao = "Ruído controlado detectado. Alta aleatoriedade simulada pelo cassino."
        prob['Empate'] += 2

    # Normaliza probabilidades
    soma = sum(prob.values())
    for k in prob:
        prob[k] = round(prob[k] / soma * 100, 1)

    # Determinar nível final baseado na variação de padrões
    if prob['Empate'] > 40 or nivel >= 6:
        nivel = min(9, nivel + 2)  # Eleva nível se manipulação forte

    # Criar cenários (3 mais prováveis)
    cenarios = sorted(prob.items(), key=lambda x: x[1], reverse=True)
    cenarios_dict = {c[0]: c[1] for c in cenarios}

    return ("Padrão Detetado", nivel, cenarios_dict, explicacao)

# --- Layout Principal ---
st.title("🔮 Football Studio Analyzer")
st.markdown("**IA para previsão e detecção de manipulação no Football Studio**")
st.markdown("---")

# --- Inserção de Resultados ---
st.subheader("1. Inserir Resultados")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🔴 Casa", use_container_width=True):
        st.session_state.historico.append('V')
        st.session_state.estatisticas['Casa'] += 1
with col2:
    if st.button("🔵 Visitante", use_container_width=True):
        st.session_state.historico.append('A')
        st.session_state.estatisticas['Visitante'] += 1
with col3:
    if st.button("🟡 Empate", use_container_width=True):
        st.session_state.historico.append('E')
        st.session_state.estatisticas['Empate'] += 1
with col4:
    if st.button("⏪ Desfazer", use_container_width=True):
        if st.session_state.historico:
            ultimo = st.session_state.historico.pop()
            st.session_state.estatisticas[nomes[ultimo]] -= 1
with col5:
    if st.button("🗑 Limpar", type="primary", use_container_width=True):
        st.session_state.historico.clear()
        for k in st.session_state.estatisticas:
            st.session_state.estatisticas[k] = 0

st.markdown("---")

# --- Histórico ---
st.subheader("2. Histórico")
historico_str = " ".join([mapear_emojis[r] for r in reversed(st.session_state.historico)])
st.markdown(f"**Mais Recente → Mais Antigo:** {historico_str if historico_str else 'Nenhum dado'}")

# --- Análise ---
st.subheader("3. Análise e Previsão")
if st.session_state.historico:
    padrao, nivel, cenarios, explicacao = analisar_padrao(list(st.session_state.historico))

    st.markdown(f"**Padrão Detectado:** `{padrao}`")
    st.markdown(f"**Nível de Manipulação:** {nivel} / 9")
    st.info(explicacao)

    st.success("### 🔍 Previsão de Cenários")
    for nome, pct in cenarios.items():
        st.markdown(f"- **{nome}: {pct}%**")

    # Gráfico de barras para probabilidades
    df_prob = pd.DataFrame(list(cenarios.items()), columns=['Lado', 'Probabilidade'])
    fig = px.bar(df_prob, x='Lado', y='Probabilidade', color='Lado', text='Probabilidade',
                 color_discrete_map={'Casa':'red','Visitante':'blue','Empate':'gold'})
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Adicione resultados para iniciar a análise.")

# Estatísticas gerais
st.markdown("---")
st.subheader("4. Estatísticas Gerais")
df_stats = pd.DataFrame(list(st.session_state.estatisticas.items()), columns=['Lado','Ocorrências'])
fig_stats = px.pie(df_stats, values='Ocorrências', names='Lado', color='Lado',
                   color_discrete_map={'Casa':'red','Visitante':'blue','Empate':'gold'})
st.plotly_chart(fig_stats, use_container_width=True)

st.markdown("<br><hr><center>⚠ Jogue com responsabilidade ⚠</center>", unsafe_allow_html=True)
