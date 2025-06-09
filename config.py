# IP e porta do remetente (sender)
SENDER_IP = "0.0.0.0"  # IP onde o emissor escutará por ACKs
SENDER_PORT = 5000     # Porta usada pelo emissor

# Porta usada pelos receptores para receber mensagens
RECEIVER_PORT = 6000

# Lista de IPs dos receptores na LAN
RECEIVER_IPS = [
    "0.0.0.0"
]

# Tamanho da janela deslizante (Sliding Window)
WINDOW_SIZE = 4

# Número total de pacotes que serão enviados
TOTAL_PACKETS = 10

# Timeout para reenvio de pacotes não reconhecidos
TIMEOUT = 2

# Timeout usado pelo receptor para encerrar caso não receba pacotes
TIMEOUT_RECEIVER = 30
