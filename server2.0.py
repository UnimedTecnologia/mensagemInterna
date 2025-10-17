import asyncio
import websockets
from aiohttp import web
import json
import base64
import os
import sqlite3
import uuid
from datetime import datetime
import logging

# =============================================
# CONFIGURAÇÕES E VARIÁVEIS GLOBAIS
# =============================================

PORTA_WS = 8765
PORTA_HTTP = 8081

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Silenciar logs do aiohttp
logging.getLogger('aiohttp.access').setLevel(logging.WARNING)

# Dicionários de clientes conectados
clientes = {}  # {client_id: websocket}
clientes_info = {}  # {client_id: user_info}

# Banco de dados
DB_PATH = "unimed_mensagens.db"

# =============================================
# MIDDLEWARE CORS
# =============================================

async def cors_middleware(app, handler):
    async def middleware_handler(request):
        if request.method == 'OPTIONS':
            response = web.Response()
        else:
            response = await handler(request)
        
        response.headers.update({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true"
        })
        return response
    return middleware_handler

# =============================================
# FUNÇÕES DE BANCO DE DADOS
# =============================================

def generate_client_id():
    return str(uuid.uuid4())

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS setores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            descricao TEXT,
            ativo BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            setor TEXT NOT NULL,
            nome_completo TEXT,
            matricula TEXT,
            ativo BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remetente TEXT NOT NULL,
            setor_destino TEXT,
            mensagem TEXT,
            tipo TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    setores_padrao = [
        ('TI', 'Tecnologia da Informação'),
        ('RH', 'Recursos Humanos'),
        ('Financeiro', 'Departamento Financeiro'),
        ('Comercial', 'Setor Comercial'),
        ('Contas Medicas', 'Contas Médicas'),
        ('Regulação', 'Setor de Regulação')
    ]
    
    for setor_nome, setor_desc in setores_padrao:
        cursor.execute(
            'INSERT OR IGNORE INTO setores (nome, descricao) VALUES (?, ?)',
            (setor_nome, setor_desc)
        )
    
    conn.commit()
    conn.close()
    logging.info("✅ Banco de dados inicializado!")

def get_user_info(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username, setor, nome_completo, matricula 
        FROM usuarios 
        WHERE username = ? AND ativo = 1
    ''', (username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        user_info = {
            'username': result[0],
            'setor': result[1],
            'nome_completo': result[2],
            'matricula': result[3]
        }
        return user_info
    return None

def get_setores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT nome FROM setores WHERE ativo = 1 ORDER BY nome')
    setores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return setores

def salvar_mensagem_no_banco(remetente, setor_destino, mensagem, tipo='text'):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mensagens (remetente, setor_destino, mensagem, tipo)
            VALUES (?, ?, ?, ?)
        ''', (remetente, setor_destino, mensagem, tipo))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"❌ Erro ao salvar mensagem no banco: {e}")
        return False

# =============================================
# WEBSOCKET HANDLER
# =============================================

async def safe_send(websocket, data):
    """Envia dados de forma segura"""
    try:
        await websocket.send(json.dumps(data))
        return True
    except websockets.exceptions.ConnectionClosed:
        return False
    except Exception as e:
        logging.error(f"❌ Erro ao enviar mensagem: {e}")
        return False

async def check_connection_health():
    """Verifica a saúde de todas as conexões ativas"""
    dead_connections = []
    
    for client_id, ws in list(clientes.items()):
        try:
            pong_waiter = await ws.ping()
            await asyncio.wait_for(pong_waiter, timeout=5.0)
        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
            dead_connections.append(client_id)
        except Exception:
            dead_connections.append(client_id)
    
    # Remove conexões mortas
    for client_id in dead_connections:
        await unregister_client(client_id)
    
    return len(dead_connections)

