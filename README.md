# Projeto: Simulação de Manutenção Inteligente de Máquinas

## Descrição do Projeto
Este projeto foi desenvolvido como parte da disciplina **Automação Industrial** do curso de Engenharia Elétrica. O objetivo é demonstrar o uso de **Inteligência Computacional** na previsão de falhas em máquinas industriais, utilizando **Redes Neurais** (RN) e **Algoritmo Genético** (AG).

Devido à confidencialidade de códigos de empresas reais, o projeto propõe uma **simulação controlada**, onde máquinas fictícias são monitoradas diariamente, permitindo testar e validar estratégias de manutenção preventiva e corretiva. O foco é analisar como o uso de AG e RN pode **maximizar o lucro líquido e o Valor Presente Líquido (VPL)** ao longo do tempo.

## Objetivo
- Criar um sistema que simule o funcionamento de várias máquinas industriais.
- Aplicar **Rede Neural** para prever falhas com base no histórico de operação e idade da máquina.
- Utilizar **Algoritmo Genético** para decidir a melhor ação para cada máquina (operar ou parada preventiva).
- Avaliar o impacto das decisões da IA sobre o lucro líquido e o VPL acumulado.
- Comparar os resultados com cenários **sem intervenção da IA**, destacando a eficiência do modelo.

## Funcionalidades
- Simulação diária de máquinas com falhas aleatórias (simples, graves ou totais).  
- Registro detalhado das decisões da IA e das previsões da RN.  
- Gráficos do lucro diário, lucro acumulado por máquina e VPL diário, com destaque visual de valores positivos (verde) e negativos (vermelho).  
- Exportação de logs e resumos em CSV para análise.

## Como Funciona
1. O sistema inicializa máquinas fictícias com idade, lucro e custo de operação.  
2. A cada dia, cada máquina pode:
   - Operar normalmente
   - Sofrer falha aleatória
   - Ser parada preventivamente pela decisão da IA
3. A RN prevê a probabilidade de falha com base em dados históricos.  
4. O AG decide a ação ótima para cada máquina, considerando a previsão da RN e os custos associados.  
5. Resultados são registrados e apresentados em gráficos e tabelas.  

## Justificativa
O projeto permite **praticar conceitos de Inteligência Computacional** aplicados à Automação Industrial, mesmo sem acesso a dados proprietários de empresas. Ele ilustra como técnicas como RN e AG podem **aumentar a eficiência operacional** e reduzir prejuízos, oferecendo uma abordagem experimental para decisões de manutenção em sistemas industriais.

## Instalação
1. Clone o repositório:
```bash
git clone https://github.com/seuusuario/seu-repositorio.git
```
2. Acesse a pasta do projeto:

```bash
cd seu-repositorio
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```
# Como Executar

Para rodar a simulação completa:
```bash
python -m src.sim.simulator
```

Para rodar a simulação sem AG/RN (dummy):
```bash
python -m src.sim.dummysimulator
```

## Resultados

- **Logs detalhados da simulação**: `simulation_log.txt`  
  Contém todos os eventos diários, decisões do AG/RN, lucros e perdas.

- **Resumo das máquinas**: `machines_summary.csv`  
  Apresenta lucro total, número de falhas simples, graves e totais, além de paradas preventivas de cada máquina.

- **Gráficos gerados**:
  - `profit_graph.png` → Lucro diário das máquinas
  - `machines_performance.png` → Lucro acumulado por máquina
  - `vpl_graph.png` → Valor Presente Líquido (VPL) diário, positivo em verde e negativo em vermelho

## Observações

- O projeto é **experimental** e os resultados podem variar devido à aleatoriedade das falhas.
- Serve como **demonstração acadêmica** do uso de Inteligência Computacional (RN + AG) em manutenção industrial.

## Estrutura de Pastas

- `src/sim/` → Código principal da simulação, incluindo `simulator.py` e `dummysimulator.py`  
- `src/sim/machine.py` → Definição e criação das máquinas fictícias  
- `src/genetic/` → Implementação do Algoritmo Genético (AG)  
- `src/nn/` → Rede Neural (RN) para previsão de falhas  
- `src/config.py` → Configurações gerais da simulação (dias, custos, durações de falha, taxas, etc.)

## Bibliotecas Utilizadas

- `matplotlib` → Para geração de gráficos  
- `csv` → Para exportação de dados em CSV  
- `random` → Para simular eventos aleatórios  
- `time` → Controle de tempo de simulação (opcional)

## Perspectivas Futuras

- Criar um **aplicativo interativo** para visualizar a simulação em tempo real.  
- Permitir que o usuário **altere parâmetros da simulação dinamicamente**, como taxa de falhas, custos ou número de máquinas.  
- Integrar visualizações gráficas em **tempo real**, mostrando lucro diário, VPL e decisões do AG/RN conforme a simulação acontece.
