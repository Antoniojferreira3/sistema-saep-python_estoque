/*
 * ARQUIVO SQL PARA SQLITE (Entrega 3)
 * Este script cria as tabelas e insere os dados iniciais.
 */

-- ===========================================
-- 1. Criação das Tabelas (na ordem correta)
-- ===========================================

-- Tabela: categoria
CREATE TABLE IF NOT EXISTS categoria (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

-- Tabela: usuario
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    cargo TEXT
);

-- Tabela: produto
CREATE TABLE IF NOT EXISTS produto (
    id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NULL,
    quantidade_em_estoque INTEGER NOT NULL DEFAULT 0,
    estoque_minimo INTEGER NOT NULL DEFAULT 0,
    localizacao TEXT,
    fk_id_categoria INTEGER NOT NULL,
    FOREIGN KEY (fk_id_categoria)
        REFERENCES categoria(id_categoria)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Tabela: movimento
CREATE TABLE IF NOT EXISTS movimento (
    id_movimento INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_movimento TEXT NOT NULL, -- 'entrada' ou 'saida'
    quantidade INTEGER NOT NULL,
    data_hora TEXT NOT NULL, -- SQLite armazena DATETIME como TEXT
    fk_id_produto INTEGER NOT NULL,
    fk_id_usuario INTEGER NOT NULL,
    FOREIGN KEY (fk_id_produto)
        REFERENCES produto(id_produto)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (fk_id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ===========================================
-- 2. Inserção de Dados Iniciais
-- (Os 'GO' foram removidos)
-- ===========================================

-- Categorias (Ignora se já existirem)
INSERT OR IGNORE INTO categoria (nome) VALUES
('Notebooks'),
('Smartphones'),
('Smart TVs');

-- Usuários (Ignora se já existirem)
-- Seu hash bcrypt correto já está aqui
INSERT OR IGNORE INTO usuario (nome, login, senha_hash, cargo) VALUES
('Admin Almoxarifado', 'admin', '$2b$12$fobHyskDH/ASfL6TVTk/betdXre.OjLsuG7vCNRo5tmxN4YViNp82', 'Administrador'),
('Joao Silva', 'joao.silva', '$2b$10$hijklmnop...', 'Almoxarife'),
('Maria Souza', 'maria.souza', '$2b$10$qrstuvwxyz...', 'Almoxarife');

-- Produtos (Ignora se já existirem)
INSERT OR IGNORE INTO produto (nome, descricao, quantidade_em_estoque, estoque_minimo, localizacao, fk_id_categoria) VALUES
('Notebook Gamer XPTO', '16GB RAM, SSD 512GB, Tela 15.6", 110v', 10, 5, 'Prateleira A-01', 1),
('Smartphone TopModel', '128GB, 8GB RAM, Tela 6.5", Bivolt', 25, 10, 'Prateleira B-03', 2),
('Smart TV 50" 4K', '50 polegadas, 4K UHD, Tizen OS, Bivolt', 8, 3, 'Prateleira C-05', 3);

-- Movimentos (Ignora se já existirem)
-- O formato de data T (ISO8601) é perfeito para o SQLite
INSERT OR IGNORE INTO movimento (tipo_movimento, quantidade, data_hora, fk_id_produto, fk_id_usuario) VALUES
('entrada', 10, '2025-10-20T09:15:00', 1, 1),
('entrada', 25, '2025-10-21T10:30:00', 2, 2),
('saida', 2, '2025-10-22T14:00:00', 1, 3);