from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

# ==================== CLASSES BASE ====================

class Transacao(ABC):
    """Interface para transações bancárias"""
    
    @abstractmethod
    def registrar(self, conta):
        pass

class Cliente:
    """Classe base para clientes"""
    
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas: List['Conta'] = []
    
    def realizar_transacao(self, conta: 'Conta', transacao: Transacao):
        """Realiza uma transação na conta especificada"""
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta: 'Conta'):
        """Adiciona uma conta ao cliente"""
        self.contas.append(conta)

class PessoaFisica(Cliente):
    """Classe para pessoa física"""
    
    def __init__(self, cpf: str, nome: str, data_nascimento: datetime, endereco: str):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Historico:
    """Classe para gerenciar histórico de transações"""
    
    def __init__(self):
        self.transacoes: List[Transacao] = []
    
    def adicionar_transacao(self, transacao: Transacao):
        """Adiciona uma transação ao histórico"""
        self.transacoes.append(transacao)

class Conta:
    """Classe base para contas bancárias"""
    
    def __init__(self, saldo: float, numero: int, agencia: str, cliente: Cliente, historico: Historico):
        self.saldo = saldo
        self.numero = numero
        self.agencia = agencia
        self.cliente = cliente
        self.historico = historico
    
    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int) -> 'Conta':
        """Método de classe para criar uma nova conta"""
        historico = Historico()
        return cls(0.0, numero, "0001", cliente, historico)
    
    def sacar(self, valor: float) -> bool:
        """Realiza saque da conta"""
        if valor <= 0:
            print("Valor inválido para saque!")
            return False
        
        if valor > self.saldo:
            print("Saldo insuficiente!")
            return False
        
        self.saldo -= valor
        print(f"Saque de R$ {valor:.2f} realizado com sucesso!")
        return True
    
    def depositar(self, valor: float) -> bool:
        """Realiza depósito na conta"""
        if valor <= 0:
            print("Valor inválido para depósito!")
            return False
        
        self.saldo += valor
        print(f"Depósito de R$ {valor:.2f} realizado com sucesso!")
        return True

class ContaCorrente(Conta):
    """Classe para conta corrente com limite e limite de saques"""
    
    def __init__(self, saldo: float, numero: int, agencia: str, cliente: Cliente, 
                 historico: Historico, limite: float, limite_saques: int):
        super().__init__(saldo, numero, agencia, cliente, historico)
        self.limite = limite
        self.limite_saques = limite_saques
        self._saques_realizados = 0
    
    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int) -> 'ContaCorrente':
        """Método de classe para criar uma nova conta corrente"""
        historico = Historico()
        return cls(0.0, numero, "0001", cliente, historico, 500.0, 3)
    
    def sacar(self, valor: float) -> bool:
        """Realiza saque com validações específicas da conta corrente"""
        if valor <= 0:
            print("Valor inválido para saque!")
            return False
        
        if self._saques_realizados >= self.limite_saques:
            print(f"Limite de {self.limite_saques} saques diários excedido!")
            return False
        
        saldo_disponivel = self.saldo + self.limite
        if valor > saldo_disponivel:
            print(f"Saldo insuficiente! Saldo disponível: R$ {saldo_disponivel:.2f}")
            return False
        
        self.saldo -= valor
        self._saques_realizados += 1
        print(f"Saque de R$ {valor:.2f} realizado com sucesso!")
        return True

# ==================== TRANSAÇÕES ====================

class Deposito(Transacao):
    """Classe para transações de depósito"""
    
    def __init__(self, valor: float):
        self.valor = valor
    
    def registrar(self, conta: Conta):
        """Registra o depósito na conta"""
        sucesso = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    """Classe para transações de saque"""
    
    def __init__(self, valor: float):
        self.valor = valor
    
    def registrar(self, conta: Conta):
        """Registra o saque na conta"""
        sucesso = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)

# ==================== FUNÇÕES AUXILIARES ====================

def menu():
    return input("""
    =============== BANCO DIO ===============
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nu] Novo Usuário
    [nc] Nova Conta
    [lc] Listar Contas
    [q] Sair
    ==========================================
    => """).lower().strip()

def obter_valor(mensagem):
    while True:
        try:
            valor = float(input(mensagem))
            if valor < 0:
                print("O valor não pode ser negativo!")
                continue
            return valor
        except ValueError:
            print("Valor inválido! Digite um número válido.")

def validar_cpf(cpf):
    return cpf.isdigit() and len(cpf) == 11

