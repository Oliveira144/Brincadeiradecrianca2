import streamlit as st
import collections

# --- Configuração da página ---
st.set_page_config(
    page_title="Analisador de Padrões de Apostas",
    page_icon="🔮",
    layout="wide"
)

# --- Variáveis de Mapeamento ---
mapear_emojis = {'V': '🔴', 'A': '🔵', 'E': '🟡'}

# --- Funções de Análise de Padrões ---
def analisar_padrao(historico):
    """
    Analisa o histórico e retorna o padrão detectado e a sugestão de aposta,
    focando na detecção das "brechas" de manipulação do cassino com maior confiança.
    """
    if len(historico) < 2:
        return "Nenhum Padrão Detectado", "Aguardando...", "Insira mais resultados para iniciar a análise."

    # Invertemos o histórico para analisar do mais recente para o mais antigo
    hist_recente = list(historico)[::-1]

    # --- ANÁLISE DAS BRECHAS DE MAIOR CONFIANÇA (Prioridade Máxima) ---

    # 1. Brecha da Saturação do Padrão (Repetição Excessiva)
    count_seq = 0
    if len(hist_recente) >= 3:
        for i in range(len(hist_recente)):
            if hist_recente[i] == hist_recente[0] and hist_recente[0] != 'E':
                count_seq += 1
            else:
                break
    
    if count_seq >= 4:
        lado_oposto = mapear_emojis['A' if hist_recente[0] == 'V' else 'V']
        sugestao_direta = f"🎯 Brecha de Saturação! Aposte na quebra: {lado_oposto}"
        sugestao_completa = f"**ALTA CONFIANÇA:** A mesma cor ({mapear_emojis[hist_recente[0]]}) venceu **{count_seq} vezes**. O cassino cria essa sequência para atrair apostas e, em seguida, a quebra. A sugestão é **inverter a aposta** no próximo jogo."
        return "Brecha 1. Saturação do Padrão", sugestao_direta, sugestao_completa

    # 2. Brecha do Empate como Âncora de Mudança
    if len(hist_recente) >= 3 and hist_recente[0] != 'E' and hist_recente[1] == 'E' and hist_recente[2] != hist_recente[0]:
        lado_oposto = mapear_emojis['A' if hist_recente[2] == 'V' else 'V']
        sugestao_direta = f"🎯 Brecha do Empate! Aposte na inversão: {lado_oposto}"
        sugestao_completa = f"**MÉDIA CONFIANÇA:** O empate ({mapear_emojis['E']}) é usado como uma âncora para reiniciar o ciclo. A tendência é que a IA force uma inversão para o lado oposto do resultado que antecedeu o empate. A sugestão é **apostar no lado oposto**."
        return "Brecha 2. Empate como Âncora", sugestao_direta, sugestao_completa
    
    # --- ANÁLISE DE BRECHAS SECUNDÁRIAS (Menor Prioridade) ---

    # 3. Brecha do Padrão Armadilha (Falso Padrão)
    count_ping_pong = 0
    if len(hist_recente) >= 4:
        for i in range(len(hist_recente) - 1):
            if hist_recente[i] != hist_recente[i+1] and hist_recente[i] != 'E' and hist_recente[i+1] != 'E':
                count_ping_pong += 1
            else:
                break
    if count_ping_pong >= 3:
        sugestao_direta = f"⚠️ Padrão Armadilha! Falso padrão em andamento."
        sugestao_completa = f"**CAUTELA:** Há um padrão de 'zig-zag' fácil de identificar ({count_ping_pong + 1} alternâncias). O cassino tende a quebrar este padrão para fisgar o jogador. A sugestão é **não seguir a alternância** e esperar por uma quebra confirmada."
        return "Brecha 4. Padrão Armadilha", sugestao_direta, sugestao_completa

    # 4. Brecha do Zig-Zag Interrompido
    if len(hist_recente) >= 5 and hist_recente[0] == hist_recente[1] and hist_recente[2] != hist_recente[3] and hist_recente[3] != hist_recente[4]:
        sugestao_direta = f"🎯 Zig-Zag Interrompido! Aposte na nova tendência: {mapear_emojis[hist_recente[0]]}"
        sugestao_completa = f"**MÉDIA CONFIANÇA:** O padrão de zig-zag foi quebrado. A IA pode ter iniciado uma nova sequência. A sugestão é **apostar no novo lado que se repetiu** para entrar na nova tendência."
        return "Brecha 7. Zig-Zag Interrompido", sugestao_direta, sugestao_completa
    
    # 5. Brecha da Inversão de Ciclo
    if len(hist_recente) >= 6 and hist_recente[0:3] == hist_recente[3:6][::-1]:
        sugestao_direta = "⚠️ Inversão de Ciclo. Espere a confirmação!"
        sugestao_completa = "**CAUTELA:** A IA repetiu um ciclo (ex: 🔴🔴🔵) e depois o inverteu (ex: 🔵🔵🔴). Este é um sinal de manipulação. A sugestão é **não apostar** até que uma nova tendência se forme."
        return "Brecha 5. Inversão de Ciclo", sugestao_direta, sugestao_completa

    # 6. Brecha do Colapso Lógico (Ruído Controlado)
    if len(historico) > 5 and 'E' not in hist_recente:
        vitorias = hist_recente.count('V')
        derrotas = hist_recente.count('A')
        if abs(vitorias - derrotas) > 4:
            sugestao_direta = "❌ Brecha de Colapso Lógico! Fique de fora!"
            sugestao_completa = "**BAIXA CONFIANÇA:** A sequência parece ignorar toda lógica estatística. O cassino pode estar em modo de manipulação bruta. **Não aposte e espere a sequência quebrar e uma nova tendência se formar.**"
            return "Brecha 6. Colapso Lógico", sugestao_direta, sugestao_completa

    # --- Padrão de Ruído Controlado / Quântico (Caso nenhum outro se encaixe) ---
    sugestao_direta = "Cautela! Nenhum padrão claro detectado."
    sugestao_completa = "A sequência atual não apresenta uma brecha clara. A sugestão é **evitar apostas pesadas** e aguardar a formação de um novo padrão de manipulação."
    return "Ruído Controlado / Quântico", sugestao_direta, sugestao_completa

