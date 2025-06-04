# Simulação de Transações Concorrentes com Deadlock

Este programa simula transações concorrentes que competem por recursos compartilhados, demonstrando a ocorrência, detecção e resolução de deadlocks usando o algoritmo wait-die.

## Requisitos
- Python 3.x

## Como Executar
1. Salve o código em um arquivo (ex: `deadlock_simulator.py`)
2. Execute com: `python deadlock_simulator.py`

## Configuração
- Número de threads: Modifique a variável `num_threads` na função `main()`
- Tempos aleatórios: Os intervalos estão definidos nos `time.sleep(random.uniform(0.1, 0.5))`

## Saída do Programa
O programa exibirá mensagens no terminal mostrando:
- Quando uma thread inicia
- Quando obtém/bloqueia um recurso
- Quando espera por um recurso
- Quando libera um recurso
- Quando é abortada (wait-die)
- Quando deadlock é detectado e qual thread foi terminada
- Quando uma thread finaliza com sucesso

## Funcionamento Interno
1. Cada thread representa uma transação com timestamp único
2. As transações tentam acessar recursos X e Y em ordem
3. O algoritmo wait-die decide quem espera e quem aborta
4. Um detector monitora o grafo de espera para deadlocks
5. Quando detectado, a transação mais antiga no ciclo é abortada

## Personalização
- Para mudar para algoritmo wound-wait, modifique a função `wait_die()`
- Para adicionar mais recursos, inclua no dicionário `resources`
- Para alterar os tempos de espera, ajuste os parâmetros dos `random.uniform()`
