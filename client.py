import asyncio
import websockets
import getpass
import tkinter as tk
from threading import Thread
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except:
    toaster = None

# usuario = "user1"  # ou getpass.getuser()
usuario = getpass.getuser()
IP_SERVIDOR = "10.11.0.144"
PORTA = 8765

def show_popup(titulo, mensagem, icon_path=None):
    """Popup Tkinter que fica até o usuário clicar em fechar"""
    def _popup():
        root = tk.Tk()
        root.title(titulo)
        root.geometry("350x150")
        root.attributes("-topmost", True)
        root.resizable(True, True)

        if icon_path:
            try:
                root.iconbitmap(icon_path)
            except:
                pass

        lbl = tk.Label(root, text=mensagem, wraplength=330, justify="left")
        lbl.pack(pady=20, padx=10)

        btn = tk.Button(root, text="Fechar", command=root.destroy)
        btn.pack(pady=10)

        root.mainloop()

    Thread(target=_popup).start()

async def listen():
    uri = f"ws://{IP_SERVIDOR}:{PORTA}"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(usuario)
                print(f"{usuario} conectado ao servidor.")
                while True:
                    msg = await websocket.recv()
                    print(f"Mensagem recebida: {msg}")

                    # Notificação na Central de Ações (win10toast)
                    if toaster:
                        Thread(target=lambda: toaster.show_toast(
                            f"Mensagem para {usuario}",
                            msg,
                            duration=5,  # só para ir para Central de Ações
                            threaded=True
                        )).start()

                    # Popup Tkinter que fica até fechar manualmente
                    show_popup(f"Mensagem para {usuario}", msg, icon_path="icon.ico")

        except Exception as e:
            print(f"Erro de conexão: {e}. Tentando reconectar em 3s...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(listen())
