# 🪟 Sliding Windows Protocol (Janela Deslizante)

Este projeto é uma implementação didática do protocolo de **Janela Deslizante (Sliding Window)**, seguindo o modelo **Go-Back-N**, com o objetivo de simular uma camada de transporte confiável sobre uma rede não confiável, sem utilizar sockets TCP ou bibliotecas prontas.



## 📘 Descrição

A técnica de Janela Deslizante permite que o remetente envie múltiplos datagramas por vez, dentro de uma "janela" de envio. Ao receber os ACKs (confirmações), o remetente desliza a janela para frente e continua a transmissão. Se algum datagrama dentro da janela se perder, ele e todos os seguintes serão retransmitidos, garantindo a entrega **ordenada e confiável**.



## 🎯 Objetivos

- Enviar vários datagramas simultaneamente.
- Garantir **ordenação perfeita** na entrega dos dados.
- **Retransmitir datagramas perdidos** usando o protocolo Go-Back-N.
- Simular comportamento similar ao protocolo TCP, **sem usar TCP**.



## 🚀 Como Executar

1. Clone este repositório:
   ```bash
   git clone https://github.com/filipeds/sliding-windows.git
   cd sliding-windows