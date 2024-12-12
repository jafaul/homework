import argparse
import socket

from homework.sockets.constants import CLIENT_TIMEOUT


class RpcVal:
    def __init__(self, key):
        self.key = key
        self.value = None


class RpcClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.timeout = CLIENT_TIMEOUT
        self.local_data = {}
        self.s = self._connect()

    def _connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(self.timeout)
        s.connect((self.host, self.port))
        return s

    def _send_request(self, request: str):
        print(request)
        self.s.send(request.encode('utf-8'))
        response = self.s.recv(1024).decode('utf-8')
        print(f"Server response: {response}")
        return response

    def __setitem__(self, key, value):
        self.local_data[key] = value
        self._send_request(f'set "{key}" {value}')

    def __getitem__(self, key):
        value = self.local_data[key] if key in self.local_data else "Error: empty value"
        return value

    def add_val(self, rpc_val: RpcVal):
        response = self._send_request(f'get "{rpc_val.key}"')
        rpc_val.value = response.split(': ')[1] if response.strip() != "Error: empty value" else response.strip()
        self.local_data[rpc_val.key] = rpc_val.value

    def __iadd__(self, key: str, value: int):
        if key in self.local_data and self.local_data[key].isdigit():
            self.local_data[key] += value
        else:
            self.local_data[key] = value

    def close(self):
        self.s.send('exit'.encode('utf-8'))
        self.s.close()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=True, help="Server hostname")
    parser.add_argument('--port', type=int, required=True, help="Server port")
    return parser.parse_args()


def main():
    args = parse_arguments()
    rpc_client = RpcClient(host=args.host, port=args.port)
    print(f"Connecting to RPC client at {rpc_client.host}:{rpc_client.port}")

    try:
        rpc_client['x'] = 4  # save value 4 locally
        rpc_client.add_val(RpcVal('y'))  # create link on server
        rpc_client['y']  # return value from server(‘Error: empty value’)
        rpc_client['y'] = 5  # set value on server
        rpc_client['y']  # return value from server (5)
        rpc_client['y'] += 4  # change value on server
        rpc_client['y']  # return value from server (9)
        rpc_client['x'] + rpc_client['y']  #  return sum ([local x, remote y])
    finally:
        rpc_client.close()


if __name__ == '__main__':
    main()
