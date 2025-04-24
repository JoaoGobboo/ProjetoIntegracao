const express = require('express');
const axios = require('axios');

const app = express();
const PORT = 4000;

app.use(express.json());

// Configs para acessar outras APIs
const API_TURMA = process.env.API_TURMA || 'http://api_turma:3000';
const API_PRESENCA = process.env.API_PRESENCA || 'http://api_presenca:5000';

// POST /chamada
app.post('/chamada', async (req, res) => {
  const { turmaID, data } = req.body;

  try {
    // Buscar alunos da turma
    const alunosResponse = await axios.get(`${API_TURMA}/turmas/${turmaID}/alunos`);
    const alunos = alunosResponse.data;

    // Criar presenças para cada aluno
    const resultados = await Promise.all(alunos.map(aluno => {
      return axios.post(`${API_PRESENCA}/presenca`, {
        alunoID: aluno.id,
        data: data,
        presente: true
      });
    }));

    res.status(201).json({ message: 'Chamada registrada', detalhes: resultados.length });

  } catch (err) {
    console.error(err.message);
    res.status(500).json({ error: 'Erro ao registrar chamada' });
  }
});

// GET /presencas/aluno/:id
app.get('/presencas/aluno/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const response = await axios.get(`${API_PRESENCA}/presenca/aluno/${id}`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Erro ao buscar presenças do aluno' });
  }
});

// GET /presencas/turma/:id
app.get('/presencas/turma/:id', async (req, res) => {
  const turmaID = req.params.id;
  try {
    const alunosResponse = await axios.get(`${API_TURMA}/turmas/${turmaID}/alunos`);
    const alunos = alunosResponse.data;

    const presencasPorAluno = await Promise.all(alunos.map(async aluno => {
      const presencas = await axios.get(`${API_PRESENCA}/presenca/aluno/${aluno.id}`);
      return {
        aluno: aluno.name,
        presencas: presencas.data
      };
    }));

    res.json(presencasPorAluno);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ error: 'Erro ao buscar presenças da turma' });
  }
});

app.listen(PORT, () => {
  console.log(`api_chamada rodando em http://localhost:${PORT}`);
});
