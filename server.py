import asyncio
import websockets
from aiohttp import web
import json

# Dicionário de clientes conectados: {nome_usuario: websocket}
clientes = {}

# --- WebSocket handler ---
async def handler(websocket):
    try:
        # Recebe nome do usuário
        nome_usuario = await websocket.recv()
        clientes[nome_usuario] = websocket
        print(f"{nome_usuario} conectado.")

        # Loop recebendo mensagens do cliente (opcional)
        async for message in websocket:
            print(f"Mensagem recebida de {nome_usuario}: {message}")

    except websockets.ConnectionClosed:
        pass
    finally:
        if nome_usuario in clientes:
            del clientes[nome_usuario]
            print(f"{nome_usuario} desconectou.")

# --- Rota HTTP para listar usuários online ---
async def lista_usuarios(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)

    return web.json_response(list(clientes.keys()), headers=headers)

# --- Rota HTTP para enviar mensagem do painel ---
async def enviar_mensagem_painel(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    # Preflight OPTIONS
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)

    # POST
    try:
        data = await request.json()
        mensagem = data.get('mensagem', '')
        if mensagem and clientes:
            await asyncio.gather(*[ws.send(mensagem) for ws in clientes.values()])
        return web.json_response({"status": "ok"}, headers=headers)
    except Exception as e:
        return web.json_response({"status": "erro", "detalhes": str(e)}, headers=headers)

# --- Envio de mensagens pelo terminal ---
async def enviar_mensagem_terminal():
    loop = asyncio.get_event_loop()
    while True:
        msg = await loop.run_in_executor(None, input, "Digite uma mensagem para todos: ")
        if clientes:
            await asyncio.gather(*[ws.send(msg) for ws in clientes.values()])
        else:
            print("Nenhum cliente conectado.")

# --- Main ---
async def main():
    # Servidor WebSocket
    ws_server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("Servidor WebSocket iniciado em ws://0.0.0.0:8765")

    # Servidor HTTP aiohttp
    app = web.Application()
    app.add_routes([
        web.route("*", "/usuarios", lista_usuarios),
        web.route("*", "/enviar", enviar_mensagem_painel)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
    print("Servidor HTTP para painel iniciado em http://0.0.0.0:8081")

    # Envio de mensagens do terminal
    await enviar_mensagem_terminal()

asyncio.run(main())
