import os
from app import app
from database import db
from models.categoria import Categoria
from models.proveedor import Proveedor
from models.producto import Producto

def seed_data():
    with app.app_context():
        # 1. Crear Categorías si no existen
        cat_nombres = ["Frutas y Verduras", "Lácteos", "Abarrotes", "Bebidas", "Limpieza"]
        categorias = {}
        for nombre in cat_nombres:
            cat = Categoria.query.filter_by(nombre=nombre).first()
            if not cat:
                cat = Categoria(nombre=nombre)
                db.session.add(cat)
                db.session.commit()
                print(f"Categoría creada: {nombre}")
            categorias[nombre] = cat

        # 2. Crear Proveedores si no existen
        prov_datos = [
            {"nombre": "Distribuidora Central", "contacto": "70012345"},
            {"nombre": "Granja Integral", "contacto": "71154321"}
        ]
        proveedores = []
        for p_data in prov_datos:
            prov = Proveedor.query.filter_by(nombre=p_data["nombre"]).first()
            if not prov:
                prov = Proveedor(nombre=p_data["nombre"], contacto=p_data["contacto"])
                db.session.add(prov)
                db.session.commit()
                print(f"Proveedor creado: {p_data['nombre']}")
            proveedores.append(prov)

        # 3. Lista de 10 productos de víveres
        productos_data = [
            {"nombre": "Arroz de Grano Largo", "desc": "Bolsa de 1kg de arroz premium", "precio": 12.50, "stock": 50, "img": "arroz.jpg", "cat": "Abarrotes"},
            {"nombre": "Leche Entera", "desc": "Litro de leche fresca pasteurizada", "precio": 6.50, "stock": 30, "img": "leche.png", "cat": "Lácteos"},
            {"nombre": "Bananas", "desc": "Penca de bananas maduras", "precio": 5.00, "stock": 20, "img": "bananas.png", "cat": "Frutas y Verduras"},
            {"nombre": "Manzanas Rojas", "desc": "Kilo de manzanas frescas", "precio": 15.00, "stock": 15, "img": "apple.png", "cat": "Frutas y Verduras"},
            {"nombre": "Fideos Tallarín", "desc": "Paquete de 500g", "precio": 8.00, "stock": 40, "img": "fideos.png", "cat": "Abarrotes"},
            {"nombre": "Detergente Líquido", "desc": "Botella de 1 litro", "precio": 22.00, "stock": 10, "img": "detergente.png", "cat": "Limpieza"},
            {"nombre": "Agua Mineral", "desc": "Botella de 2 litros sin gas", "precio": 6.00, "stock": 60, "img": "bebidas.png", "cat": "Bebidas"},
            {"nombre": "Yogurt Natural", "desc": "Vaso de 200ml", "precio": 4.50, "stock": 25, "img": "leche.png", "cat": "Lácteos"},
            {"nombre": "Aceite Vegetal", "desc": "Botella de 900ml", "precio": 18.00, "stock": 15, "img": "arroz.jpg", "cat": "Abarrotes"},
            {"nombre": "Papas", "desc": "Arroba de papas seleccionadas", "precio": 45.00, "stock": 5, "img": "frutas.png", "cat": "Frutas y Verduras"},
        ]

        # 4. Insertar Productos
        for p in productos_data:
            if not Producto.query.filter_by(nombre=p["nombre"]).first():
                nuevo_prod = Producto(
                    nombre=p["nombre"],
                    descripcion=p["desc"],
                    precio=p["precio"],
                    stock=p["stock"],
                    imagen=p["img"],
                    categoria_id=categorias[p["cat"]].id,
                    proveedor_id=proveedores[0].id if p["cat"] != "Frutas y Verduras" else proveedores[1].id
                )
                db.session.add(nuevo_prod)
                print(f"Producto añadido: {p['nombre']}")
        
        db.session.commit()
        print("\n✔ ¡Base de datos poblada con éxito!")

if __name__ == "__main__":
    seed_data()
