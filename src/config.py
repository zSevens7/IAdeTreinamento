# config.py
SIM_DAYS = 365          # quantos dias simular por execução (ex.: 365)
SECONDS_PER_DAY = 0.01    # seu requisito: 1 dia = 10s reais
NUM_MACHINES = 10       # número de máquinas na fábrica

# Intervalos de valores para gerar máquinas variadas
DURATION_RANGE = (8, 24)      # duração de operação em horas por dia
COST_RANGE = (50, 300)        # custo diário de operação/manutenção preventiva
PROFIT_RANGE = (80, 500)      # lucro diário quando operando

# Custos de reparos (valores fixos)
COST_REPAIR_SIMPLE = 500.0    # custo para consertar falha simples
COST_REPAIR_GRAVE = 2000.0    # custo para consertar quando é falha grave
COST_REPAIR_TOTAL = 10000.0   # custo para trocar a máquina quando é falha total

# Duração das falhas (em dias)
DUR_SIMPLE = 2
DUR_GRAVE = 7
DUR_TOTAL = 30

# Probabilidades de falha
BASE_FAIL_RATE = 0.01     # chance mínima de falha por dia (1%)
AGE_FAIL_FACTOR = 0.0005  # quanto a chance aumenta a cada dia de operação
MAX_FAIL_RATE = 0.05      # limite máximo de chance de falha (5%)
