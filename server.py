import asyncio
import websockets
from aiohttp import web
import json
import base64
import os
import sqlite3
import uuid
from datetime import datetime

# =============================================
# CONFIGURAÇÕES E VARIÁVEIS GLOBAIS
# =============================================

# Dicionários de clientes conectados
clientes = {}  # {client_id: websocket}
clientes_info = {}  # {client_id: user_info}

# Pasta para armazenar imagens temporariamente
IMAGES_DIR = "temp_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# Banco de dados
DB_PATH = "unimed_mensagens.db"

# =============================================
# FUNÇÕES DE BANCO DE DADOS (EXISTENTES)
# =============================================

def generate_client_id():
    """Gera um ID único para cada conexão cliente"""
    return str(uuid.uuid4())

def init_database():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de setores - NOVA TABELA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS setores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            descricao TEXT,
            ativo BOOLEAN DEFAULT 1
        )
    ''')
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            setor TEXT NOT NULL,
            nome_completo TEXT,
            matricula TEXT,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY (setor) REFERENCES setores(nome)
        )
    ''')
    
    # Tabela de mensagens (para histórico)
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
    
    # Inserir setores padrão
    # cursor.execute('''
    #     INSERT OR IGNORE INTO setores (nome, descricao) VALUES 
    #     ('TI', 'Tecnologia da Informação'),
    #     ('RH', 'Recursos Humanos'),
    #     ('Financeiro', 'Departamento Financeiro'),
    #     ('Comercial', 'Setor Comercial'),
    #     ('Contas Medicas', 'Contas Médicas')
    # ''')
    
    # Inserir alguns dados de exemplo (remova depois)
    # cursor.execute('''
    #     INSERT OR IGNORE INTO usuarios (username, setor, nome_completo) VALUES 
    #     ('user', 'TI', 'Pedro Rodrigues'),
    #     ('maria.santos', 'RH', 'Maria Santos'),
    #     ('pedro.oliveira', 'Financeiro', 'Pedro Oliveira'),
    #     ('ana.costa', 'TI', 'Ana Costa'),
    #     ('maria.silva', 'Contas Medicas', 'Maria Silva'),
    #     ('carlos.rocha', 'Comercial', 'Carlos Rocha')
    # ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado!")

def get_user_info(username):
    """Busca informações do usuário no banco"""
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
        return {
            'username': result[0],
            'setor': result[1],
            'nome_completo': result[2],
            'matricula': result[3]
        }
    return None

def get_setores():
    """Retorna lista de setores disponíveis"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT nome FROM setores WHERE ativo = 1 ORDER BY nome')
    setores = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return setores

def get_usuarios_por_setor(setor):
    """Retorna usuários de um setor específico"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username FROM usuarios 
        WHERE setor = ? AND ativo = 1
    ''', (setor,))
    
    usuarios = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return usuarios

# =============================================
# FUNÇÕES DE BANCO DE DADOS (ADMIN - NOVAS)
# =============================================

def get_all_usuarios():
    """Retorna todos os usuários do banco"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios ORDER BY setor, username')
    usuarios = []
    for row in cursor.fetchall():
        usuarios.append({
            'id': row[0],
            'username': row[1],
            'setor': row[2],
            'nome_completo': row[3],
            'matricula': row[4],
            'ativo': bool(row[5])
        })
    conn.close()
    return usuarios

def get_all_setores():
    """Retorna estatísticas dos setores"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.nome, 
               s.descricao,
               COUNT(u.id) as total_usuarios,
               SUM(CASE WHEN u.ativo = 1 THEN 1 ELSE 0 END) as ativos
        FROM setores s
        LEFT JOIN usuarios u ON s.nome = u.setor
        WHERE s.ativo = 1
        GROUP BY s.nome, s.descricao
        ORDER BY s.nome
    ''')
    
    setores = []
    for row in cursor.fetchall():
        setores.append({
            'nome': row[0],
            'descricao': row[1],
            'total_usuarios': row[2],
            'ativos': row[3]
        })
    conn.close()
    return setores

