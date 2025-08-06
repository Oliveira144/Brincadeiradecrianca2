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

# --- Inicialização do Estado ---
if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=50)
if 'estatisticas' not in st.session_state:
    st.session_state.estatisticas = {'Casa': 0, 'Visitante': 0, 'Empate': 0}
if 'pesos' not in st.session_state:
    st.session_state.pesos = {
        'empate_recente': 1.0,
        'sequencia_longa': 1.0,
        'ping_pong': 1.0,
        'ruido': 1.0
    }
if 'ultima_previsao' not in st.session_state:
    st.session_state.ultima_previsao = None
if 'historico_acertos' not in st.session_state:
    st.session_state.historico_acertos = []

# --- Função de Aprendizado Adaptativo ---
def atualizar_pesos(resultado_real):
    """
    Ajusta pesos dos padrões baseado no acerto/erro da previsão anterior
    """
    if not st.session_state.ultima_previsao:
        return

    previsao, padrao_usado = st.session_state.ultima_previsao

    if previsao == resultado_real:
        # Acerto -> aumenta peso do padrão usado
        st.session_state.pesos[padrao_usado] += 0.1
        st.session_state.historico_acertos.append(1)
    else:
        # Erro -> reduz peso do padrão usado
        st.session_state.pesos[padrao_usado] = max(0.5, st.session_state.pesos[padrao_usado] - 0.1)
        st.session_state.historico_acertos.append(0)

    # Mantém histórico de acertos limitado
    if len(st.session_state.historico_acertos) > 100:
        st.session_state.historico_acertos.pop(0)

# --- Função: Analisar e Prever ---
def analisar_padrao(historico):
    if len(historico) < 2:
        return ("Nenhum Padrão", 1, {}, "Insira mais resultados para iniciar.", None)

    hist = list(historico)[::-1]

    # Probabilidades base
    prob = {'Casa': 33, 'Visitante': 33, 'Empate': 34}
    nivel = 1
    explicacao = "Analisando padrões recentes..."
    padrao_usado = 'ruido'

    # --- Padrões e pesos adaptativos ---
    # 1. Empate recente
    if hist[0] == 'E':
        nivel = 4
        prob['Empate'] += 10 * st.session_state.pesos['empate_recente']
        explicacao = "Empate recente detectado. Alta manipulação."
        padrao_usado = 'empate_recente'

    # 2. Sequência longa
    seq = 1
    for i in range(1, len(hist)):
        if hist[i] == hist[0]:
            seq += 1
        else:
            break
    if seq >= 3:
        nivel = max(nivel, 5)
        lado = 'Casa' if hist[0] == 'V' else 'Visitante'
        prob[lado] += 10 * st.session_state.pesos['sequencia_longa']
        explicacao = f"Sequência longa ({seq})."
        padrao_usado = 'sequencia_longa'

    # 3. Ping-Pong
    alternancia = True
    for i in range(min(len(hist), 6) - 1):
        if hist[i] == hist[i+1]:
            alternancia = False
            break
    if alternancia and len(hist) >= 4:
        nivel = max(nivel, 6)
        prob['Casa'] += 5 * st.session_state.pesos['ping_pong']
        prob['Visitante'] += 5 * st.session_state.pesos['ping_pong']
        explicacao = "Padrão de alternância detectado."
        padrao_usado = 'ping_pong'

    # 4. Ruído
    if padrao_usado == 'ruido':
        explicacao = "Ruído controlado detectado."

    # Normaliza probabilidades
    soma = sum(prob.values())
    for k in prob:
        prob[k] = round(prob[k] / soma * 100, 1)

    # Determinar nível final
    if prob['Empate'] > 40 or nivel >= 6:
        nivel = min(9, nivel + 2)

    # Criar cenários
    cenarios = sorted(prob.items(), key=lambda x: x[1], reverse=True)
    cenarios_dict = {c[0]: c[1] for c in cenarios}

    # Armazena previsão principal para feedback
    st.session_state.ultima_previsao = (cenarios[0][0], padrao_usado)

    return ("Padrão Detectado", nivel, cenarios_dict, explicacao, padrao_usado)

# --- Interface ---
st.title("🔮 Football Studio Analyzer - Aprendizado Adaptativo")
st.markdown("**IA com ajuste dinâmico baseado no seu histórico**")
st.markdown("---")

# --- Inserção ---
st.subheader("1. Inserir Resultados")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🔴 Casa", use_container_width=True):
        atualizar_pesos('Casa')
        st.session_state.historico.append('V')
        st.session_state.estatisticas['Casa'] += 1
with col2:
    if st.button("🔵 Visitante", use_container_width=True):
        atualizar_pesos('Visitante')
        st.session_state.historico.append('A')
        st.session_state.estatisticas['Visitante'] += 1
with col3:
    if st.button("🟡 Empate", use_container_width=True):
        atualizar_pesos('Empate')
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
        st.session_state.ultima_previsao = None
        for k in st.session_state.estatisticas:
            st.session_state.estatisticas[k] = 0
        st.session_state.historico_acertos = []

st.markdown("---")

# --- Histórico ---
st.subheader("2. Histórico")
historico_str = " ".join([mapear_emojis[r] for r in reversed(st.session_state.historico)])
st.markdown(f"**Mais Recente → Mais Antigo:** {historico_str if historico_str else 'Nenhum dado'}")

# --- Análise ---
st.subheader("3. Análise e Previsão")
if st.session_state.historico:
    padrao, nivel, cenarios, explicacao, padrao_usado = analisar_padrao(list(st.session_state.historico))

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

    st.caption(f"📌 Padrão usado para previsão: {padrao_usado} (peso: {st.session_state.pesos[padrao_usado]:.2f})")

else:
    st.info("Adicione resultados para iniciar a análise.")

# --- Estatísticas ---
st.markdown("---")
st.subheader("4. Estatísticas Gerais")
df_stats = pd.DataFrame(list(st.session_state.estatisticas.items()), columns=['Lado','Ocorrências'])
fig_stats = px.pie(df_stats, values='Ocorrências', names='Lado', color='Lado',
                   color_discrete_map={'Casa':'red','Visitante':'blue','Empate':'gold'})
st.plotly_chart(fig_stats, use_container_width=True)

# --- Precisão do Sistema ---
if st.session_state.historico_acertos:
    taxa_acerto = sum(st.session_state.historico_acertos) / len(st.session_state.historico_acertos) * 100
    st.subheader(f"5. Precisão Atual do Sistema: {taxa_acerto:.1f}%")
    st.progress(taxa_acerto / 100)

st.markdown("<br><hr><center>⚠ Jogue com responsabilidade ⚠</center>", unsafe_allow_html=True)
