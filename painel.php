<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Painel de Mensagens - RH</title>
    <style>
        body { font-family: Arial, sans-serif; }
        #usuarios { margin-top: 20px; }
        .usuario { padding: 5px; border-bottom: 1px solid #ccc; }
    </style>
</head>
<body>
    <h2>Painel de Mensagens Interna</h2>

    <form id="formMensagem">
        <label for="mensagem">Mensagem:</label><br>
        <textarea name="mensagem" id="mensagem" rows="4" cols="50" required></textarea><br><br>
        <button type="submit">Enviar para todos</button>
    </form>

    <div id="usuarios">
        <h3>Usuários online:</h3>
        <ul id="listaUsuarios"></ul>
    </div>

    <p id="status"></p>

    <script>
        const listaUsuarios = document.getElementById('listaUsuarios');
        const form = document.getElementById('formMensagem');
        const status = document.getElementById('status');

        // Função para buscar usuários online
        async function atualizarUsuarios() {
            try {
                const res = await fetch('http://10.11.0.144:8081/usuarios'); // IP do servidor Python
                const usuarios = await res.json();

                listaUsuarios.innerHTML = '';
                usuarios.forEach(u => {
                    const li = document.createElement('li');
                    li.textContent = u;
                    li.className = 'usuario';
                    listaUsuarios.appendChild(li);
                });
            } catch (e) {
                listaUsuarios.innerHTML = '<li>Erro ao carregar usuários.</li>';
            }
        }

        // Atualiza a lista a cada 3 segundos
        setInterval(atualizarUsuarios, 3000);
        atualizarUsuarios(); // primeira chamada imediata

        // Enviar mensagem pelo painel
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = document.getElementById('mensagem').value;
            try {
                // Envia mensagem via servidor Python
                await fetch('http://10.11.0.144:8081/enviar', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensagem: msg })
                });
                status.textContent = 'Mensagem enviada!';
                document.getElementById('mensagem').value = '';
            } catch (err) {
                status.textContent = 'Erro ao enviar a mensagem.';
            }
        });
    </script>
</body>
</html>