def get_all_mensagens():
    """Retorna histórico de mensagens"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mensagens ORDER BY timestamp DESC LIMIT 100')
    mensagens = []
    for row in cursor.fetchall():
        mensagens.append({
            'id': row[0],
            'remetente': row[1],
            'setor_destino': row[2],
            'mensagem': row[3],
            'tipo': row[4],
            'timestamp': row[5]
        })
    conn.close()
    return mensagens

def get_estatisticas():
    """Retorna estatísticas gerais"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total usuários
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    total_usuarios = cursor.fetchone()[0]
    
    # Total setores
    cursor.execute('SELECT COUNT(DISTINCT setor) FROM usuarios')
    total_setores = cursor.fetchone()[0]
    
    # Total mensagens
    cursor.execute('SELECT COUNT(*) FROM mensagens')
    total_mensagens = cursor.fetchone()[0]
    
    # Setor com mais usuários
    cursor.execute('''
        SELECT setor, COUNT(*) as total 
        FROM usuarios 
        WHERE ativo = 1 
        GROUP BY setor 
        ORDER BY total DESC 
        LIMIT 1
    ''')
    result = cursor.fetchone()
    setor_mais_usuarios = result[0] if result else 'Nenhum'
    
    conn.close()
    
    return {
        'total_usuarios': total_usuarios,
        'total_setores': total_setores,
        'total_mensagens': total_mensagens,
        'setor_mais_usuarios': setor_mais_usuarios
    }

# =============================================
# WEBSOCKET HANDLER (EXISTENTE)
# =============================================

async def handler(websocket):
    client_id = generate_client_id()
    nome_usuario = None
    
    try:
        # Recebe nome do usuário
        nome_usuario = await websocket.recv()
        
        # Armazena com ID único
        clientes[client_id] = websocket
        
        # Busca informações do usuário
        user_info = get_user_info(nome_usuario)
        if user_info:
            clientes_info[client_id] = user_info
            print(f"✅ {nome_usuario} ({user_info['setor']}) conectado. ID: {client_id[:8]}")
        else:
            clientes_info[client_id] = {
                'username': nome_usuario, 
                'setor': 'NÃO CADASTRADO',
                'nome_completo': nome_usuario,
                'client_id': client_id
            }
            print(f"⚠️ {nome_usuario} (NÃO CADASTRADO) conectado. ID: {client_id[:8]}")

        # Loop recebendo mensagens do cliente
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if data['type'] == 'text':
                    print(f"💬 Mensagem de {nome_usuario}: {data['content'][:50]}...")
                    # Encaminha para todos os clientes
                    await broadcast_message(data, nome_usuario)
                    
            except json.JSONDecodeError:
                print(f"❌ Mensagem não JSON de {nome_usuario}: {message}")

    except websockets.ConnectionClosed:
        print(f"🔌 Conexão fechada para {client_id[:8]}")
    except Exception as e:
        print(f"❌ Erro no handler para {client_id[:8]}: {e}")
    finally:
        if client_id in clientes:
            del clientes[client_id]
            if client_id in clientes_info:
                user_info = clientes_info[client_id]
                print(f"🔴 {user_info['username']} desconectou. ID: {client_id[:8]}")
                del clientes_info[client_id]

async def broadcast_message(data, sender, setor_destino=None):
    """Transmite mensagem para clientes"""
    message_data = {
        'type': data['type'],
        'content': data['content'],
        'sender': sender,
        'timestamp': datetime.now().isoformat()
    }
    
    # Se for imagem, adiciona o filename e texto adicional
    if data['type'] == 'image':
        message_data['filename'] = data.get('filename', 'imagem.png')
        message_data['texto_adicional'] = data.get('texto_adicional', '')
    
    # Determina para quais clientes enviar
    if setor_destino:
        # Envia apenas para usuários do setor específico
        targets = []
        for client_id, ws in clientes.items():
            user_info = clientes_info.get(client_id, {})
            if user_info.get('setor') == setor_destino:
                targets.append(ws)
    else:
        # Envia para todos
        targets = list(clientes.values())
    
    if targets:
        await asyncio.gather(*[
            ws.send(json.dumps(message_data)) 
            for ws in targets
        ])
        print(f"📤 Mensagem enviada para {len(targets)} cliente(s) - Setor: {setor_destino or 'TODOS'}")
    else:
        print(f"⚠️ Nenhum cliente online para receber mensagem - Setor: {setor_destino or 'TODOS'}")

# =============================================
# ROTAS HTTP PRINCIPAIS (EXISTENTES)
# =============================================

async def lista_usuarios(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)

    # Agrupa por username, mostrando quantas conexões cada um tem
    usuarios_agrupados = {}
    for client_id, info in clientes_info.items():
        username = info['username']
        if username not in usuarios_agrupados:
            usuarios_agrupados[username] = {
                'username': username,
                'setor': info.get('setor', 'N/A'),
                'nome_completo': info.get('nome_completo', 'N/A'),
                'conexoes': 0,
                'client_ids': []
            }
        usuarios_agrupados[username]['conexoes'] += 1
        usuarios_agrupados[username]['client_ids'].append(client_id)

    return web.json_response(list(usuarios_agrupados.values()), headers=headers)

