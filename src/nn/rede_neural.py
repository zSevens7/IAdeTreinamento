# src/nn/rede_neural.py

import torch
import torch.nn as nn
import torch.optim as optim
from src.config import COST_REPAIR_SIMPLE, COST_REPAIR_GRAVE, COST_REPAIR_TOTAL, NUM_MACHINES

# ===================== DEFINIÇÃO DA REDE NEURAL =====================
class MachinePredictor(nn.Module):
    def __init__(self, input_size=6, hidden_size=32, output_size=1): # Saída é a prob. de falha
        super(MachinePredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

# Modelo global que será treinado
model = MachinePredictor()

# ===================== FUNÇÃO DE TREINO =====================
def train(model, data_loader, epochs=50, lr=0.001):
    """Treina a rede neural com os dados coletados."""
    criterion = nn.BCELoss() # Bom para classificação binária (falhou/não falhou)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    model.train() # Coloca o modelo em modo de treino
    print(f"Iniciando treinamento por {epochs} épocas...")
    for epoch in range(epochs):
        total_loss = 0
        for X, y in data_loader:
            optimizer.zero_grad()
            outputs = model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            print(f"Época {epoch+1}/{epochs}, Perda Média: {total_loss / len(data_loader):.4f}")
    print("Treinamento concluído.")

# ===================== FUNÇÃO DE PREDIÇÃO =====================
THRESHOLD_FACTOR = 1.0 # Ajustado: Recomenda parada se o custo esperado de falha superar o custo da parada.

def predict_maintenance(machine):
    """
    Usa a RN treinada para prever se a manutenção é necessária.
    Retorna True se a parada for recomendada, False caso contrário.
    """
    model.eval() # Coloca o modelo em modo de avaliação (importante)
    
    # Monta o tensor de features para a máquina
    features = torch.tensor([[
        machine.age,
        machine.last_fail_days,
        machine.profit,
        machine.cost,
        machine.fail_count_simple,
        machine.fail_count_grave + machine.fail_count_total # Falhas graves e totais juntas
    ]], dtype=torch.float32)

    with torch.no_grad(): # Não calcula gradientes durante a predição
        fail_prob = model(features)[0].item()

    # Custo esperado de uma falha (simplificado)
    # Média ponderada dos custos de reparo
    avg_repair_cost = (0.6 * COST_REPAIR_SIMPLE + 0.3 * COST_REPAIR_GRAVE + 0.1 * COST_REPAIR_TOTAL)
    expected_fail_cost = fail_prob * avg_repair_cost

    # Decisão: Parar se o custo esperado da falha for maior que o custo da manutenção
    return expected_fail_cost > machine.cost * THRESHOLD_FACTOR