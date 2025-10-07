<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <link rel="icon" href="icon.png" type="image/png">
    <title>Painel de Mensagens - Unimed</title>
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #008E55 0%, #00b368 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
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
        
        /* Estilos para as abas de setores */
        .setor-tabs {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 15px 0;
        }
        .setor-tab {
            padding: 10px 20px;
            background: #e9ecef;
            border: 2px solid #dee2e6;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        .setor-tab:hover {
            background: #dee2e6;
        }
        .setor-tab.active {
            background: #008E55;
            color: white;
            border-color: #008E55;
        }
        
        .usuarios-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .usuario-card {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        .usuario-card.offline {
            border-left-color: #6c757d;
            opacity: 0.6;
        }
        .usuario-nome {
            font-weight: bold;
            color: #333;
        }
        .usuario-setor {
            font-size: 12px;
            color: #666;
        }
        .usuario-status {
            font-size: 10px;
            color: #28a745;
        }
        .usuario-status.offline {
            color: #6c757d;
        }

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
            background: #006b41; 
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
        .stats {
            display: flex;
            justify-content: space-between;
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #008E55;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
        }
        .connection-info {
            background: #e8f5e8;
            border: 1px solid #008E55;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
        }
        .server-status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .server-online {
            background: #28a745;
        }
        .server-offline {
            background: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Painel de Mensagens - Unimed</h2>
            <p>Envie mensagens por setor ou para todos os colaboradores</p>
        </div>
        
        <div class="content">
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number" id="totalOnline">0</div>
                    <div class="stat-label">Conexões Online</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="totalSetores">0</div>
                    <div class="stat-label">Setores</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="setorSelecionado">-</div>
                    <div class="stat-label">Setor Selecionado</div>
                </div>
            </div>

            <div class="connection-info">
                <span class="server-status server-online" id="serverStatus"></span>
                <span id="serverMessage">Conectado ao servidor</span>
                <span id="lastUpdate" style="float: right;"></span>
            </div>

            <form id="formMensagem">
                <div class="form-group">
                    <label for="setorDestino">🎯 Enviar para:</label>
                    <div class="setor-tabs" id="setorTabs">
                        <div class="setor-tab active" data-setor="todos">👥 Todos os Setores</div>
                        <!-- Setores serão carregados via JavaScript -->
                    </div>
                </div>

                <div class="form-group">
                    <label for="mensagem">💬 Mensagem:</label>
                    <textarea name="mensagem" id="mensagem" placeholder="Digite sua mensagem aqui..." required></textarea>
                </div>

                <div class="image-section">
                    <label for="imageUpload">📎 Anexar Imagem (Opcional):</label>
                    <input type="file" id="imageUpload" accept="image/*">
                    <div id="imagePreviewContainer">
                        <img id="imagePreview" class="image-preview">
                    </div>
                </div>

                <button type="submit" id="submitButton">
                    📤 Enviar Mensagem para <span id="destinoTexto">Todos os Setores</span>
                </button>
            </form>

            <div id="usuarios">
                <h3>👥 Colaboradores Online por Setor:</h3>
                <div id="listaUsuarios" class="usuarios-grid">
                    <!-- Usuários serão carregados via JavaScript -->
                </div>
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
        const setorTabs = document.getElementById('setorTabs');
        const totalOnline = document.getElementById('totalOnline');
        const totalSetores = document.getElementById('totalSetores');
        const setorSelecionado = document.getElementById('setorSelecionado');
        const destinoTexto = document.getElementById('destinoTexto');
        const serverStatus = document.getElementById('serverStatus');
        const serverMessage = document.getElementById('serverMessage');
        const lastUpdate = document.getElementById('lastUpdate');

        let setorAtual = 'todos';
        let setoresDisponiveis = [];
        let usuariosOnline = [];
        let serverOnline = true;

        // Carregar setores disponíveis
        async function carregarSetores() {
            try {
                const res = await fetch('http://10.11.0.144:8081/setores');
                if (!res.ok) throw new Error('Servidor não respondeu');
                
                setoresDisponiveis = await res.json();
                
                setorTabs.innerHTML = '';
                
                // Botão "Todos"
                const tabTodos = document.createElement('div');
                tabTodos.className = 'setor-tab active';
                tabTodos.textContent = '👥 Todos os Setores';
                tabTodos.dataset.setor = 'todos';
                tabTodos.onclick = () => selecionarSetor('todos');
                setorTabs.appendChild(tabTodos);
                
                // Setores individuais
                setoresDisponiveis.forEach(setor => {
                    const tab = document.createElement('div');
                    tab.className = 'setor-tab';
                    tab.textContent = setor;
                    tab.dataset.setor = setor;
                    tab.onclick = () => selecionarSetor(setor);
                    setorTabs.appendChild(tab);
                });
                
                totalSetores.textContent = setoresDisponiveis.length;
                updateServerStatus(true, 'Conectado ao servidor');
                
            } catch (e) {
                console.error('Erro ao carregar setores:', e);
                updateServerStatus(false, 'Erro ao conectar com o servidor');
            }
        }

        // Atualizar status do servidor
        function updateServerStatus(online, message) {
            serverOnline = online;
            serverStatus.className = online ? 'server-status server-online' : 'server-status server-offline';
            serverMessage.textContent = message;
            lastUpdate.textContent = new Date().toLocaleTimeString();
        }

        // Selecionar setor
        function selecionarSetor(setor) {
            setorAtual = setor;
            
            // Atualizar tabs
            document.querySelectorAll('.setor-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelector(`.setor-tab[data-setor="${setor}"]`).classList.add('active');
            
            // Atualizar interface
            setorSelecionado.textContent = setor === 'todos' ? 'Todos' : setor;
            destinoTexto.textContent = setor === 'todos' ? 'Todos os Setores' : `Setor ${setor}`;
            
            // Atualizar lista de usuários
            atualizarListaUsuarios();
        }

        // Preview da imagem
        imageUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Verificar tamanho do arquivo (máximo 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showStatus('Imagem muito grande! Máximo 5MB.', false);
                    imageUpload.value = '';
                    return;
                }

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
                if (!res.ok) throw new Error('Servidor não respondeu');
                
                usuariosOnline = await res.json();
                
                // Atualizar estatísticas
                const totalConexoes = usuariosOnline.reduce((total, user) => total + user.conexoes, 0);
                totalOnline.textContent = totalConexoes;
                
                // Agrupar usuários por setor para display
                atualizarListaUsuarios();
                updateServerStatus(true, `Conectado - ${totalConexoes} conexões ativas`);
                
            } catch (e) {
                console.error('Erro ao carregar usuários:', e);
                totalOnline.textContent = '0';
                updateServerStatus(false, 'Erro ao carregar dados');
                listaUsuarios.innerHTML = '<div class="usuario-card">Erro ao carregar usuários online</div>';
            }
        }

        // Atualizar lista de usuários filtrada por setor
        function atualizarListaUsuarios() {
            listaUsuarios.innerHTML = '';
            
            const usuariosFiltrados = setorAtual === 'todos' 
                ? usuariosOnline 
                : usuariosOnline.filter(u => u.setor === setorAtual);
            
            if (usuariosFiltrados.length === 0) {
                const emptyCard = document.createElement('div');
                emptyCard.className = 'usuario-card';
                emptyCard.innerHTML = setorAtual === 'todos' 
                    ? 'Nenhum usuário online no momento' 
                    : `Nenhum usuário online no setor ${setorAtual}`;
                listaUsuarios.appendChild(emptyCard);
                return;
            }
            
            usuariosFiltrados.forEach(usuario => {
                const card = document.createElement('div');
                card.className = 'usuario-card';
                
                // Ícone diferente para múltiplas conexões
                const connectionIcon = usuario.conexoes > 1 ? '🖥️×' + usuario.conexoes : '🖥️';
                const displayName = usuario.nome_completo && usuario.nome_completo !== 'N/A' 
                    ? usuario.nome_completo 
                    : usuario.username;
                
                card.innerHTML = `
                    <div class="usuario-nome">${displayName}</div>
                    <div class="usuario-setor">${usuario.setor}</div>
                    <div class="usuario-status">
                        ${connectionIcon} ${usuario.conexoes} conexão(ões)
                    </div>
                `;
                
                listaUsuarios.appendChild(card);
            });
        }

        // Atualiza a lista a cada 3 segundos
        setInterval(atualizarUsuarios, 3000);
        
        // Inicializar
        carregarSetores();
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
            
            if (!serverOnline) {
                showStatus('Servidor offline. Não é possível enviar mensagens.', false);
                return;
            }
            
            try {
                const msg = mensagemTextarea.value.trim();
                if (!msg) {
                    showStatus('Digite uma mensagem!', false);
                    return;
                }

                const file = imageUpload.files[0];
                let payload = {
                    setor_destino: setorAtual === 'todos' ? null : setorAtual
                };

                if (file) {
                    // Verificar tamanho da imagem
                    if (file.size > 5 * 1024 * 1024) {
                        showStatus('Imagem muito grande! Máximo 5MB.', false);
                        return;
                    }

                    // Envio com imagem
                    const base64Image = await imageToBase64(file);
                    payload.type = 'image';
                    payload.mensagem = base64Image;
                    payload.filename = file.name;
                    payload.texto_adicional = msg;
                } else {
                    // Envio apenas de texto
                    payload.type = 'text';
                    payload.mensagem = msg;
                }

                // Mostrar loading
                const submitButton = document.getElementById('submitButton');
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '⏳ Enviando...';
                submitButton.disabled = true;

                // Envia via servidor Python
                const response = await fetch('http://10.11.0.144:8081/enviar', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                const result = await response.json();
                
                // Restaurar botão
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
                
                if (result.status === 'ok') {
                    const destino = setorAtual === 'todos' ? 'todos os setores' : `setor ${setorAtual}`;
                    const successMsg = file 
                        ? `✅ Mensagem com imagem enviada para ${destino}!` 
                        : `✅ Mensagem enviada para ${destino}!`;
                    
                    showStatus(successMsg, true);
                    
                    // Limpa o formulário
                    mensagemTextarea.value = '';
                    imageUpload.value = '';
                    imagePreviewContainer.style.display = 'none';
                } else {
                    showStatus('❌ Erro ao enviar: ' + (result.detalhes || 'Erro desconhecido'), false);
                }
                
            } catch (err) {
                // Restaurar botão em caso de erro
                const submitButton = document.getElementById('submitButton');
                submitButton.innerHTML = '📤 Enviar Mensagem para <span id="destinoTexto">Todos os Setores</span>';
                submitButton.disabled = false;
                
                showStatus('❌ Erro de conexão com o servidor!', false);
                console.error(err);
            }
        });

        // Atualizar hora da última atualização
        setInterval(() => {
            lastUpdate.textContent = new Date().toLocaleTimeString();
        }, 60000);
    </script>
</body>
</html>