async def broadcast_message(data, sender, setor_destino=None):
    """Transmite mensagem para clientes"""
    # Primeiro verifica a saúde das conexões
    dead_count = await check_connection_health()
    if dead_count > 0:
        logging.info(f"🧹 Removidas {dead_count} conexões mortas")
    
    message_data = {
        'type': data['type'],
        'content': data['content'],
        'sender': sender,
        'timestamp': datetime.now().isoformat(),
        'message_id': str(uuid.uuid4())[:8]  # ID único para cada mensagem
    }
    
    if data['type'] == 'image':
        message_data['filename'] = data.get('filename', 'imagem.png')
        message_data['texto_adicional'] = data.get('texto_adicional', '')
    
    disconnected_clients = []
    sent_count = 0
    
    # Mostrar informações dos clientes conectados
    logging.info(f"🔍 {len(clientes)} clientes conectados:")
    for client_id, user_info in clientes_info.items():
        if client_id in clientes:
            logging.info(f"   👤 {user_info.get('nome_completo', 'N/A')} - Setor: {user_info.get('setor', 'N/A')}")
    
    # Determinar para quais clientes enviar
    for client_id, ws in list(clientes.items()):
        try:
            user_info = clientes_info.get(client_id, {})
            user_setor = user_info.get('setor', 'N/A')
            user_nome = user_info.get('nome_completo', client_id[:8])
            
            should_send = False
            
            if setor_destino:
                # Enviar apenas para usuários do setor específico
                if user_setor == setor_destino:
                    should_send = True
                    logging.info(f"🎯 Enviando para {user_nome} (Setor: {user_setor})")
            else:
                # Enviar para todos
                should_send = True
                logging.info(f"📢 Enviando para {user_nome} (Setor: {user_setor})")
            
            if should_send:
                success = await safe_send(ws, message_data)
                if success:
                    sent_count += 1
                    logging.info(f"✅ Enviado com sucesso para {user_nome}")
                else:
                    disconnected_clients.append(client_id)
                    
        except Exception as e:
            logging.error(f"❌ Erro ao enviar para {client_id}: {e}")
            disconnected_clients.append(client_id)
    
    # Limpar clientes desconectados
    for client_id in disconnected_clients:
        await unregister_client(client_id)
    
    if data['type'] == 'text':
        salvar_mensagem_no_banco(sender, setor_destino, data['content'], data['type'])
    
    # ⚠️ CORREÇÃO: Não mostrar mensagem completa no log
    mensagem_resumo = data['content'][:50] + "..." if len(data['content']) > 50 else data['content']
    logging.info(f"📤 '{mensagem_resumo}' enviada para {sent_count} cliente(s) - Setor: {setor_destino or 'TODOS'}")
    
    return sent_count

async def unregister_client(client_id):
    """Remove um cliente de forma segura"""
    if client_id in clientes:
        try:
            if client_id in clientes_info:
                user_info = clientes_info[client_id]
                username = user_info.get('username', 'Desconhecido')
                logging.info(f"🔌 {username} desconectado")
                del clientes_info[client_id]
            del clientes[client_id]
        except Exception as e:
            logging.error(f"Erro ao remover cliente {client_id}: {e}")

async def handler(websocket):
    """Manipula uma conexão WebSocket"""
    client_id = generate_client_id()
    nome_usuario = None
    
    try:
        # Receber handshake
        nome_usuario = await asyncio.wait_for(websocket.recv(), timeout=30.0)
        
        # Registrar cliente
        clientes[client_id] = websocket
        
        # Buscar informações do usuário
        user_info = get_user_info(nome_usuario)
        if user_info:
            clientes_info[client_id] = user_info
            logging.info(f"✅ {user_info['nome_completo']} ({user_info['setor']}) conectou")
        else:
            clientes_info[client_id] = {
                'username': nome_usuario, 
                'setor': 'NÃO CADASTRADO',
                'nome_completo': nome_usuario
            }
            logging.info(f"⚠️ {nome_usuario} (NÃO CADASTRADO) conectou")

        # ⚠️ CORREÇÃO: NÃO enviar mensagem de boas-vindas que abre popup
        # Apenas enviar confirmação silenciosa de conexão
        connection_msg = {
            'type': 'connection_status',
            'content': 'Conectado ao servidor',
            'sender': 'Sistema',
            'timestamp': datetime.now().isoformat(),
            'status': 'connected'
        }
        
        await safe_send(websocket, connection_msg)
        
        # Loop principal para receber mensagens
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get('type', 'unknown')
                
                if message_type == 'text':
                    await broadcast_message(data, nome_usuario)
                elif message_type == 'ping':
                    await safe_send(websocket, {'type': 'pong'})
                elif message_type == 'image':
                    await broadcast_message(data, nome_usuario)
                    
            except json.JSONDecodeError:
                logging.warning(f"JSON inválido de {nome_usuario}")
            except Exception as e:
                logging.error(f"Erro ao processar mensagem de {nome_usuario}: {e}")

    except asyncio.TimeoutError:
        logging.warning(f"Timeout no handshake")
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        logging.error(f"Erro no handler: {e}")
    finally:
        await unregister_client(client_id)

# =============================================
# ROTAS HTTP
# =============================================

async def lista_usuarios(request):
    """Retorna lista de usuários conectados"""
    usuarios_agrupados = {}
    for client_id, info in clientes_info.items():
        if client_id in clientes:
            username = info['username']
            if username not in usuarios_agrupados:
                usuarios_agrupados[username] = {
                    'username': username,
                    'setor': info.get('setor', 'N/A'),
                    'nome_completo': info.get('nome_completo', 'N/A'),
                    'conexoes': 0
                }
            usuarios_agrupados[username]['conexoes'] += 1

    return web.json_response(list(usuarios_agrupados.values()))

async def lista_setores(request):
    """Retorna lista de setores"""
    setores = get_setores()
    return web.json_response(setores)

