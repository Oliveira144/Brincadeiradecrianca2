import streamlit as st
import collections
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

# --- Estado da Sessão ---
if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=100)
if 'estatisticas' not in st.session_state:
    st.session_state.estatisticas = {'Casa': 0, 'Visitante': 0, 'Empate': 0}
if 'ultima_previsao' not in st.session_state:
    st.session_state.ultima_previsao = None
if 'ultimo_resultado' not in st.session_state:
    st.session_state.ultimo_resultado = None
if 'nivel_evolucao' not in st.session_state:
    st.session_state.nivel_evolucao = []

# --- Função de Análise com Cache ---
@st.cache_data(ttl=10, show_spinner=False)
def analisar_padrao_quântico(historico):
    if len(historico) < 3:
        return ("Nenhum Padrão", 1, {}, "Insira mais resultados para análise.", None, "Aguardando...")

    hist = list(historico)[::-1]  # Último resultado primeiro
    prob = {'Casa': 33, 'Visitante': 33, 'Empate': 34}
    nivel = 1
    explicacao = "Analisando padrões..."
    alerta_quântico = False

    # --- CAMADA 1: Padrões Fundamentais ---
    # 1. Sequência longa (mín. 3 iguais)
    seq = 1
    for i in range(1, len(hist)):
        if hist[i] == hist[0]:
            seq += 1
        else:
            break
    if seq >= 3:
        nivel = max(nivel, 4)
        lado = nomes[hist[0]]
        prob[lado] += 15
        explicacao = f"Sequência longa detectada ({seq} repetições)"

    # 2. Alternância (mín. 4 jogadas intercaladas)
    if len(hist) >= 4:
        alternancia = True
        for i in range(3):
            if hist[i] == hist[i+1]:
                alternancia = False
                break
        if alternancia:
            nivel = max(nivel, 5)
            prob['Casa'] += 8
            prob['Visitante'] += 8
            explicacao = "Padrão de alternância detectado"

    # --- CAMADA 2: Padrões Intermediários ---
    # 3. Empate como âncora
    if len(hist) >= 4 and 'E' in hist[:4]:
        nivel = max(nivel, 6)
        prob['Empate'] += 12
        explicacao = "Empate atuando como âncora"

    # 4. Armadilha pós-ganho
    if len(hist) >= 3 and hist[0] == hist[1] and hist[2] != hist[0]:
        nivel = max(nivel, 7)
        lado_oposto = nomes[hist[2]]
        prob[lado_oposto] += 10
        explicacao = "Armadilha pós-ganho detectada"
        alerta_quântico = True

    # 5. Quebra de ciclo esperado
    if len(hist) >= 4:
        # Padrão: XXY (dois pares iguais consecutivos, mas diferentes entre si)
        if hist[0] == hist[1] and hist[2] == hist[3] and hist[0] != hist[2]:
            nivel = max(nivel, 7)
            prob['Empate'] += 7
            explicacao = "Quebra de ciclo esperado"
            alerta_quântico = True

    # 6. Dupla reversa
    if len(hist) >= 5:
        # Padrão: X Y X X Y
        if hist[0] == hist[2] == hist[3] and hist[1] == hist[4] and hist[0] != hist[1]:
            nivel = max(nivel, 8)
            lado_alvo = nomes[hist[1]]
            prob[lado_alvo] += 12
            explicacao = "Dupla reversa detectada"
            alerta_quântico = True

    # 7. Falso padrão
    if len(hist) >= 6:
        # Padrão: três iguais seguidos, depois um diferente
        if hist[0] == hist[1] == hist[2] and hist[3] != hist[0]:
            nivel = max(nivel, 8)
            lado_quebrou = nomes[hist[3]]
            prob[lado_quebrou] += 10
            explicacao = "Falso padrão identificado"
            alerta_quântico = True

    # 8. Padrão espelhado
    if len(hist) >= 5:
        # Padrão: X Y Z Y X
        if hist[0] == hist[4] and hist[1] == hist[3] and len(set(hist[:5])) == 3:
            nivel = max(nivel, 8)
            prob['Empate'] += 10
            explicacao = "Padrão espelhado detectado"
            alerta_quântico = True

    # --- CAMADA 3: Padrões Avançados ---
    # 9. Ruído quântico
    if len(hist) >= 6 and len(set(hist[:6])) == 3:
        nivel = 9
        prob = {'Casa': 33.3, 'Visitante': 33.3, 'Empate': 33.4}
        explicacao = "ALERTA: Ruído quântico máximo"
        alerta_quântico = True

    # --- Pós-processamento ---
    # Normalizar probabilidades
    soma = sum(prob.values())
    for k in prob:
        prob[k] = round(prob[k] / soma * 100, 1)

    # Ordenar cenários por probabilidade
    cenarios = sorted(prob.items(), key=lambda x: x[1], reverse=True)
    melhor_opcao, melhor_pct = cenarios[0]
    segunda_opcao, segundo_pct = cenarios[1]
    diferenca = melhor_pct - segundo_pct

    # --- Lógica de Sugestão ---
    sugestao = "❓ Sem clareza: aguarde"
    if alerta_quântico or nivel >= 8:
        sugestao = "⚠️ ALERTA: Mercado instável - NÃO entrar"
    else:
        if st.session_state.ultima_previsao and st.session_state.ultimo_resultado:
            if st.session_state.ultima_previsao == st.session_state.ultimo_resultado:
                explicacao += " | Última previsão correta"
                if diferenca >= 7:
                    sugestao = f"✅ Aposte em {melhor_opcao} ({melhor_pct}%)"
            else:
                explicacao += " | Última previsão falhou"
                if melhor_opcao != st.session_state.ultima_previsao and diferenca >= 6:
                    sugestao = f"🔄 Inverta para {melhor_opcao} ({melhor_pct}%)"
        elif diferenca >= 10 and nivel >= 5:
            sugestao = f"✅ Forte sinal: {melhor_opcao} ({melhor_pct}%)"
        elif diferenca >= 5:
            sugestao = f"⚠️ Moderado: {melhor_opcao} ({melhor_pct}%)"

    # Atualizar memória e evolução
    if len(st.session_state.nivel_evolucao) >= 100:
        st.session_state.nivel_evolucao.pop(0)
    st.session_state.nivel_evolucao.append(nivel)
    st.session_state.ultima_previsao = melhor_opcao

    return ("Padrão Detectado", nivel, dict(cenarios), explicacao, alerta_quântico, sugestao)

