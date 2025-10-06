# src/genetic/genetic_algorithm.py

import random
from src.config import (
    COST_REPAIR_GRAVE,
    NUM_MACHINES
)
from src.nn.rede_neural import predict_maintenance

# ==================== Parâmetros do AG ====================
POPULATION_SIZE = 100
GENERATIONS = 50
MUTATION_RATE = 0.2
NUM_EVAL_SIMULATIONS = 10 # NOVO: Número de simulações para estabilizar o fitness

# ==================== Estratégia ==========================
class Strategy:
    """
    Representa uma decisão diária para todas as máquinas:
    - True = operar
    - False = parada/manutenção preventiva
    """
    def __init__(self, genes=None):
        if genes:
            self.genes = genes
        else:
            # Genes agora são um dicionário {machine_id: T/F} para clareza
            self.genes = {i: random.choice([True, False]) for i in range(NUM_MACHINES)}
        self.fitness = None

    def mutate(self):
        for i in self.genes:
            if random.random() < MUTATION_RATE:
                self.genes[i] = not self.genes[i]

    @staticmethod
    def crossover(parent1, parent2):
        cut = random.randint(1, NUM_MACHINES - 1)
        child_genes = {}
        for i in range(NUM_MACHINES):
            if i < cut:
                child_genes[i] = parent1.genes[i]
            else:
                child_genes[i] = parent2.genes[i]
        return Strategy(child_genes)

# ==================== Simulação para Avaliação (Função Auxiliar) ==========================
def simulate_day_profit_for_eval(m, operate):
    """
    Simula o lucro de UMA MÁQUINA para UM DIA.
    Esta função é usada APENAS DENTRO DA AVALIAÇÃO DO AG.
    Retorna o lucro líquido do dia.
    """
    from src.config import (
        BASE_FAIL_RATE, AGE_FAIL_FACTOR, MAX_FAIL_RATE,
        COST_REPAIR_SIMPLE, COST_REPAIR_GRAVE, COST_REPAIR_TOTAL
    )

    if not operate:
        return -m.cost # Custo da parada preventiva

    # Chance de falha no dia
    fail_chance = min(BASE_FAIL_RATE + m.age * AGE_FAIL_FACTOR, MAX_FAIL_RATE)
    if random.random() < fail_chance:
        fail_type = random.choices(
            ["simples", "grave", "total"],
            weights=[0.6, 0.3, 0.1], k=1
        )[0]

        if fail_type == "simples":
            return -COST_REPAIR_SIMPLE
        elif fail_type == "grave":
            return -COST_REPAIR_GRAVE
        else: # total
            return -COST_REPAIR_TOTAL

    # Se não falhou e operou
    return m.profit - m.cost

# ==================== Avaliação (Fitness Corrigido) ==========================
def evaluate(strategy, machines, rn_predictions):
    """
    CORRIGIDO: Calcula o fitness da estratégia rodando múltiplas simulações
    para obter um resultado médio e estável, eliminando a sorte.
    """
    total_profit_sum = 0
    for _ in range(NUM_EVAL_SIMULATIONS): # Roda a simulação várias vezes
        current_sim_profit = 0
        for m in machines:
            gene = strategy.genes[m.id]
            rn_pred = rn_predictions[m.id]

            # Simula o resultado financeiro do dia
            daily_profit = simulate_day_profit_for_eval(m, gene)

            # Penalidades e bônus por seguir (ou não) a recomendação da RN
            if gene and rn_pred: # AG opera, mas RN previu falha (ruim)
                daily_profit -= 0.5 * COST_REPAIR_GRAVE # Penalidade
            elif not gene and rn_pred: # AG parou e RN previu falha (bom)
                daily_profit += 0.5 * m.profit # Bônus

            current_sim_profit += daily_profit
        
        total_profit_sum += current_sim_profit

    strategy.fitness = total_profit_sum / NUM_EVAL_SIMULATIONS # Usa a média
    return strategy.fitness

# ==================== AG Diário (Função Principal) ==========================
def run_genetic(machines, day_logs, day):
    """
    Executa o Algoritmo Genético para escolher a melhor estratégia do dia.
    """
    # Previsões da RN para todas as máquinas (uma vez por dia)
    rn_predictions = {m.id: predict_maintenance(m) for m in machines}

    # População inicial
    population = [Strategy() for _ in range(POPULATION_SIZE)]

    for _ in range(GENERATIONS):
        # Avalia todas as estratégias
        for strat in population:
            evaluate(strat, machines, rn_predictions)

        # Seleção (torneio ou roleta seria melhor, mas top 50% é ok)
        population.sort(key=lambda s: s.fitness, reverse=True)
        top_half = population[:POPULATION_SIZE // 2]

        # Crossover e mutação
        new_population = top_half[:]
        while len(new_population) < POPULATION_SIZE:
            p1, p2 = random.sample(top_half, 2)
            child = Strategy.crossover(p1, p2)
            child.mutate()
            new_population.append(child)
        population = new_population

    # Reavalia a população final para garantir o melhor
    for strat in population:
        evaluate(strat, machines, rn_predictions)
        
    best_strategy = max(population, key=lambda s: s.fitness)

    return best_strategy