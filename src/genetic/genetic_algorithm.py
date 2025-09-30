import random
from src.sim.machine import Machine, create_random_machines
from src.sim.logger import save_logs
from src.nn.rede_neural import predict_maintenance  # integra a RN

# Parâmetros do AG
POPULATION_SIZE = 10       # número de estratégias por geração
GENERATIONS = 5            # quantas gerações testar por dia
MUTATION_RATE = 0.2        # chance de mutação
NUM_MACHINES = 10          # deve ser igual ao simulador

class Strategy:
    """
    Cada estratégia representa uma decisão diária:
    - True = operar
    - False = parar/manutenção preventiva
    """
    def __init__(self, genes=None):
        if genes:
            self.genes = genes
        else:
            self.genes = [random.choice([True, False]) for _ in range(NUM_MACHINES)]
        self.fitness = None

    def mutate(self):
        for i in range(len(self.genes)):
            if random.random() < MUTATION_RATE:
                self.genes[i] = not self.genes[i]

    @staticmethod
    def crossover(parent1, parent2):
        cut = random.randint(1, NUM_MACHINES-1)
        child_genes = parent1.genes[:cut] + parent2.genes[cut:]
        return Strategy(child_genes)

def evaluate(strategy, machines, rn_predictions):
    """
    Calcula o lucro líquido da estratégia aplicada nas máquinas
    Considera pequenas bonificações se AG concordar com a RN
    """
    total_profit = 0
    for gene, m, rn_pred in zip(strategy.genes, machines, rn_predictions):
        if gene:  # operando
            total_profit += m.profit - m.cost
            if rn_pred:
                total_profit -= m.cost * 0.3  # penalidade leve se RN previa falha
        else:  # parada preventiva
            total_profit -= m.cost
            if rn_pred:
                total_profit += m.cost * 0.3  # bônus leve se RN previa falha
    strategy.fitness = total_profit
    return total_profit

def run_genetic(machines, day_logs, day):
    """
    Executa AG para escolher a melhor estratégia do dia
    Considera previsões da RN
    """
    # Primeiro, obter previsões da RN para todas as máquinas
    rn_predictions = [predict_maintenance(m) for m in machines]

    # criar população inicial
    population = [Strategy() for _ in range(POPULATION_SIZE)]

    for _ in range(GENERATIONS):
        # avaliar fitness
        for strat in population:
            evaluate(strat, machines, rn_predictions)

        # seleção: top 50%
        population.sort(key=lambda s: s.fitness, reverse=True)
        top_half = population[:POPULATION_SIZE//2]

        # gerar nova população por crossover + mutação
        new_population = top_half.copy()
        while len(new_population) < POPULATION_SIZE:
            p1, p2 = random.sample(top_half, 2)
            child = Strategy.crossover(p1, p2)
            child.mutate()
            new_population.append(child)
        population = new_population

    # garantir que todas as estratégias tenham fitness calculado
    for strat in population:
        if strat.fitness is None:
            evaluate(strat, machines, rn_predictions)

    # melhor estratégia final
    best = max(population, key=lambda s: s.fitness)

    # aplicar decisões no log diário, considerando RN
    for idx, gene in enumerate(best.genes):
        rn_prediction = rn_predictions[idx]
        if not gene:
            if rn_prediction:
                day_logs.append(
                    f"Dia {day} - Máquina {idx} -> RN previu falha: True, AG concordou e decidiu parada preventiva"
                )
            else:
                day_logs.append(
                    f"Dia {day} - Máquina {idx} -> RN previu falha: False, AG discordou mas ainda decidiu parada preventiva"
                )
        else:
            if rn_prediction:
                day_logs.append(
                    f"Dia {day} - Máquina {idx} -> RN previu falha: True, AG discordou e manteve operando"
                )
            else:
                day_logs.append(
                    f"Dia {day} - Máquina {idx} -> RN previu falha: False, AG operando normalmente"
                )

    return best
