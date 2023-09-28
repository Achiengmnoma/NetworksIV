import threading
import socket
host = '127.0.0.1' # localhost
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
class Server:
        def __init__(self):
            self.clients = []
            self.nicknames = []

        def broadcast(self,message):
            for client in self.clients:
                client.send(message)

        def handle(self,client):
            while True:
                try:
                    message = client.recv(1024)
                    self.broadcast(message)
                except:
                    index = self.clients.index(client)
                    self.clients.remove(client)
                    client.close()
                    nickname = self.nicknames[index]
                    self.broadcast(f'{nickname} left the chat!'.encode('ascii'))
                    self.nicknames.remove(nickname)
                    break

        def receive(self):
            while True:
                client, address = server.accept()
                print(f"Connected with {str(address)}")

                client.send('NICK'.encode('ascii'))
                nickname = client.recv(1024).decode('ascii')
                self.nicknames.append(nickname)
                self.clients.append(client)

                print(f'Nickname of the client is {nickname}!')
                self.broadcast(f'{nickname} joined the chat!'.encode('ascii'))
                client.send('Connected to the server!'.encode('ascii'))

                thread = threading.Thread(target=self.handle, args=(self.client,))
                thread.start()

print("Server is listening...")
server = Server()
server.receive()
