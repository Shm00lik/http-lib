import socket

class Communication:
    @staticmethod
    def getData(clientSocket: socket.socket, timeout: float = 1) -> str:
        result = ""

        # for preventing dDoS attacks
        clientSocket.settimeout(timeout)

        while True:
            try:
                chunk = clientSocket.recv(1024)
            except socket.timeout:
                break

            if not chunk:
                break

            result += chunk.decode()

            if "\r\n\r\n" in result:
                break

        return result
