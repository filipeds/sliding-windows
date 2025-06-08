import socket
import json
from config import *

expected_seq = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("Ip receptor", RECEIVER_PORT))  # ou o IP da sua máquina

sock.settimeout(TIMEOUT_RECEIVER)  # Timeout opcional de 30 segundos

print("📡 Receptor pronto...")

while True:
    try:
        data, addr = sock.recvfrom(1024)
        pacote = json.loads(data.decode())

        # Pacote de encerramento
        if pacote.get("fim"):
            print("📴 Fim da transmissão recebido. Encerrando receptor.")
            break

        if not pacote.get("ack"):
            seq = pacote["seq"]
            print(f"📦 Recebido: {pacote}")

            if seq == expected_seq:
                print(f"✔ Pacote {seq} OK")
                ack = { "seq": seq, "ack": True }
                sock.sendto(json.dumps(ack).encode(), addr)
                expected_seq += 1
            else:
                print(f"❌ Pacote {seq} fora de ordem (esperado: {expected_seq})")
                ack = { "seq": expected_seq - 1, "ack": True }
                sock.sendto(json.dumps(ack).encode(), addr)

    except socket.timeout:
        print("⏳ Timeout: nenhum pacote recebido. Encerrando receptor.")
        break
