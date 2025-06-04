import threading
import time
import random
from collections import defaultdict

class Resource:
    def __init__(self, item_id):
        self.item_id = item_id
        self.locked = False
        self.locking_transaction = None
        self.waiting_queue = []

class Transaction:
    def __init__(self, tid, timestamp):
        self.tid = tid
        self.timestamp = timestamp
        self.resources_held = set()
        self.finished = False

class DeadlockDetector:
    def __init__(self):
        self.wait_for_graph = defaultdict(set)
    
    def add_edge(self, requester, resource_holder):
        self.wait_for_graph[requester].add(resource_holder)
    
    def remove_transaction(self, tid):
        if tid in self.wait_for_graph:
            del self.wait_for_graph[tid]
        for waiting in self.wait_for_graph.values():
            if tid in waiting:
                waiting.remove(tid)
    
    def detect_deadlock(self):
        graph = self.wait_for_graph
        cycles = []
        
        def dfs(node, path):
            if node in path:
                cycle = path[path.index(node):]
                cycles.append(cycle)
                return
            if node in graph:
                path.append(node)
                for neighbor in graph[node]:
                    dfs(neighbor, path.copy())
        
        for node in list(graph.keys()):
            dfs(node, [])
        
        if cycles:
            # Encontra a transação mais antiga (menor timestamp) no ciclo
            oldest_in_cycle = min(cycles[0], key=lambda tid: transactions[tid].timestamp)
            return oldest_in_cycle
        return None

# Variáveis globais
resources = {
    'X': Resource('X'),
    'Y': Resource('Y')
}

transactions = {}
detector = DeadlockDetector()
lock = threading.Lock()

def wait_die(requester_tid, resource_holder_tid):
    """Implementa o algoritmo wait-die"""
    if transactions[requester_tid].timestamp < transactions[resource_holder_tid].timestamp:
        # Requester é mais antigo - espera (wait)
        return True
    else:
        # Requester é mais novo - morre (die)
        return False

def acquire_lock(resource_id, tid):
    with lock:
        resource = resources[resource_id]
        
        if not resource.locked:
            # Recurso disponível
            resource.locked = True
            resource.locking_transaction = tid
            transactions[tid].resources_held.add(resource_id)
            print(f"Thread T({tid}) obteve o bloqueio do recurso {resource_id}")
            return True
        else:
            # Recurso já está bloqueado
            holder_tid = resource.locking_transaction
            print(f"Thread T({tid}) está esperando pelo recurso {resource_id} (bloqueado por T({holder_tid}))")
            
            # Adiciona ao grafo de espera
            detector.add_edge(tid, holder_tid)
            
            # Verifica deadlock
            deadlock_victim = detector.detect_deadlock()
            if deadlock_victim:
                print(f"Deadlock detectado! Terminando a transação T({deadlock_victim})")
                # Remove a transação vítima
                release_all_resources(deadlock_victim)
                detector.remove_transaction(deadlock_victim)
                transactions[deadlock_victim].finished = True
                print(f"Thread T({deadlock_victim}) finalizada devido a deadlock")
            
            # Aplica wait-die
            if wait_die(tid, holder_tid):
                # Adiciona à fila de espera
                resource.waiting_queue.append(tid)
                return False
            else:
                # Transação morre (será reiniciada)
                print(f"Thread T({tid}) abortada (wait-die)")
                return 'abort'
    return False

def release_lock(resource_id, tid):
    with lock:
        resource = resources[resource_id]
        
        if resource.locking_transaction == tid:
            resource.locked = False
            resource.locking_transaction = None
            transactions[tid].resources_held.remove(resource_id)
            print(f"Thread T({tid}) liberou o recurso {resource_id}")
            
            # Remove do grafo de espera
            detector.remove_transaction(tid)
            
            # Atende próximo da fila de espera, se houver
            if resource.waiting_queue:
                next_tid = resource.waiting_queue.pop(0)
                resource.locked = True
                resource.locking_transaction = next_tid
                transactions[next_tid].resources_held.add(resource_id)
                print(f"Thread T({next_tid}) obteve o bloqueio do recurso {resource_id} após espera")
        else:
            print(f"ERRO: Thread T({tid}) tentou liberar recurso {resource_id} que não possui")

def release_all_resources(tid):
    with lock:
        for resource_id in list(transactions[tid].resources_held):
            resource = resources[resource_id]
            resource.locked = False
            resource.locking_transaction = None
            print(f"Thread T({tid}) liberou o recurso {resource_id} (abortada)")
            
            # Atende próximo da fila de espera, se houver
            if resource.waiting_queue:
                next_tid = resource.waiting_queue.pop(0)
                resource.locked = True
                resource.locking_transaction = next_tid
                transactions[next_tid].resources_held.add(resource_id)
                print(f"Thread T({next_tid}) obteve o bloqueio do recurso {resource_id} após espera")
        
        transactions[tid].resources_held.clear()
        detector.remove_transaction(tid)

def transaction_work(tid, timestamp):
    transactions[tid] = Transaction(tid, timestamp)
    print(f"Thread T({tid}) entrou em execução (timestamp: {timestamp})")
    
    while not transactions[tid].finished:
        try:
            # Operação randômica
            time.sleep(random.uniform(0.1, 0.5))
            
            # Tenta bloquear X
            result = acquire_lock('X', tid)
            if result == 'abort':
                time.sleep(1)  # Espera antes de reiniciar
                continue
            elif not result:
                continue  # Está esperando
            
            # Operação randômica
            time.sleep(random.uniform(0.1, 0.5))
            
            # Tenta bloquear Y
            result = acquire_lock('Y', tid)
            if result == 'abort':
                release_lock('X', tid)
                time.sleep(1)  # Espera antes de reiniciar
                continue
            elif not result:
                release_lock('X', tid)
                continue  # Está esperando
            
            # Operação randômica
            time.sleep(random.uniform(0.1, 0.5))
            
            # Libera X
            release_lock('X', tid)
            
            # Operação randômica
            time.sleep(random.uniform(0.1, 0.5))
            
            # Libera Y
            release_lock('Y', tid)
            
            # Operação randômica
            time.sleep(random.uniform(0.1, 0.5))
            
            print(f"Thread T({tid}) finalizou com sucesso")
            transactions[tid].finished = True
            
        except Exception as e:
            print(f"Erro na thread T({tid}): {e}")
            release_all_resources(tid)
            transactions[tid].finished = True

def main():
    num_threads = 3  # Número de threads/transações
    threads = []
    
    for i in range(num_threads):
        timestamp = time.time()  # Usamos o timestamp atual como identificador de idade
        t = threading.Thread(target=transaction_work, args=(i+1, timestamp))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("Todas as threads terminaram")

if __name__ == "__main__":
    main()