import os
import time
from flask import Flask, request, render_template, session
from flask_migrate import Migrate
from extensions import mail
from database import db
from models.usuario import Usuario
from models.carrito import Carrito
from models.direccion import Direccion
from datetime import datetime
import pytz

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
app.config["SECRET_KEY"] = "supersecreto"

# 👉 Base de datos PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://bd_tienda_online_user:Jae0pZfKDU5OGGmmjZwzW4CwLBUNpEpR@dpg-d1e50n6mcj7s73b2ljgg-a.oregon-postgres.render.com/bd_tienda_online"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ramosjhonatan659@gmail.com'
app.config['MAIL_PASSWORD'] = 'ledx byup nooa ffpb'
app.config['MAIL_DEFAULT_SENDER'] = 'ramosjhonatan659@gmail.com'

# Inicialización
mail.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)

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
    return render_template("index.html")

# Ejecución local
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                nombre='jhonatan',
                username='admin',
                password='admin',
                rol='admin'
            )
            admin.save()
            print("✔ Usuario administrador creado (usuario: admin, clave: admin123)")

    app.run(debug=True)
