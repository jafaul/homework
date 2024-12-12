import socket
from typing import Optional

# socket.SOCK_STREAM - TCP
# SOCK_DGRAM - UDP

# Command examples:
# 1. Get the value of a dictionary key: get "<%dict_key%>"
# 2. Set a value for a dictionary key: set "<%dict_key%>" <%value%>
# 3. Get all dictionary keys: getkeys
# 4. Exit the command interface: exit

HOST = '127.0.0.1'
PORT = 53554
COMMANDS = ("get", "set", "getkeys", "exit")


class DictManager:
    def __init__(self, dict_data: Optional[dict] = None):
        self.dict_data = dict_data if dict_data is not None else {}

    @property
    def getkeys(self) -> list:
        return list(self.dict_data.keys())

    def get(self, dict_key: str) -> str:
        value = self.dict_data.get(dict_key)
        return f"Result: {value}" if value is not None else "Error: empty value"

    def set(self, dict_key, dict_value) -> str | None:
        if not dict_value.isdigit():
            return "Error: not a number"
        else:
            self.dict_data[dict_key] = dict_value


class CommandParser:
    def __init__(self, command: str):
        self.command = command

    @property
    def cmd(self):
        return self.command.split(" ")[0].lower()

    @property
    def params(self) -> list:
        if len(self.command) == len(self.cmd): return []
        command_parts = self.command.split(self.cmd)[1].strip().split('"')

        attributes = [command_part.strip() for command_part in command_parts if command_part.strip()]
        return attributes


class RpcServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.dict_manager = DictManager()

    def __process_command(self, command):
        cmd_parser = CommandParser(command)
        if cmd_parser.cmd == "get":
            result = self.dict_manager.get(cmd_parser.params[0])
        elif cmd_parser.cmd == "set":
            result = self.dict_manager.set(cmd_parser.params[0], cmd_parser.params[1])
        elif cmd_parser.cmd == "getkeys":
            result = self.dict_manager.getkeys
        elif not cmd_parser.cmd or cmd_parser.cmd == "exit":
            result = cmd_parser.cmd
        else:
            result = f"Unknown method '{cmd_parser.cmd}'"
            
        if result and not result.endswith("\r\n"): result += "\r\n"
        return result 

    def _handle_client(self, conn, addr):
        while conn:
            print(f"Connected by {addr}")
            while True:
                buf = conn.recv(1024)

                command = buf.decode("utf-8").strip()
                print(f"Received request: '{request}'")

                if command == "exit":
                    print("Exit command received. Closing connection.")
                    break
                result = self.__process_command(command)
                 if result == "exit":
                    print("Exit command received. Closing connection.")
                    conn = False
                    break

                if result is not None:
                    print(f"{result}")

                conn.sendall(f"{result}".encode("utf-8"))

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # setsockopt helps to avoid bind() exception: OSError: [Errno 48] Address already in use
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen(5)
            conn, addr = s.accept()
            self._handle_client(conn, addr)


if __name__ == "__main__":
    rpc_server = RpcServer(HOST, PORT)
    rpc_server.start()
