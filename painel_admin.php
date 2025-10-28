<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <link rel="icon" href="icon.png" type="image/png">
    <title>Painel Administrativo - Unimed</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.3.0/font/bootstrap-icons.css">
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #008E55 0%, #00b368 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
       /* HEADER MELHORADO */
        .header {
            background: linear-gradient(135deg, #008E55 0%, #006b41 100%);
            color: white;
            padding: 25px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .header::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #00b368, #ffffff, #00b368);
        }
        .logo-container {
            display: flex;
            align-items: center;
        }
        .logo {
            height: 70px;
            margin-right: 20px;
            border-radius: 8px; 
            padding: 5px; /* Espaço ao redor da logo */
            box-shadow: 0 5px 8px rgba(0,0,0,0.1); /* Sombra sutil */
        }
        .header-text {
            flex: 1;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .header p {
            margin: 8px 0 0 0;
            opacity: 0.9;
            font-size: 16px;
            font-weight: 300;
        }
        .header-badge {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .content {
            padding: 30px;
        }
        
        /* Abas do sistema */
        .admin-tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 2px solid #008E55;
        }
        .admin-tab {
            padding: 12px 24px;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            font-weight: bold;
        }
        .admin-tab:hover {
            background: #e9ecef;
        }
        .admin-tab.active {
            background: #008E55;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        
        /* Tabelas */
        .table-container {
            overflow-x: auto;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        th {
            background: #008E55;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background: #f8f9fa;
        }
        
        /* Forms */
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #e9ecef;
            border-radius: 5px;
            font-size: 14px;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #008E55;
        }
        
        /* Botões */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
            margin: 5px;
        }
        .btn-primary {
            background: #008E55;
            color: white;
        }
        .btn-primary:hover {
            background: #006b41;
        }
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover {
            background: #218838;
        }
        
        /* Status */
        .status-ativo {
            color: #28a745;
            font-weight: bold;
        }
        .status-inativo {
            color: #dc3545;
            font-weight: bold;
        }
        
        /* Cards de estatísticas */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #008E55;
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #008E55;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
        }
        
        /* Mensagens */
        #status {
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            display: none;
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

        /* Responsividade para o header */
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                text-align: center;
                padding: 20px;
            }
            .logo-container {
                margin-bottom: 15px;
                justify-content: center;
            }
            .header-badge {
                margin-top: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-container">
                <img src="logo_unimed.png" alt="Logo Unimed" class="logo">
                <div class="header-text">
                    <h1>Painel Administrativo - Unimed</h1>
                    <p>Gerenciamento de Usuários e Setores</p>
                </div>
            </div>
            <div class="header-badge">
                Sistema de Comunicação Interna
            </div>
        </div>    
    <!-- <div class="header">
            <h2>Painel Administrativo - Unimed</h2>
            <p>Gerenciamento de Usuários e Setores</p>
        </div> -->
        
        <div class="content">
            <div class="admin-tabs">
                <button class="admin-tab active" onclick="openTab('tabUsuarios')">👥 Usuários</button>
                <button class="admin-tab" onclick="openTab('tabSetores')">📂 Setores</button>
                <!-- <button class="admin-tab" onclick="openTab('tabMensagens')">📨 Histórico</button> -->
                <!-- <button class="admin-tab" onclick="openTab('tabEstatisticas')">📊 Estatísticas</button> -->
            </div>
            
            <!-- Aba de Usuários -->
            <div id="tabUsuarios" class="tab-content active">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="totalUsuarios">0</div>
                        <div class="stat-label">Total de Usuários</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="usuariosAtivos">0</div>
                        <div class="stat-label">Usuários Ativos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="usuariosInativos">0</div>
                        <div class="stat-label">Usuários Inativos</div>
                    </div>
                </div>
                
                <button class="btn btn-primary" onclick="abrirModalUsuario()">➕ Adicionar Usuário</button>
                
                <div class="table-container">
                    <table id="tabelaUsuarios">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Nome Completo</th>
                                <th>Setor</th>
                                <th>Matrícula</th>
                                <th>Status</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody id="corpoTabelaUsuarios">
                            <!-- Dados carregados via JavaScript -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Aba de Setores -->
            <div id="tabSetores" class="tab-content">
                <div class="form-group">
                    <label for="novoSetor">Adicionar Novo Setor:</label>
                    <div style="display: flex; gap: 10px; flex-direction: column;">
                        <input type="text" id="novoSetor" placeholder="Nome do setor">
                        <input type="text" id="descricaoSetor" placeholder="Descrição (opcional)">
                        <button class="btn btn-success" onclick="adicionarSetor()">➕ Adicionar Setor</button>
                    </div>
                </div>
                
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Setor</th>
                                <th>Descrição</th>
                                <th>Total de Usuários</th>
                                <th>Usuários Ativos</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody id="corpoTabelaSetores">
                            <!-- Dados carregados via JavaScript -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Aba de Histórico de Mensagens -->
            <div id="tabMensagens" class="tab-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="totalMensagens">0</div>
                        <div class="stat-label">Total de Mensagens</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="mensagensTexto">0</div>
                        <div class="stat-label">Mensagens de Texto</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="mensagensImagem">0</div>
                        <div class="stat-label">Mensagens com Imagem</div>
                    </div>
                </div>
                
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Remetente</th>
                                <th>Setor Destino</th>
                                <th>Tipo</th>
                                <th>Mensagem</th>
                                <th>Data/Hora</th>
                            </tr>
                        </thead>
                        <tbody id="corpoTabelaMensagens">
                            <!-- Dados carregados via JavaScript -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Aba de Estatísticas -->
            <div id="tabEstatisticas" class="tab-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="statTotalUsers">0</div>
                        <div class="stat-label">Usuários Cadastrados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="statTotalSetores">0</div>
                        <div class="stat-label">Setores</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="statTotalMsgs">0</div>
                        <div class="stat-label">Mensagens Enviadas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="statSetorMaisUsuarios">-</div>
                        <div class="stat-label">Setor com Mais Usuários</div>
                    </div>
                </div>
                
                <h3>📈 Distribuição por Setor</h3>
                <div id="graficoSetores" style="height: 300px; margin: 20px 0;">
                    <!-- Gráfico será gerado aqui -->
                </div>
            </div>
            
            <p id="status"></p>
        </div>
    </div>

    <!-- Modal para Adicionar/Editar Usuário -->
    <div id="modalUsuario" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 10px; width: 500px;">
            <h3 id="modalTitulo">Adicionar Usuário</h3>
            <form id="formUsuario">
                <input type="hidden" id="usuarioId">
                <div class="form-group">
                    <div class="row">
                        <label for="modalUsername">Nome do dispositivo + nome do usuário:<i class="bi bi-info-circle" title="Para descobrir o nome da maquina utilize Win+X e depois aperte S" ></i></label>
                        
                     </div>
                    <input type="text" id="modalUsername" required>
                </div>
                <div class="form-group">
                    <label for="modalNomeCompleto">Nome Completo:</label>
                    <input type="text" id="modalNomeCompleto" required>
                </div>
                <div class="form-group">
                    <label for="modalSetor">Setor:</label>
                    <select id="modalSetor" required>
                        <option value="">Selecione um setor</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="modalMatricula">Matrícula (Opcional):</label>
                    <input type="text" id="modalMatricula">
                </div>
                <div class="form-group">
                    <label for="modalAtivo">Status:</label>
                    <select id="modalAtivo">
                        <option value="1">Ativo</option>
                        <option value="0">Inativo</option>
                    </select>
                </div>
                <div style="text-align: right; margin-top: 20px;">
                    <button type="button" class="btn" onclick="fecharModalUsuario()" style="background: #6c757d; color: white;">Cancelar</button>
                    <button type="submit" class="btn btn-primary">Salvar</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // Variáveis globais
        let usuarios = [];
        let setores = [];
        let mensagens = [];

        // Funções de abas
        function openTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.admin-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            event.currentTarget.classList.add('active');
            
            // Recarregar dados da aba
            if (tabName === 'tabUsuarios') carregarUsuarios();
            if (tabName === 'tabSetores') carregarSetores();
            if (tabName === 'tabMensagens') carregarMensagens();
            if (tabName === 'tabEstatisticas') carregarEstatisticas();
        }

        // API Base URL
        // const API_BASE = 'http://192.168.16.166:8081'; // TESTE LOCAL
        const API_BASE = 'http://192.168.1.253:8081'; // TESTE LOCAL
        // const API_BASE = 'http://10.10.10.51:8081'; //! SERVIDOR

        // Carregar usuários
        async function carregarUsuarios() {
            try {
                const response = await fetch(`${API_BASE}/admin/usuarios`);
                usuarios = await response.json();
                
                atualizarTabelaUsuarios();
                atualizarEstatisticasUsuarios();
                
            } catch (error) {
                showStatus('Erro ao carregar usuários: ' + error.message, false);
            }
        }

        // Atualizar tabela de usuários
        function atualizarTabelaUsuarios() {
            const tbody = document.getElementById('corpoTabelaUsuarios');
            tbody.innerHTML = '';
            
            usuarios.forEach(usuario => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${usuario.id}</td>
                    <td>${usuario.username}</td>
                    <td>${usuario.nome_completo || '-'}</td>
                    <td>${usuario.setor}</td>
                    <td>${usuario.matricula || '-'}</td>
                    <td class="${usuario.ativo ? 'status-ativo' : 'status-inativo'}">
                        ${usuario.ativo ? 'Ativo' : 'Inativo'}
                    </td>
                    <td>
                        <button class="btn btn-primary" onclick="editarUsuario(${usuario.id})">✏️ Editar</button>
                        <button class="btn btn-danger" onclick="excluirUsuario(${usuario.id})">🗑️ Excluir</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Atualizar estatísticas de usuários
        function atualizarEstatisticasUsuarios() {
            const total = usuarios.length;
            const ativos = usuarios.filter(u => u.ativo).length;
            const inativos = total - ativos;
            
            document.getElementById('totalUsuarios').textContent = total;
            document.getElementById('usuariosAtivos').textContent = ativos;
            document.getElementById('usuariosInativos').textContent = inativos;
        }

        // Carregar setores
        async function carregarSetores() {
            try {
                const response = await fetch(`${API_BASE}/admin/setores`);
                setores = await response.json();
                atualizarTabelaSetores();
                atualizarSelectSetores();
            } catch (error) {
                showStatus('Erro ao carregar setores: ' + error.message, false);
            }
        }

        // Atualizar tabela de setores
        function atualizarTabelaSetores() {
            const tbody = document.getElementById('corpoTabelaSetores');
            tbody.innerHTML = '';
            
            setores.forEach(setor => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${setor.nome}</td>
                    <td>${setor.descricao}</td>
                    <td>${setor.total_usuarios}</td>
                    <td>${setor.ativos}</td>
                    <td>
                        <button class="btn btn-danger" onclick="excluirSetor('${setor.nome}')">🗑️ Excluir</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Atualizar select de setores no modal
        function atualizarSelectSetores() {
            const select = document.getElementById('modalSetor');
            select.innerHTML = '<option value="">Selecione um setor</option>';
            
            setores.forEach(setor => {
                const option = document.createElement('option');
                option.value = setor.nome;
                option.textContent = setor.nome;
                select.appendChild(option);
            });
        }

        // Carregar mensagens
        async function carregarMensagens() {
            try {
                const response = await fetch(`${API_BASE}/admin/mensagens`);
                mensagens = await response.json();
                atualizarTabelaMensagens();
                atualizarEstatisticasMensagens();
            } catch (error) {
                showStatus('Erro ao carregar mensagens: ' + error.message, false);
            }
        }

        // Atualizar tabela de mensagens
        function atualizarTabelaMensagens() {
            const tbody = document.getElementById('corpoTabelaMensagens');
            tbody.innerHTML = '';
            
            mensagens.forEach(msg => {
                const mensagemPreview = msg.tipo === 'image' 
                    ? '📷 Imagem' 
                    : msg.mensagem.length > 50 
                        ? msg.mensagem.substring(0, 50) + '...' 
                        : msg.mensagem;
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${msg.id}</td>
                    <td>${msg.remetente}</td>
                    <td>${msg.setor_destino || 'Todos'}</td>
                    <td>${msg.tipo === 'image' ? '📷 Imagem' : '📝 Texto'}</td>
                    <td title="${msg.mensagem}">${mensagemPreview}</td>
                    <td>${new Date(msg.timestamp).toLocaleString()}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Atualizar estatísticas de mensagens
        function atualizarEstatisticasMensagens() {
            const total = mensagens.length;
            const texto = mensagens.filter(m => m.tipo === 'text').length;
            const imagem = mensagens.filter(m => m.tipo === 'image').length;
            
            document.getElementById('totalMensagens').textContent = total;
            document.getElementById('mensagensTexto').textContent = texto;
            document.getElementById('mensagensImagem').textContent = imagem;
        }

        // Carregar estatísticas
        async function carregarEstatisticas() {
            try {
                const response = await fetch(`${API_BASE}/admin/estatisticas`);
                const stats = await response.json();
                
                document.getElementById('statTotalUsers').textContent = stats.total_usuarios;
                document.getElementById('statTotalSetores').textContent = stats.total_setores;
                document.getElementById('statTotalMsgs').textContent = stats.total_mensagens;
                document.getElementById('statSetorMaisUsuarios').textContent = stats.setor_mais_usuarios;
                
            } catch (error) {
                showStatus('Erro ao carregar estatísticas: ' + error.message, false);
            }
        }

        // Modal de usuário
        function abrirModalUsuario(usuario = null) {
            document.getElementById('modalTitulo').textContent = usuario ? 'Editar Usuário' : 'Adicionar Usuário';
            document.getElementById('usuarioId').value = usuario ? usuario.id : '';
            document.getElementById('modalUsername').value = usuario ? usuario.username : '';
            document.getElementById('modalNomeCompleto').value = usuario ? usuario.nome_completo : '';
            document.getElementById('modalSetor').value = usuario ? usuario.setor : '';
            document.getElementById('modalMatricula').value = usuario ? usuario.matricula : '';
            document.getElementById('modalAtivo').value = usuario ? (usuario.ativo ? '1' : '0') : '1';
            
            document.getElementById('modalUsuario').style.display = 'block';
        }

        function fecharModalUsuario() {
            document.getElementById('modalUsuario').style.display = 'none';
            document.getElementById('formUsuario').reset();
        }

        // Formulário de usuário
        document.getElementById('formUsuario').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const usuarioData = {
                username: document.getElementById('modalUsername').value,
                nome_completo: document.getElementById('modalNomeCompleto').value,
                setor: document.getElementById('modalSetor').value,
                matricula: document.getElementById('modalMatricula').value,
                ativo: document.getElementById('modalAtivo').value
            };
            
            const usuarioId = document.getElementById('usuarioId').value;
            const url = usuarioId ? `${API_BASE}/admin/usuarios/${usuarioId}` : `${API_BASE}/admin/usuarios`;
            const method = usuarioId ? 'PUT' : 'POST';
            
            try {
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(usuarioData)
                });
                
                const result = await response.json();
                
                if (result.status === 'ok') {
                    showStatus(usuarioId ? 'Usuário atualizado com sucesso!' : 'Usuário adicionado com sucesso!', true);
                    fecharModalUsuario();
                    carregarUsuarios();
                } else {
                    showStatus('Erro: ' + result.detalhes, false);
                }
            } catch (error) {
                showStatus('Erro de conexão: ' + error.message, false);
            }
        });

        // Editar usuário
        function editarUsuario(id) {
            const usuario = usuarios.find(u => u.id === id);
            if (usuario) {
                abrirModalUsuario(usuario);
            }
        }

        // Excluir usuário
        async function excluirUsuario(id) {
            if (confirm('Tem certeza que deseja excluir este usuário?')) {
                try {
                    const response = await fetch(`${API_BASE}/admin/usuarios/${id}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'ok') {
                        showStatus('Usuário excluído com sucesso!', true);
                        carregarUsuarios();
                    } else {
                        showStatus('Erro: ' + result.detalhes, false);
                    }
                } catch (error) {
                    showStatus('Erro de conexão: ' + error.message, false);
                }
            }
        }

        // Adicionar setor
        async function adicionarSetor() {
            const novoSetor = document.getElementById('novoSetor').value.trim();
            const descricaoSetor = document.getElementById('descricaoSetor').value.trim();
            
            if (!novoSetor) {
                showStatus('Digite o nome do setor!', false);
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/admin/setores`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        nome: novoSetor,
                        descricao: descricaoSetor 
                    })
                });
                
                const result = await response.json();
                
                if (result.status === 'ok') {
                    showStatus('Setor adicionado com sucesso!', true);
                    document.getElementById('novoSetor').value = '';
                    document.getElementById('descricaoSetor').value = '';
                    carregarSetores();
                } else {
                    showStatus('Erro: ' + result.detalhes, false);
                }
            } catch (error) {
                showStatus('Erro de conexão: ' + error.message, false);
            }
        }

        // Excluir setor
        async function excluirSetor(nomeSetor) {
            if (confirm(`Tem certeza que deseja excluir o setor "${nomeSetor}"?`)) {
                try {
                    const response = await fetch(`${API_BASE}/admin/setores/${encodeURIComponent(nomeSetor)}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'ok') {
                        showStatus('Setor excluído com sucesso!', true);
                        carregarSetores();
                    } else {
                        showStatus('Erro: ' + result.detalhes, false);
                    }
                } catch (error) {
                    showStatus('Erro de conexão: ' + error.message, false);
                }
            }
        }

        // Mostrar status
        function showStatus(message, isSuccess) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = isSuccess ? 'success' : 'error';
            status.style.display = 'block';
            setTimeout(() => {
                status.style.display = 'none';
            }, 5000);
        }

        // Inicializar
        document.addEventListener('DOMContentLoaded', function() {
            carregarUsuarios();
            carregarSetores();
        });
    </script>
</body>
</html>