async def lista_setores(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)

    setores = get_setores()
    return web.json_response(setores, headers=headers)

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
        mensagem_type = data.get('type', 'text')
        setor_destino = data.get('setor_destino', None)  # None = todos os setores
        
        if not mensagem:
            return web.json_response({"status": "erro", "detalhes": "Mensagem vazia"}, headers=headers)
            
        if not clientes:
            return web.json_response({"status": "erro", "detalhes": "Nenhum cliente conectado"}, headers=headers)

        message_data = {
            'type': mensagem_type,
            'content': mensagem,
            'sender': 'PAINEL_RH',
            'timestamp': datetime.now().isoformat()
        }
        
        # Se for imagem, adiciona o filename e texto adicional
        if mensagem_type == 'image':
            message_data['filename'] = data.get('filename', 'imagem.png')
            message_data['texto_adicional'] = data.get('texto_adicional', '')
        
        await broadcast_message(message_data, 'PAINEL_RH', setor_destino)
        
        return web.json_response({"status": "ok"}, headers=headers)
        
    except Exception as e:
        print(f"❌ Erro em enviar_mensagem_painel: {e}")
        return web.json_response({"status": "erro", "detalhes": str(e)}, headers=headers)

# =============================================
# ROTAS ADMINISTRATIVAS (NOVAS)
# =============================================

async def admin_usuarios(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)
    
    if request.method == 'GET':
        usuarios = get_all_usuarios()
        return web.json_response(usuarios, headers=headers)
    
    elif request.method == 'POST':
        try:
            data = await request.json()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO usuarios (username, setor, nome_completo, matricula, ativo)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data['username'],
                data['setor'],
                data['nome_completo'],
                data.get('matricula', ''),
                int(data.get('ativo', 1))
            ))
            
            conn.commit()
            conn.close()
            return web.json_response({"status": "ok"}, headers=headers)
            
        except sqlite3.IntegrityError:
            return web.json_response({"status": "erro", "detalhes": "Username já existe"}, headers=headers)
        except Exception as e:
            return web.json_response({"status": "erro", "detalhes": str(e)}, headers=headers)

