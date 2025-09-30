import csv
import matplotlib.pyplot as plt

# ===================== LOGS DETALHADOS =====================
def save_logs(logs, filename="simulation_log.txt"):
    """Salva todos os logs detalhados da simulação"""
    with open(filename, "w", encoding="utf-8") as f:
        for day, daily_profit, details in logs:
            f.write(f"Dia {day} -> Lucro líquido: {daily_profit}\n")
            for d in details:
                f.write(f"  {d}\n")
            f.write("\n")

# ===================== RESUMO POR MÁQUINA =====================
def save_machines_csv(logs, filename="machines_summary.csv", num_machines=10):
    """Cria um CSV resumido das máquinas"""
    machines_data = {i: {"profit_total": 0, "simples": 0, "grave": 0, "total": 0, "preventiva": 0} 
                     for i in range(num_machines)}

    for _, _, day_logs in logs:
        for log in day_logs:
            parts = log.split(":")
            try:
                mid = int(parts[0].split()[1])
            except (IndexError, ValueError):
                continue

            if mid not in machines_data:
                machines_data[mid] = {"profit_total": 0, "simples": 0, "grave": 0, "total": 0, "preventiva": 0}

            if "lucro líquido" in log:
                event = parts[1].split(",")[0].strip()
                try:
                    profit = float(parts[1].split("lucro líquido")[1].strip())
                except (IndexError, ValueError):
                    profit = 0
                machines_data[mid]["profit_total"] += profit

                if event.startswith("falha_simples"):
                    machines_data[mid]["simples"] += 1
                elif event.startswith("falha_grave"):
                    machines_data[mid]["grave"] += 1
                elif event.startswith("falha_total"):
                    machines_data[mid]["total"] += 1
                elif "parada preventiva" in event:
                    machines_data[mid]["preventiva"] += 1
            else:
                machines_data[mid]["preventiva"] += 1

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Máquina", "Lucro Líquido Total", "Falhas Simples",
                         "Falhas Graves", "Falhas Totais", "Paradas Preventivas"])
        for mid, data in sorted(machines_data.items()):
            writer.writerow([mid, data["profit_total"], data["simples"],
                             data["grave"], data["total"], data["preventiva"]])

# ===================== GRÁFICOS =====================
def plot_profit(logs, filename="profit_graph.png"):
    """Gráfico do lucro líquido diário"""
    days = [day for day, _, _ in logs]
    profits = [profit for _, profit, _ in logs]

    plt.figure(figsize=(12,6))
    plt.plot(days, profits, marker='o', linestyle='-', color='blue', label="Lucro Líquido")
    plt.title("Lucro Líquido Diário")
    plt.xlabel("Dia")
    plt.ylabel("Lucro Líquido")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.axhline(0, color='black', linewidth=1)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

def plot_machine_performance(logs, num_machines=10, filename="machines_performance.png"):
    """Gráfico mostrando lucro líquido total por máquina"""
    machines_data = [0]*num_machines
    for _, _, day_logs in logs:
        for log in day_logs:
            if "lucro líquido" in log:
                try:
                    mid = int(log.split(":")[0].split()[1])
                    profit = float(log.split("lucro líquido")[1].strip())
                    if mid < len(machines_data):
                        machines_data[mid] += profit
                except (IndexError, ValueError):
                    continue

    plt.figure(figsize=(12,6))
    plt.bar(range(len(machines_data)), machines_data, color='orange')
    plt.title("Lucro Líquido Acumulado por Máquina")
    plt.xlabel("Máquina")
    plt.ylabel("Lucro Líquido Total")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

def plot_vpl(logs, discount_rate=0.0, filename="vpl_graph.png"):
    """
    Gráfico de VPL diário.
    - discount_rate: taxa de desconto diária (0 para sem desconto)
    - positivo em verde, negativo em vermelho
    """
    days = []
    vpl_values = []
    vpl_acc = 0

    for day, daily_profit, _ in logs:
        if discount_rate > 0:
            vpl_acc += daily_profit / ((1 + discount_rate) ** day)
        else:
            vpl_acc += daily_profit
        days.append(day)
        vpl_values.append(vpl_acc)

    plt.figure(figsize=(12,6))
    colors = ['green' if val >= 0 else 'red' for val in vpl_values]
    plt.bar(days, vpl_values, color=colors)
    plt.title("VPL Diário Acumulado")
    plt.xlabel("Dia")
    plt.ylabel("VPL")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.axhline(0, color='black', linewidth=1)
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

# ===================== LOG DA IA =====================
def log_ai_action(day, machine_id, action, prediction=None, filename="ai_learning_log.txt"):
    """Salva uma ação tomada pela IA (AG ou RN)"""
    with open(filename, "a", encoding="utf-8") as f:
        line = f"Dia {day} - Máquina {machine_id} -> Ação: {action}"
        if prediction is not None:
            line += f", Previsão: {prediction}"
        f.write(line + "\n")
