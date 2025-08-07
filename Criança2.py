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
    Analisa o histórico com base nas "brechas do cassino" para prever a quebra de padrões.
    A lógica agora é preditiva e se baseia na manipulação do jogo.
    """
    if len(historico) < 2:
        return "Aguardando Resultados", "Insira mais resultados para iniciar a análise.", "Aguarde o jogo andar para buscar um padrão."

    # Invertemos o histórico para analisar do mais recente para o mais antigo
    hist_recente = list(historico)[::-1]
    
    # Define os lados (Vencedor, Visitante) para facilitar a leitura
    lado_mais_recente = hist_recente[0]
    
    # --- ANÁLISE PRIORITÁRIA DAS BRECHAS DO CASSINO ---

    # 1. Brecha da Saturação do Padrão (Repetição Excessiva) - Após 3 repetições, prepare-se para a quebra
    if len(hist_recente) >= 4 and hist_recente[0] == hist_recente[1] == hist_recente[2] == hist_recente[3]:
        lado_saturado = mapear_emojis[lado_mais_recente]
        return "Saturação do Padrão", f"Aguarde a quebra!", f"Brecha da Saturação. A IA está atraindo apostas com {lado_saturado}. Prepare-se para a quebra e aposte no oposto."
    
    # 2. Brecha do Empate como Âncora de Mudança
    if len(hist_recente) >= 3 and hist_recente[1] == 'E':
        lado_anterior_ao_empate = hist_recente[2]
        lado_oposto = 'A' if lado_anterior_ao_empate == 'V' else 'V'
        sugestao = mapear_emojis[lado_oposto]
        return "Empate como Âncora", f"Aposte em {sugestao}", "Brecha do Empate como Âncora. O empate foi usado para reiniciar o ciclo. Aposte no oposto do resultado anterior ao empate."

    # 3. Brecha do Delay de Manipulação
    if len(hist_recente) >= 4 and hist_recente[0] != hist_recente[1] and hist_recente[1] == hist_recente[2] and hist_recente[2] != hist_recente[3]:
        lado_oposto = mapear_emojis[hist_recente[3]]
        return "Delay de Manipulação", f"Aposte em {lado_oposto}", "Brecha do Delay de Manipulação. Após uma sequência curta, a IA faz uma pausa para confundir e retoma o lado oposto. Aposte na nova tendência."

    # 4. Brecha do Padrão Armadilha (Falso Padrão)
    # Exemplo: 🔴🔵🔴🔵 -> A IA vai quebrar na próxima jogada
    count_alternancia = 0
    if len(hist_recente) >= 2:
        for i in range(len(hist_recente) - 1):
            if hist_recente[i] != hist_recente[i+1]:
                count_alternancia += 1
            else:
                break
    if count_alternancia >= 3:
        lado_quebra = mapear_emojis[hist_recente[0]]
        return "Padrão Armadilha", f"Cautela! Pode haver quebra", f"Brecha do Padrão Armadilha. O padrão de alternância parece fácil demais. A IA pode quebrar este padrão agora. Sugestão: Aposte contra a alternância ou espere a quebra."

    # 5. Brecha da Inversão de Ciclo (Ciclo Reverso)
    if len(hist_recente) >= 6 and hist_recente[0:3] == hist_recente[3:6][::-1] and 'E' not in hist_recente[0:6]:
        lado_oposto_ultimo_ciclo = mapear_emojis[hist_recente[5]]
        return "Inversão de Ciclo", f"Aposte em {lado_oposto_ultimo_ciclo}", "Brecha da Inversão de Ciclo. A IA inverte um ciclo anterior para confundir. Aposte no lado do primeiro resultado do ciclo anterior."

    # 6. Brecha do Colapso Lógico (Manipulação Bruta)
    # Se a sequência de um lado é maior que 6 e não há padrão óbvio, é manipulação bruta.
    count_seq = 0
    for r in hist_recente:
        if r == lado_mais_recente:
            count_seq += 1
        else:
            break
    if count_seq >= 6:
        return "Colapso Lógico", "NÃO APOSTE!", "Brecha do Colapso Lógico. A sequência é longa demais e improvável. O cassino está forçando. Espere a quebra e o novo padrão surgir."

    # 7. Brecha do Zig-Zag Interrompido
    # Exemplo: 🔴🔵🔴🔵🔵 -> A quebra ocorreu no final
    if len(hist_recente) >= 5 and hist_recente[0] == hist_recente[1] and hist_recente[2] != hist_recente[3] and hist_recente[3] == hist_recente[4]:
        lado_novo = mapear_emojis[hist_recente[0]]
        return "Zig-Zag Interrompido", f"Aposte em {lado_novo}", "Brecha do Zig-Zag Interrompido. A alternância foi quebrada. O cassino está tentando iniciar uma nova sequência. Acompanhe a nova tendência."

    # 8. Brecha da Frequência Dominante com Interrupção
    # Conta a frequência dos últimos 10 resultados
    if len(hist_recente) >= 10:
        contagem = collections.Counter(hist_recente[0:10])
        lado_dominante, freq_dominante = contagem.most_common(1)[0]
        if freq_dominante > 5 and lado_mais_recente != lado_dominante:
            sugestao = mapear_emojis[lado_mais_recente]
            return "Frequência Dominante", f"Aposte em {sugestao}", "Brecha da Frequência Dominante. Uma cor estava dominante, mas a IA mudou de direção. Aposte na nova tendência, que pode se tornar a próxima dominante."

    # Se nenhum padrão foi detectado, consideramos a análise como Ruído Controlado
    return "Ruído Controlado", "Cautela!", "A sequência parece aleatória. Evite apostas pesadas e espere por um padrão claro."

# --- Inicialização do estado da sessão ---
if 'historico' not in st.session_state:
    st.session_state.historico = collections.deque(maxlen=30) 

# --- Layout do aplicativo ---
st.title("🔮 Analisador de Padrões de Apostas")
st.markdown("Uma ferramenta para identificar e analisar padrões em sequências de resultados.")
st.markdown("---")

## 1. Inserir Resultados
st.markdown("### 1. Inserir Resultados")
st.write("Clique nos botões correspondentes ao resultado do jogo para adicionar ao histórico.")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔴 Vitória da Casa", use_container_width=True):
        st.session_state.historico.append('V')
with col2:
    if st.button("🔵 Vitória do Visitante", use_container_width=True):
        st.session_state.historico.append('A')
with col3:
    if st.button("🟡 Empate", use_container_width=True):
        st.session_state.historico.append('E')

col4, col5 = st.columns([0.5, 1.5])
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

## 2. Histórico de Resultados
st.markdown("### 2. Histórico de Resultados")
historico_str = " ".join([mapear_emojis[r] for r in reversed(st.session_state.historico)])
st.markdown(f"**Mais Recente → Mais Antigo:**")
st.markdown(f"### `{historico_str}`")

st.markdown("---")

## 3. Análise e Sugestão
st.markdown("### 3. Análise e Sugestão")
if st.session_state.historico:
    padrao, sugestao_direta, sugestao_completa = analisar_padrao(list(st.session_state.historico))
    
    st.markdown(f"**Padrão Detectado:** `{padrao}`")
    st.success(f"**{sugestao_direta}**")
    st.info(f"**Explicação:** {sugestao_completa}")
else:
    st.info("O histórico está vazio. Insira resultados para começar a análise.")

# Agradecimento
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.write("Desenvolvido para análise de padrões de cassino. **Lembre-se:** jogue com responsabilidade.")
