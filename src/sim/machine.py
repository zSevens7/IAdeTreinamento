import random
from ..config import NUM_MACHINES, DURATION_RANGE, COST_RANGE, PROFIT_RANGE


class Machine:
    def __init__(self, id, duration, cost, profit):
        self.id = id
        self.duration = duration
        self.cost = cost
        self.profit = profit
        
        # Atributos de Estado (Inicializados no Simulator, mas presentes aqui)
        self.age = 0
        self.unavailable_days = 0 # Dias que a máquina está em reparo/manutenção
        self.last_fail_days = 0 # Dias desde a última falha

        # NOVOS ATRIBUTOS: Dados dos Sensores para a RN
        # Usamos valores normalizados (0.0 a 1.0) para simplificar a RN
        self.temp_stress = 0.0      # Estresse térmico/temperatura
        self.vibration_level = 0.0  # Nível de vibração
        self.efficiency = 1.0       # Eficiência (diminui com o tempo)

        # CONTADORES DE FALHAS (adicionados para corrigir o erro)
        self.fail_count_simple = 0
        self.fail_count_grave = 0
        self.fail_count_total = 0

    def update_sensors(self):
        """
        Simula a degradação diária dos sensores. 
        A degradação é uma função da idade, com alguma aleatoriedade.
        """
        # Fator de degradação baseado na idade (quanto mais velha, mais rápido degrada)
        degradation_factor = self.age / 500.0
        
        # Aumenta o stress com o tempo e adiciona um ruído aleatório
        # O valor é limitado a 1.0 (condição de falha crítica)
        
        # Estresse de Temperatura: aumenta mais lentamente que a vibração
        increase_t = (degradation_factor * 0.005) + (random.random() * 0.005)
        self.temp_stress = min(1.0, self.temp_stress + increase_t)
        
        # Nível de Vibração: aumenta mais rápido
        increase_v = (degradation_factor * 0.01) + (random.random() * 0.01)
        self.vibration_level = min(1.0, self.vibration_level + increase_v)
        
        # Eficiência: diminui com o stress
        self.efficiency = max(0.5, 1.0 - (self.temp_stress * 0.2 + self.vibration_level * 0.4))
        
        # Atualiza a idade e o tempo desde a última falha (será feito no Simulator)
        # self.age += 1 
        # self.last_fail_days += 1
        
    def reset_condition(self):
        """
        Reseta os parâmetros de degradação após uma falha/reparo/preventiva.
        """
        self.age = 0
        self.temp_stress = 0.0
        self.vibration_level = 0.0
        self.efficiency = 1.0
        self.last_fail_days = 0
        # NOTA: Não resetamos os contadores de falhas pois são históricos acumulativos

    def register_failure(self, failure_type):
        """
        Registra uma falha e incrementa os contadores apropriados.
        """
        if failure_type == "simple":
            self.fail_count_simple += 1
        elif failure_type == "grave":
            self.fail_count_grave += 1
        
        self.fail_count_total = self.fail_count_simple + self.fail_count_grave

    def get_rn_input(self):
        """
        Retorna a lista de inputs para a Rede Neural.
        """
        return [
            self.age, 
            self.temp_stress, 
            self.vibration_level, 
            self.last_fail_days,
            self.fail_count_simple,  # Adicionado contador de falhas simples
            self.fail_count_grave,   # Adicionado contador de falhas graves
        ]

    def fitness(self):
        # A aptidão instantânea pode ser ajustada pela eficiência
        return (self.profit * self.efficiency) - self.cost 

    def __repr__(self):
        return (f"Machine(id={self.id}, age={self.age}, Vibe={self.vibration_level:.2f}, Temp={self.temp_stress:.2f}, "
                f"Fails: S={self.fail_count_simple}, G={self.fail_count_grave}, T={self.fail_count_total})")


def create_random_machines(n=NUM_MACHINES):
    machines = []
    for i in range(n):
        duration = random.randint(*DURATION_RANGE)
        cost = random.randint(*COST_RANGE)
        profit = random.randint(*PROFIT_RANGE)
        machines.append(Machine(i, duration, cost, profit))
    return machines