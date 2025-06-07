import socket
import json
import threading
import time
from config import *

base = 0
next_seq = 0
timers = {}
ack_table = {i: set() for i in range(TOTAL_PACKETS)}
lock = threading.Lock()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SENDER_IP, SENDER_PORT))

def enviar_pacote(seq):
    pacote = {
        "seq": seq,
        "data": f"Mensagem {seq}",
        "ack": False
    }
    for ip in RECEIVER_IPS:
        sock.sendto(json.dumps(pacote).encode(), (ip, RECEIVER_PORT))
    print(f"📤 Enviado: {pacote}")

def start_timer(seq):
    timer = threading.Timer(TIMEOUT, timeout_handler, [seq])
    timer.start()
    timers[seq] = timer

def timeout_handler(seq):
    global base, next_seq
    with lock:
        print(f"⏰ Timeout no pacote {seq}. Reenviando a partir de {base}")
        for i in range(base, next_seq):
            enviar_pacote(i)
            start_timer(i)

def escutar_acks():
    global base
    while True:
        data, addr = sock.recvfrom(1024)
        ack = json.loads(data.decode())
        if ack.get("ack"):
            with lock:
                seq_ack = ack["seq"]
                sender_ip = addr[0]
                ack_table[seq_ack].add(sender_ip)
                print(f"✅ ACK de {sender_ip} para pacote {seq_ack}")

                # Avança base somente se todos os receptores confirmaram
                while base < TOTAL_PACKETS and all(ip in ack_table[base] for ip in RECEIVER_IPS):
                    if base in timers:
                        timers[base].cancel()
                        del timers[base]
                    base += 1

def emissor():
    global next_seq
    threading.Thread(target=escutar_acks, daemon=True).start()

    while base < TOTAL_PACKETS:
        with lock:
            while next_seq < base + WINDOW_SIZE and next_seq < TOTAL_PACKETS:
                enviar_pacote(next_seq)
                start_timer(next_seq)
                next_seq += 1
        time.sleep(0.5)

    # Espera fim dos ACKs
    while base < TOTAL_PACKETS:
        time.sleep(1)

    print("✅ Todos os pacotes enviados e reconhecidos por todos os receptores!")

if __name__ == "__main__":
    emissor()
