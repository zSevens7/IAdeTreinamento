# dummysimulation.py
import matplotlib.pyplot as plt
from src.sim.simulator import Simulator
from src.sim.logger import plot_profit, plot_vpl

def run_dummy_simulation(days=890):
    # ---------- Simulação sem AG/RN ----------
    sim_dummy = Simulator()
    
    # Força DummyStrategy durante toda a simulação
    class AlwaysDummyStrategy:
        def __init__(self, machines):
            self.genes = {m.id: True for m in machines}  # todas operando
    
    # Substitui o método run para usar sempre DummyStrategy
    original_simulate_day = sim_dummy.simulate_day
    def simulate_day_dummy():
        sim_dummy_day = sim_dummy.day
        # Troca temporariamente a estratégia para Dummy
        sim_dummy.run_strategy = AlwaysDummyStrategy(sim_dummy.machines)
        original_simulate_day()
    sim_dummy.simulate_day = simulate_day_dummy

    sim_dummy.run(days=days)
    
    # ---------- Simulação com AG/RN ----------
    sim_ag = Simulator()
    sim_ag.run(days=days)

    # ---------- VPL Acumulado ----------
    days_list = [day for day, _, _ in sim_dummy.logs]
    vpl_dummy = [sum(p for _, p, _ in sim_dummy.logs[:i+1]) for i in range(len(days_list))]
    vpl_ag = [sum(p for _, p, _ in sim_ag.logs[:i+1]) for i in range(len(days_list))]

    plt.figure(figsize=(10,5))
    plt.plot(days_list, vpl_dummy, label="Sem AG/RN", color="red")
    plt.plot(days_list, vpl_ag, label="Com AG/RN", color="green")
    plt.title("Comparativo de VPL Acumulado")
    plt.xlabel("Dia")
    plt.ylabel("VPL")
    plt.legend()
    plt.grid(True)
    plt.savefig("vpl_comparativo.png")
    plt.show()

    # ---------- Lucro diário ----------
    profits_dummy = [profit for _, profit, _ in sim_dummy.logs]
    profits_ag = [profit for _, profit, _ in sim_ag.logs]

    plt.figure(figsize=(10,5))
    plt.plot(days_list, profits_dummy, label="Sem AG/RN", color="red", alpha=0.6)
    plt.plot(days_list, profits_ag, label="Com AG/RN", color="green", alpha=0.6)
    plt.title("Comparativo de Lucro Diário")
    plt.xlabel("Dia")
    plt.ylabel("Lucro Diário")
    plt.legend()
    plt.grid(True)
    plt.savefig("lucro_comparativo.png")
    plt.show()

    print("Simulações concluídas. Gráficos salvos: vpl_comparativo.png e lucro_comparativo.png")

if __name__ == "__main__":
    run_dummy_simulation(days=720)
