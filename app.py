# app.py
import os
import sqlite3  # Trocado de pyodbc para sqlite3
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from functools import wraps

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# ==============================================================================
# 1. Configuração do App Flask e Banco de Dados
# ==============================================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

def get_db_conn():
    """Cria e retorna uma nova conexão com o banco de dados SQLite."""
    db_file = os.getenv('DB_FILENAME') # Pega o nome do .env (ex: saep_db2.db)
    try:
        conn = sqlite3.connect(db_file)
        # Isso faz com que possamos acessar colunas pelo nome (ex: user['nome'])
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
        return None

# ==============================================================================
# 2. Decorador de Autenticação
# ==============================================================================
def login_required(f):
    """Garante que o usuário esteja logado para acessar a rota."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==============================================================================
# 3. Rotas de Autenticação (Entregas 4 e 5)
# ==============================================================================

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """(ENTREGA 4) Rota de Login."""
    if request.method == 'POST':
        login = request.form['login']
        senha_form = request.form['senha']

        conn = get_db_conn()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'danger')
            return render_template('login.html')

        cursor = conn.cursor()
        try:
            # No SQLite, ? é o placeholder
            cursor.execute("SELECT id_usuario, nome, senha_hash FROM usuario WHERE login = ?", (login,))
            user = cursor.fetchone() # fetchone() já usa o row_factory

            # (ENTREGA 4 - Requisito: Mensagem clara)
            # user.senha_hash já vem como string, não precisamos decodificar
            if user and bcrypt.checkpw(senha_form.encode('utf-8'), user['senha_hash'].encode('utf-8')):
                # Login bem-sucedido
                session['user_id'] = user['id_usuario']
                session['user_name'] = user['nome']
                return redirect(url_for('principal'))
            else:
                # (ENTREGA 4 - Requisito: Redirecionar em caso de falha)
                flash('Login ou senha inválidos.', 'danger')
                return redirect(url_for('login'))
        
        except Exception as e:
            flash(f'Erro durante o login: {e}', 'danger')
            return redirect(url_for('login'))
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """(ENTREGA 5) Rota de Logout."""
    session.clear()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login'))

@app.route('/principal')
@login_required
def principal():
    """(ENTREGA 5) Rota da Interface Principal."""
    return render_template('principal.html')

# ==============================================================================
# 4. Rotas de Produtos (Entrega 6)
# ==============================================================================

@app.route('/produtos', methods=['GET'])
@login_required
def cadastro_produto():
    """(ENTREGA 6) Lista produtos e serve a página de cadastro."""
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # (ENTREGA 6 - Requisito: Campo de busca)
    busca = request.args.get('busca', '') # Pega o parâmetro 'busca' da URL
    
    # Lógica de busca
    if busca:
        query_produtos = """
            SELECT p.id_produto, p.nome, p.descricao, p.quantidade_em_estoque, p.estoque_minimo, p.localizacao, c.nome as nome_categoria, p.fk_id_categoria
            FROM produto p
            JOIN categoria c ON p.fk_id_categoria = c.id_categoria
            WHERE p.nome LIKE ? OR p.descricao LIKE ?
        """
        produtos = cursor.execute(query_produtos, (f'%{busca}%', f'%{busca}%')).fetchall()
    else:
        # (ENTREGA 6 - Requisito: Carregar dados do banco)
        query_produtos = """
            SELECT p.id_produto, p.nome, p.descricao, p.quantidade_em_estoque, p.estoque_minimo, p.localizacao, c.nome as nome_categoria, p.fk_id_categoria
            FROM produto p
            JOIN categoria c ON p.fk_id_categoria = c.id_categoria
        """
        produtos = cursor.execute(query_produtos).fetchall()

    # Busca categorias para o formulário
    query_categorias = "SELECT id_categoria, nome FROM categoria"
    categorias = cursor.execute(query_categorias).fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('cadastro_produto.html', produtos=produtos, categorias=categorias, busca=busca)


@app.route('/produtos/add', methods=['POST'])
@login_required
def add_produto():
    """(ENTREGA 6) Adiciona um novo produto."""
    if request.method == 'POST':
        # (ENTREGA 6 - Requisito: Validar campos)
        nome = request.form['nome']
        categoria = request.form['categoria']
        if not nome or not categoria:
            flash('Nome e Categoria são obrigatórios!', 'danger')
            return redirect(url_for('cadastro_produto'))

        descricao = request.form.get('descricao', '')
        estoque_minimo = request.form.get('estoque_minimo', 0)
        localizacao = request.form.get('localizacao', '')

        conn = get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO produto (nome, descricao, estoque_minimo, localizacao, fk_id_categoria)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, descricao, int(estoque_minimo), localizacao, int(categoria)))
            conn.commit()
            flash('Produto cadastrado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao cadastrar produto: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('cadastro_produto'))


@app.route('/produtos/edit/<int:id_produto>', methods=['POST'])
@login_required
def edit_produto(id_produto):
    """(ENTREGA 6) Edita um produto existente."""
    if request.method == 'POST':
        nome = request.form['nome']
        categoria = request.form['categoria']
        
        # (ENTREGA 6 - Requisito: Validar campos)
        if not nome or not categoria:
            flash('Nome e Categoria são obrigatórios!', 'danger')
            return redirect(url_for('cadastro_produto'))
        
        descricao = request.form.get('descricao', '')
        estoque_minimo = request.form.get('estoque_minimo', 0)
        localizacao = request.form.get('localizacao', '')

        conn = get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE produto 
                SET nome = ?, descricao = ?, estoque_minimo = ?, localizacao = ?, fk_id_categoria = ?
                WHERE id_produto = ?
            """, (nome, descricao, int(estoque_minimo), localizacao, int(categoria), id_produto))
            conn.commit()
            flash('Produto atualizado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar produto: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return redirect(url_for('cadastro_produto'))


@app.route('/produtos/delete/<int:id_produto>', methods=['POST'])
@login_required
def delete_produto(id_produto):
    """(ENTREGA 6) Exclui um produto."""
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        # ATENÇÃO: Se houver movimentos, o ON DELETE CASCADE no seu SQL irá apagar o histórico.
        cursor.execute("DELETE FROM produto WHERE id_produto = ?", (id_produto,))
        conn.commit()
        flash('Produto excluído com sucesso!', 'success')
    except sqlite3.IntegrityError: # Erro específico do SQLite para Foreign Key
        flash('Erro: Não é possível excluir um produto que possui histórico de movimentações (se ON DELETE RESTRICT estiver ativo).', 'danger')
    except Exception as e:
        flash(f'Erro ao excluir produto: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('cadastro_produto'))

# ==============================================================================
# 5. Rotas de Gestão de Estoque (Entrega 7)
# ==============================================================================

@app.route('/estoque', methods=['GET'])
@login_required
def gestao_estoque():
    """(ENTREGA 7) Lista produtos para gestão de estoque."""
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # (ENTREGA 7 - Requisito: Ordem alfabética)
    query = """
        SELECT id_produto, nome, quantidade_em_estoque, estoque_minimo 
        FROM produto 
        ORDER BY nome ASC
    """
    produtos = cursor.execute(query).fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('gestao_estoque.html', produtos=produtos)


@app.route('/estoque/movimentar', methods=['POST'])
@login_required
def movimentar_estoque():
    """(ENTREGA 7) Registra uma entrada ou saída."""
    
    # Estas variáveis precisam ser declaradas antes do try,
    # para que o 'finally' possa acessá-las
    conn = None
    cursor = None
    
    try:
        produto_id = int(request.form['produto_id'])
        tipo_movimento = request.form['tipo_movimento'] # 'entrada' ou 'saida'
        quantidade = int(request.form['quantidade'])
        user_id = session['user_id']
        
        if quantidade <= 0:
            flash('A quantidade deve ser positiva.', 'danger')
            return redirect(url_for('gestao_estoque'))

        conn = get_db_conn()
        cursor = conn.cursor()

        # 1. Pega o estado atual do produto
        cursor.execute("SELECT nome, quantidade_em_estoque, estoque_minimo FROM produto WHERE id_produto = ?", (produto_id,))
        produto = cursor.fetchone()
        if not produto:
            flash('Produto não encontrado.', 'danger')
            return redirect(url_for('gestao_estoque'))

        # 2. Verifica se a saída é válida
        if tipo_movimento == 'saida':
            if produto['quantidade_em_estoque'] < quantidade:
                flash(f'Erro: Estoque insuficiente para "{produto["nome"]}". Disponível: {produto["quantidade_em_estoque"]}', 'danger')
                return redirect(url_for('gestao_estoque'))
            
            nova_quantidade = produto['quantidade_em_estoque'] - quantidade
        else: # 'entrada'
            nova_quantidade = produto['quantidade_em_estoque'] + quantidade
        
        # 3. Inicia uma transação para garantir consistência
        # No SQLite, a transação começa automaticamente em comandos DML (INSERT/UPDATE)
        # conn.autocommit = False (Não é necessário como no pyodbc)
        
        # 4. Atualiza o estoque do produto
        cursor.execute("UPDATE produto SET quantidade_em_estoque = ? WHERE id_produto = ?", (nova_quantidade, produto_id))
        
        # 5. Registra a movimentação (com data do SQLite)
        cursor.execute("""
            INSERT INTO movimento (tipo_movimento, quantidade, data_hora, fk_id_produto, fk_id_usuario)
            VALUES (?, ?, DATETIME('now', 'localtime'), ?, ?)
        """, (tipo_movimento, quantidade, produto_id, user_id))
        
        # 6. Salva as mudanças
        conn.commit()
        
        flash('Movimentação registrada com sucesso!', 'success')

        # 7. (ENTREGA 7 - Requisito: Alerta de estoque mínimo)
        if nova_quantidade < produto['estoque_minimo']:
            flash(f'Atenção: O produto "{produto["nome"]}" está abaixo do estoque mínimo! (Qtd: {nova_quantidade}, Mín: {produto["estoque_minimo"]})', 'warning')

    # ESTA É A INDENTAÇÃO CORRETA
    except Exception as e:
        if conn:
            conn.rollback() # Desfaz a transação em caso de erro
        flash(f'Erro ao registrar movimentação: {e}', 'danger')
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('gestao_estoque'))


@app.route('/historico')
def historico_movimentacoes():
    import sqlite3

    conexao = sqlite3.connect('saep_db.db')
    cursor = conexao.cursor()

    cursor.execute('''
        SELECT h.id, p.nome, h.tipo_movimentacao, h.quantidade, 
               h.responsavel, h.data_movimentacao
        FROM historico_movimentacao h
        JOIN produto p ON p.id_produto = h.id_produto
        ORDER BY h.data_movimentacao DESC
    ''')
    historico = cursor.fetchall()
    conexao.close()

    return render_template('historico.html', historico=historico)



# ==============================================================================
# 6. Inicialização do Servidor
# ==============================================================================
if __name__ == '__main__':
    # Antes de rodar, garante que o banco de dados exista
    # Importamos aqui para evitar circularidade
    from init_db import initialize_database
    initialize_database()
    
    app.run(debug=True, port=5000) # debug=True ajuda no desenvolvimento