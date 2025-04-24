const express = require('express');
const mysql = require('mysql2/promise');
const redis = require('redis');

const app = express();
const PORT = 3000;

// Config Redis
const redisClient = redis.createClient({ url: 'redis://redis:6379' });
redisClient.connect().then(() => {
  console.log('Conectado ao Redis');
}).catch(console.error);

// Config DB
const dbConfig = {
  host: process.env.DB_HOST || 'mysql_db',
  port: process.env.DB_PORT || 3306,
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASS || 'root',
  database: process.env.DB_NAME || 'escola'
};

app.get('/turmas/:id/alunos', async (req, res) => {
  const turmaID = req.params.id;
  const cacheKey = `turma:${turmaID}:alunos`;

  try {
    // 1. Verifica se está em cache
    const cached = await redisClient.get(cacheKey);
    if (cached) {
      console.log('Dados vindos do cache');
      return res.json(JSON.parse(cached));
    }

    // 2. Se não, busca no banco
    const connection = await mysql.createConnection(dbConfig);
    const [rows] = await connection.execute(
      'SELECT * FROM alunos WHERE turmaID = ?',
      [turmaID]
    );
    await connection.end();

    // 3. Armazena no Redis (com tempo de expiração de 60 segundos)
    await redisClient.set(cacheKey, JSON.stringify(rows), { EX: 60 });

    console.log('Dados vindos do banco');
    res.json(rows);
  } catch (err) {
    console.error('Erro ao buscar alunos:', err.message);
    res.status(500).json({ erro: 'Erro ao buscar alunos da turma' });
  }
});

app.listen(PORT, () => {
  console.log(`api_turma rodando em http://localhost:${PORT}`);
});
