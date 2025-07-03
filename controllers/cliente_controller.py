from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from models.producto import Producto
from models.direccion import Direccion

cliente_bp = Blueprint('cliente', __name__, url_prefix='/cliente')

# Página de inicio para clientes
@cliente_bp.route('/inicio')
def inicio():
    if session.get('rol') != 'cliente':
        flash('Acceso denegado: solo para clientes.', 'danger')
        return redirect(url_for('usuario.login'))
    
    productos = Producto.query.all()
    return render_template('cliente/inicio.html', productos=productos)

# Mostrar formulario para agregar dirección
@cliente_bp.route('/direccion/agregar')
def agregar_direccion():
    if session.get('rol') != 'cliente':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('usuario.login'))
    
    return render_template('cliente/agregar_direccion.html')

# Guardar nueva dirección
@cliente_bp.route('/direccion/guardar', methods=['POST'])
def guardar_direccion():
    if session.get('rol') != 'cliente' or 'id' not in session:
        flash('Iniciá sesión como cliente.', 'danger')
        return redirect(url_for('usuario.login'))

    direccion = request.form.get('direccion')
    referencia = request.form.get('referencia')
    lat = request.form.get('latitud')
    lng = request.form.get('longitud')

    if not direccion:
        flash('La dirección es obligatoria.', 'warning')
        return redirect(url_for('cliente.agregar_direccion'))

    nueva = Direccion(
        usuario_id=session['id'],
        direccion=direccion,
        referencia=referencia,
        latitud=lat if lat else None,
        longitud=lng if lng else None
    )
    nueva.save()

    flash('Dirección guardada con éxito.', 'success')
    return redirect(url_for('carrito.index'))

# Buscador tradicional (con recarga)
@cliente_bp.route('/buscar')
def inicio_busqueda():
    termino = request.args.get('q', '').strip()

    if not termino:
        return render_template('cliente/inicio.html', productos=[])

    productos = Producto.query.filter(Producto.nombre.ilike(f'%{termino}%')).all()
    return render_template('cliente/inicio.html', productos=productos)

# Buscador en vivo (API que devuelve JSON)
@cliente_bp.route('/api/buscar')
def api_buscar_productos():
    termino = request.args.get('q', '').strip()

    if not termino:
        productos = Producto.query.limit(20).all()
    else:
        productos = Producto.query.filter(Producto.nombre.ilike(f'%{termino}%')).all()

    productos_json = [{
        'id': p.id,
        'nombre': p.nombre,
        'descripcion': p.descripcion,
        'precio': float(p.precio),
        'stock': p.stock,
        'imagen': p.imagen
    } for p in productos]

    return jsonify(productos_json)

@cliente_bp.route('/api/filtrar_categoria')
def api_filtrar_categoria():
    id_cat = request.args.get('id', type=int)
    
    if not id_cat or id_cat == 0:
        productos = Producto.query.limit(20).all()
    else:
        productos = Producto.query.filter_by(categoria_id=id_cat).all()

    return jsonify([{
        'id': p.id,
        'nombre': p.nombre,
        'descripcion': p.descripcion,
        'precio': float(p.precio),
        'stock': p.stock,
        'imagen': p.imagen
    } for p in productos])