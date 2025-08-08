import streamlit as st
import time
from collections import defaultdict

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

# Função que detecta padrões avançados considerando todo o histórico
def detect_patterns(data):
    patterns = []
    results = [d['result'] for d in data]
    
    if not results:
        return patterns

    # Análise de distribuição geral
    total = len(results)
    count_c = results.count('C')
    count_v = results.count('V')
    count_e = results.count('E')
    
    # Streak atual
    streak_len = 1
    for i in range(len(results) - 2, -1, -1):
        if results[i] == results[-1]:
            streak_len += 1
        else:
            break
            
    if streak_len >= 2:
        patterns.append({
            'type': 'streak',
            'color': results[-1],
            'length': streak_len,
            'description': f"{streak_len}x {get_color_name(results[-1])} seguidas (atual)"
        })

    # Streak mais longo do histórico
    max_streak = 1
    current = 1
    for i in range(1, len(results)):
        if results[i] == results[i-1]:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 1
    patterns.append({
        'type': 'max-streak',
        'length': max_streak,
        'description': f"Maior sequência do histórico: {max_streak}x"
    })

    # Frequência de cada resultado
    patterns.append({
        'type': 'frequency',
        'C': count_c,
        'V': count_v,
        'E': count_e,
        'description': f"Distribuição: 🔴{count_c} 🔵{count_v} 🟡{count_e}"
    })

    # Padrões de alternância (versão simplificada e correta)
    alternancias = 0
    for i in range(1, len(results)):
        if results[i] != results[i-1]:
            alternancias += 1
    percent_alt = (alternancias / (len(results)-1)) * 100 if len(results) > 1 else 0
    patterns.append({
        'type': 'alternancia',
        'percent': percent_alt,
        'description': f"Taxa de alternância: {percent_alt:.1f}%"
    })

    # Padrões específicos em janelas móveis
    window_size = min(10, len(results))
    for i in range(len(results) - window_size + 1):
        window = results[i:i+window_size]
        
        # Padrão 2x2 (ex: C C V V C C V V)
        if len(window) >= 4:
            for j in range(0, len(window)-3):
                if window[j] == window[j+1] and window[j+2] == window[j+3] and window[j] != window[j+2]:
                    patterns.append({
                        'type': '2x2-pattern',
                        'position': i+j,
                        'description': f"Padrão 2x2 detectado nas posições {i+j}-{i+j+3}"
                    })
        
        # Sequência de empates
        if window.count('E') >= 3:
            patterns.append({
                'type': 'empate-cluster',
                'position': i,
                'description': f"Cluster de empates nas posições {i}-{i+window_size-1}"
            })

    return patterns

