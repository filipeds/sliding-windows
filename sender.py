import socket
import json
import threading
import time
from config import *

# Variáveis de controle
base = 0                 # Primeiro pacote ainda não confirmado
next_seq = 0             # Próximo número de sequência a ser enviado
timers = {}              # Dicionário que armazena os temporizadores por sequência
ack_table = {i: set() for i in range(TOTAL_PACKETS)}  # Armazena os ACKs recebidos por pacote
lock = threading.Lock()  # Lock para garantir acesso seguro às variáveis em múltiplas threads

# Cria o socket UDP do emissor
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SENDER_IP, SENDER_PORT))  # Liga o socket à porta para receber ACKs

# Envia um pacote com determinado número de sequência para todos os receptores
def enviar_pacote(seq):
    pacote = {
        "seq": seq,
        "data": f"Mensagem {seq}",
        "ack": False
    }
    for ip in RECEIVER_IPS:
        sock.sendto(json.dumps(pacote).encode(), (ip, RECEIVER_PORT))
    print(f"📤 Enviado: {pacote}")

# Inicia um temporizador para reenviar o pacote caso não receba ACK a tempo
def start_timer(seq):
    timer = threading.Timer(TIMEOUT, timeout_handler, [seq])
    timer.start()
    timers[seq] = timer

# Função chamada quando o tempo de espera por ACK expira
def timeout_handler(seq):
    global base, next_seq
    with lock:
        print(f"⏰ Timeout no pacote {seq}. Reenviando a partir de {base}")
        for i in range(base, next_seq):  # Reenvia todos os pacotes pendentes
            enviar_pacote(i)
            start_timer(i)

# Thread que escuta por ACKs recebidos dos receptores
def escutar_acks():
    global base
    while True:
        data, addr = sock.recvfrom(1024)
        ack = json.loads(data.decode())
        if ack.get("ack"):
            with lock:
                seq_ack = ack["seq"]
                sender_ip = addr[0]
                ack_table[seq_ack].add(sender_ip)  # Marca que esse IP reconheceu o pacote
                print(f"✅ ACK de {sender_ip} para pacote {seq_ack}")

                # Move a base se todos os receptores confirmaram o pacote atual
                while base < TOTAL_PACKETS and all(ip in ack_table[base] for ip in RECEIVER_IPS):
                    if base in timers:
                        timers[base].cancel()
                        del timers[base]
                    base += 1

# Função principal de envio de pacotes com controle de janela e tempo
def emissor():
    global next_seq
    threading.Thread(target=escutar_acks, daemon=True).start()  # Inicia thread para escutar ACKs

    while base < TOTAL_PACKETS:
        with lock:
            # Envia novos pacotes dentro da janela
            while next_seq < base + WINDOW_SIZE and next_seq < TOTAL_PACKETS:
                enviar_pacote(next_seq)
                start_timer(next_seq)
                next_seq += 1
        time.sleep(0.5)  # Intervalo para evitar envio muito agressivo

    while base < TOTAL_PACKETS:
        time.sleep(1)  # Aguarda todos os ACKs finais

    print("✅ Todos os pacotes enviados e reconhecidos por todos os receptores!")

    # Envia pacote especial para indicar o fim da transmissão
    fim_pacote = json.dumps({ "fim": True }).encode()
    for ip in RECEIVER_IPS:
        sock.sendto(fim_pacote, (ip, RECEIVER_PORT))
    print("📴 Pacotes de fim enviados.")

if __name__ == "__main__":
    emissor()  # Inicia o processo de envio
