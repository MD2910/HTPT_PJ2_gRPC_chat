import grpc
import chat_pb2
import chat_pb2_grpc
import threading


class ChatClient:
    def __init__(self, username):
        self.username = username
        self.seq_number = 0

    def SendMessage(self, message):
        self.seq_number += 1
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = chat_pb2_grpc.ChatServiceStub(channel)
            response = stub.SendMessage(chat_pb2.ChatMessage(username=self.username, message=message, seq_number=self.seq_number))

    def Start(self):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = chat_pb2_grpc.ChatServiceStub(channel)
            request_iterator = iter([chat_pb2.ChatMessage(username=self.username, message="", seq_number=0)])
            response_iterator = stub.RegisterUser(request_iterator)
            for response in response_iterator:
                if response.username:
                    print(f"{response.username}: {response.message}")
                elif response.message:
                    print(response.message)


def main():
    username = input("Enter username: ")
    client = ChatClient(username)
    t = threading.Thread(target=client.Start)
    t.start()
    while True:
        message = input()
        client.SendMessage(message)


if __name__ == '__main__':
    main()
