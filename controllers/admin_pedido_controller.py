from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models.pedido import Pedido
from database import db
from flask_mail import Message
from extensions import mail
from flask import current_app, make_response
import io
from xhtml2pdf import pisa
from models.detalle_pedido import DetallePedido


admin_pedido_bp = Blueprint('admin_pedido', __name__, url_prefix='/admin/pedidos')

@admin_pedido_bp.route('/')
def lista():
    pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    return render_template('admin/pedidos/lista.html', pedidos=pedidos)

@admin_pedido_bp.route('/editar/<int:pedido_id>', methods=['GET', 'POST'])
def editar(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)

    if request.method == 'POST':
        nuevo_estado = request.form.get('estado')
        if nuevo_estado in ['pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado']:
            pedido.estado = nuevo_estado
            db.session.commit()
            flash('Estado actualizado correctamente.', 'success')
        else:
            flash('Estado inválido.', 'danger')
        return redirect(url_for('admin_pedido.lista'))

    return render_template('admin/pedidos/editar.html', pedido=pedido)

@admin_pedido_bp.route('/detalle/<int:pedido_id>')
def detalle(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('admin/pedidos/detalle.html', pedido=pedido)

@admin_pedido_bp.route('/enviar-correo/<int:pedido_id>')
def enviar_factura_por_correo(pedido_id):
    from models.pedido import Pedido  # si no lo tenés importado ya
    pedido = Pedido.query.get_or_404(pedido_id)

    if not pedido.usuario.correo or not pedido.factura:
        flash('No se puede enviar el correo: faltan datos del cliente o la factura no ha sido generada.', 'warning')
        return redirect(url_for('admin_pedido.detalle', pedido_id=pedido_id))

    try:
        archivo_limpio = pedido.factura.archivo_pdf.replace('\\', '/')
        ruta_pdf = f"static/{archivo_limpio}"
        asunto = f"Factura Pedido #{pedido.id}"
        mensaje = (
                f"🧾 ¡Hola {pedido.usuario.nombre}!\n\n"
                f"Gracias por tu compra en nuestra tienda 🛍️.\n\n"
                f"Adjuntamos tu factura correspondiente al pedido #{pedido.id} en formato PDF 📎.\n"
                f"Si tenés alguna duda o necesitás más información, no dudes en contactarnos 😊.\n\n"
                f"Saludos cordiales,\n"
                f"El equipo de atención"
            )

        msg = Message(subject=asunto,
                      recipients=[pedido.usuario.correo],
                      body=mensaje)

        with current_app.open_resource(ruta_pdf) as fp:
            msg.attach(filename=f"pedido_{pedido.id}.pdf",
                       content_type="application/pdf",
                       data=fp.read())

        mail.send(msg)
        flash("📩 Correo enviado correctamente al cliente.", "success")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        flash("❌ Hubo un error al enviar el correo.", "danger")

    return redirect(url_for('admin_pedido.detalle', pedido_id=pedido_id))

@admin_pedido_bp.route('/generar-factura/<int:pedido_id>')
def generar_factura(pedido_id):
    from utils.generador_pdf import generar_y_guardar_factura
    pedido = Pedido.query.get_or_404(pedido_id)
    
    if not pedido.factura:
        generar_y_guardar_factura(pedido)
        flash('Comprobante generado correctamente.', 'success')
    else:
        flash('El comprobante ya estaba generado.', 'info')
        
    return redirect(url_for('admin_pedido.detalle', pedido_id=pedido_id))


@admin_pedido_bp.route('/ticket/<int:pedido_id>')
def ver_ticket(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    detalles = DetallePedido.query.filter_by(pedido_id=pedido.id).all()
    html = render_template('pdf/pedido_ticket.html', pedido=pedido, detalles=detalles)

    result = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=result)

    response = make_response(result.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=ticket_{pedido.id}.pdf"
    return response