# --- INTERFACE ---
st.title("🔮 Football Studio Analyzer - IA Quântica v4")
st.markdown("**Análise com 9 padrões quânticos + evolução gráfica**")
st.markdown("---")

# Disclaimer Legal
st.sidebar.warning("""
## AVISO LEGAL
Este é um simulador teórico para fins educacionais. 
Jogos de azar envolvem riscos financeiros e vício. 
Não garantimos resultados. Use por conta própria.
""")

# Inserção de dados
st.subheader("1. Inserir Resultados")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🔴 Casa", use_container_width=True, key="casa"):
        st.session_state.historico.append('V')
        st.session_state.estatisticas['Casa'] += 1
        st.session_state.ultimo_resultado = "Casa"
        st.rerun()
with col2:
    if st.button("🔵 Visitante", use_container_width=True, key="visitante"):
        st.session_state.historico.append('A')
        st.session_state.estatisticas['Visitante'] += 1
        st.session_state.ultimo_resultado = "Visitante"
        st.rerun()
with col3:
    if st.button("🟡 Empate", use_container_width=True, key="empate"):
        st.session_state.historico.append('E')
        st.session_state.estatisticas['Empate'] += 1
        st.session_state.ultimo_resultado = "Empate"
        st.rerun()
with col4:
    if st.button("⏪ Desfazer", use_container_width=True, key="desfazer"):
        if st.session_state.historico:
            ultimo = st.session_state.historico.pop()
            st.session_state.estatisticas[nomes[ultimo]] -= 1
            if st.session_state.historico:
                ultimo_removido = st.session_state.historico[-1]
                st.session_state.ultimo_resultado = nomes[ultimo_removido]
            else:
                st.session_state.ultimo_resultado = None
            st.rerun()
with col5:
    if st.button("🗑 Limpar", type="primary", use_container_width=True, key="limpar"):
        st.session_state.historico.clear()
        st.session_state.nivel_evolucao.clear()
        for k in st.session_state.estatisticas:
            st.session_state.estatisticas[k] = 0
        st.session_state.ultima_previsao = None
        st.session_state.ultimo_resultado = None
        st.rerun()

st.markdown("---")

# HISTÓRICO EM GRADE
st.subheader("2. Histórico em Grade")
if st.session_state.historico:
    matriz = []
    linha = []
    for i, r in enumerate(st.session_state.historico):
        linha.append(mapear_emojis[r])
        if (i + 1) % 10 == 0:
            matriz.append(linha)
            linha = []
    if linha:
        matriz.append(linha)

    for row in matriz:
        st.write(" ".join(row))
else:
    st.info("Nenhum dado no histórico.")

# ANÁLISE E SUGESTÃO
st.subheader("3. Análise e Previsão")
if st.session_state.historico:
    # Chama a função de análise (com cache)
    padrao, nivel, cenarios, explicacao, alerta, sugestao = analisar_padrao_quântico(list(st.session_state.historico))

    st.markdown(f"**Padrão Detectado:** `{padrao}`")
    st.progress(nivel/9)  # Barra de progresso do nível
    st.markdown(f"**Nível de Complexidade:** {nivel} / 9")
    st.info(explicacao)

    st.success("### 🔍 Probabilidades")
    cols = st.columns(3)
    for i, (nome, pct) in enumerate(cenarios.items()):
        with cols[i]:
            st.metric(label=nome, value=f"{pct}%")

    if alerta:
        st.error(f"**Alerta Quântico:** Mercado instável")
    st.warning(f"**Sugestão de Entrada:** {sugestao}")

    st.markdown(f"**Último Resultado:** {st.session_state.ultimo_resultado}")
    st.markdown(f"**Última Previsão:** {st.session_state.ultima_previsao}")
else:
    st.info("Adicione resultados para iniciar a análise.")

# GRÁFICO DE EVOLUÇÃO
st.markdown("---")
st.subheader("4. Evolução do Nível de Complexidade")
if st.session_state.nivel_evolucao:
    df = pd.DataFrame({"Jogada": list(range(1, len(st.session_state.nivel_evolucao) + 1),
                       "Nível": st.session_state.nivel_evolucao})
    fig = px.line(df, x="Jogada", y="Nível", markers=True, title="Evolução do Nível Quântico")
    fig.update_traces(line=dict(color="purple", width=3))
    fig.update_layout(yaxis=dict(range=[0, 10]))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhum dado para exibir no gráfico.")

# ESTATÍSTICAS GERAIS
st.markdown("---")
st.subheader("5. Estatísticas Gerais")
cols_stats = st.columns(3)
for i, (lado, qtd) in enumerate(st.session_state.estatisticas.items()):
    with cols_stats[i]:
        st.metric(label=lado, value=qtd)

st.markdown("<br><hr><center>⚠ Jogue com responsabilidade ⚠</center>", unsafe_allow_html=True)
