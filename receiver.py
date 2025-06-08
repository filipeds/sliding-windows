import socket
import json
from config import *

expected_seq = 0  # Número de sequência esperado (para manter a ordem)

# Criação e configuração do socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("Ip receptor", RECEIVER_PORT))  # Substitua por IP real da máquina receptora

sock.settimeout(TIMEOUT_RECEIVER)  # Define timeout de inatividade

print("📡 Receptor pronto...")

while True:
    try:
        data, addr = sock.recvfrom(1024)  # Espera por dados do emissor
        pacote = json.loads(data.decode())

        # Verifica se é um pacote de encerramento
        if pacote.get("fim"):
            print("📴 Fim da transmissão recebido. Encerrando receptor.")
            break

        # Se for um pacote de dados
        if not pacote.get("ack"):
            seq = pacote["seq"]
            print(f"📦 Recebido: {pacote}")

            # Se for o pacote esperado, envia ACK e avança
            if seq == expected_seq:
                print(f"✔ Pacote {seq} OK")
                ack = { "seq": seq, "ack": True }
                sock.sendto(json.dumps(ack).encode(), addr)
                expected_seq += 1
            else:
                # Pacote fora de ordem: reenvia o último ACK conhecido
                print(f"❌ Pacote {seq} fora de ordem (esperado: {expected_seq})")
                ack = { "seq": expected_seq - 1, "ack": True }
                sock.sendto(json.dumps(ack).encode(), addr)

    except socket.timeout:
        print("⏳ Timeout: nenhum pacote recebido. Encerrando receptor.")
        break
