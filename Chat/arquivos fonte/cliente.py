import socket
import tkinter as tk
from tkinter import messagebox
import threading
import re

# Códigos ANSI para cores
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
PADRAO = "\033[0m"  # Reseta a cor para o padrão

# Função para enviar mensagens do chat
def enviar_mensagem():
    mensagem_texto = mensagem.get()
    if mensagem_texto and client_socket:
        client_socket.send(mensagem_texto.encode('utf-8'))
        chat_area.insert(tk.END, f"Você: ", "azul")
        chat_area.insert(tk.END, f"{mensagem_texto}\n")
        chat_area.yview(tk.END)
        mensagem.delete(0, tk.END)
        if mensagem_texto.lower() == 'sair':
            client_socket.close()


def voltar():
    server_listbox.pack_forget()
    connect_button.pack_forget()
    nome_label.place(relx=0.5, rely=0.15, anchor="center")
    nome_entry.place(relx=0.5, rely=0.18, anchor="center", width=140)
    porta_label.place(relx=0.5, rely=0.21, anchor="center")
    porta_entry.place(relx=0.5, rely=0.24, anchor="center", width=140)
    discover_button.place(relx=0.5, rely=0.29, anchor="center")
    voltar_lista_servidores.pack_forget()


# Função para receber mensagens do servidor em uma thread separada
def receive_messages(client_socket):
    while True:
        try:
            response = client_socket.recv(1024).decode('utf-8')
            if response:
                chat_area.insert(tk.END, f"{response}\n")
                chat_area.yview(tk.END)
            else:
                break
        except:
            chat_area.insert(tk.END, "Conexão com o servidor perdida.\n")
            break

# Função para se conectar a um servidor de chat
def connect_to_chat_server():
    global client_socket
    server_index = server_listbox.curselection()
    if not server_index:
        chat_area.insert(tk.END, "Por favor, selecione um servidor para se conectar.\n")
        return

    ip, port = server_listbox.get(server_index[0]).split(":")
    port = int(port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))

    # Envia o nome do usuário
    client_name = nome_entry.get()
    if not client_name:
        chat_area.insert(tk.END, "Por favor, digite seu nome antes de se conectar.\n")
        return
    client_socket.send(client_name.encode('utf-8'))

    chat_area.insert(tk.END, f"Conectado ao servidor {ip}:{port}.\n")

    # Inicia uma thread para receber mensagens do servidor
    receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receiver_thread.daemon = True
    receiver_thread.start()

    # Oculta elementos desnecessários e mostra a área de mensagens
    nome_label.pack_forget()
    nome_entry.pack_forget()
    porta_label.pack_forget()
    porta_entry.pack_forget()
    discover_button.pack_forget()
    server_listbox.pack_forget()
    connect_button.pack_forget()
    voltar_lista_servidores.pack_forget()
    chat_area.pack(fill="x")
    mensagem.pack(side="left", padx=5, ipady=5)
    botao_enviar.pack(side="left", padx=5)

# Função para descobrir servidores de chat
def discover_chat_servers():
    try:
        porta_broadcast = int(porta_entry.get())

        discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        discovery_socket.sendto("Descubra servidores de chat".encode('utf-8'), ('<broadcast>', porta_broadcast))
        chat_area.insert(tk.END, "Enviado pedido de descoberta...\n")

        servers = []
        try:
            discovery_socket.settimeout(3)
            while True:
                message, address = discovery_socket.recvfrom(1024)
                message = message.decode('utf-8')
                match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', message)
                if match:
                    ip = match.group(1)
                    port = int(match.group(2))
                    servers.append((ip, port))
                    server_listbox.insert(tk.END, f"{ip}:{port}")
        except socket.timeout:
            if not servers:
                messagebox.showerror("timeout", "Nenhum servidor encontrado, por favor, tente novamente!")


        # Mostra a lista de servidores e o botão de conexão se houver servidores encontrados
        if servers:
            server_listbox.pack(ipadx=10, ipady=20, padx = 3)
            connect_button.pack()
            voltar_lista_servidores.pack()

    except ValueError:
        messagebox.showerror("Erro de Entrada", "Por favor, digite uma porta válida.")


# Configuração da interface gráfica
janela = tk.Tk()
janela.geometry("500x700")
janela.title("AppWhats, o mensageiro mais rápido!")

janela.resizable(False, False)

# Cria o rótulo com o texto "AppWhats", fundo verde, texto branco e centralizado horizontalmente
label = tk.Label(janela, text="AppWhats", fg="green", font=("Helvetica", 40))
label.pack()

# Campo para entrada de nome
nome_label = tk.Label(janela, text="Digite seu nome:", font=("Helvetica", 13))
nome_label.place(relx=0.5, rely=0.15, anchor="center")
nome_entry = tk.Entry(janela)
nome_entry.place(relx=0.5, rely=0.18, anchor="center", width=140)

# Campo para entrada de porta de broadcast
porta_label = tk.Label(janela, text="Porta de broadcast:", font=("Helvetica", 12))
porta_label.place(relx=0.5, rely=0.21, anchor="center")
porta_entry = tk.Entry(janela)
porta_entry.place(relx=0.5, rely=0.24, anchor="center", width=140)

# Botão para buscar servidores
discover_button = tk.Button(janela, text="Buscar Servidores", font=("Helvetica", 12), fg="white", bg="green", command=discover_chat_servers)
discover_button.place(relx=0.5, rely=0.29, anchor="center")

# Lista de servidores encontrados (inicialmente oculto)
server_listbox = tk.Listbox(janela)

# Botão para conectar ao servidor selecionado (inicialmente oculto)
connect_button = tk.Button(janela, text="Conectar", font=("Helvetica", 12), fg="white", bg="green", command=connect_to_chat_server)
voltar_lista_servidores = tk.Button(janela, text="voltar", font=("Helvetica", 12), fg="white", bg="green", command=voltar)

# Área de chat
chat_area = tk.Text(janela, state='normal', height=32)
chat_area.tag_config("azul", foreground="blue")

# Campo para escrever mensagens (inicialmente oculto)
mensagem = tk.Entry(janela, width=63)

# Botão para enviar mensagem (inicialmente oculto)
imagem_botao_enviar = tk.PhotoImage(file="../imagens/enviar.png")
botao_enviar = tk.Button(janela, image=imagem_botao_enviar, borderwidth=0, relief="flat", command=enviar_mensagem)

# pressiona o botão enviar quando damos enter enquanto estamos digitando o texto
mensagem.bind("<Return>", lambda event: botao_enviar.invoke())

# Variável global para o socket do cliente
client_socket = None

janela.mainloop()
