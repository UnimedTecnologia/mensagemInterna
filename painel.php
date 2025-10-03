<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Painel de Mensagens - Unimed</title>
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #008E55 0%, #0077cc 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: #008E55;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h2 {
            margin: 0;
            font-size: 24px;
        }
        .header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        #usuarios { 
            margin-top: 25px; 
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #008E55;
        }
        .usuario { 
            padding: 8px 12px; 
            border-bottom: 1px solid #e9ecef; 
            display: flex;
            align-items: center;
        }
        .usuario:before {
            content: "🟢";
            margin-right: 10px;
            font-size: 12px;
        }
        .usuario:last-child { border-bottom: none; }
        
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        textarea, input[type="file"] {
            width: 100%;
            max-width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        textarea:focus, input[type="file"]:focus {
            outline: none;
            border-color: #008E55;
        }
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        .image-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 2px dashed #dee2e6;
            margin: 20px 0;
        }
        .image-preview { 
            max-width: 100%; 
            max-height: 300px; 
            margin: 15px 0; 
            border: 2px solid #008E55;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        #imagePreviewContainer { 
            display: none; 
            text-align: center;
        }
        button { 
            padding: 15px 30px; 
            background: #008E55; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
            display: block;
            width: 100%;
            margin-top: 20px;
        }
        button:hover { 
            background: #003d7a; 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        #status { 
            padding: 15px; 
            margin: 20px 0; 
            border-radius: 8px; 
            display: none;
            text-align: center;
            font-weight: bold;
        }
        .success { 
            background: #d4edda; 
            color: #155724; 
            border: 1px solid #c3e6cb; 
        }
        .error { 
            background: #f8d7da; 
            color: #721c24; 
            border: 1px solid #f5c6cb; 
        }
        .online-count {
            background: #28a745;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Painel de Mensagens - Unimed</h2>
            <p>Envie mensagens e imagens para todos os colaboradores</p>
        </div>
        
        <div class="content">
            <form id="formMensagem">
                <div class="form-group">
                    <label for="mensagem">Mensagem:</label>
                    <textarea name="mensagem" id="mensagem" placeholder="Digite sua mensagem aqui..." required></textarea>
                </div>

                <div class="image-section">
                    <label for="imageUpload">📎 Anexar Imagem (Opcional):</label>
                    <input type="file" id="imageUpload" accept="image/*">
                    <div id="imagePreviewContainer">
                        <img id="imagePreview" class="image-preview">
                    </div>
                </div>

                <button type="submit" id="submitButton">📤 Enviar Mensagem</button>
            </form>

            <div id="usuarios">
                <h3>👥 Colaboradores Online: <span id="onlineCount" class="online-count">0</span></h3>
                <ul id="listaUsuarios"></ul>
            </div>

            <p id="status"></p>
        </div>
    </div>

    <script>
        const listaUsuarios = document.getElementById('listaUsuarios');
        const form = document.getElementById('formMensagem');
        const status = document.getElementById('status');
        const imageUpload = document.getElementById('imageUpload');
        const imagePreview = document.getElementById('imagePreview');
        const imagePreviewContainer = document.getElementById('imagePreviewContainer');
        const mensagemTextarea = document.getElementById('mensagem');
        const onlineCount = document.getElementById('onlineCount');

        // Preview da imagem
        imageUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreviewContainer.style.display = 'block';
                }
                reader.readAsDataURL(file);
            } else {
                imagePreviewContainer.style.display = 'none';
            }
        });

        // Função para buscar usuários online
        async function atualizarUsuarios() {
            try {
                const res = await fetch('http://10.11.0.144:8081/usuarios');
                const usuarios = await res.json();

                listaUsuarios.innerHTML = '';
                usuarios.forEach(u => {
                    const li = document.createElement('li');
                    li.textContent = u;
                    li.className = 'usuario';
                    listaUsuarios.appendChild(li);
                });
                
                onlineCount.textContent = usuarios.length;
            } catch (e) {
                listaUsuarios.innerHTML = '<li>Erro ao carregar usuários.</li>';
                onlineCount.textContent = '0';
            }
        }

        // Atualiza a lista a cada 3 segundos
        setInterval(atualizarUsuarios, 3000);
        atualizarUsuarios();

        // Converter imagem para Base64
        function imageToBase64(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = () => {
                    const base64 = reader.result.split(',')[1];
                    resolve(base64);
                };
                reader.onerror = error => reject(error);
            });
        }

        // Mostrar status
        function showStatus(message, isSuccess) {
            status.textContent = message;
            status.className = isSuccess ? 'success' : 'error';
            status.style.display = 'block';
            setTimeout(() => {
                status.style.display = 'none';
            }, 4000);
        }

        // Enviar mensagem pelo painel
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const msg = mensagemTextarea.value.trim();
                if (!msg) {
                    showStatus('Digite uma mensagem!', false);
                    return;
                }

                const file = imageUpload.files[0];
                let payload = {};

                if (file) {
                    // Envio com imagem
                    const base64Image = await imageToBase64(file);
                    payload = {
                        type: 'image',
                        mensagem: base64Image,
                        filename: file.name,
                        texto_adicional: msg
                    };
                } else {
                    // Envio apenas de texto
                    payload = {
                        type: 'text',
                        mensagem: msg
                    };
                }

                // Envia via servidor Python
                const response = await fetch('http://10.11.0.144:8081/enviar', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                const result = await response.json();
                
                if (result.status === 'ok') {
                    const successMsg = file ? 'Mensagem com imagem enviada!' : 'Mensagem enviada!';
                    showStatus(successMsg, true);
                    
                    // Limpa o formulário
                    mensagemTextarea.value = '';
                    imageUpload.value = '';
                    imagePreviewContainer.style.display = 'none';
                } else {
                    showStatus('Erro ao enviar: ' + result.detalhes, false);
                }
                
            } catch (err) {
                showStatus('Erro de conexão com o servidor!', false);
                console.error(err);
            }
        });
    </script>
</body>
</html>