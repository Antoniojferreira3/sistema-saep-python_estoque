/*
 * ARQUIVO SQL PARA SQLITE (Versão Ferramentas)
 * Sistema: Sistema de Gestão de Estoque - SAEP
 * Este script cria as tabelas e insere dados iniciais para o controle de ferramentas.
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
-- ===========================================

-- Categorias (Ignora se já existirem)
INSERT OR IGNORE INTO categoria (nome) VALUES
('Martelos'),
('Chaves de Fenda'),
('Alicates'),
('Trenas'),
('Chaves Inglesas');

-- Usuários (Ignora se já existirem)
-- Hashes de senha são placeholders e devem ser ajustados conforme seu sistema
INSERT OR IGNORE INTO usuario (nome, login, senha_hash, cargo) VALUES
('Admin Almoxarifado', 'admin', '$2b$12$fobHyskDH/ASfL6TVTk/betdXre.OjLsuG7vCNRo5tmxN4YViNp82', 'Administrador'),
('Joao Silva', 'joao.silva', '$2b$10$hijklmnop...', 'Almoxarife'),
('Maria Souza', 'maria.souza', '$2b$10$qrstuvwxyz...', 'Almoxarife');

-- Produtos (Ignora se já existirem)
INSERT OR IGNORE INTO produto (nome, descricao, quantidade_em_estoque, estoque_minimo, localizacao, fk_id_categoria) VALUES
('Martelo de Unha 27mm', 'Cabo de madeira, cabeça de aço forjado, 500g', 15, 5, 'Prateleira A-01', 1),
('Chave de Fenda Phillips 6"', 'Cabo emborrachado, ponta magnética', 30, 10, 'Prateleira B-03', 2),
('Alicate Universal 8"', 'Revestimento isolante até 1000V, aço carbono', 20, 5, 'Prateleira C-05', 3),
('Trena 5m', 'Trava automática, fita de aço com revestimento antiferrugem', 25, 8, 'Prateleira D-02', 4),
('Chave Inglesa 12"', 'Ajuste rápido, aço cromo-vanádio', 12, 4, 'Prateleira E-01', 5);

-- Movimentos (Ignora se já existirem)
INSERT OR IGNORE INTO movimento (tipo_movimento, quantidade, data_hora, fk_id_produto, fk_id_usuario) VALUES
('entrada', 15, '2025-11-01T09:15:00', 1, 1),
('entrada', 30, '2025-11-02T10:30:00', 2, 2),
('saida', 3, '2025-11-03T14:00:00', 1, 3),
('entrada', 25, '2025-11-04T09:50:00', 4, 1),
('saida', 2, '2025-11-05T15:20:00', 5, 2);
