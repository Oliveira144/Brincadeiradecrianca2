import streamlit as st
import collections

# --- Configuração da Página ---
st.set_page_config(
    page_title="Football Studio Analyzer",
    page_icon="🔮",
    layout="wide"
)

# --- Variáveis ---
mapear_emojis = {'V': '🔴', 'A': '🔵', 'E': '🟡'}
nomes = {'V': 'Casa', 'A': 'Visitante', 'E': 'Empate'}

# --- Estado da Sessão ---
if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=50)
if 'estatisticas' not in st.session_state:
    st.session_state.estatisticas = {'Casa': 0, 'Visitante': 0, 'Empate': 0}
if 'ultima_previsao' not in st.session_state:
    st.session_state.ultima_previsao = None
if 'ultimo_resultado' not in st.session_state:
    st.session_state.ultimo_resultado = None

# --- Função Principal ---
def analisar_padrao_quântico(historico):
    if len(historico) < 3:
        return ("Nenhum Padrão", 1, {}, "Insira mais resultados para análise.", None, "Aguardando...")

    hist = list(historico)[::-1]  # Mais recente primeiro
    prob = {'Casa': 33, 'Visitante': 33, 'Empate': 34}
    nivel = 1
    explicacao = "Analisando padrões..."
    alerta_quântico = False

    # --- CAMADA 1: Padrões clássicos ---
    seq = 1
    for i in range(1, len(hist)):
        if hist[i] == hist[0]:
            seq += 1
        else:
            break

    if seq >= 3:
        nivel = max(nivel, 4)
        lado = 'Casa' if hist[0] == 'V' else 'Visitante'
        prob[lado] += 12
        explicacao = f"Sequência longa detectada ({seq})."
    
    alternancia = True
    for i in range(min(len(hist), 6) - 1):
        if hist[i] == hist[i+1]:
            alternancia = False
            break
    if alternancia and len(hist) >= 4:
        nivel = max(nivel, 5)
        prob['Casa'] += 5
        prob['Visitante'] += 5
        explicacao = "Alternância (Ping-Pong) detectada."

    # --- CAMADA 2: Padrões ocultos ---
    if 'E' in hist[:4]:
        nivel = max(nivel, 6)
        prob['Empate'] += 10
        explicacao = "Empate recente atuando como âncora."

    # Detectar reset ou armadilha pós-ganho
    if len(hist) >= 4 and hist[0] == hist[1] and hist[2] != hist[0]:
        nivel = max(nivel, 7)
        alerta_quântico = True
        explicacao = "Possível armadilha pós-ganho detectada."

    # --- CAMADA 3: Ruído Quântico ---
    if len(hist) >= 6 and len(set(hist[:6])) == 3:
        nivel = 9
        alerta_quântico = True
        explicacao = "Ruído quântico detectado: mercado em colapso."

    # Ajustar probabilidades
    soma = sum(prob.values())
    for k in prob:
        prob[k] = round(prob[k] / soma * 100, 1)

    # --- Sugestão baseada em contexto ---
    cenarios = sorted(prob.items(), key=lambda x: x[1], reverse=True)
    melhor_opcao, melhor_pct = cenarios[0]
    segunda_opcao, segundo_pct = cenarios[1]
    diferenca = melhor_pct - segundo_pct

    # --- Lógica adaptativa ---
    sugestao = "❓ Sem clareza: aguarde."
    if alerta_quântico or nivel >= 8:
        sugestao = "⚠ Mercado perigoso: NÃO entrar agora."
    else:
        if st.session_state.ultima_previsao and st.session_state.ultimo_resultado:
            if st.session_state.ultima_previsao == st.session_state.ultimo_resultado:
                explicacao += " Última previsão foi correta, mantendo lógica."
            else:
                explicacao += " Última previsão falhou, ajustando estratégia para reversão."
                if melhor_opcao != st.session_state.ultima_previsao:
                    sugestao = f"🔄 Ajuste: Aposte em **{melhor_opcao}** ({melhor_pct}%)"
        else:
            if diferenca >= 8 and nivel >= 5:
                sugestao = f"✅ Forte: Aposte em **{melhor_opcao}** ({melhor_pct}%)"
            elif diferenca >= 5:
                sugestao = f"⚠ Moderado: Aposte em **{melhor_opcao}** ({melhor_pct}%)"

    # Atualizar memória
    st.session_state.ultima_previsao = melhor_opcao

    return ("Padrão Detectado", nivel, dict(cenarios), explicacao, alerta_quântico, sugestao)

# --- INTERFACE ---
st.title("🔮 Football Studio Analyzer - IA Quântica v2")
st.markdown("**Análise avançada: padrões clássicos + ocultos + camada quântica adaptativa**")
st.markdown("---")

# Inserção de dados
st.subheader("1. Inserir Resultados")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🔴 Casa", use_container_width=True):
        st.session_state.historico.append('V')
        st.session_state.estatisticas['Casa'] += 1
        st.session_state.ultimo_resultado = "Casa"
with col2:
    if st.button("🔵 Visitante", use_container_width=True):
        st.session_state.historico.append('A')
        st.session_state.estatisticas['Visitante'] += 1
        st.session_state.ultimo_resultado = "Visitante"
with col3:
    if st.button("🟡 Empate", use_container_width=True):
        st.session_state.historico.append('E')
        st.session_state.estatisticas['Empate'] += 1
        st.session_state.ultimo_resultado = "Empate"
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

# Histórico
st.subheader("2. Histórico")
historico_str = " ".join([mapear_emojis[r] for r in reversed(st.session_state.historico)])
st.markdown(f"**Mais Recente → Mais Antigo:** {historico_str if historico_str else 'Nenhum dado'}")

# Análise
st.subheader("3. Análise e Previsão")
if st.session_state.historico:
    padrao, nivel, cenarios, explicacao, alerta, sugestao = analisar_padrao_quântico(list(st.session_state.historico))

    st.markdown(f"**Padrão Detectado:** `{padrao}`")
    st.markdown(f"**Nível de Manipulação:** {nivel} / 9")
    st.info(explicacao)

    st.success("### 🔍 Probabilidades")
    for nome, pct in cenarios.items():
        st.metric(label=nome, value=f"{pct}%")

    if alerta:
        st.error(f"**Alerta Quântico:** Mercado instável")
    st.warning(f"**Sugestão de Entrada:** {sugestao}")

else:
    st.info("Adicione resultados para iniciar a análise.")

# Estatísticas
st.markdown("---")
st.subheader("4. Estatísticas Gerais")
for lado, qtd in st.session_state.estatisticas.items():
    st.metric(label=lado, value=qtd)

st.markdown("<br><hr><center>⚠ Jogue com responsabilidade ⚠</center>", unsafe_allow_html=True)
