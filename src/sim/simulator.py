# src/sim/simulator.py

import time
import random
import copy
import torch
from torch.utils.data import TensorDataset, DataLoader

from .machine import create_random_machines
from ..config import (
    SIM_DAYS, SECONDS_PER_DAY, NUM_MACHINES,
    DUR_SIMPLE, DUR_GRAVE, DUR_TOTAL,
    BASE_FAIL_RATE, AGE_FAIL_FACTOR, MAX_FAIL_RATE,
    COST_REPAIR_SIMPLE, COST_REPAIR_GRAVE, COST_REPAIR_TOTAL
)
from .logger import save_logs, plot_profit, plot_vpl_comparativo
from src.genetic.genetic_algorithm import run_genetic
from src.nn.rede_neural import model, train # Importa o modelo e a função de treino

class Simulator:
    def __init__(self, machines, use_ai=False):
        self.machines = machines
        self.use_ai = use_ai
        self.day = 0
        self.logs = []
        self.training_data = [] # Para coletar dados para a RN

    def simulate_day(self):
        daily_profit = 0
        day_log = []
        
        # Define a estratégia para o dia
        if self.use_ai and self.day >= 365:
            best_strategy = run_genetic(self.machines, day_log, self.day)
        else:
            # Estratégia padrão: sempre operar (run-to-failure)
            best_strategy = type('Dummy', (object,), {'genes': {m.id: True for m in self.machines}})()

        for m in self.machines:
            m.current_day = self.day
            day_profit_machine = 0
            event = "n/a"
            
            # Coleta de features ANTES da ação do dia
            features = [
                m.age, m.last_fail_days, m.profit, m.cost, 
                m.fail_count_simple, m.fail_count_grave + m.fail_count_total
            ]
            failed_today = 0

            if m.unavailable_days > 0:
                event = f"indisponível ({m.unavailable_days} dias restantes)"
                m.unavailable_days -= 1
            else:
                operate_decision = best_strategy.genes[m.id]
                
                # A máquina só pode quebrar se a decisão for operar
                if operate_decision:
                    fail_chance = min(BASE_FAIL_RATE + m.age * AGE_FAIL_FACTOR, MAX_FAIL_RATE)
                    if random.random() < fail_chance:
                        failed_today = 1 # A máquina falhou
                        fail_type = random.choices(["simples", "grave", "total"], weights=[0.6, 0.3, 0.1])[0]
                        m.last_fail_days = 0
                        m.age = 0
                        if fail_type == "simples":
                            day_profit_machine = -COST_REPAIR_SIMPLE
                            m.unavailable_days = DUR_SIMPLE
                            m.fail_count_simple += 1
                            event = "falha_simples"
                        elif fail_type == "grave":
                            day_profit_machine = -COST_REPAIR_GRAVE
                            m.unavailable_days = DUR_GRAVE
                            m.fail_count_grave += 1
                            event = "falha_grave"
                        else: # total
                            day_profit_machine = -COST_REPAIR_TOTAL
                            m.unavailable_days = DUR_TOTAL
                            m.fail_count_total += 1
                            event = "falha_total"
                    else:
                        # Operou normalmente sem falha
                        day_profit_machine = m.profit - m.cost
                        event = "operando"
                        m.age += 1
                else:
                    # CORRIGIDO: Lógica da parada preventiva
                    day_profit_machine = -m.cost
                    event = "parada_preventiva"
                    m.age = 0 # Manutenção "rejuvenesce" a máquina
            
            # Atualiza contadores e logs
            m.last_fail_days += 1
            daily_profit += day_profit_machine
            day_log.append(f"Máquina {m.id}: {event}, Lucro: {day_profit_machine:.2f}")

            # Salva dados para treino apenas na fase de coleta
            if not self.use_ai and self.day < 365:
                self.training_data.append((features, [failed_today]))

        self.logs.append((self.day, daily_profit, day_log))
        self.day += 1

    def run(self, days=SIM_DAYS):
        for _ in range(days):
            self.simulate_day()
            # time.sleep(SECONDS_PER_DAY)

    def report(self, filename_prefix="simulation"):
        total_profit = sum(p for _, p, _ in self.logs)
        print(f"\n=== Relatório para '{filename_prefix}' ===")
        print(f"Lucro líquido total após {self.day} dias: ${total_profit:,.2f}")
        save_logs(self.logs, f"output/{filename_prefix}_log.txt")
        plot_profit(self.logs, filename=f"output/{filename_prefix}_profit.png")
        print(f"Gráficos e logs salvos na pasta 'output/' com o prefixo '{filename_prefix}'")


# ==================== BLOCO DE EXECUÇÃO PRINCIPAL ====================
if __name__ == "__main__":
    initial_machines = create_random_machines()

    # --- FASE 1: Coleta de Dados ---
    print("--- FASE 1: Coletando dados por 365 dias (sem IA) ---")
    data_collector = Simulator(machines=copy.deepcopy(initial_machines), use_ai=False)
    data_collector.run(days=365)
    print(f"{len(data_collector.training_data)} registros de dados coletados.")

    # --- FASE 2: Treinamento da Rede Neural ---
    print("\n--- FASE 2: Treinando a Rede Neural ---")
    features_tensor = torch.tensor([item[0] for item in data_collector.training_data], dtype=torch.float32)
    labels_tensor = torch.tensor([item[1] for item in data_collector.training_data], dtype=torch.float32)
    
    train_dataset = TensorDataset(features_tensor, labels_tensor)
    train_loader = DataLoader(dataset=train_dataset, batch_size=64, shuffle=True)
    
    # A função train treina o 'model' global importado
    train(model, train_loader, epochs=50)

    # --- FASE 3: Simulação Comparativa ---
    total_sim_days = 10 * 365 # Ex: 10 anos
    
    # Simulação COM IA (usando o modelo treinado)
    print(f"\n--- FASE 3.1: Rodando simulação COM IA por {total_sim_days} dias ---")
    sim_ai = Simulator(machines=copy.deepcopy(initial_machines), use_ai=True)
    sim_ai.run(days=total_sim_days)
    sim_ai.report(filename_prefix="with_ai")

    # Simulação SEM IA (run-to-failure)
    print(f"\n--- FASE 3.2: Rodando simulação SEM IA por {total_sim_days} dias ---")
    sim_no_ai = Simulator(machines=copy.deepcopy(initial_machines), use_ai=False)
    sim_no_ai.run(days=total_sim_days)
    sim_no_ai.report(filename_prefix="without_ai")

    # --- FASE 4: Relatório Final Comparativo ---
    print("\n--- FASE 4: Gerando relatório comparativo ---")
    plot_vpl_comparativo(sim_ai.logs, sim_no_ai.logs, discount_rate=0.08, filename_prefix="vpl_comparativo")
    print("Simulação concluída. Gráfico comparativo de VPL gerado.")