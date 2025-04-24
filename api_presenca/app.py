from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

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

        return jsonify({"message": "Presença registrada com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/presenca/aluno/<int:aluno_id>', methods=['GET'])
def listar_presencas(aluno_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM presencas WHERE alunoID = %s', (aluno_id,))
        presencas = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(presencas), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
