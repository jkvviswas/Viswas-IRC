import socket
import threading
import argparse
import datetime

# Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def ts():
    return datetime.datetime.now().strftime("[%H:%M:%S]")

parser = argparse.ArgumentParser()
parser.add_argument("--server", default="irc.libera.chat")
parser.add_argument("--port", type=int, default=6667)
parser.add_argument("--nick", required=True)
parser.add_argument("--channel", required=True)
args =parser.parse_args()

server = args.server
port = args.port
nick = args.nick
channel = args.channel

state = {
    "nick": nick,
    "connected": True,
    "channel": channel
}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server, port))
print(GREEN + ts(), "Connected to server" + RESET)

sock.sendall(f"NICK {nick}\r\n".encode())
sock.sendall(f"USER {nick} 0 * :{nick}\r\n".encode())
sock.sendall(f"JOIN {channel}\r\n".encode())

def receive():
    while True:
        try:
            data = sock.recv(4096).decode(errors="ignore")
            for line in data.split("\r\n"):
                if not line:
                    continue

                if line.startswith("PING"):
                    sock.sendall((line.replace("PING", "PONG") + "\r\n").encode())
                    print(YELLOW + ts(), "PING received, sent PONG" + RESET)
                    continue

                print(BLUE + ts(), line + RESET)

        except:
            print(RED + ts(), "Disconnected by server" + RESET)
            break

def send():
    while True:
        try:
            msg = input()
            if not msg:
                continue

            if msg.startswith("/join"):
                ch = msg.split()[1]
                state["channel"] = ch
                sock.sendall(f"JOIN {ch}\r\n".encode())
                print(GREEN + ts(), "Joined", ch + RESET)

            elif msg == "/quit":
                sock.sendall("QUIT :Bye\r\n".encode())
                sock.close()
                print(RED + ts(), "Quit" + RESET)
                break

            elif msg == "/part":
                if state["channel"]:
                    sock.sendall(f"PART {state['channel']}\r\n".encode())
                    print("Left channel", state["channel"])
                    state["channel"] = ""   # not None
                else:
                    print("You are not in any channel")

            else:
                if not state["channel"]:
                    print("Join a channel first using /join #channel")
                    continue
                sock.sendall(f"PRIVMSG {state['channel']} :{msg}\r\n".encode())
                print(GREEN + ts(), "You:", msg + RESET)

        except:
           print(RED + ts(), "Disconnected by server" + RESET)
           break

threading.Thread(target=receive, daemon=True).start()
send()
