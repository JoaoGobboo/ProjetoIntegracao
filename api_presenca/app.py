from flask import Flask, request, jsonify
import mysql.connector
import os
import redis
import json
import datetime  # Adicionando importação para datetime

app = Flask(__name__)

# Conexão com o Redis
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

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

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('INSERT INTO presencas (alunoID, data, presente) VALUES (%s, %s, %s)', 
                       (aluno_id, data, presente))

        conn.commit()
        cursor.close()
        conn.close()

        # Limpar cache de presenças do aluno
        redis_client.delete(f"presencas:{aluno_id}")

        return jsonify({"message": "Presença registrada com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/presenca/aluno/<int:aluno_id>', methods=['GET'])
def listar_presencas(aluno_id):
    try:
        cache_key = f"presencas:{aluno_id}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            print('Dados vindos do cache')
            return jsonify(json.loads(cached_data)), 200

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM presencas WHERE alunoID = %s', (aluno_id,))
        presencas = cursor.fetchall()

        cursor.close()
        conn.close()

        # Converter datas para string (ISO 8601)
        for presenca in presencas:
            if isinstance(presenca['data'], (datetime.date, datetime.datetime)):
                presenca['data'] = presenca['data'].isoformat()

        # Armazena no Redis com expiração de 60 segundos
        redis_client.setex(cache_key, 60, json.dumps(presencas))

        print('Dados vindos do banco')
        return jsonify(presencas), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
