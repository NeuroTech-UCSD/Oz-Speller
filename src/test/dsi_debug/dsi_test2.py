import socket

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(('localhost',8844))
    while True:
        data = sock.recv(921600)
        # data = sock.recv(294912)
        # val = 80
        # sock.sendall(val.to_bytes(1,'big'))