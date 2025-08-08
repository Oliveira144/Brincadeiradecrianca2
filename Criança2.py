import streamlit as st
import time

# Configuração da página
st.set_page_config(page_title="Football Studio AI Predictor", layout="wide")

# Emojis e nomes
emoji_map = {'C': '🔴', 'V': '🔵', 'E': '🟡'}
color_name = {'C': 'Vermelho', 'V': 'Azul', 'E': 'Empate'}

# Inicialização do estado
if 'history' not in st.session_state:
    st.session_state.history = []

if 'analysis' not in st.session_state:
    st.session_state.analysis = {}

# Função para obter nome da cor
def get_color_name(c):
    return color_name.get(c, '')

# Função para adicionar resultado
def add_result(result):
    st.session_state.history.append({'result': result, 'timestamp': time.time()})
    analyze()

# Resetar histórico
def reset():
    st.session_state.history = []
    st.session_state.analysis = {}

# Função que detecta padrões avançados
def detect_patterns(data):
    patterns = []
    results = [d['result'] for d in data]

    # Streak
    streak_len = 1
    for i in range(len(results) - 2, -1, -1):
        if results[i] == results[i + 1]:
            streak_len += 1
        else:
            break
    if streak_len >= 2:
        patterns.append({
            'type': 'streak',
            'color': results[-1],
            'length': streak_len,
            'description': f"{streak_len}x {get_color_name(results[-1])} seguidas"
        })

    # Alternância camuflada (últimos 6 resultados alternando)
    if len(results) >= 6:
        alt_like = all(results[i] != results[i+1] for i in range(-6, -1))
        if alt_like:
            patterns.append({'type': 'alt-camuflada', 'description': 'Alternância oculta detectada'})

    # Padrão 2x2 reverso (ex: C C V V ou V V C C)
    if len(results) >= 4:
        if results[-1] == results[-2] and results[-3] == results[-4] and results[-1] != results[-3]:
            patterns.append({'type': '2x2-reverse', 'description': '2x2 reverso detectado'})

    # Empate âncora (quando empate antecede mudança)
    if len(results) >= 5:
        if results[-2] == 'E' and results[-1] != 'E':
            patterns.append({'type': 'empate-âncora', 'description': 'Empate atuando como âncora de quebra'})

    return patterns

# Função que avalia nível de manipulação (1 a 9)
def get_manipulation_level(data):
    score = 0
    types = []
    results = [d['result'] for d in data]

    # Empate como âncora oculta
    if results.count('E') >= len(results)*0.2:
        score += 20
        types.append("Empate Camuflado")

    # Alternância forçada
    if len(results) >= 6 and all(results[i] != results[i+1] for i in range(len(results)-1)):
        score += 15
        types.append("Alternância Forçada")

    # Streak longo com quebra por empate
    for i in range(len(results)-4):
        if results[i] == results[i+1] == results[i+2] and results[i+3] == 'E':
            score += 15
            types.append("Colapso com Empate")

    # Padrão 2x2 repetido
    rep_2x2 = 0
    for i in range(0, len(results)-3, 2):
        if results[i] == results[i+1] and results[i+2] == results[i+3] and results[i] != results[i+2]:
            rep_2x2 += 1
    if rep_2x2 >= 2:
        score += 20
        types.append("2x2 Repetido")

    # Domínio forte de uma cor
    for c in ['C', 'V']:
        if results.count(c)/len(results) > 0.75:
            score += 25
            types.append(f"Domínio de {get_color_name(c)}")

    level = min(score//10 + 1, 9)
    return level, list(set(types))

# Função avançada de predição
def predict_next(data, level, patterns):
    results = [d['result'] for d in data]
    last = results[-1]
    confidence = 50
    prediction = None

    # Padrão 2x2 reverso
    if any(p['type'] == '2x2-reverse' for p in patterns):
        prediction = 'E'
        confidence = 78 - level * 2

    # Alternância camuflada
    elif any(p['type'] == 'alt-camuflada' for p in patterns):
        prediction = 'V' if last == 'C' else 'C'
        confidence = 75 - level

    # Streak longo e manipulação alta
    streak = next((p for p in patterns if p['type'] == 'streak'), None)
    if streak:
        if streak['length'] >= 5 and level >= 6:
            prediction = 'E'
            confidence = 70
        elif streak['length'] >= 3:
            prediction = streak['color']
            confidence = 80 - level * 3

    # Empate âncora
    if 'empate-âncora' in [p['type'] for p in patterns]:
        prediction = 'E'
        confidence = 85 - level * 2

    if prediction is None:
        prediction = 'C' if last == 'V' else 'V'
        confidence = 55 - level * 2

    confidence = max(40, min(confidence, 95))

    return {
        'color': prediction,
        'confidence': confidence
    }

# Detecta brechas para evitar apostar
def detect_breach(data, level, manipulation_types):
    if level >= 7:
        return True
    if "Empate Camuflado" in manipulation_types:
        return True
    return False

# Função que faz toda análise combinada
def analyze():
    data = st.session_state.history[-90:]
    if len(data) < 9:
        st.session_state.analysis = {}
        return

    level, manipulation_types = get_manipulation_level(data)
    patterns = detect_patterns(data)
    prediction_info = predict_next(data, level, patterns)
    breach = detect_breach(data, level, manipulation_types)

    recommendation = "Apostar" if prediction_info['confidence'] >= 70 and not breach else "Aguardar"

    st.session_state.analysis = {
        'manipulation_level': level,
        'manipulation_types': manipulation_types,
        'patterns': patterns,
        'prediction': prediction_info['color'],
        'confidence': prediction_info['confidence'],
        'breach_detected': breach,
        'recommendation': recommendation
    }

# Interface Streamlit
st.title("🎯 Football Studio - Sistema Inteligente com IA Avançada")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎮 Inserir Resultado")
    c1, c2, c3 = st.columns(3)
    with c1: st.button("🔴 Vermelho (C)", on_click=add_result, args=("C",))
    with c2: st.button("🔵 Azul (V)", on_click=add_result, args=("V",))
    with c3: st.button("🟡 Empate (E)", on_click=add_result, args=("E",))
    st.button("🔄 Resetar Histórico", on_click=reset)

    if st.session_state.history:
        st.subheader("📊 Histórico (mais recente à esquerda)")
        hist = st.session_state.history[::-1]
        for i in range(0, len(hist), 9):
            row = hist[i:i+9]
            st.markdown("**" + " ".join(emoji_map[d['result']] for d in row) + "**")
    else:
        st.info("Nenhum resultado inserido ainda.")

with col2:
    st.subheader("📈 Análise")

    analysis = st.session_state.analysis
    if analysis:
        st.write(f"🔢 Nível de Manipulação: {analysis['manipulation_level']} / 9")
        if analysis['manipulation_types']:
            st.write("⚠️ Tipos de Manipulação Detectados:")
            for t in analysis['manipulation_types']:
                st.write(f"- {t}")

        st.write(f"🎯 Previsão: {emoji_map.get(analysis['prediction'], '...')}  ({analysis['confidence']}%)")
        st.write("🔎 Padrões Detectados:")
        for p in analysis['patterns']:
            st.write(f"- {p['description']}")

        st.write(f"⚠️ Brecha Detectada: {'Sim' if analysis['breach_detected'] else 'Não'}")
        st.write(f"✅ Recomendação: {analysis['recommendation']}")
    else:
        st.write("Aguardando inserção de dados para análise...")