# --- Inicialização do estado da sessão ---
if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=20)

# --- Layout do aplicativo ---
st.title("🔮 Analisador de Padrões de Apostas (versão Brechas Otimizada)")
st.markdown("---")

st.markdown("### 1. Inserir Resultados")
st.write("Clique nos botões correspondentes ao resultado do jogo.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🔴 Vitória da Casa", use_container_width=True):
        st.session_state.historico.append('V')
with col2:
    if st.button("🔵 Vitória do Visitante", use_container_width=True):
        st.session_state.historico.append('A')
with col3:
    if st.button("🟡 Empate", use_container_width=True):
        st.session_state.historico.append('E')
with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Desfazer", help="Remove o último resultado inserido", use_container_width=True):
        if st.session_state.historico:
            st.session_state.historico.pop()
with col5:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Limpar Histórico", help="Apaga todos os resultados", type="primary", use_container_width=True):
        st.session_state.historico.clear()

st.markdown("---")

st.markdown("### 2. Histórico de Resultados")
historico_str = " ".join([mapear_emojis[r] for r in reversed(st.session_state.historico)])
st.markdown(f"**Mais Recente → Mais Antigo:** {historico_str}")

st.markdown("---")

st.markdown("### 3. Análise e Sugestão de Entrada")
if st.session_state.historico:
    padrao, sugestao_direta, sugestao_completa = analisar_padrao(list(st.session_state.historico))
    st.markdown(f"**Padrão Detectado:** `{padrao}`")
    
    if "🎯" in sugestao_direta:
        st.success(f"**{sugestao_direta}**")
    elif "⚠️" in sugestao_direta:
        st.warning(f"**{sugestao_direta}**")
    else:
        st.info(f"**{sugestao_direta}**")
    
    st.info(f"**Explicação:** {sugestao_completa}")
else:
    st.info("O histórico está vazio. Insira resultados para começar a análise.")

# Agradecimento
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("---")
st.write("Desenvolvido para análise de padrões de cassino com Streamlit. **Lembre-se:** jogue com responsabilidade.")
