const express = require('express');
const mysql = require('mysql2/promise');
const app = express();
const PORT = 3000;

// Configuração do banco de dados usando variáveis de ambiente
const dbConfig = {
  host: process.env.DB_HOST || 'mysql_db',    // Nome do serviço no docker-compose
  port: process.env.DB_PORT || 3306,
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASS || 'root',
  database: process.env.DB_NAME || 'escola'
};

app.get('/turmas/:id/alunos', async (req, res) => {
  const turmaID = req.params.id;

  try {
    const connection = await mysql.createConnection(dbConfig);
    const [rows] = await connection.execute(
      'SELECT * FROM alunos WHERE turmaID = ?',
      [turmaID]
    );
    await connection.end();

    res.json(rows);
  } catch (err) {
    console.error('Erro ao buscar alunos:', err.message);
    res.status(500).json({ erro: 'Erro ao buscar alunos da turma' });
  }
});

app.listen(PORT, () => {
  console.log(`api_turma rodando em http://localhost:${PORT}`);
});