# Função que avalia nível de manipulação (1 a 9) considerando todo o histórico
def get_manipulation_level(data):
    score = 0
    types = []
    results = [d['result'] for d in data]
    
    if not results:
        return 1, []

    # Frequência de empates
    empate_percent = results.count('E') / len(results)
    if empate_percent > 0.25:
        score += min(30, int(empate_percent * 100))
        types.append(f"Empates elevados ({empate_percent:.0%})")

    # Domínio de uma cor
    for c in ['C', 'V']:
        c_percent = results.count(c) / len(results)
        if c_percent > 0.7:
            score += 25
            types.append(f"Domínio de {get_color_name(c)} ({c_percent:.0%})")

    # Streaks longos
    max_streak = 1
    current = 1
    for i in range(1, len(results)):
        if results[i] == results[i-1] and results[i] != 'E':
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 1
    
    if max_streak >= 5:
        score += min(30, (max_streak - 4) * 5)
        types.append(f"Sequência longa ({max_streak}x)")

    # Alternância perfeita
    alt_perfeita = all(results[i] != results[i+1] for i in range(len(results)-1))
    if alt_perfeita and len(results) >= 6:
        score += 20
        types.append("Alternância perfeita")

    # Padrões repetitivos
    padroes_repetidos = defaultdict(int)
    for i in range(len(results)-3):
        padrao = "".join(results[i:i+4])
        padroes_repetidos[padrao] += 1
    
    for padrao, count in padroes_repetidos.items():
        if count >= 2:
            score += 15
            types.append(f"Padrão repetido: {padrao}")

    level = min(score//10 + 1, 9)
    return level, list(set(types))

# Função avançada de predição considerando todo o histórico
def predict_next(data, level, patterns):
    results = [d['result'] for d in data]
    if not results:
        return {'color': None, 'confidence': 0}
    
    last = results[-1]
    confidence = 50
    prediction = None

    # Análise de distribuição
    count_c = results.count('C')
    count_v = results.count('V')
    count_e = results.count('E')
    total = len(results)
    
    # Tendência geral
    if count_c > count_v + 5:
        prediction = 'V'
        confidence = 60 + min(20, (count_c - count_v) // 2)
    elif count_v > count_c + 5:
        prediction = 'C'
        confidence = 60 + min(20, (count_v - count_c) // 2)

    # Streak atual
    streak_info = next((p for p in patterns if p['type'] == 'streak'), None)
    if streak_info:
        if streak_info['length'] >= 3:
            # Quanto maior o streak, maior a chance de quebra
            prediction = 'E' if streak_info['length'] >= 5 else ('V' if streak_info['color'] == 'C' else 'C')
            confidence = 40 + min(40, streak_info['length'] * 5)

    # Empates recentes
    last_10 = results[-10:] if len(results) >= 10 else results
    if last_10.count('E') >= 3:
        prediction = 'E'
        confidence = 65

    # Se não houver predição clara, usar alternância simples
    if prediction is None:
        prediction = 'V' if last == 'C' else 'C'
        confidence = 55 - level

    confidence = max(40, min(confidence, 85))
    
    return {
        'color': prediction,
        'confidence': confidence
    }

# Detecta brechas para evitar apostar
def detect_breach(data, level, manipulation_types):
    if level >= 7:
        return True
    if any("Empates elevados" in t for t in manipulation_types):
        return True
    if any("Sequência longa" in t for t in manipulation_types) and level >= 5:
        return True
    return False

# Função que faz toda análise combinada
def analyze():
    data = st.session_state.history
    if len(data) < 5:
        st.session_state.analysis = {}
        return

    level, manipulation_types = get_manipulation_level(data)
    patterns = detect_patterns(data)
    prediction_info = predict_next(data, level, patterns)
    breach = detect_breach(data, level, manipulation_types)

    recommendation = "Apostar" if prediction_info['confidence'] >= 65 and not breach else "Aguardar"

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
        st.subheader("📊 Histórico Completo (mais recente à esquerda)")
        hist = st.session_state.history[::-1]
        for i in range(0, len(hist), 12):
            row = hist[i:i+12]
            st.markdown("**" + " ".join(emoji_map[d['result']] for d in row) + "**")
            
        # Estatísticas do histórico
        st.subheader("📈 Estatísticas do Histórico")
        if st.session_state.analysis.get('patterns'):
            freq_pattern = next((p for p in st.session_state.analysis['patterns'] if p['type'] == 'frequency'), None)
            if freq_pattern:
                st.write(f"🔢 Distribuição total: {freq_pattern['description']}")
                
            alt_pattern = next((p for p in st.session_state.analysis['patterns'] if p['type'] == 'alternancia'), None)
            if alt_pattern:
                st.write(f"🔄 {alt_pattern['description']}")
                
            max_streak = next((p for p in st.session_state.analysis['patterns'] if p['type'] == 'max-streak'), None)
            if max_streak:
                st.write(f"📏 {max_streak['description']}")
    else:
        st.info("Nenhum resultado inserido ainda.")

with col2:
    st.subheader("📈 Análise em Tempo Real")

    analysis = st.session_state.analysis
    if analysis:
        st.write(f"🔢 Nível de Manipulação: {analysis['manipulation_level']}/9")
        if analysis['manipulation_types']:
            st.write("⚠️ Tipos de Manipulação Detectados:")
            for t in analysis['manipulation_types']:
                st.write(f"- {t}")

        st.write(f"🎯 Previsão: {emoji_map.get(analysis['prediction'], '...')} ({analysis['confidence']}%)")
        
        st.write("🔎 Padrões Detectados:")
        unique_patterns = set()
        for p in analysis['patterns']:
            if p['description'] not in unique_patterns:
                st.write(f"- {p['description']}")
                unique_patterns.add(p['description'])

        st.write(f"⚠️ Brecha Detectada: {'Sim' if analysis['breach_detected'] else 'Não'}")
        st.write(f"✅ Recomendação: {analysis['recommendation']}")
    else:
        st.write("Aguardando mais dados para análise (mínimo 5 resultados)...")
