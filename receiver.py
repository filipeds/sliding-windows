import socket
import json
from config import *

expected_seq = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", RECEIVER_PORT))

print("📡 Receptor pronto...")

while True:
    data, addr = sock.recvfrom(1024)
    pacote = json.loads(data.decode())

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
