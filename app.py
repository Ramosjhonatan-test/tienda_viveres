import eventlet
eventlet.monkey_patch()

import os
import time
from flask import Flask, request, render_template, session
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from extensions import mail
from database import db
from models.usuario import Usuario
from models.carrito import Carrito
from models.direccion import Direccion
from models.producto import Producto
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Controladores
from controllers import usuario_controller
from controllers.admin_controller import admin_bp
from controllers.cliente_controller import cliente_bp
from controllers.producto_controller import producto_bp
from controllers.categoria_controller import categoria_bp
from controllers.proveedor_controller import proveedor_bp
from controllers.carrito_controller import carrito_bp
from controllers.pedido_controller import pedido_bp
from controllers.detalle_pedido_controller import detalle_pedido_bp
from controllers.mensaje_controller import mensaje_bp
from views.contacto_view import contacto_view
from controllers.admin_pedido_controller import admin_pedido_bp
from controllers.test_mail_controller import test_mail_bp
from controllers.dashboard_controller import dashboard_bp

basedir = os.path.abspath(os.path.dirname(__file__))

# Establecer zona horaria a Bolivia
la_paz = pytz.timezone('America/La_Paz')
ahora = datetime.now(la_paz)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecreto_dev")

# 👉 Configuración de Base de Datos (usando .env)
database_url = os.getenv("DATABASE_URL")

if database_url:
    # Fix for Render (postgres:// -> postgresql://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"{database_url}?client_encoding=utf8"
else:
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "tienda_viveres")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?client_encoding=utf8"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

# Inicialización
mail.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins="*")

# Blueprints
app.register_blueprint(usuario_controller.usuario_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(producto_bp)
app.register_blueprint(categoria_bp)
app.register_blueprint(proveedor_bp)
app.register_blueprint(carrito_bp)
app.register_blueprint(pedido_bp)
app.register_blueprint(detalle_pedido_bp)
app.register_blueprint(contacto_view)
app.register_blueprint(admin_pedido_bp)
app.register_blueprint(test_mail_bp)
app.register_blueprint(mensaje_bp)
app.register_blueprint(dashboard_bp)

# Plantillas
@app.context_processor
def inject_active_path():
    def is_active(path):
        return 'active' if request.path == path else ''
    return dict(is_active=is_active)

@app.context_processor
def cantidad_carrito():
    def contar_productos():
        if session.get('rol') == 'cliente' and session.get('id'):
            items = Carrito.query.filter_by(usuario_id=session['id']).all()
            return len(items)
        return 0
    return dict(cantidad_en_carrito=contar_productos())

@app.route("/")
def home():
    productos = Producto.query.order_by(Producto.id.desc()).all()
    return render_template("index.html", productos=productos)

# Eventos de SocketIO para tiempo real
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado al socket')

@socketio.on('notificacion_admin')
def handle_notification(data):
    emit('mostrar_alerta', data, broadcast=True)

# Variable para que Vercel encuentre la app
app_vercel = app

# Ejecución local
if __name__ == "__main__":
    with app.app_context():
        # db.create_all() # Ya migraste a Render, no es necesario crear todo de nuevo
        pass

    socketio.run(app, debug=True)
