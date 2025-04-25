from flask import Flask, request, jsonify
import mysql.connector
import os
import redis
import json
import datetime
import logging

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

@app.route('/presenca/aluno/<int:aluno_id>', methods=['POST'])
def registrar_presenca_por_aluno(aluno_id):
    try:
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

@app.route('/presenca/aluno/<int:aluno_id>', methods=['PUT'])
def editar_presenca(aluno_id):
    try:
        data_original = request.json['data_original']
        data_nova = request.json.get('data_nova', data_original)
        presente = request.json.get('presente')

        logger.info(f"Editando presença para aluno {aluno_id} na data {data_original}")
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se o registro existe
        cursor.execute('SELECT COUNT(*) FROM presencas WHERE alunoID = %s AND data = %s', 
                       (aluno_id, data_original))
        if cursor.fetchone()[0] == 0:
            logger.error(f"Registro de presença não encontrado para aluno {aluno_id} na data {data_original}")
            return jsonify({"error": "Registro de presença não encontrado"}), 404

        # Montar a query de atualização
        update_fields = []
        update_values = []
        if data_nova != data_original:
            update_fields.append("data = %s")
            update_values.append(data_nova)
        if presente is not None:
            update_fields.append("presente = %s")
            update_values.append(presente)

        if not update_fields:
            logger.info("Nenhum campo para atualizar")
            return jsonify({"message": "Nenhum campo para atualizar"}), 200

        update_query = f"UPDATE presencas SET {', '.join(update_fields)} WHERE alunoID = %s AND data = %s"
        update_values.extend([aluno_id, data_original])

        cursor.execute(update_query, update_values)
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Limpando cache para presencas:{aluno_id}")
        redis_client.delete(f"presencas:{aluno_id}")

        logger.info("Presença editada com sucesso")
        return jsonify({"message": "Presença editada com sucesso!"}), 200
    except Exception as e:
        logger.error(f"Erro ao editar presença: {str(e)}")
        return jsonify({"error": str(e)}), 400
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

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