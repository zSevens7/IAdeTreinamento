# app.py

import streamlit as st
import pandas as pd
import copy
import io
import contextlib
import torch
from torch.utils.data import TensorDataset, DataLoader

# Importações do seu projeto
from src.sim.simulator import Simulator
from src.sim.machine import create_random_machines
from src.nn.rede_neural import model, train
from src.sim.logger import (
    plot_profit,
    plot_machine_performance,
    plot_vpl,
    plot_vpl_comparativo,
    save_logs,
    save_machines_csv
)

# ======================== Configuração da Página ========================
st.set_page_config(
    page_title="Simulação de Manutenção Preditiva com IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 Simulação de Manutenção Preditiva com IA")
st.markdown("""
Esta aplicação simula e compara duas estratégias de manutenção industrial:
1.  **Reativa (Sem IA):** Consertar a máquina apenas quando ela quebra.
2.  **Preditiva (Com IA):** Usar um **Algoritmo Genético** e uma **Rede Neural** para prever falhas e decidir sobre paradas preventivas, visando maximizar o lucro.
""")

# ======================== Controles da Simulação ========================
st.sidebar.header("Parâmetros da Simulação")
num_days = st.sidebar.slider(
    "Duração da Simulação (dias)", 
    min_value=365,          # Mínimo de 1 ano para ter efeito pós-treino
    max_value=10*365, 
    value=5*365,            # Padrão de 5 anos
    step=365
)
run_sim = st.sidebar.button("🚀 Iniciar Simulação Completa")
st.sidebar.info("A simulação inclui coleta de dados, treinamento da IA e a execução comparativa. Pode levar alguns instantes.")

# ======================== Função de Simulação em Cache ==========================
# NOVO: Usamos o cache para não re-executar a simulação inteira a cada interação
@st.cache_data
def run_full_simulation(simulation_days):
    """
    Executa todo o pipeline: coleta, treino e simulação comparativa.
    """
    # Cria um conjunto único de máquinas para garantir uma comparação justa
    initial_machines = create_random_machines()
    
    # --- FASE 1: Coleta de Dados ---
    status_log.text("Fase 1/3: Coletando dados para a IA (365 dias)...")
    data_collector = Simulator(machines=copy.deepcopy(initial_machines), use_ai=False)
    data_collector.run(days=365)
    
    # --- FASE 2: Treinamento da Rede Neural ---
    status_log.text("Fase 2/3: Treinando a Rede Neural...")
    features_tensor = torch.tensor([item[0] for item in data_collector.training_data], dtype=torch.float32)
    labels_tensor = torch.tensor([item[1] for item in data_collector.training_data], dtype=torch.float32)
    
    train_dataset = TensorDataset(features_tensor, labels_tensor)
    train_loader = DataLoader(dataset=train_dataset, batch_size=64, shuffle=True)
    
    # Captura o log de treino para exibir na tela
    training_output = io.StringIO()
    with contextlib.redirect_stdout(training_output):
        train(model, train_loader, epochs=50)
    training_log = training_output.getvalue()

    # --- FASE 3: Simulação Comparativa ---
    status_log.text("Fase 3/3: Rodando simulações comparativas...")
    
    # Simulação COM IA (usando o modelo treinado)
    sim_ai = Simulator(machines=copy.deepcopy(initial_machines), use_ai=True)
    sim_ai.run(days=simulation_days)

    # Simulação SEM IA
    sim_no_ai = Simulator(machines=copy.deepcopy(initial_machines), use_ai=False)
    sim_no_ai.run(days=simulation_days)
    
    status_log.empty()
    return sim_ai, sim_no_ai, training_log

# ======================== Execução e Exibição dos Resultados ==========================
# Placeholder para mensagens de status
status_log = st.empty()

if run_sim:
    sim_ai_results, sim_no_ai_results, training_log = run_full_simulation(num_days)
    
    st.success("✅ Simulação concluída com sucesso!")
    
    # Expander para mostrar o log de treino da IA
    with st.expander("Ver Log de Treinamento da Rede Neural"):
        st.code(training_log)

    # ======================== Relatórios Gerais ==========================
    st.header("📊 Resultados Gerais")
    
    total_profit_ai = sum(p for _, p, _ in sim_ai_results.logs)
    total_profit_no_ai = sum(p for _, p, _ in sim_no_ai_results.logs)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Lucro Total (Com IA)", f"R$ {total_profit_ai:,.2f}")
    with col2:
        st.metric("Lucro Total (Sem IA)", f"R$ {total_profit_no_ai:,.2f}")

    st.header("📈 Gráfico Comparativo de Valor Presente Líquido (VPL)")
    # Cria e exibe o gráfico sem salvar em arquivo
    fig = plot_vpl_comparativo(sim_ai_results.logs, sim_no_ai_results.logs, discount_rate=0.08, save_to_file=False)
    st.pyplot(fig)

    # ======================== Análise Detalhada =======================
    st.header("🔬 Análise Detalhada")
    tab_ai, tab_no_ai = st.tabs(["Análise COM IA", "Análise SEM IA"])

    with tab_ai:
        st.subheader("Resumo de Performance (Com IA)")
        df_ai = save_machines_csv(sim_ai_results.logs, num_machines=len(sim_ai_results.machines))
        st.dataframe(df_ai)
        st.subheader("Lucro Acumulado por Máquina (Com IA)")
        st.pyplot(plot_machine_performance(sim_ai_results.logs, num_machines=len(sim_ai_results.machines)))
        
    with tab_no_ai:
        st.subheader("Resumo de Performance (Sem IA)")
        df_no_ai = save_machines_csv(sim_no_ai_results.logs, num_machines=len(sim_no_ai_results.machines))
        st.dataframe(df_no_ai)
        st.subheader("Lucro Acumulado por Máquina (Sem IA)")
        st.pyplot(plot_machine_performance(sim_no_ai_results.logs, num_machines=len(sim_no_ai_results.machines)))