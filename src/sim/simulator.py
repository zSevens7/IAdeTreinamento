# src/sim/simulator.py
import time
import random
from .machine import create_random_machines
from ..config import SIM_DAYS, SECONDS_PER_DAY
from ..config import DUR_SIMPLE, DUR_GRAVE, DUR_TOTAL
from ..config import BASE_FAIL_RATE, AGE_FAIL_FACTOR, MAX_FAIL_RATE
from ..config import COST_REPAIR_SIMPLE, COST_REPAIR_GRAVE, COST_REPAIR_TOTAL
from .logger import save_logs, save_machines_csv, plot_profit, plot_machine_performance
from src.genetic.genetic_algorithm import run_genetic  # AG
from src.nn.rede_neural import predict_maintenance  # RN

class Simulator:
    def __init__(self):
        self.machines = create_random_machines()
        # Garantir IDs corretos
        for idx, m in enumerate(self.machines):
            m.id = idx
            m.unavailable_days = 0
            m.current_day = 0  # usado para log da RN
        self.day = 0
        self.logs = []

    def simulate_day(self):
        daily_profit = 0
        day_log = []

        # Atualiza o dia das máquinas
        for m in self.machines:
            m.current_day = self.day

        # Executa AG que já considera a RN
        best_strategy = run_genetic(self.machines, day_log, self.day)

        for m in self.machines:
            day_profit = 0

            # Máquina indisponível por falha anterior
            if m.unavailable_days > 0:
                event = f"indisponível ({m.unavailable_days} dias restantes)"
                day_profit = 0
                m.unavailable_days -= 1
            else:
                # Chance de falha aleatória
                fail_chance = min(BASE_FAIL_RATE + m.age * AGE_FAIL_FACTOR, MAX_FAIL_RATE)
                event = "operando"
                if random.random() < fail_chance:
                    fail_type = random.choices(
                        ["simples", "grave", "total"], weights=[0.6, 0.3, 0.1], k=1
                    )[0]

                    if fail_type == "simples":
                        day_profit -= COST_REPAIR_SIMPLE
                        m.unavailable_days = DUR_SIMPLE
                        event = "falha_simples"
                        m.age = 0
                    elif fail_type == "grave":
                        day_profit -= COST_REPAIR_GRAVE
                        m.unavailable_days = DUR_GRAVE
                        event = "falha_grave"
                        m.age = 0
                    elif fail_type == "total":
                        day_profit -= COST_REPAIR_TOTAL
                        m.unavailable_days = DUR_TOTAL
                        event = "falha_total"
                        m.age = 0

                # Aplicar decisão final do AG (já considera RN internamente)
                elif best_strategy.genes[m.id]:
                    # AG decidiu operar
                    day_profit = m.profit - m.cost
                    event = "operando"
                else:
                    # AG decidiu parada preventiva
                    m.unavailable_days = 1
                    day_profit = -m.cost
                    event = "parada preventiva decidida pelo AG"

            daily_profit += day_profit
            day_log.append(f"Máquina {m.id}: {event}, lucro líquido {day_profit}")

            if event == "operando":
                m.age += 1

        self.logs.append((self.day, daily_profit, day_log))
        self.day += 1

    def run(self, days=SIM_DAYS):
        for _ in range(days):
            self.simulate_day()
            time.sleep(SECONDS_PER_DAY)

    def report(self):
        print(f"=== Relatório de {self.day} dias ===")
        total_profit = sum(p for _, p, _ in self.logs)
        print(f"Lucro líquido total: {total_profit}")
        print("Último dia detalhado:")
        for log in self.logs[-1][2]:
            print(log)

        save_logs(self.logs, "simulation_log.txt")
        # Previne KeyError criando todas as chaves no dict antes
        save_machines_csv(self.logs, "machines_summary.csv", num_machines=len(self.machines))
        plot_profit(self.logs, "profit_graph.png")
        plot_machine_performance(self.logs, filename="machines_performance.png")


if __name__ == "__main__":
    sim = Simulator()
    sim.run(days=390)  # simula 390 dias
    sim.report()
