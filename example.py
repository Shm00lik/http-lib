from server import Server
import protocol


def handleClient(request: protocol.Request, clientSocket, clientAddress):
    print(f"New client connected: {clientAddress}")
    print(f"Request headers: {request.url}")

    clientSocket.sendall(protocol.Response(content="Hello!").generate().encode())


server = Server(handleClient)
server.start()

input("Press enter to stop server...")
server.stop()
