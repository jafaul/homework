import os
import socket
import sys
from typing import Optional

from homework.sockets.constants import SERVER_HOST, SERVER_PORT


# socket.SOCK_STREAM - TCP
# SOCK_DGRAM - UDP

# Command examples:
# 1. Get the value of a dictionary key: get "<%dict_key%>"
# 2. Set a value for a dictionary key: set "<%dict_key%>" <%value%>
# 3. Get all dictionary keys: getkeys
# 4. Exit the command interface: exit


class DictManager:
    def __init__(self, dict_data: Optional[dict] = None):
        self.dict_data = dict_data if dict_data is not None else {}
        self.COMMANDS = {
            "get": self.__get,
            "set": self.__set,
            "getkeys": self.__getkeys,
            "exit": "exit"
        }

    @property
    def __getkeys(self) -> list:
        return list(self.dict_data.keys())

    def __get(self, dict_key: str) -> str:
        value = self.dict_data.get(dict_key)
        return f"Result: {value}" if value is not None else "Error: empty value"

    def __set(self, dict_key, dict_value) -> str | None:
        if not dict_value.isdigit():
            return "Error: not a number"
        else:
            self.dict_data[dict_key] = dict_value
            return f"Set {dict_key} to {dict_value}"


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
        command_func = self.dict_manager.COMMANDS.get(cmd_parser.cmd)

        if not command_func:
            return f"Unknown method '{cmd_parser.cmd}'\r\n"

        if callable(command_func):
            result = command_func(*cmd_parser.params)
        else:
            result = command_func

        if result and not result.endswith("\r\n"):
            result += "\r\n"
        return result 

    def _handle_client(self, conn, addr):
        print(f"Connected by {addr}")
        with conn:
            while True:
                buf = conn.recv(1024)
                command = buf.decode("utf-8").strip()
                print(f"Received request: '{command}'")

                result = self.__process_command(command)
                if result.strip() == "exit":
                    print("Exit command received. Closing connection.")
                    conn.close()
                    break
                if result is not None:
                    print(f"{result}")

                conn.sendall(f"{result}".encode("utf-8"))

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # setsockopt helps to avoid bind() exception: OSError: [Errno 48] Address already in use
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            s.bind((self.host, self.port))
            s.listen(5)
            while True:
                conn, addr = s.accept()
                pid = os.fork()
                # from pdb import set_trace; set_trace()
                # pid is a process ID
                if pid == 0:
                    # parent process
                    continue
                else:
                    try:
                        # current already existed process
                        self._handle_client(conn, addr)
                    except Exception as e:
                        print(e)
                    sys.exit(0)


if __name__ == "__main__":
    rpc_server = RpcServer(SERVER_HOST, SERVER_PORT)
    rpc_server.start()
