import random
from ..config import NUM_MACHINES, DURATION_RANGE, COST_RANGE, PROFIT_RANGE


class Machine:
    def __init__(self, id, duration, cost, profit):
        self.id = id
        self.duration = duration
        self.cost = cost
        self.profit = profit
        self.age = 0

    def fitness(self):
        return self.profit - self.cost

    def __repr__(self):
        return (f"Machine(id={self.id}, duration={self.duration}h, "
                f"cost={self.cost}, profit={self.profit})")


def create_random_machines(n=NUM_MACHINES):
    machines = []
    for i in range(n):
        duration = random.randint(*DURATION_RANGE)
        cost = random.randint(*COST_RANGE)
        profit = random.randint(*PROFIT_RANGE)
        machines.append(Machine(i, duration, cost, profit))
    return machines


if __name__ == "__main__":
    machines = create_random_machines()
    print("Máquinas geradas:")
    for m in machines:
        print(m, "-> fitness:", m.fitness())
