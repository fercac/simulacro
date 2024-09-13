from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from random import sample
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://db_proyecto_9jbb_user:WsO37mgJvqXHCIZvRLtGb7fvLuZ0DihR@dpg-crgfo7aj1k6c739hkqr0-a/db_proyecto_9jbb'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Tabla A
class TablaA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pregunta = db.Column(db.String(200), nullable=False)
    respuesta = db.Column(db.String(200), nullable=False)
    tema = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.String(50), nullable=False)

# Tabla B
class TablaB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campo1 = db.Column(db.String(100), nullable=True)
    campo2 = db.Column(db.String(100), nullable=True)
    campo3 = db.Column(db.String(100), nullable=True)
    campo4 = db.Column(db.String(100), nullable=True)
    campo5 = db.Column(db.String(100), nullable=True)
    campo6 = db.Column(db.String(100), nullable=True)
    campo7 = db.Column(db.String(100), nullable=True)
    campo8 = db.Column(db.String(100), nullable=True)
    campo9 = db.Column(db.String(100), nullable=True)
    campo10 = db.Column(db.String(100), nullable=True)

# API para generar un nuevo ID en la Tabla B
@app.route("/generate_id", methods=["POST"])
def generate_id():
    new_instance = TablaB()  # Se crea una nueva instancia de TablaB
    db.session.add(new_instance)  # Se agrega a la sesión de la base de datos
    db.session.commit()  # Se confirman los cambios para obtener un ID
    return jsonify({"id": new_instance.id}), 201

# API para actualizar un campo en la Tabla B
@app.route("/update_field", methods=["POST"])
def update_field():
    data = request.get_json()
    id_b = data["id"]
    campo = data["campo"]
    contenido = data["contenido"]

    entry = TablaB.query.get(id_b)
    if not entry:
        return jsonify({"error": "ID no encontrado"}), 404

    setattr(entry, campo, contenido)  # Se actualiza el campo especificado
    db.session.commit()

    return jsonify({"message": f"Campo {campo} actualizado correctamente en el ID {id_b}"}), 200

# API para guardar en la Tabla A
@app.route("/save_question", methods=["POST"])
def save_question():
    data = request.get_json()
    pregunta = data["pregunta"]
    respuesta = data["respuesta"]
    tema = data["tema"]
    nivel = data["nivel"]

    new_question = TablaA(pregunta=pregunta, respuesta=respuesta, tema=tema, nivel=nivel)
    db.session.add(new_question)
    db.session.commit()

    return jsonify({"message": "Pregunta guardada correctamente", "id": new_question.id}), 201

@app.route("/update_question", methods=["POST"])
def update_question():
    data = request.get_json()
    id = data["id"]
    pregunta = data["pregunta"]
    respuesta = data["respuesta"]
    tema = data["tema"]
    nivel = data["nivel"]

    # Buscar la entrada en la base de datos
    entry = TablaA.query.get(id)
    if not entry:
        return jsonify({"error": "ID no encontrado"}), 404

    # Actualizar los campos individualmente
    entry.pregunta = pregunta
    entry.respuesta = respuesta
    entry.tema = tema
    entry.nivel = nivel

    # Guardar los cambios en la base de datos
    db.session.commit()

    return jsonify({"message": f"Pregunta actualizada correctamente en el ID {id}"}), 200


# API para seleccionar aleatoriamente 10 IDs de la Tabla A y retornar preguntas
@app.route("/random_questions", methods=["GET"])
def random_questions():
    total_questions = TablaA.query.count()
    if total_questions < 10:
        return jsonify({"error": "No hay suficientes preguntas en la base de datos"}), 400

    random_ids = sample([q.id for q in TablaA.query.all()], 10)  # Seleccionar 10 IDs aleatoriamente
    selected_questions = TablaA.query.filter(TablaA.id.in_(random_ids)).all()

    response = [{"id": q.id, "pregunta": q.pregunta} for q in selected_questions]
    return jsonify(response), 200

# API para comparar respuestas de la Tabla A y Tabla B
@app.route("/compare_answers", methods=["POST"])
def compare_answers():
    data = request.get_json()
    id_b = data["id_b"]
    random_ids = data["random_ids"]

    # Obtener las respuestas del usuario de TablaB
    user_responses = TablaB.query.get(id_b)
    if not user_responses:
        return jsonify({"error": "ID de Tabla B no encontrado"}), 404

    user_answers = [
        user_responses.campo1, user_responses.campo2, user_responses.campo3, 
        user_responses.campo4, user_responses.campo5, user_responses.campo6, 
        user_responses.campo7, user_responses.campo8, user_responses.campo9, 
        user_responses.campo10
    ]

    # Obtener las respuestas correctas de TablaA para los IDs aleatorios
    correct_answers = []
    for id_a in random_ids:
        question = TablaA.query.get(id_a)
        if question:
            correct_answers.append(question.respuesta)

    # Comparar respuestas y contar cuántas coinciden
    correct_count = sum([1 for ua, ca in zip(user_answers, correct_answers) if ua == ca])

    return jsonify({"correctas": correct_count}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear tablas en la base de datos
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port, debug=False) 
