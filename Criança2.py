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
    focando na detecção das "brechas" de manipulação do cassino.
    """
    if len(historico) < 2:
        return "Nenhum Padrão Detectado", "Aguardando...", "Insira mais resultados para iniciar a análise."

    # Invertemos o histórico para analisar do mais recente para o mais antigo
    hist_recente = list(historico)[::-1]

    # --- ANÁLISE DE BRECHAS DE MANIPULAÇÃO (prioridade) ---
    
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
        sugestao_direta = f"⚠️ CUIDADO! Brecha da Saturação. Aposte em {lado_oposto}"
        sugestao_completa = f"A mesma cor ({mapear_emojis[hist_recente[0]]}) venceu {count_seq} vezes. O cassino tende a quebrar este padrão agora. A sugestão é **inverter a aposta**."
        return "Brecha 1. Saturação do Padrão", sugestao_direta, sugestao_completa

    # 2. Brecha do Empate como Âncora de Mudança
    if len(hist_recente) >= 3 and hist_recente[0] != 'E' and hist_recente[1] == 'E' and hist_recente[2] != hist_recente[0]:
        lado_oposto = mapear_emojis['A' if hist_recente[2] == 'V' else 'V']
        sugestao_direta = f"⚠️ Brecha do Empate. Aposte em {lado_oposto}"
        sugestao_completa = f"Empate ({mapear_emojis['E']}) como âncora após um resultado de {mapear_emojis[hist_recente[2]]}. O cassino pode estar reiniciando o ciclo. Aposte no oposto do resultado anterior ao empate."
        return "Brecha 2. Empate como Âncora", sugestao_direta, sugestao_completa
    
    # 3. Brecha do Delay de Manipulação
    if len(hist_recente) >= 4 and hist_recente[0] != hist_recente[1] and hist_recente[1] == hist_recente[2] and hist_recente[2] == hist_recente[3]:
        lado_oposto = mapear_emojis['A' if hist_recente[1] == 'V' else 'V']
        sugestao_direta = f"Brecha do Delay detectada. Aposte em {lado_oposto}"
        sugestao_completa = f"O cassino repetiu a cor ({mapear_emojis[hist_recente[1]]}) e deu uma pausa com um resultado oposto ({mapear_emojis[hist_recente[0]]}). A tendência é inverter agora."
        return "Brecha 3. Delay de Manipulação", sugestao_direta, sugestao_completa

    # 4. Brecha do Padrão Armadilha (Falso Padrão)
    count_ping_pong = 0
    if len(hist_recente) >= 4:
        for i in range(len(hist_recente) - 1):
            if hist_recente[i] != hist_recente[i+1]:
                count_ping_pong += 1
            else:
                break
    if count_ping_pong >= 3:
        sugestao_direta = f"⚠️ Padrão Armadilha! Aposta na quebra: {mapear_emojis[hist_recente[0]]}"
        sugestao_completa = f"Padrão de 'zig-zag' fácil de identificar ({count_ping_pong + 1} alternâncias). O cassino tende a quebrar este padrão para fisgar o jogador. Sugestão: **Não siga a alternância.**"
        return "Brecha 4. Padrão Armadilha", sugestao_direta, sugestao_completa

    # 5. Brecha da Inversão de Ciclo
    if len(hist_recente) >= 6 and hist_recente[0:3] == hist_recente[3:6][::-1]:
        sugestao_direta = "Cautela! Inversão de Ciclo detectada"
        sugestao_completa = "A IA do cassino repetiu um ciclo (ex: 🔴🔴🔵) e depois o inverteu (ex: 🔵🔵🔴). Espere para ver a nova tendência."
        return "Brecha 5. Inversão de Ciclo", sugestao_direta, sugestao_completa

    # 6. Brecha do Colapso Lógico (Ruído Controlado)
    if len(historico) > 5 and 'E' not in hist_recente:
        vitorias = hist_recente.count('V')
        derrotas = hist_recente.count('A')
        if abs(vitorias - derrotas) > 4: # Um valor arbitrário para identificar desbalanceamento extremo
            sugestao_direta = "⚠️ CUIDADO! Colapso Lógico. Fique de fora!"
            sugestao_completa = "A sequência parece ignorar toda lógica estatística. O cassino pode estar em modo de manipulação bruta. **Não aposte e espere a sequência quebrar.**"
            return "Brecha 6. Colapso Lógico", sugestao_direta, sugestao_completa
    
    # 7. Brecha do Zig-Zag Interrompido
    if len(hist_recente) >= 5 and hist_recente[0] == hist_recente[1] and hist_recente[2] != hist_recente[3] and hist_recente[3] != hist_recente[4]:
        sugestao_direta = f"Aposta na nova tendência: {mapear_emojis[hist_recente[0]]}"
        sugestao_completa = "Um padrão de zig-zag foi quebrado. O cassino pode ter iniciado uma nova sequência. A sugestão é apostar no novo lado que se repetiu."
        return "Brecha 7. Zig-Zag Interrompido", sugestao_direta, sugestao_completa
    
    # 8. Brecha da Frequência Dominante
    if len(historico) > 6:
        last_dominant = collections.Counter(hist_recente[3:6]).most_common(1)[0][0]
        current_dominant = collections.Counter(hist_recente[0:3]).most_common(1)[0][0]
        if last_dominant != current_dominant:
            sugestao_direta = f"Frequência Dominante mudando. Aposte em {mapear_emojis[current_dominant]}"
            sugestao_completa = f"A IA pode ter usado a dominância anterior ({mapear_emojis[last_dominant]}) para atrair apostas e agora está mudando para o lado oposto ({mapear_emojis[current_dominant]})."
            return "Brecha 8. Frequência Dominante", sugestao_direta, sugestao_completa

    # --- Padrão de Ruído Controlado / Quântico (Caso nenhum outro se encaixe) ---
    sugestao_direta = "Cautela! Não aposte pesado"
    sugestao_completa = "A sequência parece aleatória. Sugestão: Cautela, não há padrão claro. Evite apostas pesadas."
    return "Ruído Controlado / Quântico", sugestao_direta, sugestao_completa

# --- Inicialização do estado da sessão ---
if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=20) # Limita a 20 resultados

# --- Layout do aplicativo ---
st.title("🔮 Analisador de Padrões de Apostas (versão Brechas)")
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

st.markdown("### 3. Análise e Sugestão")
if st.session_state.historico:
    padrao, sugestao_direta, sugestao_completa = analisar_padrao(list(st.session_state.historico))
    st.markdown(f"**Padrão Detectado:** `{padrao}`")
    
    # Adicionando um destaque para as sugestões de cautela
    if "CUIDADO!" in sugestao_direta or "Fique de fora!" in sugestao_direta:
        st.warning(f"**{sugestao_direta}**")
    else:
        st.success(f"**{sugestao_direta}**")
    
    st.info(f"**Explicação:** {sugestao_completa}")
else:
    st.info("O histórico está vazio. Insira resultados para começar a análise.")

# Agradecimento
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("---")
st.write("Desenvolvido para análise de padrões de cassino com Streamlit. **Lembre-se:** jogue com responsabilidade.")