def encontrar_cliente(cpf, clientes):
    for cliente in clientes:
        if isinstance(cliente, PessoaFisica) and cliente.cpf == cpf:
            return cliente
    return None

def criar_usuario(clientes):
    cpf = input("Informe o CPF (somente números): ").strip()
    if not validar_cpf(cpf):
        print("CPF inválido!")
        return
    
    if encontrar_cliente(cpf, clientes):
        print("Usuário já cadastrado!")
        return
    
    nome = input("Informe o nome completo: ").strip()
    data_nascimento_str = input("Informe a data de nascimento (dd/mm/aaaa): ").strip()
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/UF): ").strip()
    
    try:
        data_nascimento = datetime.strptime(data_nascimento_str, "%d/%m/%Y")
    except ValueError:
        print("Data de nascimento inválida! Use o formato dd/mm/aaaa")
        return
    
    cliente = PessoaFisica(cpf, nome, data_nascimento, endereco)
    clientes.append(cliente)
    print("Usuário criado com sucesso!")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do usuário: ").strip()
    cliente = encontrar_cliente(cpf, clientes)
    
    if cliente:
        conta = ContaCorrente.nova_conta(cliente, numero_conta)
        cliente.adicionar_conta(conta)
        contas.append(conta)
        print("Conta criada com sucesso!")
    else:
        print("Cliente não encontrado!")

def listar_contas(contas):
    if not contas:
        print("Nenhuma conta cadastrada.")
        return
    
    for conta in contas:
        print(f"\n{'='*40}")
        print(f"Agência: {conta.agencia}")
        print(f"Conta: {conta.numero}")
        print(f"Titular: {conta.cliente.nome}")
        print(f"Saldo: R$ {conta.saldo:.2f}")
        if isinstance(conta, ContaCorrente):
            print(f"Limite: R$ {conta.limite:.2f}")
            print(f"Saques restantes: {conta.limite_saques - conta._saques_realizados}")

def exibir_extrato(conta):
    print("\n" + "="*50)
    print("EXTRATO".center(50))
    print("="*50)
    
    if not conta.historico.transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for transacao in conta.historico.transacoes:
            if isinstance(transacao, Deposito):
                print(f"Depósito: R$ {transacao.valor:.2f}")
            elif isinstance(transacao, Saque):
                print(f"Saque: R$ {transacao.valor:.2f}")
    
    print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
    if isinstance(conta, ContaCorrente):
        saldo_disponivel = conta.saldo + conta.limite
        print(f"Saldo disponível: R$ {saldo_disponivel:.2f}")
    print("="*50)

def selecionar_conta(cliente):
    """Permite ao cliente selecionar uma de suas contas"""
    if len(cliente.contas) == 1:
        return cliente.contas[0]
    
    print(f"\n{cliente.nome}, você possui {len(cliente.contas)} conta(s):")
    for i, conta in enumerate(cliente.contas, 1):
        print(f"[{i}] Conta {conta.numero} - Agência {conta.agencia}")
    
    while True:
        try:
            escolha = int(input("Escolha o número da conta: ")) - 1
            if 0 <= escolha < len(cliente.contas):
                return cliente.contas[escolha]
            else:
                print("Opção inválida!")
        except ValueError:
            print("Digite um número válido!")

# ==================== PROGRAMA PRINCIPAL ====================

def main():
    clientes = []
    contas = []
    
    print("Bem-vindo ao Sistema Bancário DIO!")
    
    while True:
        opcao = menu()
        
        if opcao == "nu":
            criar_usuario(clientes)
            
        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
            
        elif opcao == "lc":
            listar_contas(contas)
            
        elif opcao in ["d", "s", "e"]:
            cpf = input("Informe o CPF do titular: ").strip()
            cliente = encontrar_cliente(cpf, clientes)
            
            if not cliente:
                print("Cliente não encontrado!")
                continue
                
            if not cliente.contas:
                print("Cliente não possui contas.")
                continue
            
            conta = selecionar_conta(cliente)
            
            if opcao == "d":
                valor = obter_valor("Informe o valor do depósito: R$ ")
                transacao = Deposito(valor)
                cliente.realizar_transacao(conta, transacao)
                
            elif opcao == "s":
                valor = obter_valor("Informe o valor do saque: R$ ")
                transacao = Saque(valor)
                cliente.realizar_transacao(conta, transacao)
                
            elif opcao == "e":
                exibir_extrato(conta)
                
        elif opcao == "q":
            print("Obrigado por usar o sistema bancário DIO. Até logo!")
            break
            
        else:
            print("Operação inválida. Tente novamente.")

if __name__ == "__main__":
    main()