async def enviar_mensagem_painel(request):
    """Envia mensagem via painel web"""
    try:
        data = await request.json()
        mensagem = data.get('mensagem', '').strip()
        setor_destino = data.get('setor_destino', None)
        mensagem_type = data.get('type', 'text')
        
        # ⚠️ CORREÇÃO: Não logar mensagem completa
        mensagem_resumo = mensagem[:50] + "..." if len(mensagem) > 50 else mensagem
        logging.info(f"🌐 Mensagem do painel: '{mensagem_resumo}' para setor: {setor_destino}")
        
        if not mensagem:
            return web.json_response({"status": "erro", "detalhes": "Mensagem vazia"})
            
        if not clientes:
            return web.json_response({"status": "erro", "detalhes": "Nenhum cliente conectado"})

        message_data = {
            'type': mensagem_type,
            'content': mensagem,
            'sender': 'PAINEL_ADMIN',
            'timestamp': datetime.now().isoformat()
        }
        
        if mensagem_type == 'image':
            message_data['filename'] = data.get('filename', 'imagem.png')
            message_data['texto_adicional'] = data.get('texto_adicional', '')
        
        sent_count = await broadcast_message(message_data, 'PAINEL_ADMIN', setor_destino)
        
        return web.json_response({
            "status": "ok",
            "enviado_para": sent_count,
            "mensagem": "Mensagem enviada com sucesso!"
        })
        
    except Exception as e:
        logging.error(f"❌ Erro em enviar_mensagem_painel: {e}")
        return web.json_response({"status": "erro", "detalhes": str(e)})

# =============================================
# ROTAS ADMINISTRATIVAS
# =============================================

async def admin_verificar_usuario(request):
    try:
        username = request.match_info['username']
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, setor, nome_completo 
            FROM usuarios 
            WHERE username = ? AND ativo = 1
        ''', (username,))
        
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            return web.json_response({
                'cadastrado': True,
                'usuario': {
                    'id': usuario[0],
                    'username': usuario[1],
                    'setor': usuario[2],
                    'nome_completo': usuario[3]
                }
            })
        else:
            return web.json_response({
                'cadastrado': False
            })
            
    except Exception as e:
        return web.json_response({
            'cadastrado': False,
            'erro': str(e)
        })

async def admin_cadastro_usuario(request):
    try:
        data = await request.json()
        
        if not all(k in data for k in ['username', 'nome_completo', 'setor']):
            return web.json_response({
                "status": "erro", 
                "detalhes": "Dados incompletos. Nome e setor são obrigatórios."
            })
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT nome FROM setores WHERE nome = ? AND ativo = 1', (data['setor'],))
        if not cursor.fetchone():
            conn.close()
            return web.json_response({
                "status": "erro", 
                "detalhes": f"Setor '{data['setor']}' não encontrado."
            })
        
        cursor.execute('SELECT id FROM usuarios WHERE username = ?', (data['username'],))
        if cursor.fetchone():
            conn.close()
            return web.json_response({
                "status": "erro", 
                "detalhes": "Usuário já cadastrado."
            })
        
        cursor.execute('''
            INSERT INTO usuarios (username, setor, nome_completo, matricula, ativo)
            VALUES (?, ?, ?, ?, 1)
        ''', (
            data['username'],
            data['setor'],
            data['nome_completo'],
            data.get('matricula', '')
        ))
        
        conn.commit()
        conn.close()
        
        logging.info(f"✅ NOVO USUÁRIO: {data['nome_completo']} ({data['setor']})")
        
        return web.json_response({
            "status": "ok",
            "mensagem": "Usuário cadastrado com sucesso!"
        })
        
    except Exception as e:
        logging.error(f"❌ Erro no cadastro: {e}")
        return web.json_response({
            "status": "erro", 
            "detalhes": f"Erro interno: {str(e)}"
        })

# =============================================
# MAIN
# =============================================

async def main():
    init_database()
    
    # Servidor WebSocket
    ws_server = await websockets.serve(
        handler,
        "0.0.0.0", 
        PORTA_WS,
        ping_interval=20,
        ping_timeout=10,
        close_timeout=10
    )
    
    logging.info(f"🚀 Servidor WebSocket: ws://0.0.0.0:{PORTA_WS}")

    # Servidor HTTP com middleware CORS
    app = web.Application(middlewares=[cors_middleware])
    
    # Rotas principais
    app.add_routes([
        web.get("/usuarios", lista_usuarios),
        web.get("/setores", lista_setores),
        web.post("/enviar", enviar_mensagem_painel),
        web.get("/admin/verificar_usuario/{username}", admin_verificar_usuario),
        web.post("/admin/cadastro_usuario", admin_cadastro_usuario),
    ])
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORTA_HTTP)
    await site.start()
    logging.info(f"🌐 Servidor HTTP: http://0.0.0.0:{PORTA_HTTP}")
    
    print("\n" + "="*60)
    print("✅ SERVIDOR V2.0 - MENSAGENS OTIMIZADAS")
    # print("="*60)
    # print("• Popup só aparece quando admin envia mensagem")
    # print("• Logs mostram apenas resumo das mensagens") 
    # print("• Suporte a múltiplas mensagens na mesma janela")
    print("="*60)

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        logging.info("👋 Servidor parado")
    finally:
        ws_server.close()
        await ws_server.wait_closed()
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🔴 Servidor encerrado")
    except Exception as e:
        logging.error(f"❌ Erro: {e}")