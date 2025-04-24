Create databse escola;

-- Usar o banco de dados 'escola'
USE escola;

-- Criar a tabela 'turmas'
CREATE TABLE IF NOT EXISTS turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
);

-- Criar a tabela 'alunos'
CREATE TABLE IF NOT EXISTS alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    turmaID INT,
    FOREIGN KEY (turmaID) REFERENCES turmas(id)
);

-- Criar a tabela 'presencas'
CREATE TABLE IF NOT EXISTS presencas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alunoID INT,
    data DATE NOT NULL,
    presente BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (alunoID) REFERENCES alunos(id)
);

-- Inserir algumas turmas
INSERT INTO turmas (nome) VALUES ('Turma A');
INSERT INTO turmas (nome) VALUES ('Turma B');
INSERT INTO turmas (nome) VALUES ('Turma C');

-- Inserir alguns alunos
INSERT INTO alunos (name, turmaID) VALUES ('João Silva', 1);
INSERT INTO alunos (name, turmaID) VALUES ('Ana Souza', 1);
INSERT INTO alunos (name, turmaID) VALUES ('Carlos Pereira', 1);
INSERT INTO alunos (name, turmaID) VALUES ('Maria Oliveira', 1);
INSERT INTO alunos (name, turmaID) VALUES ('Pedro Costa', 1);

INSERT INTO alunos (name, turmaID) VALUES ('Juliana Lima', 2);
INSERT INTO alunos (name, turmaID) VALUES ('Felipe Santos', 2);
INSERT INTO alunos (name, turmaID) VALUES ('Rafaela Barbosa', 2);
INSERT INTO alunos (name, turmaID) VALUES ('Bruno Almeida', 2);

INSERT INTO alunos (name, turmaID) VALUES ('Lucas Rocha', 3);
INSERT INTO alunos (name, turmaID) VALUES ('Mariana Pereira', 3);
INSERT INTO alunos (name, turmaID) VALUES ('Gabriel Martins', 3);
INSERT INTO alunos (name, turmaID) VALUES ('Isabela Fernandes', 3);
INSERT INTO alunos (name, turmaID) VALUES ('Ricardo Silva', 3);