# app.py
import streamlit as st
import pandas as pd
from src.sim.simulator import Simulator
from src.sim.logger import plot_profit, plot_machine_performance, plot_vpl, save_logs, save_machines_csv

# ======================== Configuração da Página ========================
st.set_page_config(
    page_title="Simulação de Manutenção Industrial",
    layout="wide"
)

st.title("Simulação de Manutenção Industrial com IA")
st.markdown("""
Este aplicativo demonstra o uso de **Algoritmo Genético (AG)** e **Rede Neural (RN)**
para prever falhas em máquinas e decidir paradas preventivas.
""")

# ======================== Controles da Simulação ========================
st.sidebar.header("Parâmetros da Simulação")
num_days = st.sidebar.slider("Dias de simulação", min_value=100, max_value=1000, value=500, step=50)

run_sim = st.sidebar.button("Rodar Simulação")

# ======================== Rodando a Simulação ==========================
if run_sim:
    sim = Simulator()
    with st.spinner("Rodando simulação..."):
        sim.run(days=num_days)
    
    st.success("Simulação finalizada!")

    # ======================== Relatório Geral ==========================
    total_profit = sum(p for _, p, _ in sim.logs)
    st.metric("Lucro Líquido Total", f"{total_profit:.2f}")

    st.subheader("Último dia detalhado")
    last_day_logs = pd.DataFrame(sim.logs[-1][2], columns=["Detalhes"])
    st.dataframe(last_day_logs)

    # ======================== Salvando Logs e CSV ======================
    save_logs(sim.logs, "simulation_log.txt")
    save_machines_csv(sim.logs, "machines_summary.csv", num_machines=len(sim.machines))

    # ======================== Gráficos ================================
    st.subheader("Lucro Diário")
    st.pyplot(plot_profit(sim.logs))

    st.subheader("Lucro Acumulado por Máquina")
    st.pyplot(plot_machine_performance(sim.logs, num_machines=len(sim.machines)))

    st.subheader("VPL Diário")
    st.pyplot(plot_vpl(sim.logs))

    # ======================== Tabelas Resumidas ========================
    st.subheader("Resumo por Máquina")
    machine_data = pd.read_csv("machines_summary.csv")
    st.dataframe(machine_data)
