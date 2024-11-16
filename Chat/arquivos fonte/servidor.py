import socket
import threading


# Códigos ANSI para cores
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
PADRAO = "\033[0m"  # Reseta a cor para o padrão

# função para achar uma porta de broadcast livre
def encontrar_porta_livre():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 0))
    porta_livre = s.getsockname()[1]
    s.close()
    return porta_livre

porta_chat = encontrar_porta_livre()

# Função para gerenciar a comunicação com um cliente
def handle_client(client_socket, client_address):
    print(f"Cliente {client_address} conectado.")
    try:

        # recebe o nome do cliente
        client_name = client_socket.recv(1024).decode('utf-8').strip()
        print(GREEN + f"{client_name} (IP: {client_address}) se juntou ao chat." + PADRAO)

        # Envia uma mensagem de boas-vindas para o cliente
        client_socket.send(f"\nBem-vindo ao chat, {client_name}!\n".encode('utf-8'))

        # Transmite a entrada do novo usuário para os outros
        broadcast(f"\n{client_name} entrou no chat.\n", client_socket)

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Mensagem de {client_name}: {message}")
            broadcast(f"{client_name}: {message}", client_socket)
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        print(RED + f"{client_name} ({client_address}) saiu do chat." + PADRAO)
        clients.remove(client_socket)
        broadcast(f"\n{client_name} saiu do chat.\n", client_socket)
        client_socket.close()


# Função para enviar mensagens a todos os outros clientes
def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                clients.remove(client)

# Lista de clientes conectados
clients = []


# Função principal que cria o servidor de chat
def chat_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', porta_chat))
    server_socket.listen(5)

    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()


# Função de resposta ao broadcast de descoberta (para os clientes)
def listen_for_discovery():
    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    porta_descorberta = encontrar_porta_livre()
    discovery_socket.bind(('0.0.0.0', porta_descorberta))  # Porta 5556 para escutar discovery
    print("Servidor esperando por solicitações para entrar no chat...")
    print(GREEN + f"porta de broadcast do chat: " + PADRAO + f"{porta_descorberta}")

    while True:
        # Espera por uma solicitação de broadcast
        message, address = discovery_socket.recvfrom(1024)
        print(f"ip: {address} quer se juntar ao chat!")

        # Responde com IP e Porta
        discovery_socket.sendto(
            f"ip: {socket.gethostbyname(socket.gethostname())}:{porta_chat}".encode('utf-8'),
            address)


# Inicia a thread para escutar solicitações de descoberta
discovery_thread = threading.Thread(target=listen_for_discovery, daemon=True)
discovery_thread.start()

# Inicia o servidor de chat
chat_server_thread = threading.Thread(target=chat_server, daemon=True)
chat_server_thread.start()

# Mantém o servidor rodando
while True:
    pass
