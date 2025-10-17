SERVER

cd C:\xampp\htdocs\mensagemInterna
python server.py

CLIENT

cd C:\xampp\htdocs\mensagemInterna
python client.py

GERAR EXECUTAVEL DO CLIENT PYTHON
INSTALAR -----> pip install pyinstaller

cd C:\xampp\htdocs\mensagemInterna
pyinstaller --onefile --noconsole client.py

__________________________________________________
ACESSAR NO SERVIDOR LINUX
No Windows powershell:
ssh -L 8088:localhost:8088 unimed@10.10.10.51
senha: Y1tTr2ybpLttC0R1

Caminho server.py do servidor Linux:
cd /var/www/html/mensagemInterna
python3 server.py
__________________________________________________


---------CONFIGURAÇÃO SERVIDOR------------------------------------------------------
NO WINDOWS:
cd C:\xampp\htdocs\mensagemInterna
scp unimed@10.10.10.51:/home/unimed/


NO PUTTY:
# Atualiza a lista de pacotes
sudo yum update

# Instala Python3 e pip (gerenciador de pacotes Python)
sudo yum install python3 python3-pip

# Instala as bibliotecas necessárias
pip3 install websockets aiohttp pillow
# OU sudo yum install python3-pip

--------
# Vá para a pasta onde está o server.py
cd /home/unimed

# Execute para testar
python3 server.py


----- LIBERAR PORTAS
# Libera a porta do WebSocket (8765)
sudo firewall-cmd --permanent --add-port=8765/tcp

# Libera a porta HTTP (8081) 
sudo firewall-cmd --permanent --add-port=8081/tcp

# Aplica as mudanças
sudo firewall-cmd --reload

# Verifica se as portas estão liberadas
sudo firewall-cmd --list-ports

