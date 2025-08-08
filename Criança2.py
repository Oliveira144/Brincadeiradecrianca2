# Parte inicial igual...
import streamlit as st
import time

st.set_page_config(page_title="Sistema de Análise Preditiva - Cassino", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

if 'analysis' not in st.session_state:
    st.session_state.analysis = {
        'patterns': [],
        'riskLevel': 'low',
        'manipulation': 'none',
        'prediction': None,
        'confidence': 0,
        'recommendation': 'watch',
        'manipulation_level': 1,
        'manipulation_notes': []
    }

emoji_map = {'C': '🔴', 'V': '🔵', 'E': '🟡'}

def add_result(result):
    st.session_state.history.append({'result': result, 'timestamp': time.time()})
    analyze_data()

def reset_history():
    st.session_state.history = []
    st.session_state.analysis = {
        'patterns': [],
        'riskLevel': 'low',
        'manipulation': 'none',
        'prediction': None,
        'confidence': 0,
        'recommendation': 'watch',
        'manipulation_level': 1,
        'manipulation_notes': []
    }

# ⚙️ ANALISE COMPLETA
def analyze_data():
    data = st.session_state.history
    if len(data) < 6: return

    recent = data[-27:]
    patterns = detect_patterns(recent)
    riskLevel = assess_risk(recent)
    manipulation = detect_manipulation(recent)
    prediction = make_prediction(recent, patterns)
    level, notes = classify_manipulation_level(recent)

    st.session_state.analysis = {
        'patterns': patterns,
        'riskLevel': riskLevel,
        'manipulation': manipulation,
        'prediction': prediction['color'],
        'confidence': prediction['confidence'],
        'recommendation': get_recommendation(riskLevel, manipulation, patterns),
        'manipulation_level': level,
        'manipulation_notes': notes
    }

# 🔍 FUNÇÕES PARA DETECÇÃO DOS 10 NÍVEIS
def classify_manipulation_level(data):
    results = [d['result'] for d in data]
    level = 1
    notes = []

    if detect_simple_streak(results): level = 1; notes.append("Streak simples identificado")
    elif detect_alternating(results): level = 2; notes.append("Alternância clara (1x1)")
    elif detect_2x2_or_3x3(results): level = 3; notes.append("Padrão 2x2 ou 3x3")
    elif detect_fake_streak_break(results): level = 4; notes.append("Quebra proposital de streak")
    elif detect_anchor_empates(results): level = 5; notes.append("Empates como âncora")
    elif detect_hidden_loop(results): level = 6; notes.append("Loop reverso escondido")
    elif detect_strategic_break(results): level = 7; notes.append("Quebra estratégica após padrão")
    elif detect_quantum_manipulation(results): level = 8; notes.append("Interferência quântica detectada")
    elif detect_collapse_with_draw(results): level = 9; notes.append("Colapso de possibilidades + empate")
    elif detect_camouflaged_quantum(results): level = 10; notes.append("Manipulação quântica camuflada")

    return level, notes

# 🔬 LÓGICAS BÁSICAS DOS NÍVEIS
def detect_simple_streak(results):
    return len(results) >= 3 and results[-1] == results[-2] == results[-3]

def detect_alternating(results):
    return len(results) >= 4 and all(results[i] != results[i+1] for i in range(-4, -1))

def detect_2x2_or_3x3(results):
    if len(results) >= 6:
        last6 = results[-6:]
        return last6[:3] == last6[3:] or (last6[0] == last6[1] and last6[2] == last6[3] and last6[4] == last6[5])
    return False

def detect_fake_streak_break(results):
    if len(results) >= 5:
        return results[-3] == results[-2] and results[-1] != results[-2]
    return False

def detect_anchor_empates(results):
    return results[-1] == 'E' and ('C' in results[-4:-1] or 'V' in results[-4:-1])

def detect_hidden_loop(results):
    return len(results) >= 6 and results[-6] == results[-3] == results[-1]

def detect_strategic_break(results):
    if len(results) >= 7:
        if results[-3] == results[-4] == results[-5] and results[-1] != results[-2]:
            return True
    return False

def detect_quantum_manipulation(results):
    return results.count('E') >= 3 and len(set(results[-5:])) >= 4

def detect_collapse_with_draw(results):
    return results[-1] == 'E' and results[-2] != results[-3] and results[-4] == results[-5]

def detect_camouflaged_quantum(results):
    return results[-1] == 'C' and results[-2] == 'V' and results[-3] == 'E' and results[-4] == 'C'

# 🔮 FUNÇÕES ORIGINAIS (ajustadas se necessário) — CONTINUA...
def detect_patterns(data):
    patterns = []
    results = [d['result'] for d in data]

    current_streak = 1
    current_color = results[-1]
    for i in range(len(results)-2, -1, -1):
        if results[i] == current_color:
            current_streak += 1
        else:
            break

    if current_streak >= 2:
        patterns.append({
            'type': 'streak',
            'color': current_color,
            'length': current_streak,
            'description': f"{current_streak}x {get_color_name(current_color)} seguidas"
        })

    if len(results) >= 4:
        alternating = True
        for i in range(-1, -4, -1):
            if i-1 >= -len(results) and results[i] == results[i-1]:
                alternating = False
                break
        if alternating:
            patterns.append({'type': 'alternating', 'description': 'Padrão alternado detectado'})

        last4 = results[-4:]
        if last4[0] == last4[1] and last4[2] == last4[3] and last4[0] != last4[2]:
            patterns.append({'type': '2x2', 'description': 'Padrão 2x2 detectado'})

    return patterns

def assess_risk(data):
    results = [d['result'] for d in data]
    risk_score = 0

    max_streak = 1
    current_streak = 1
    current_color = results[0]
    for i in range(1, len(results)):
        if results[i] == current_color:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
            current_color = results[i]

    if max_streak >= 5: risk_score += 40
    elif max_streak >= 4: risk_score += 25
    elif max_streak >= 3: risk_score += 10

    empate_streak = 0
    for r in reversed(results):
        if r == 'E': empate_streak += 1
        else: break
    if empate_streak >= 2: risk_score += 30

    if risk_score >= 50: return 'high'
    if risk_score >= 25: return 'medium'
    return 'low'

def detect_manipulation(data):
    results = [d['result'] for d in data]
    manipulation_score = 0

    empate_count = results.count('E')
    if empate_count / len(results) > 0.25: manipulation_score += 30

    if len(results) >= 6:
        recent6 = results[-6:]
        p1, p2 = recent6[:3], recent6[3:]
        if len(set(p1)) == 1 and len(set(p2)) == 1 and p1[0] != p2[0]:
            manipulation_score += 25

    if manipulation_score >= 40: return 'high'
    if manipulation_score >= 20: return 'medium'
    return 'low'

def make_prediction(data, patterns):
    results = [d['result'] for d in data]
    last_result = results[-1]
    prediction = {'color': None, 'confidence': 0}

    streak = next((p for p in patterns if p['type'] == 'streak'), None)
    if streak:
        if streak['length'] >= 3:
            other_colors = ['C', 'V']
            other_colors.remove(streak['color'])
            prediction['color'] = other_colors[0]
            prediction['confidence'] = min(90, 50 + streak['length'] * 10)
        else:
            prediction['color'] = streak['color']
            prediction['confidence'] = 65
    else:
        prediction['color'] = 'C' if last_result == 'V' else 'V'
        prediction['confidence'] = 55

    return prediction

def get_recommendation(risk, manipulation, patterns):
    if risk == 'high' or manipulation == 'high': return 'avoid'
    if patterns and risk == 'low': return 'bet'
    return 'watch'

def get_color_name(color):
    return {'C': 'Vermelho', 'V': 'Azul', 'E': 'Empate'}.get(color, '')

# INTERFACE STREAMLIT 🔲
st.title("🎰 Sistema de Análise Preditiva - Cassino")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Inserir Resultados")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("🔴 Vermelho (C)", on_click=add_result, args=('C',))
    with c2:
        st.button("🔵 Azul (V)", on_click=add_result, args=('V',))
    with c3:
        st.button("🟡 Empate (E)", on_click=add_result, args=('E',))

    st.button("🔄 Resetar Histórico", on_click=reset_history)

    st.subheader("📊 Histórico (Mais recente à esquerda)")
    if st.session_state.history:
        max_results = 90
        recent_history = st.session_state.history[-max_results:][::-1]

        lines = []
        for i in range(0, len(recent_history), 9):
            row = recent_history[i:i+9]
            emojis = [emoji_map[r['result']] for r in row]
            lines.append(" ".join(emojis))

        for line in lines:
            st.markdown(f"**{line}**")
    else:
        st.info("Nenhum resultado inserido ainda.")

with col2:
    st.subheader("📈 Análise")
    analysis = st.session_state.analysis

    st.write("**🔒 Nível de Manipulação:**", f"Nível {analysis['manipulation_level']}")
    for note in analysis['manipulation_notes']:
        st.write(f"📌 {note}")

    st.write("**⚠️ Risco:**", analysis['riskLevel'].capitalize())
    st.write("**🎭 Manipulação Aparente:**", analysis['manipulation'].capitalize())

    st.write("**🎯 Previsão:**", emoji_map.get(analysis['prediction'], "Aguardando..."))
    st.write("**📊 Confiança:**", f"{analysis['confidence']}%")
    st.write("**💡 Recomendação:**", analysis['recommendation'].capitalize())

    if analysis['patterns']:
        st.write("### 🧩 Padrões Detectados:")
        for p in analysis['patterns']:
            st.write(f"- {p['description']}")
