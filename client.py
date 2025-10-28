import warnings
warnings.filterwarnings("ignore")
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
import re 
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except:
    toaster = None

# Configurações
usuario = getpass.getuser()

# //* Configurações para LOCAL
IP_SERVIDOR = "192.168.1.253" # LOCAL
PORTA = 8765 #LOCAL
HTTP_SERVIDOR = f"http://{IP_SERVIDOR}:8081" # LOCAL

LOGO_PATH = "logo_unimed.png"

# =============================================
# SISTEMA MELHORADO DE JANELAS - SOLUÇÃO DEFINITIVA
# =============================================

class WindowManager:
    """Gerenciador de janelas com solução definitiva para imagens"""
    def __init__(self):
        self.window_count = 0
        self.logo_image = None
        self._load_logo()
    
    def _load_logo(self):
        """Carrega o logo uma vez"""
        if os.path.exists(LOGO_PATH):
            try:
                logo_img = Image.open(LOGO_PATH)
                logo_img = logo_img.resize((100, 40), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(logo_img)
            except Exception as e:
                print(f"⚠️ Erro ao carregar logo: {e}")

# Instância global
window_manager = WindowManager()

def show_popup(titulo, mensagem, icon_path=None, message_data=None):
    """Popup Tkinter com solução definitiva para múltiplas imagens"""
    
    def _create_window():
        try:
            # Criar nova instância Tk para cada mensagem - ISOLADA
            root = tk.Tk()
            root.title(titulo)
            root.configure(bg='#f0f2f5')
            root.minsize(500, 400)
            root.resizable(True, True)
            # Manter por 1 segundo no topo, depois liberar
            root.attributes("-topmost", True)
            root.after(1000, lambda: root.attributes("-topmost", False))

            # Container principal
            main_frame = tk.Frame(root, bg='#f0f2f5')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

            # Header fixo
            header_frame = tk.Frame(main_frame, bg='#008E55', height=80)
            header_frame.pack(fill=tk.X, padx=0, pady=0)
            header_frame.pack_propagate(False)
            
            header_content = tk.Frame(header_frame, bg='#008E55')
            header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            if window_manager.logo_image:
                logo_label = tk.Label(header_content, image=window_manager.logo_image, bg='#008E55')
                logo_label.image = window_manager.logo_image
                logo_label.pack(side=tk.LEFT)
            
            title_container = tk.Frame(header_content, bg='#008E55')
            title_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))
            
            main_title = tk.Label(title_container, 
                                text="Mensagem Interna - Unimed", 
                                font=('Arial', 14, 'bold'), 
                                fg='white', 
                                bg='#008E55')
            main_title.pack(anchor='w')
            
            sub_title = tk.Label(title_container, 
                              text="Comunicação Corporativa", 
                              font=('Arial', 9), 
                              fg='#e8f5e8', 
                              bg='#008E55')
            sub_title.pack(anchor='w', pady=(2, 0))

            # Frame de conteúdo com scroll
            content_container = tk.Frame(main_frame, bg='#ffffff')
            content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

            # Criar canvas e scrollbar
            canvas = tk.Canvas(content_container, bg='#ffffff', highlightthickness=0)
            scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#ffffff')

            # Configurar scroll
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Empacotar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Scroll com mouse
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind("<MouseWheel>", _on_mousewheel)

            # Conteúdo da mensagem
            content_frame = tk.Frame(scrollable_frame, bg='#ffffff')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

            # Cabeçalho da mensagem
            header_message = tk.Frame(content_frame, bg='#ffffff')
            header_message.pack(fill=tk.X, pady=(0, 20))

            # Ícone e informações
            message_type = message_data.get('type', 'text') if message_data else 'text'
            icon = "📷" if message_type == 'image' else "💬"
            
            icon_label = tk.Label(header_message, text=icon, font=('Arial', 16), bg='#ffffff')
            icon_label.pack(side=tk.LEFT, padx=(0, 10))

            info_frame = tk.Frame(header_message, bg='#ffffff')
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            sender_name = tk.Label(info_frame, 
                                 text=f"De: {message_data.get('sender', 'Sistema')}",
                                 font=('Arial', 11, 'bold'),
                                 bg='#ffffff',
                                 fg='#2c3e50')
            sender_name.pack(anchor='w')

            timestamp = message_data.get('timestamp', '')[:19] if message_data else ''
            time_label = tk.Label(info_frame, 
                                text=timestamp, 
                                font=('Arial', 9),
                                bg='#ffffff',
                                fg='#7f8c8d')
            time_label.pack(anchor='w', pady=(2, 0))

            # Badge de tipo
            type_badge = tk.Frame(header_message, bg='#e8f5e8', relief='flat', bd=1)
            type_badge.pack(side=tk.RIGHT, padx=(10, 0))
            
            type_text = "IMAGEM" if message_type == 'image' else "TEXTO"
            type_label = tk.Label(type_badge, 
                                text=type_text,
                                font=('Arial', 8, 'bold'),
                                bg='#e8f5e8',
                                fg='#008E55',
                                padx=8,
                                pady=2)
            type_label.pack()

            # Container da mensagem
            message_container = tk.Frame(content_frame, bg='#f8f9fa', relief='flat', bd=1)
            message_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

            message_inner = tk.Frame(message_container, bg='#ffffff')
            message_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # SOLUÇÃO DEFINITIVA: Cada janela tem seu próprio namespace de imagens
            image_references = []  # Lista para manter referências FORTES

            if message_data and message_data.get('type') == 'image':
                try:
                    # Configurar tamanho para imagens
                    root.geometry("650x700")
                    
                    # Texto adicional
                    texto_adicional = message_data.get('texto_adicional', '')
                    if texto_adicional:
                        text_frame = tk.Frame(message_inner, bg='#ffffff')
                        text_frame.pack(fill=tk.X, pady=(0, 20))
                        
                        text_label = tk.Label(text_frame, 
                                            text=texto_adicional, 
                                            wraplength=580, 
                                            justify="left",
                                            font=('Arial', 11),
                                            bg='#ffffff',
                                            fg='#2c3e50')
                        text_label.pack(anchor='w')
                    
                    # SOLUÇÃO: Processamento de imagem isolado por janela
                    image_data = base64.b64decode(message_data['content'])
                    
                    # Usar BytesIO para carregar a imagem
                    image_buffer = io.BytesIO(image_data)
                    original_image = Image.open(image_buffer)
                    
                    # Calcular tamanho proporcional
                    max_width = 580
                    max_height = 400
                    
                    # Manter proporção
                    ratio = min(max_width/original_image.width, max_height/original_image.height)
                    new_width = int(original_image.width * ratio)
                    new_height = int(original_image.height * ratio)
                    
                    # Redimensionar
                    resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # CONVERTER para formato compatível com Tkinter
                    if resized_image.mode in ('RGBA', 'LA'):
                        # Converter imagens com transparência para RGB
                        background = Image.new('RGB', resized_image.size, (255, 255, 255))
                        background.paste(resized_image, mask=resized_image.split()[-1] if resized_image.mode == 'RGBA' else None)
                        resized_image = background
                    
                    # Criar PhotoImage - REFERÊNCIA FORTE na lista
                    photo_image = ImageTk.PhotoImage(resized_image, master=root)
                    image_references.append(photo_image)  # MANTER REFERÊNCIA
                    
                    # Frame para imagem centralizada
                    image_frame = tk.Frame(message_inner, bg='#ffffff')
                    image_frame.pack(fill=tk.BOTH, expand=True)
                    
                    # Criar label da imagem
                    img_label = tk.Label(image_frame, image=photo_image, bg='#ffffff')
                    img_label.image = photo_image  # Referência adicional
                    img_label.pack(expand=True)
                    
                    # Informações da imagem
                    info_frame = tk.Frame(message_inner, bg='#ffffff')
                    info_frame.pack(fill=tk.X, pady=(15, 0))
                    
                    filename = message_data.get('filename', 'imagem.png')
                    file_info = tk.Label(info_frame, 
                                       text=f"📎 {filename} | 📏 {original_image.width}×{original_image.height} → {new_width}×{new_height}",
                                       font=('Arial', 9),
                                       bg='#ffffff',
                                       fg='#7f8c8d')
                    file_info.pack(anchor='w')
                    
                    # Fechar buffer
                    image_buffer.close()
                    
                    print(f"🖼️ Imagem carregada com sucesso: {filename} ({new_width}x{new_height})")
                    
                except Exception as e:
                    print(f"❌ Erro ao carregar imagem: {e}")
                    error_frame = tk.Frame(message_inner, bg='#ffffff')
                    error_frame.pack(fill=tk.BOTH, expand=True)
                    
                    error_label = tk.Label(error_frame, 
                                         text=f"❌ Erro ao carregar imagem\n{str(e)}", 
                                         fg='#e74c3c', 
                                         wraplength=500,
                                         font=('Arial', 10),
                                         bg='#ffffff',
                                         justify='center')
                    error_label.pack(expand=True)
            else:
                # Mensagem de texto
                root.geometry("600x550")
                
                # Frame para texto com scroll interno se necessário
                text_container = tk.Frame(message_inner, bg='#ffffff')
                text_container.pack(fill=tk.BOTH, expand=True)
                
                # Texto da mensagem
                text_frame = tk.Frame(text_container, bg='#ffffff')
                text_frame.pack(fill=tk.BOTH, expand=True)
                
                # Usar Text widget para melhor controle de texto longo
                text_widget = tk.Text(text_frame, 
                                    wrap=tk.WORD,
                                    font=('Arial', 11),
                                    bg='#ffffff',
                                    fg='#2c3e50',
                                    padx=10,
                                    pady=10,
                                    relief='flat',
                                    borderwidth=0,
                                    highlightthickness=0)
                
                # Inserir texto
                text_widget.insert('1.0', mensagem)
                text_widget.config(state='disabled')  # Tornar readonly
                
                # Scrollbar para texto muito longo
                text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
                text_widget.configure(yscrollcommand=text_scrollbar.set)
                
                text_widget.pack(side="left", fill="both", expand=True)
                text_scrollbar.pack(side="right", fill="y")

            # Botão de fechar
            button_frame = tk.Frame(content_frame, bg='#ffffff')
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            btn_close = tk.Button(button_frame, 
                               text="✓ Entendi", 
                               command=lambda: _safe_destroy(root, image_references), 
                               font=('Arial', 11, 'bold'),
                               bg='#008E55',
                               fg='white',
                               padx=30,
                               pady=10,
                               relief='flat',
                               cursor='hand2')
            btn_close.pack(pady=10)
            
            # Efeitos hover
            def on_enter(e):
                btn_close.config(bg='#006b41')
            def on_leave(e):
                btn_close.config(bg='#008E55')
            
            btn_close.bind("<Enter>", on_enter)
            btn_close.bind("<Leave>", on_leave)

            # Configurar fechamento seguro
            def _safe_destroy(window, img_refs):
                window_manager.window_count -= 1
                # Fechar janela primeiro
                window.destroy()
                # As referências serão liberadas automaticamente pelo garbage collector
                print(f"📁 Janela fechada ({window_manager.window_count} restantes)")

            root.protocol("WM_DELETE_WINDOW", lambda: _safe_destroy(root, image_references))

            # Posicionamento inteligente
            window_manager.window_count += 1
            root.update_idletasks()
            
            # Calcular posição com offset
            width = root.winfo_width()
            height = root.winfo_height()
            offset = (window_manager.window_count % 4) * 30
            
            x = (root.winfo_screenwidth() // 2) - (width // 2) + offset
            y = (root.winfo_screenheight() // 2) - (height // 2) + offset
            root.geometry(f"+{x}+{y}")

            # Focar na janela
            root.focus_force()
            root.lift()

            print(f"📁 Nova janela aberta ({window_manager.window_count} total)")

            # Ajustar scroll para o topo
            canvas.update_idletasks()
            canvas.yview_moveto(0.0)
            
            # SOLUÇÃO CRÍTICA: Manter referência da janela root
            def keep_alive():
                try:
                    root.mainloop()
                except Exception as e:
                    print(f"Janela finalizada: {e}")
            
            keep_alive()

        except Exception as e:
            print(f"❌ Erro crítico ao criar janela: {e}")

    # Executar em thread separada
    Thread(target=_create_window, daemon=True).start()

# =============================================
# FUNÇÕES ORIGINAIS (MANTIDAS)
# =============================================

def get_system_unique_id():
    """Gera um ID único baseado no hostname e usuário"""
    try:
        hostname = socket.gethostname()
        username = getpass.getuser()
        
        hostname_clean = re.sub(r'[^a-zA-Z0-9]', '', hostname)
        username_clean = re.sub(r'[^a-zA-Z0-9]', '', username)
        
        unique_id = f"{hostname_clean}_{username_clean}"
        
        print(f"🔑 ID único gerado: {unique_id}")
        return unique_id
        
    except Exception as e:
        print(f"⚠️ Erro ao gerar ID único: {e}")
        return f"{getpass.getuser()}_{socket.gethostname()}"

def show_registration_form(system_info):
    """Mostra formulário de cadastro para novos usuários"""
    def _form():
        root = tk.Tk()
        root.title("Cadastro - Unimed")
        root.geometry("500x400")
        root.configure(bg='#008E55')
        root.resizable(False, False)
        root.attributes("-topmost", True)
        
        
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

        # Botão simples
        btn_frame = tk.Frame(container, bg='white')
        btn_frame.pack(fill=tk.X, pady=20)
        
        btn = tk.Button(btn_frame, text="✅ Cadastro Automático", 
                      command=root.destroy,
                      font=('Arial', 12, 'bold'),
                      bg='#008E55', fg='white', padx=20, pady=10)
        btn.pack()
        
        root.mainloop()
        return True

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
            'unique_id': unique_id
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

def show_connection_status(connected):
    """Mostra status da conexão na bandeja do sistema"""
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
        cadastro_sucesso = show_registration_form(system_info)
        
        if cadastro_sucesso:
            print("✅ Cadastro realizado com sucesso! Conectando ao servidor...")
            await asyncio.sleep(2)
        else:
            print("❌ Cadastro não realizado. Tentando conectar como usuário não cadastrado...")
    else:
        print("✅ Usuário já cadastrado. Conectando ao servidor...")
    
    # Conexão normal com o servidor WebSocket
    username_para_conexao = unique_id
    uri = f"ws://{IP_SERVIDOR}:{PORTA}"
    reconnect_count = 0
    max_reconnect_delay = 30
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
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

                        # Notificação na Central de Ações
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
                                     message_data=data)
                        else:
                            texto_popup = data.get('texto_adicional', 'Nova imagem recebida')
                            show_popup("Imagem - Unimed", 
                                     texto_popup,
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