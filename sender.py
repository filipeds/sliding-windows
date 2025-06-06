import socket
import json
import threading
import time
from config import *

base = 0
next_seq = 0
timers = {}
lock = threading.Lock()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SENDER_IP, SENDER_PORT))

def enviar_pacote(seq):
    pacote = {
        "seq": seq,
        "data": f"Mensagem {seq}",
        "ack": False
    }
    sock.sendto(json.dumps(pacote).encode(), (RECEIVER_IP, RECEIVER_PORT))
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
        data, _ = sock.recvfrom(1024)
        ack = json.loads(data.decode())
        if ack.get("ack"):
            with lock:
                seq_ack = ack["seq"]
                if seq_ack >= base:
                    print(f"✅ ACK recebido: {seq_ack}")
                    for i in range(base, seq_ack + 1):
                        if i in timers:
                            timers[i].cancel()
                            del timers[i]
                    base = seq_ack + 1

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

    print("✅ Todos os pacotes enviados e reconhecidos!")

if __name__ == "__main__":
    emissor()