async def admin_usuario_detail(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)
    
    usuario_id = request.match_info['id']
    
    if request.method == 'PUT':
        try:
            data = await request.json()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE usuarios 
                SET username = ?, setor = ?, nome_completo = ?, matricula = ?, ativo = ?
                WHERE id = ?
            ''', (
                data['username'],
                data['setor'],
                data['nome_completo'],
                data.get('matricula', ''),
                int(data.get('ativo', 1)),
                usuario_id
            ))
            
            conn.commit()
            conn.close()
            return web.json_response({"status": "ok"}, headers=headers)
            
        except Exception as e:
            return web.json_response({"status": "erro", "detalhes": str(e)}, headers=headers)
    
    elif request.method == 'DELETE':
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
            conn.commit()
            conn.close()
            return web.json_response({"status": "ok"}, headers=headers)
        except Exception as e:
            return web.json_response({"status": "erro", "detalhes": str(e)}, headers=headers)

async def admin_setores(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)
    
    if request.method == 'GET':
        setores = get_all_setores()
        return web.json_response(setores, headers=headers)
    
    elif request.method == 'POST':
        try:
            data = await request.json()
            setor_nome = data['nome'].strip()
            setor_descricao = data.get('descricao', '')
            
            if not setor_nome:
                return web.json_response({"status": "erro", "detalhes": "Nome do setor vazio"}, headers=headers)
            
            # Inserir setor diretamente na tabela setores
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO setores (nome, descricao) VALUES (?, ?)',
                (setor_nome, setor_descricao)
            )
            conn.commit()
            conn.close()
            
            return web.json_response({"status": "ok"}, headers=headers)
            
        except sqlite3.IntegrityError:
            return web.json_response({"status": "erro", "detalhes": "Setor já existe"}, headers=headers)
        except Exception as e:
            return web.json_response({"status": "erro", "detalhes": str(e)}, headers=headers)

async def admin_setor_detail(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)
    
    setor_nome = request.match_info['nome']
    
    if request.method == 'DELETE':
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Verificar se há usuários no setor
            cursor.execute('SELECT COUNT(*) FROM usuarios WHERE setor = ?', (setor_nome,))
            if cursor.fetchone()[0] > 0:
                return web.json_response({
                    "status": "erro", 
                    "detalhes": "Não é possível excluir setor com usuários vinculados"
                }, headers=headers)
            
            # Excluir setor (usando UPDATE para manter histórico)
            cursor.execute('UPDATE setores SET ativo = 0 WHERE nome = ?', (setor_nome,))
            conn.commit()
            conn.close()
            
            return web.json_response({"status": "ok"}, headers=headers)
            
        except Exception as e:
            return web.json_response({"status": "erro", "detalhes": str(e)}, headers=headers)

async def admin_mensagens(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)
    
    if request.method == 'GET':
        mensagens = get_all_mensagens()
        return web.json_response(mensagens, headers=headers)

async def admin_estatisticas(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    if request.method == 'OPTIONS':
        return web.Response(status=200, headers=headers)
    
    if request.method == 'GET':
        stats = get_estatisticas()
        return web.json_response(stats, headers=headers)

# =============================================
# ENVIO VIA TERMINAL (EXISTENTE)
# =============================================

async def enviar_mensagem_terminal():
    loop = asyncio.get_event_loop()
    
    print("\n" + "="*50)
    print("🎮 MODO TERMINAL ATIVADO")
    print("="*50)
    
    while True:
        try:
            print(f"\n📊 Estatísticas:")
            print(f"   👥 Clientes conectados: {len(clientes)}")
            print(f"   👤 Usuários únicos: {len(clientes_info)}")
            
            # Mostrar usuários online
            if clientes_info:
                print(f"\n🟢 Usuários Online:")
                for client_id, info in clientes_info.items():
                    print(f"   • {info['username']} ({info.get('setor', 'N/A')}) - ID: {client_id[:8]}")
            
            print("\n🔧 Opções:")
            print("   1. 📢 Enviar para todos")
            print("   2. 🎯 Enviar para setor específico")
            print("   3. 🔄 Atualizar lista")
            print("   4. ❌ Sair")
            
            opcao = await loop.run_in_executor(None, input, "\nEscolha uma opção (1-4): ")
            
            if opcao == '4':
                break
            elif opcao == '3':
                continue
            elif opcao in ['1', '2']:
                setor_destino = None
                
                if opcao == '2':
                    setores = get_setores()
                    if not setores:
                        print("❌ Nenhum setor cadastrado no banco!")
                        continue
                        
                    print("\n📂 Setores disponíveis:")
                    for i, setor in enumerate(setores, 1):
                        print(f"   {i}. {setor}")
                    
                    try:
                        setor_idx = await loop.run_in_executor(None, input, "\nEscolha o setor (número): ")
                        setor_destino = setores[int(setor_idx) - 1]
                        print(f"🎯 Setor selecionado: {setor_destino}")
                    except (ValueError, IndexError):
                        print("❌ Setor inválido!")
                        continue
                
                msg = await loop.run_in_executor(None, input, "\n💬 Digite a mensagem: ")
                
                if msg.strip():
                    message_data = {
                        'type': 'text',
                        'content': msg,
                        'sender': 'TERMINAL',
                        'timestamp': datetime.now().isoformat()
                    }
                    await broadcast_message(message_data, 'TERMINAL', setor_destino)
                    print(f"✅ Mensagem enviada!")
                else:
                    print("❌ Mensagem vazia!")
            else:
                print("❌ Opção inválida!")
                
        except Exception as e:
            print(f"❌ Erro no terminal: {e}")

# =============================================
# MAIN (EXISTENTE COM ADIÇÕES)
# =============================================

async def main():
    # Inicializa banco de dados
    init_database()
    
    # Servidor WebSocket
    ws_server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("🚀 Servidor WebSocket iniciado em ws://0.0.0.0:8765")

    # Servidor HTTP aiohttp
    app = web.Application()
    
    # === ROTAS EXISTENTES ===
    app.add_routes([
        web.route("*", "/usuarios", lista_usuarios),
        web.route("*", "/setores", lista_setores),
        web.route("*", "/enviar", enviar_mensagem_painel)
    ])
    
    # === NOVAS ROTAS ADMINISTRATIVAS ===
    app.add_routes([
        web.route("*", "/admin/usuarios", admin_usuarios),
        web.route("*", "/admin/usuarios/{id}", admin_usuario_detail),
        web.route("*", "/admin/setores", admin_setores),
        web.route("*", "/admin/setores/{nome}", admin_setor_detail),
        web.route("*", "/admin/mensagens", admin_mensagens),
        web.route("*", "/admin/estatisticas", admin_estatisticas)
    ])
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
    print("🌐 Servidor HTTP para painel iniciado em http://0.0.0.0:8081")
    
    print("\n" + "="*50)
    print("✅ SISTEMA INICIADO COM SUCESSO!")
    print("="*50)
    print(f"📊 Clientes conectados: {len(clientes)}")
    print(f"📂 Setores cadastrados: {len(get_setores())}")
    print("🎮 Painel Admin disponível em: http://10.11.0.144:8081/painel_admin.php")
    print("📱 Painel Mensagens disponível em: http://10.11.0.144:8081/painel.php")
    print("="*50)

    # Envio de mensagens do terminal
    await enviar_mensagem_terminal()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🔴 Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")