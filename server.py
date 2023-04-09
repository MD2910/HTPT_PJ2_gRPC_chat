import time
import grpc
from concurrent import futures
import chat_pb2
import chat_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class ChatServer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.clients = []
        self.messages = []

    def SendMessage(self, request, context):
        message = f"{request.username}: {request.message}"
        self.messages.append(message)
        for client in self.clients:
            client.SendMessage(chat_pb2.ChatMessage(username=request.username, message=request.message, seq_number=request.seq_number))
        return chat_pb2.Empty()

    def RegisterUser(self, request_iterator, context):
        for request in request_iterator:
            self.clients.append(context)
            for message in self.messages:
                context.SendMessage(chat_pb2.ChatMessage(username="", message=message, seq_number=0))
            while True:
                try:
                    request = next(request_iterator)
                    self.HandleLike(request.seq_number, request.username)
                except StopIteration:
                    self.clients.remove(context)
                    return chat_pb2.Empty()

    def HandleLike(self, seq_number, username):
        count = sum(1 for message in self.messages if message.endswith(f"{seq_number-1})"))
        if count >= 2:
            message = f"{username} liked message ({seq_number-1})"
            self.messages.append(message)
            for client in self.clients:
                client.SendMessage(chat_pb2.ChatMessage(username="", message=message, seq_number=0))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
