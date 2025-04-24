from flask import Flask, request, jsonify
import mysql.connector
import os
import redis
import json
import datetime
import logging  # Importando o módulo logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Conexão com o Redis
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# Testar conexão com Redis
try:
    logger.info(f"Conexão com Redis: {redis_client.ping()}")
except Exception as e:
    logger.error(f"Erro ao conectar ao Redis: {str(e)}")

# Conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', 'root'),
        database=os.getenv('DB_NAME', 'escola')
    )

@app.route('/presenca', methods=['POST'])
def registrar_presenca():
    try:
        aluno_id = request.json['alunoID']
        data = request.json['data']
        presente = request.json['presente']

        logger.info(f"Registrando presença para aluno {aluno_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('INSERT INTO presencas (alunoID, data, presente) VALUES (%s, %s, %s)', 
                       (aluno_id, data, presente))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Limpando cache para presencas:{aluno_id}")
        redis_client.delete(f"presencas:{aluno_id}")

        logger.info("Presença registrada com sucesso")
        return jsonify({"message": "Presença registrada com sucesso!"}), 201
    except Exception as e:
        logger.error(f"Erro ao registrar presença: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/presenca/aluno/<int:aluno_id>', methods=['GET'])
def listar_presencas(aluno_id):
    try:
        cache_key = f"presencas:{aluno_id}"
        logger.info(f"Verificando cache para aluno {aluno_id}")
        cached_data = redis_client.get(cache_key)

        if cached_data:
            logger.info("Dados vindos do cache")
            return jsonify(json.loads(cached_data)), 200

        logger.info("Consultando banco de dados")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM presencas WHERE alunoID = %s', (aluno_id,))
        presencas = cursor.fetchall()

        cursor.close()
        conn.close()

        for presenca in presencas:
            if isinstance(presenca['data'], (datetime.date, datetime.datetime)):
                presenca['data'] = presenca['data'].isoformat()

        logger.info("Armazenando dados no cache")
        redis_client.setex(cache_key, 60, json.dumps(presencas))

        logger.info("Dados vindos do banco")
        return jsonify(presencas), 200
    except Exception as e:
        logger.error(f"Erro ao buscar presenças: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)