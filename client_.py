import asyncio
import websockets
from plyer import notification
import getpass

usuario = getpass.getuser()
IP_SERVIDOR = "10.11.0.144"  # IP do servidor
PORTA = 8765

async def listen():
    while True:
        try:
            async with websockets.connect(f"ws://{IP_SERVIDOR}:{PORTA}") as websocket:
                await websocket.send(usuario)
                print(f"{usuario} conectado ao servidor.")

                while True:
                    msg = await websocket.recv()
                    print(f"Mensagem recebida: {msg}")
                    notification.notify(
                        title=f"Mensagem para {usuario}",
                        message=msg,
                        timeout=5
                    )

        except Exception as e:
            print(f"Erro de conexão: {e}. Tentando reconectar em 3s...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(listen())
