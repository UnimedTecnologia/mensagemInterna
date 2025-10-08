import asyncio
import websockets
import getpass
import tkinter as tk
from tkinter import ttk, messagebox  
from threading import Thread
import json
import base64
from PIL import Image, ImageTk
import io
import os
import socket
import platform
import requests
import uuid
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except:
    toaster = None

# Configurações
usuario = getpass.getuser()  # Nome do usuário do Windows
IP_SERVIDOR = "10.11.0.144" # TESTE LOCAL
# IP_SERVIDOR = "10.10.10.51" 
PORTA = 8765
HTTP_SERVIDOR = f"http://{IP_SERVIDOR}:8081"

# IP_SERVIDOR = "10.10.10.51"
# PORTA = 8080        # ← WebSocket (DEVE SER 8080)
# HTTP_SERVIDOR = f"http://{IP_SERVIDOR}:8088"  # ← HTTP (DEVE SER 8088)

# Caminho para o logo da Unimed (ajuste conforme necessário)
LOGO_PATH = "logo_unimed.png"  # Coloque o logo na mesma pasta do client.py

# =============================================
# SISTEMA DE IDENTIFICAÇÃO ÚNICA (NOVO)
# =============================================

def get_system_unique_id():
    """Gera um ID único baseado nas informações da máquina"""
    try:
        hostname = socket.gethostname()
        username = getpass.getuser()
        
        # Tenta obter o endereço MAC para mais unicidade
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0, 2*6, 2)][::-1])
        
        # Combina as informações para criar um ID único
        unique_id = f"{hostname}_{username}_{mac}"
        return unique_id
    except Exception as e:
        print(f"⚠️ Erro ao gerar ID único: {e}")
        # Fallback: usa apenas username + hostname
        return f"{getpass.getuser()}_{socket.gethostname()}"

# =============================================
# FORMULÁRIO DE CADASTRO AUTOMÁTICO (NOVO)
# =============================================

