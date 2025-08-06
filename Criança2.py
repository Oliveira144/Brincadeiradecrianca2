import streamlit as st
import collections
import pandas as pd
import plotly.express as px

# --- Configuração da Página (sempre primeiro!) ---
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

# --- Função Principal ---
def analisar_padrao_quântico(historico):
    if len(historico) < 3:
        return ("Nenhum Padrão", 1, {}, "Insira mais resultados para análise.", None, "Aguardando...")

    hist = list(historico)[::-1]
    prob = {'Casa': 33, 'Visitante': 33, 'Empate': 34}
    nivel = 1
    explicacao = "Analisando padrões..."
    alerta_quântico = False

    # CAMADA 1: Padrões clássicos
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
        explicacao = "Alternância detectada."

    # CAMADA 2: Empate e armadilhas
    if 'E' in hist[:4]:
        nivel = max(nivel, 6)
        prob['Empate'] += 10
        explicacao = "Empate atuando como âncora."
    if len(hist) >= 4 and hist[0] == hist[1] and hist[2] != hist[0]:
        nivel = max(nivel, 7)
        alerta_quântico = True
        explicacao = "Armadilha pós-ganho detectada."

    # CAMADA 3: Ruído quântico
    if len(hist) >= 6 and len(set(hist[:6])) == 3:
        nivel = 9
        alerta_quântico = True
        explicacao = "Ruído quântico detectado."

    # Normalizar probabilidades
    soma = sum(prob.values())
    for k in prob:
        prob[k] = round(prob[k] / soma * 100, 1)

    # Sugestão
    cenarios = sorted(prob.items(), key=lambda x: x[1], reverse=True)
    melhor_opcao, melhor_pct = cenarios[0]
    segunda_opcao, segundo_pct = cenarios[1]
    diferenca = melhor_pct - segundo_pct

    sugestao = "❓ Sem clareza: aguarde."
    if alerta_quântico or nivel >= 8:
        sugestao = "⚠ Mercado perigoso: NÃO entrar agora."
    else:
        if st.session_state.ultima_previsao and st.session_state.ultimo_resultado:
            if st.session_state.ultima_previsao == st.session_state.ultimo_resultado:
                explicacao += " Última previsão correta."
                if diferenca >= 5:
                    sugestao = f"✅ Aposte em **{melhor_opcao}** ({melhor_pct}%)"
            else:
                explicacao += " Última previsão falhou, invertendo lógica."
                if melhor_opcao != st.session_state.ultima_previsao:
                    sugestao = f"🔄 Ajuste: Aposte em **{melhor_opcao}** ({melhor_pct}%)"
        else:
            if diferenca >= 8 and nivel >= 5:
                sugestao = f"✅ Forte: Aposte em **{melhor_opcao}** ({melhor_pct}%)"
            elif diferenca >= 5:
                sugestao = f"⚠ Moderado: Aposte em **{melhor_opcao}** ({melhor_pct}%)"

    # Atualizar memória e evolução
    max_evolucao = 100
    if len(st.session_state.nivel_evolucao) >= max_evolucao:
        st.session_state.nivel_evolucao.pop(0)
    st.session_state.nivel_evolucao.append(nivel)
    st.session_state.ultima_previsao = melhor_opcao

    return ("Padrão Detectado", nivel, dict(cenarios), explicacao, alerta_quântico, sugestao)

# --- INTERFACE ---
st.title("🔮 Football Studio Analyzer - IA Quântica v3")
st.markdown("**Análise com histórico em grade + evolução gráfica**")
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
            if st.session_state.historico:
                ultimo_removido = st.session_state.historico[-1]
                st.session_state.ultimo_resultado = nomes[ultimo_removido]
            else:
                st.session_state.ultimo_resultado = None
with col5:
    if st.button("🗑 Limpar", type="primary", use_container_width=True):
        st.session_state.historico.clear()
        st.session_state.nivel_evolucao.clear()
        for k in st.session_state.estatisticas:
            st.session_state.estatisticas[k] = 0
        st.session_state.ultima_previsao = None
        st.session_state.ultimo_resultado = None

st.markdown("---")

# HISTÓRICO EM GRADE
st.subheader("2. Histórico em Grade")
if st.session_state.historico:
    matriz = []
    linha = []
    # Mostra mais antigo para mais recente (esquerda para direita, topo para baixo)
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

    # Mostrar último resultado e previsão
    st.markdown(f"**Último Resultado:** {st.session_state.ultimo_resultado}")
    st.markdown(f"**Última Previsão:** {st.session_state.ultima_previsao}")

else:
    st.info("Adicione resultados para iniciar a análise.")

# GRÁFICO DE EVOLUÇÃO
st.markdown("---")
st.subheader("4. Evolução do Nível de Manipulação")
if st.session_state.nivel_evolucao:
    df = pd.DataFrame({"Jogada": list(range(1, len(st.session_state.nivel_evolucao) + 1)),
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
for lado, qtd in st.session_state.estatisticas.items():
    st.metric(label=lado, value=qtd)

st.markdown("<br><hr><center>⚠ Jogue com responsabilidade ⚠</center>", unsafe_allow_html=True)
