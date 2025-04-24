const express = require('express');
const axios = require('axios');
const redis = require('redis');

const app = express();
const PORT = 4000;

app.use(express.json());

// Configs para acessar outras APIs
const API_TURMA = process.env.API_TURMA || 'http://api_turma:3000';
const API_PRESENCA = process.env.API_PRESENCA || 'http://api_presenca:5000';

// Conexão com Redis
const redisClient = redis.createClient({ url: 'redis://redis:6379' });

redisClient.connect()
  .then(() => console.log('Conectado ao Redis'))
  .catch(err => console.error('Erro ao conectar ao Redis:', err));

// POST /chamada
app.post('/chamada', async (req, res) => {
  const { turmaID, data } = req.body;

  try {
    console.log(`Registrando chamada para turma ${turmaID} na data ${data}`);
    const alunosResponse = await axios.get(`${API_TURMA}/turmas/${turmaID}/alunos`);
    const alunos = alunosResponse.data;
    console.log(`Alunos obtidos da api_turma: ${alunos.length}`);

    const resultados = await Promise.all(alunos.map(async aluno => {
      console.log(`Limpando cache para presencas:${aluno.id}`);
      await redisClient.del(`presencas:${aluno.id}`);
      console.log(`Registrando presença para aluno ${aluno.id} via api_presenca`);
      return axios.post(`${API_PRESENCA}/presenca`, {
        alunoID: aluno.id,
        data,
        presente: true
      });
    }));

    console.log(`Chamada registrada para ${resultados.length} alunos`);
    res.status(201).json({ message: 'Chamada registrada', detalhes: resultados.length });
  } catch (err) {
    console.error(`Erro ao registrar chamada: ${err.message}`);
    res.status(500).json({ error: 'Erro ao registrar chamada' });
  }
});

// GET /presencas/aluno/:id com cache
app.get('/presencas/aluno/:id', async (req, res) => {
  const alunoID = req.params.id;
  const cacheKey = `presencas:${alunoID}`;

  try {
    console.log(`Verificando cache para presencas:${alunoID}`);
    const cached = await redisClient.get(cacheKey);

    if (cached) {
      console.log('Dados vindos do cache');
      return res.json(JSON.parse(cached));
    }

    console.log('Consultando api_presenca');
    const response = await axios.get(`${API_PRESENCA}/presenca/aluno/${alunoID}`);
    const dados = response.data;

    console.log('Armazenando dados no cache');
    await redisClient.setEx(cacheKey, 60, JSON.stringify(dados));

    console.log('Dados vindos da api_presenca');
    res.json(dados);
  } catch (err) {
    console.error(`Erro ao buscar presenças do aluno ${alunoID}: ${err.message}`);
    res.status(500).json({ error: 'Erro ao buscar presenças do aluno' });
  }
});

// GET /presencas/turma/:id (sem cache por enquanto)
app.get('/presencas/turma/:id', async (req, res) => {
  const turmaID = req.params.id;
  try {
    console.log(`Buscando presenças para turma ${turmaID}`);
    const alunosResponse = await axios.get(`${API_TURMA}/turmas/${turmaID}/alunos`);
    const alunos = alunosResponse.data;
    console.log(`Alunos obtidos da api_turma: ${alunos.length}`);

    const presencasPorAluno = await Promise.all(alunos.map(async aluno => {
      console.log(`Buscando presenças para aluno ${aluno.id} via api_presenca`);
      const presencas = await axios.get(`${API_PRESENCA}/presenca/aluno/${aluno.id}`);
      return {
        aluno: aluno.name,
        presencas: presencas.data
      };
    }));

    console.log('Presenças da turma obtidas');
    res.json(presencasPorAluno);
  } catch (err) {
    console.error(`Erro ao buscar presenças da turma ${turmaID}: ${err.message}`);
    res.status(500).json({ error: 'Erro ao buscar presenças da turma' });
  }
});

app.listen(PORT, () => {
  console.log(`api_chamada rodando em http://localhost:${PORT}`);
});