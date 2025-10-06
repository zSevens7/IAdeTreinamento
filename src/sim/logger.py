import csv
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as mticker
import os

# ===================== FUNÇÃO CALCULATE_VPL (ADICIONADA) =====================
def calculate_vpl(logs, discount_rate=0.08):
    """
    Calcula o Valor Presente Líquido acumulado dia a dia
    """
    daily_profits = [daily_profit for _, daily_profit, _ in logs]
    vpl_accumulated = []
    current_vpl = 0
    
    for day, profit in enumerate(daily_profits, 1):
        # Fator de desconto: 1/(1+r)^t
        discount_factor = 1 / ((1 + discount_rate) ** (day / 365))
        current_vpl += profit * discount_factor
        vpl_accumulated.append(current_vpl)
    
    return vpl_accumulated

# ===================== LOGS DETALHADOS =====================
def save_logs(logs, filename="output/simulation_log.txt"):
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        for day, daily_profit, details in logs:
            f.write(f"Dia {day} -> Lucro líquido: {daily_profit}\n")
            for d in details:
                f.write(f"  {d}\n")
            f.write("\n")

# ===================== RESUMO POR MÁQUINA (CSV) =====================
def save_machines_csv(logs, filename="output/machines_summary.csv", num_machines=10):
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
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
                continue

            event_part = parts[1].split(",")[0].strip()
            
            # CORRIGIDO: Procurar por "Lucro:" em vez de "lucro líquido"
            if "Lucro:" in log:
                try:
                    profit = float(parts[1].split("Lucro:")[1].strip())
                    machines_data[mid]["profit_total"] += profit
                except (IndexError, ValueError):
                    pass # Se não houver lucro, não faz nada
            
            if event_part.startswith("falha_simples"):
                machines_data[mid]["simples"] += 1
            elif event_part.startswith("falha_grave"):
                machines_data[mid]["grave"] += 1
            elif event_part.startswith("falha_total"):
                machines_data[mid]["total"] += 1
            elif event_part.startswith("parada_preventiva"):
                machines_data[mid]["preventiva"] += 1

    df = pd.DataFrame.from_dict(machines_data, orient='index')
    df.index.name = "Máquina"
    df.columns = ["Lucro Total", "Falhas Simples", "Falhas Graves", "Falhas Totais", "Paradas Preventivas"]
    df.to_csv(filename) # Salva o dataframe em CSV

    return df # Retorna o dataframe para ser exibido no Streamlit

# ===================== GRÁFICOS =====================
def plot_profit(logs, filename=None):
    days = [day for day, _, _ in logs]
    profits = [profit for _, profit, _ in logs]
    cumulative_profits = []
    current_total = 0
    
    for profit in profits:
        current_total += profit
        cumulative_profits.append(current_total)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Gráfico de lucro diário
    ax1.plot(days, profits, color='blue', alpha=0.7, linewidth=1)
    ax1.set_title("Lucro Diário")
    ax1.set_xlabel("Dia")
    ax1.set_ylabel("Lucro Diário (R$)")
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Gráfico de lucro acumulado
    ax2.plot(days, cumulative_profits, color='green', linewidth=2)
    ax2.set_title("Lucro Acumulado")
    ax2.set_xlabel("Dia")
    ax2.set_ylabel("Lucro Acumulado (R$)")
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # Formata os eixos Y para valores monetários
    for ax in [ax1, ax2]:
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('R$ {x:,.0f}'))
    
    plt.tight_layout()

    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        fig.savefig(filename, dpi=300, bbox_inches='tight')
    return fig

def plot_machine_performance(logs, num_machines=10, filename=None):
    machines_data = {i: 0 for i in range(num_machines)}
    for _, _, day_logs in logs:
        for log in day_logs:
            # CORRIGIDO: Procurar por "Lucro:" em vez de "lucro líquido"
            if "Lucro:" in log:
                try:
                    mid = int(log.split(":")[0].split()[1])
                    profit = float(log.split("Lucro:")[1].strip())
                    if mid in machines_data:
                        machines_data[mid] += profit
                except (IndexError, ValueError):
                    continue
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(machines_data.keys(), machines_data.values(), color='skyblue', edgecolor='black')
    ax.set_title("Lucro Líquido Acumulado por Máquina")
    ax.set_xlabel("ID da Máquina")
    ax.set_ylabel("Lucro Líquido Total")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Formata o eixo Y para valores monetários
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('R$ {x:,.0f}'))
    
    plt.tight_layout()

    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        fig.savefig(filename, dpi=300, bbox_inches='tight')
    return fig

def plot_vpl(logs, discount_rate=0.08, filename=None):
    vpl_values = calculate_vpl(logs, discount_rate)
    days = list(range(1, len(vpl_values) + 1))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(days, vpl_values, color='purple', linewidth=2)
    ax.set_xlabel('Dias')
    ax.set_ylabel('Valor Presente Líquido (R$)')
    ax.set_title('Evolução do Valor Presente Líquido (VPL)')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Formata o eixo Y para valores monetários
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('R$ {x:,.0f}'))
    
    plt.tight_layout()

    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        fig.savefig(filename, dpi=300, bbox_inches='tight')
    return fig

def plot_vpl_comparativo(logs_ai, logs_no_ai, discount_rate=0.08, filename_prefix="vpl_comparativo", save_to_file=True):
    """
    Gera gráfico comparativo de VPL
    save_to_file: Se True, salva em arquivo. Se False, apenas retorna a figura.
    """
    # Cálculos do VPL
    vpl_ai = calculate_vpl(logs_ai, discount_rate)
    vpl_no_ai = calculate_vpl(logs_no_ai, discount_rate)
    
    # Criação do gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    days = list(range(1, len(vpl_ai) + 1))
    
    ax.plot(days, vpl_ai, label='Com IA', color='green', linewidth=2)
    ax.plot(days, vpl_no_ai, label='Sem IA', color='red', linewidth=2)
    
    # Configurações do gráfico
    ax.set_xlabel('Dias')
    ax.set_ylabel('Valor Presente Líquido (R$)')
    ax.set_title('Comparação de VPL: Manutenção Preditiva vs Reativa')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Formata o eixo Y para mostrar valores monetários
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('R$ {x:,.0f}'))
    
    plt.tight_layout()
    
    # Salva apenas se solicitado
    if save_to_file:
        os.makedirs('output', exist_ok=True)
        fig.savefig(f"output/{filename_prefix}.png", dpi=300, bbox_inches='tight')
    
    return fig  # ⬅️ SEMPRE retorna a figura para o Streamlit

# ===================== LOG DA IA =====================
def log_ai_action(day, machine_id, action, prediction=None, filename="ai_learning_log.txt"):
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "a", encoding="utf-8") as f:
        line = f"Dia {day} - Máquina {machine_id} -> Ação: {action}"
        if prediction is not None:
            line += f", Previsão: {prediction}"
        f.write(line + "\n")