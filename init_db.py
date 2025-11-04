# init_db.py
import sqlite3
import os
from dotenv import load_dotenv

# Carrega o .env para saber o nome do arquivo do banco
load_dotenv()
DB_FILENAME = os.getenv('DB_FILENAME')
SQL_SCRIPT_FILE = 'saep_db.sql'

def initialize_database():
    """
    Cria e popula o banco de dados SQLite a partir do script SQL.
    """
    # Verifica se o banco já existe. Se sim, não faz nada.
    if os.path.exists(DB_FILENAME):
        print(f"O banco de dados '{DB_FILENAME}' já existe. Nenhuma ação foi tomada.")
        return

    print(f"Criando o banco de dados '{DB_FILENAME}'...")
    
    # Lê o script SQL
    try:
        with open(SQL_SCRIPT_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{SQL_SCRIPT_FILE}' não encontrado.")
        return

    # Conecta ao banco (isso cria o arquivo) e executa o script
    try:
        conn = sqlite3.connect(DB_FILENAME)
        cursor = conn.cursor()
        cursor.executescript(sql_script) # 'executescript' roda múltiplos comandos
        conn.commit()
        print("Banco de dados criado e populado com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao executar o script SQL: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    initialize_database()