import csv
import matplotlib.pyplot as plt
import os

def save_logs(logs, filename="simulation_log.txt"):
    """Salva todos os logs detalhados da simulação"""
    with open(filename, "w", encoding="utf-8") as f:
        for day, daily_profit, details in logs:
            f.write(f"Dia {day} -> Lucro líquido: {daily_profit}\n")
            for d in details:
                f.write(f"  {d}\n")
            f.write("\n")

def save_machines_csv(logs, filename="machines_summary.csv", num_machines=10):
    """
    Cria um CSV resumido das máquinas:
    - Lucro líquido acumulado
    - Número de falhas por tipo
    - Número de paradas preventivas (decididas pelo AG)
    """
    # Inicializa dados (garante que todas as chaves existem)
    machines_data = {}
    for i in range(num_machines):
        machines_data[i] = {"profit_total": 0, "cost_total": 0,
                            "simples": 0, "grave": 0, "total": 0,
                            "preventiva": 0}

    for _, _, day_logs in logs:
        for log in day_logs:
            # Extrai ID da máquina
            parts = log.split(":")
            try:
                mid = int(parts[0].split()[1])
            except (IndexError, ValueError):
                continue  # ignora logs mal formatados

            # Se ID maior que num_machines, adiciona dinamicamente
            if mid not in machines_data:
                machines_data[mid] = {"profit_total": 0, "cost_total": 0,
                                      "simples": 0, "grave": 0, "total": 0,
                                      "preventiva": 0}

            if "lucro líquido" in log:
                event = parts[1].split(",")[0].strip()
                profit_str = parts[1].split("lucro líquido")[1].strip()
                try:
                    profit = float(profit_str)
                except ValueError:
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
                # Caso log seja só ação do AG sem "lucro líquido"
                machines_data[mid]["preventiva"] += 1

    # Salva CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Máquina", "Lucro Líquido Total", "Falhas Simples",
                         "Falhas Graves", "Falhas Totais", "Paradas Preventivas"])
        for mid, data in sorted(machines_data.items()):
            writer.writerow([mid, data["profit_total"], data["simples"],
                             data["grave"], data["total"], data["preventiva"]])




def plot_profit(logs, filename="profit_graph.png"):
    """Gráfico do lucro líquido diário"""
    days = [day for day, _, _ in logs]
    profits = [profit for _, profit, _ in logs]

    plt.figure(figsize=(10,5))
    plt.plot(days, profits, marker='o', label="Lucro Líquido")
    plt.title("Lucro Líquido Diário")
    plt.xlabel("Dia")
    plt.ylabel("Lucro Líquido")
    plt.grid(True)
    plt.legend()
    plt.savefig(filename)
    plt.show()

def plot_machine_performance(logs, num_machines=10, filename="machines_performance.png"):
    """Gráfico mostrando lucro líquido total por máquina"""
    machines_data = [0]*num_machines
    for _, _, day_logs in logs:
        for log in day_logs:
            if "lucro líquido" in log:
                mid = int(log.split(":")[0].split()[1])
                profit = float(log.split("lucro líquido")[1].strip())  # 🔹 corrigido para float
                machines_data[mid] += profit

    plt.figure(figsize=(10,5))
    plt.bar(range(num_machines), machines_data)
    plt.title("Lucro Líquido Acumulado por Máquina")
    plt.xlabel("Máquina")
    plt.ylabel("Lucro Líquido Total")
    plt.grid(axis='y')
    plt.savefig(filename)
    plt.show()

# ================= NOVO =================
def log_ai_action(day, machine_id, action, prediction=None, filename="ai_learning_log.txt"):
    """
    Salva uma ação tomada pela IA (AG ou rede neural) para comprovar que "aprendeu algo".
    - action: string descrevendo a decisão
    - prediction: valor previsto pela rede neural (opcional)
    """
    with open(filename, "a", encoding="utf-8") as f:
        line = f"Dia {day} - Máquina {machine_id} -> Ação: {action}"
        if prediction is not None:
            line += f", Previsão: {prediction}"
        f.write(line + "\n")
