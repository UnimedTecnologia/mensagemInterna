import socket
import requests

def test_port(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            result = s.connect_ex((host, port))
            if result == 0:
                return f"✅ Porta {port} ABERTA"
            else:
                return f"❌ Porta {port} FECHADA"
    except Exception as e:
        return f"❌ Erro na porta {port}: {e}"

def test_http():
    try:
        response = requests.get("http://10.10.10.51:8081/setores", timeout=5)
        return f"✅ HTTP OK - Status: {response.status_code}"
    except Exception as e:
        return f"❌ HTTP FALHOU: {e}"

print("🔍 Testando conectividade com o servidor...")
print(test_port("10.10.10.51", 8765))
print(test_port("10.10.10.51", 8081))
print(test_http())