def show_registration_form(system_info):
    """Mostra formulário de cadastro para novos usuários"""
    def _form():
        root = tk.Tk()
        root.title("Cadastro - Unimed")
        root.geometry("500x650+100+40")
        root.configure(bg='#008E55')
        root.resizable(False, False)
        root.attributes("-topmost", True)
        
        
        # Centralizar na tela
        # root.eval('tk::PlaceWindow . center')

        # Header
        header = tk.Frame(root, bg='#008E55', height=80)
        header.pack(fill=tk.X, padx=0, pady=0)
        
        title = tk.Label(header, text="📝 Cadastro de Colaborador", 
                        font=('Arial', 16, 'bold'), fg='white', bg='#008E55')
        title.pack(pady=20)

        # Container principal
        container = tk.Frame(root, bg='white')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Informações da máquina
        info_frame = tk.Frame(container, bg='#f8f9fa', relief=tk.SUNKEN, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(info_frame, text="💻 Informações da Máquina:", 
                font=('Arial', 10, 'bold'), bg='#f8f9fa').pack(anchor='w', pady=(10,5), padx=10)
        tk.Label(info_frame, text=f"Computador: {system_info['hostname']}", 
                font=('Arial', 9), bg='#f8f9fa').pack(anchor='w', padx=10)
        tk.Label(info_frame, text=f"Usuário Windows: {system_info['username']}", 
                font=('Arial', 9), bg='#f8f9fa').pack(anchor='w', padx=10, pady=(0,10))

        # Formulário
        form_frame = tk.Frame(container, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Nome Completo
        tk.Label(form_frame, text="Nome Completo:*", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(5,2))
        nome_entry = tk.Entry(form_frame, font=('Arial', 11), width=40)
        nome_entry.pack(fill=tk.X, pady=(0,10))
        nome_entry.focus() # //* Foca no campo nome inicialmente

        # Setor
        tk.Label(form_frame, text="Setor:*", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(5,2))
        setor_var = tk.StringVar(root)
        setor_combo = ttk.Combobox(form_frame, textvariable=setor_var, 
                                font=('Arial', 11), width=38, state="normal")  # ← AGORA EDITÁVEL
        setor_combo['values'] = ['Carregando setores...']
        setor_combo.pack(fill=tk.X, pady=(0,10))

        # Matrícula (opcional)
        tk.Label(form_frame, text="Matrícula (opcional):", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(5,2))
        matricula_entry = tk.Entry(form_frame, font=('Arial', 11), width=40)
        matricula_entry.pack(fill=tk.X, pady=(0,20))

        # Status
        status_label = tk.Label(form_frame, text="", font=('Arial', 9), bg='white')
        status_label.pack(pady=5)

        # Variável para controle
        cadastro_realizado = False

                # Carregar setores do servidor
        def carregar_setores():
            try:
                response = requests.get(f'{HTTP_SERVIDOR}/setores', timeout=5)
                if response.status_code == 200:
                    setores = response.json()
                    if setores:
                        setor_combo['values'] = setores
                        setor_combo.set(setores[0])  # Seleciona o primeiro por padrão
                        status_label.config(text="✅ Setores carregados - Selecione ou digite um novo", fg="green")
                        
                        # REMOVA ou COMENTE esta linha que focava no setor:
                        # root.after(300, lambda: setor_combo.focus())  # ← REMOVA ESTA LINHA
                        
                    else:
                        status_label.config(text="⚠️ Nenhum setor cadastrado - Digite o nome do setor", fg="orange")
                else:
                    status_label.config(text="❌ Erro ao carregar setores - Digite manualmente", fg="red")
            except Exception as e:
                status_label.config(text="❌ Servidor indisponível - Digite manualmente", fg="red")
                print(f"Erro ao carregar setores: {e}")

        # Botão de cadastro
        def cadastrar():
            nonlocal cadastro_realizado
            nome = nome_entry.get().strip()
            setor = setor_var.get().strip()
            matricula = matricula_entry.get().strip()

            if not nome:
                status_label.config(text="❌ Preencha o nome completo!", fg="red")
                nome_entry.focus()
                return

            if not setor or setor == 'Carregando setores...':
                status_label.config(text="❌ Selecione um setor!", fg="red")
                setor_combo.focus()
                return

            try:
                dados = {
                    'username': system_info['unique_id'],
                    'nome_completo': nome,
                    'setor': setor,
                    'matricula': matricula,
                    'hostname': system_info['hostname']
                }
                
                status_label.config(text="⏳ Realizando cadastro...", fg="blue")
                
                response = requests.post(
                    f'{HTTP_SERVIDOR}/admin/cadastro_usuario', 
                    json=dados, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result['status'] == 'ok':
                        status_label.config(text="✅ Cadastro realizado com sucesso!", fg="green")
                        cadastro_realizado = True
                        # Fecha após 2 segundos
                        root.after(2000, root.destroy)
                    else:
                        status_label.config(text=f"❌ Erro: {result.get('detalhes', 'Erro desconhecido')}", fg="red")
                else:
                    status_label.config(text="❌ Erro no servidor", fg="red")
                    
            except requests.exceptions.Timeout:
                status_label.config(text="❌ Tempo esgotado - tente novamente", fg="red")
            except requests.exceptions.ConnectionError:
                status_label.config(text="❌ Erro de conexão - verifique o servidor", fg="red")
            except Exception as e:
                status_label.config(text="❌ Erro inesperado", fg="red")
                print(f"Erro no cadastro: {e}")

        # Botão cadastrar
        btn_cadastrar = tk.Button(form_frame, text="📋 Realizar Cadastro", 
                                command=cadastrar, font=('Arial', 12, 'bold'),
                                bg='#008E55', fg='white', padx=20, pady=8)
        btn_cadastrar.pack(pady=5)

        # Botão cancelar (opcional)
        btn_cancelar = tk.Button(form_frame, text="⏩ Pular Cadastro", 
                                command=root.destroy, font=('Arial', 10),
                                bg='#6c757d', fg='white', padx=15, pady=5)
        btn_cancelar.pack(pady=5)

        # Enter no formulário executa cadastro
        def on_enter(event):
            cadastrar()
        
        nome_entry.bind('<Return>', on_enter)
        setor_combo.bind('<Return>', on_enter)
        matricula_entry.bind('<Return>', on_enter)

        # Carregar setores após a interface estar pronta
        root.after(100, carregar_setores)
        
        # Focar no campo nome
        root.after(200, lambda: nome_entry.focus())
        
        root.mainloop()
        return cadastro_realizado

    return _form()

def get_system_info():
    """Coleta informações completas da máquina"""
    try:
        hostname = socket.gethostname()
        username = getpass.getuser()
        sistema_operacional = platform.system()
        unique_id = get_system_unique_id()
        
        system_info = {
            'hostname': hostname,
            'username': username,
            'os': sistema_operacional,
            'platform': platform.platform(),
            'unique_id': unique_id  # ← ID único para cadastro
        }
        return system_info
    except Exception as e:
        print(f"⚠️ Erro ao coletar informações do sistema: {e}")
        return {'username': getpass.getuser(), 'unique_id': getpass.getuser()}

def verificar_usuario_cadastrado(unique_id):
    """Verifica se o usuário já está cadastrado no servidor"""
    try:
        response = requests.get(
            f'{HTTP_SERVIDOR}/admin/verificar_usuario/{unique_id}', 
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('cadastrado', False)
        else:
            print(f"❌ Erro na verificação: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão na verificação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado na verificação: {e}")
        return False

def show_popup(titulo, mensagem, icon_path=None, message_data=None):
    """Popup Tkinter personalizado com logo da Unimed e scroll"""
    def _popup():
        root = tk.Tk()
        root.title(titulo)
        root.attributes("-topmost", True)
        root.resizable(True, True)
        root.configure(bg='#008E55')  # Cor Unimed
        root.minsize(500, 400)  # Tamanho mínimo

        # Tenta carregar o logo
        logo_image = None
        try:
            if os.path.exists(LOGO_PATH):
                logo_img = Image.open(LOGO_PATH)
                logo_img = logo_img.resize((100, 40), Image.Resampling.LANCZOS)
                logo_image = ImageTk.PhotoImage(logo_img)
        except Exception as e:
            print(f"⚠️ Erro ao carregar logo: {e}")

        # Header com logo (fixo - sem scroll)
        header_frame = tk.Frame(root, bg='#008E55', height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)  # Mantém o tamanho fixo
        
        if logo_image:
            logo_label = tk.Label(header_frame, image=logo_image, bg='#008E55')
            logo_label.image = logo_image
            logo_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        title_label = tk.Label(header_frame, 
                             text="Mensagem Interna - Unimed", 
                             font=('Arial', 12, 'bold'), 
                             fg='white', 
                             bg='#008E55')
        title_label.pack(side=tk.LEFT, padx=5, pady=10)

        # Frame principal com scroll
        main_frame = tk.Frame(root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Canvas e Scrollbar
        canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Empacotar canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configurar scroll com mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # Exibe conteúdo baseado no tipo
        if message_data and message_data.get('type') == 'image':
            try:
                root.geometry("600x650")  # Tamanho inicial maior
                
                # Frame do conteúdo
                content_frame = tk.Frame(scrollable_frame, bg='white')
                content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                # Informações do remetente
                sender_frame = tk.Frame(content_frame, bg='white')
                sender_frame.pack(fill=tk.X, pady=(0, 15))
                
                sender_label = tk.Label(sender_frame, 
                                      text=f"De: {message_data.get('sender', 'Unknown')}",
                                      font=('Arial', 10, 'bold'),
                                      bg='white',
                                      fg='#333333')
                sender_label.pack(side=tk.LEFT)
                
                timestamp = message_data.get('timestamp', '')[:19]
                time_label = tk.Label(sender_frame, 
                                    text=timestamp, 
                                    font=('Arial', 8),
                                    bg='white',
                                    fg='#666666')
                time_label.pack(side=tk.RIGHT)
                
                # Texto adicional se existir
                texto_adicional = message_data.get('texto_adicional', '')
                if texto_adicional:
                    text_frame = tk.Frame(content_frame, bg='white')
                    text_frame.pack(fill=tk.X, pady=(0, 20))
                    
                    text_label = tk.Label(text_frame, 
                                        text=texto_adicional, 
                                        wraplength=550, 
                                        justify="left",
                                        font=('Arial', 11),
                                        bg='white',
                                        fg='#333333')
                    text_label.pack(anchor='w')
                
                # Frame da imagem
                image_frame = tk.Frame(content_frame, bg='#f8f9fa', relief=tk.SUNKEN, bd=1)
                image_frame.pack(fill=tk.BOTH, pady=(0, 15))
                
                # Decodifica e exibe imagem com melhor resolução
                image_data = base64.b64decode(message_data['content'])
                image = Image.open(io.BytesIO(image_data))
                
                # Redimensiona mantendo qualidade - tamanho maior
                max_size = (550, 450)  # Tamanho maior para melhor visualização
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                img_label = tk.Label(image_frame, image=photo, bg='#f8f9fa')
                img_label.image = photo
                img_label.pack(pady=20, padx=20)
                
                # Rodapé com informações do arquivo
                footer_frame = tk.Frame(content_frame, bg='white')
                footer_frame.pack(fill=tk.X, pady=(10, 0))
                
                filename_label = tk.Label(footer_frame, 
                                        text=f"📎 {message_data.get('filename', 'imagem')}",
                                        font=('Arial', 9),
                                        bg='white',
                                        fg='#666666')
                filename_label.pack(anchor='w')
                
            except Exception as e:
                error_frame = tk.Frame(scrollable_frame, bg='white')
                error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                error_label = tk.Label(error_frame, 
                                     text=f"Erro ao carregar imagem: {e}", 
                                     fg='red', 
                                     wraplength=380,
                                     font=('Arial', 10),
                                     bg='white')
                error_label.pack(expand=True)
        else:
            # Mensagem de texto normal
            root.geometry("550x500")
            
            content_frame = tk.Frame(scrollable_frame, bg='white')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Informações do remetente
            sender_frame = tk.Frame(content_frame, bg='white')
            sender_frame.pack(fill=tk.X, pady=(0, 15))
            
            sender_label = tk.Label(sender_frame, 
                                  text=f"De: {message_data.get('sender', 'Unknown')}",
                                  font=('Arial', 10, 'bold'),
                                  bg='white',
                                  fg='#333333')
            sender_label.pack(side=tk.LEFT)
            
            timestamp = message_data.get('timestamp', '')[:19]
            time_label = tk.Label(sender_frame, 
                                text=timestamp, 
                                font=('Arial', 8),
                                bg='white',
                                fg='#666666')
            time_label.pack(side=tk.RIGHT)
            
            # Mensagem
            message_frame = tk.Frame(content_frame, bg='#f8f9fa', relief=tk.SUNKEN, bd=1)
            message_frame.pack(fill=tk.BOTH, expand=True)
            
            # Frame interno para a mensagem com scroll se necessário
            message_inner_frame = tk.Frame(message_frame, bg='#f8f9fa')
            message_inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            message_label = tk.Label(message_inner_frame, 
                                   text=mensagem, 
                                   wraplength=480, 
                                   justify="left", 
                                   font=('Arial', 11),
                                   bg='#f8f9fa',
                                   fg='#333333')
            message_label.pack(anchor='nw')  # Alinha ao topo esquerdo

        # Botão de fechar (fixo - sem scroll)
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(5, 5))
        
        btn = tk.Button(button_frame, 
                       text="Fechar", 
                       command=root.destroy, 
                       font=('Arial', 10, 'bold'),
                       bg='#008E55',
                       fg='white',
                       padx=30,
                       pady=8,
                       relief=tk.FLAT,
                       cursor='hand2')
        btn.pack(pady=5)

        # Ajustar o scroll para o topo
        canvas.update_idletasks()
        canvas.yview_moveto(0.0)

        # Focar na janela
        root.focus_force()
        root.lift()

        root.mainloop()

    Thread(target=_popup, daemon=True).start()

def show_connection_status(connected):
    """Mostra status da conexão na bandeja do sistema (para versão futura)"""
    if toaster:
        status = "conectado" if connected else "desconectado"
        Thread(target=lambda: toaster.show_toast(
            "Sistema de Mensagens - Unimed",
            f"Status: {status}",
            duration=3,
            threaded=True
        )).start()

async def listen():
    # Coletar informações únicas do sistema
    system_info = get_system_info()
    unique_id = system_info['unique_id']
    hostname = system_info.get('hostname', 'N/A')
    
    print("=" * 50)
    print("🚀 CLIENTE DE MENSAGENS - UNIMED")
    print("=" * 50)
    print(f"👤 Usuário Windows: {system_info['username']}")
    print(f"💻 Computador: {hostname}")
    print(f"🔑 ID Único: {unique_id}")
    print("=" * 50)
    
    # Verificar se usuário já está cadastrado
    print("🔍 Verificando cadastro no servidor...")
    usuario_cadastrado = verificar_usuario_cadastrado(unique_id)
    
    if not usuario_cadastrado:
        print("📝 Usuário não cadastrado. Iniciando processo de cadastro...")
        
        # Mostrar formulário de cadastro
        cadastro_sucesso = show_registration_form(system_info)
        
        if cadastro_sucesso:
            print("✅ Cadastro realizado com sucesso! Conectando ao servidor...")
            # Pequena pausa para processar o cadastro
            await asyncio.sleep(2)
        else:
            print("❌ Cadastro não realizado. Tentando conectar como usuário não cadastrado...")
            # Continua mesmo sem cadastro, mas como "NÃO CADASTRADO"
    else:
        print("✅ Usuário já cadastrado. Conectando ao servidor...")
    
    # Conexão normal com o servidor WebSocket
    # Usa o unique_id como username para o servidor
    username_para_conexao = unique_id
    
    uri = f"ws://{IP_SERVIDOR}:{PORTA}"
    reconnect_count = 0
    max_reconnect_delay = 30
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                # Envia o unique_id como username para o servidor
                await websocket.send(username_para_conexao)
                
                print(f"✅ Conectado ao servidor com sucesso!")
                print(f"📡 Enviando como: {username_para_conexao}")
                show_connection_status(True)
                reconnect_count = 0
                
                while True:
                    msg = await websocket.recv()
                    try:
                        data = json.loads(msg)
                        sender = data.get('sender', 'Unknown')
                        msg_type = data.get('type', 'text')
                        
                        print(f"📨 Mensagem recebida de {sender}: {msg_type.upper()}")

                        # Notificação na Central de Ações (win10toast)
                        if toaster:
                            if msg_type == 'text':
                                notification_msg = data['content']
                                notification_title = f"Unimed - {sender}"
                            else:
                                texto_adicional = data.get('texto_adicional', '')
                                if texto_adicional:
                                    notification_msg = f"📷 {texto_adicional}"
                                else:
                                    notification_msg = "📷 Nova imagem recebida"
                                notification_title = f"Unimed - {sender}"
                                
                            Thread(target=lambda: toaster.show_toast(
                                notification_title,
                                notification_msg,
                                duration=5,
                                threaded=True
                            )).start()

                        # Popup Tkinter
                        if msg_type == 'text':
                            show_popup("Mensagem - Unimed", 
                                     data['content'], 
                                     icon_path="icon.ico",
                                     message_data=data)
                        else:
                            texto_popup = data.get('texto_adicional', 'Nova imagem recebida')
                            show_popup("Imagem - Unimed", 
                                     texto_popup,
                                     icon_path="icon.ico",
                                     message_data=data)

                    except json.JSONDecodeError:
                        print(f"❌ Mensagem não JSON recebida: {msg}")
                    except Exception as e:
                        print(f"❌ Erro ao processar mensagem: {e}")

        except websockets.ConnectionClosed:
            print(f"🔌 Conexão com o servidor foi fechada")
            show_connection_status(False)
        except ConnectionRefusedError:
            print(f"❌ Servidor recusou a conexão. Verifique se o servidor está rodando.")
            show_connection_status(False)
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            show_connection_status(False)

        # Reconexão com backoff exponencial
        reconnect_count += 1
        delay = min(3 * reconnect_count, max_reconnect_delay)
        
        print(f"🔄 Tentando reconectar em {delay} segundos... (Tentativa {reconnect_count})")
        await asyncio.sleep(delay)

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    missing_deps = []
    
    try:
        import websockets
    except ImportError:
        missing_deps.append("websockets")
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    if missing_deps:
        print("❌ Dependências faltando:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print(f"\n💡 Instale com: pip install {' '.join(missing_deps)}")
        return False
    
    return True

if __name__ == "__main__":
    # Verificar dependências
    if not check_dependencies():
        input("Pressione Enter para sair...")
        exit(1)
    
    try:
        print("Iniciando cliente de mensagens...")
        asyncio.run(listen())
    except KeyboardInterrupt:
        print("\n\n🔴 Cliente encerrado pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        input("Pressione Enter para sair...")