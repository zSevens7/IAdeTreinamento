# src/nn/rede_neural.py
import torch
import torch.nn as nn
import torch.optim as optim
from src.sim.logger import log_ai_action
from src.config import COST_REPAIR_SIMPLE, COST_REPAIR_GRAVE, COST_REPAIR_TOTAL

class MachinePredictor(nn.Module):
    """
    Rede Neural para prever falhas das máquinas:
    - Entrada: features da máquina (idade, dias desde última falha, lucro, número de falhas, etc.)
    - Saída: probabilidade de falha simples, grave e total
    """
    def __init__(self, input_size=6, hidden_size=32, output_size=3):
        super(MachinePredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()  # saída entre 0 e 1

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

# modelo global instanciado
model = MachinePredictor()

def train(model, data_loader, epochs=10, lr=0.001):
    """
    Função de treino simples
    - data_loader: PyTorch DataLoader com tuplas (X, y)
    - epochs: número de épocas
    - lr: learning rate
    """
    criterion = nn.BCELoss()  # como saída é probabilidade
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        for X, y in data_loader:
            optimizer.zero_grad()
            outputs = model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")

def predict_maintenance(machine):
    """
    Retorna True se a RN decidir fazer manutenção preventiva.
    Considera lucro perdido versus custo esperado de falha.
    Também salva a previsão na própria máquina para o AG usar.
    """
    # Cria features para a RN
    features = torch.tensor([[machine.age,
                              getattr(machine, "last_fail_days", 0),
                              machine.profit,
                              getattr(machine, "fail_count_simple", 0),
                              getattr(machine, "fail_count_grave", 0),
                              getattr(machine, "fail_count_total", 0)
                             ]], dtype=torch.float32)
    
    # Saída: probabilidade de falha simples, grave e total
    pred = model(features)[0]  # tensor com 3 valores
    
    # Calcula custo esperado de falha
    expected_cost = (
        pred[0].item() * COST_REPAIR_SIMPLE +
        pred[1].item() * COST_REPAIR_GRAVE +
        pred[2].item() * COST_REPAIR_TOTAL
    )

    # Compara com o custo da parada preventiva
    action = expected_cost > machine.cost

    # Salva previsão na máquina para o AG usar depois
    machine.rn_prediction = action
    machine.rn_prediction_prob = pred.tolist()  # opcional, se quiser detalhar

    # LOG opcional para monitoramento
    log_ai_action(
        day=getattr(machine, "current_day", 0),
        machine_id=machine.id,
        action="parada preventiva" if action else "continuar operando",
        prediction=pred.tolist()
    )

    return action




if __name__ == "__main__":
    # teste rápido
    class DummyMachine:
        id = 0
        age = 10
        profit = 200
        cost = 100
        current_day = 0

    machine = DummyMachine()
    y = predict_maintenance(machine)
    print("Manutenção preventiva pela RN?", y)
