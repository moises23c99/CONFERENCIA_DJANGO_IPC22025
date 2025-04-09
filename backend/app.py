from flask import Flask
from flask_cors import CORS
from routes import api

app = Flask(__name__)
CORS(app)  # Habilita CORS para evitar problemas con el frontend

app.register_blueprint(api)  # Importa las rutas desde routes.py

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Inicia el servidor en el puerto 5000
