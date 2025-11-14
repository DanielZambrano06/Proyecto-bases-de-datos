from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
import os
import sqlite3
import subprocess

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'cambia_esta_clave'

db = SQLAlchemy(app)

# --------------------
# MODELOS
# --------------------
class Cliente(db.Model):
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(120))
    reservas = db.relationship('Reserva', backref='cliente', lazy=True)

class Cancha(db.Model):
    id_cancha = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    ubicacion = db.Column(db.String(50))
    reservas = db.relationship('Reserva', backref='cancha', lazy=True)

class Reserva(db.Model):
    id_reserva = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'), nullable=False)
    id_cancha = db.Column(db.Integer, db.ForeignKey('cancha.id_cancha'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Auditoria(db.Model):
    id_log = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    accion = db.Column(db.String(200))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    resultado = db.Column(db.String(20))
    ip = db.Column(db.String(50))

# --------------------
# helpers
# --------------------
def registrar_auditoria(usuario, accion, resultado='exitoso', ip='127.0.0.1'):
    log = Auditoria(usuario=usuario, accion=accion, resultado=resultado, ip=ip)
    db.session.add(log)
    db.session.commit()

def init_db(force=False):
    if force:
        # no borrar, solo crear si falta
        db.drop_all()
    db.create_all()

    db.create_all()
    # insertar datos de ejemplo si la tabla Cancha está vacía
    if Cancha.query.count() == 0:
        canchas = [
            Cancha(nombre='Cancha Norte', tipo='Fútbol', ubicacion='Zona A'),
            Cancha(nombre='Cancha Sur', tipo='Baloncesto', ubicacion='Zona B'),
            Cancha(nombre='Cancha Central', tipo='Tenis', ubicacion='Zona C'),
            Cancha(nombre='Cancha Techada', tipo='Fútbol', ubicacion='Zona D'),
            Cancha(nombre='Cancha Sintética', tipo='Fútbol', ubicacion='Zona E'),
        ]
        db.session.bulk_save_objects(canchas)
        db.session.commit()
    if Cliente.query.count() == 0:
        clientes = [
            Cliente(nombre='Carlos', apellido='Pérez', telefono='300111222', correo='carlos@mail.com'),
            Cliente(nombre='María', apellido='Gómez', telefono='300222333', correo='maria@mail.com'),
            Cliente(nombre='Juan', apellido='Rodríguez', telefono='300333444', correo='juan@mail.com'),
            Cliente(nombre='Laura', apellido='Martínez', telefono='300444555', correo='laura@mail.com'),
            Cliente(nombre='Andrés', apellido='Suárez', telefono='300555666', correo='andres@mail.com'),
        ]
        db.session.bulk_save_objects(clientes)
        db.session.commit()

# --------------------
# RUTAS
# --------------------
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    canchas = Cancha.query.all()
    return render_template('index.html', canchas=canchas)

@app.route('/clientes')
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            telefono = request.form['telefono']
            correo = request.form['correo']

            nuevo = Cliente(nombre=nombre, apellido=apellido, telefono=telefono, correo=correo)
            db.session.add(nuevo)
            db.session.commit()

            flash('✅ Cliente registrado con éxito', 'success')
            return redirect(url_for('listar_clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al registrar cliente: {str(e)}', 'danger')

    return render_template('nuevo_cliente.html')

@app.route('/canchas')
def listar_canchas():
    canchas = Cancha.query.all()
    return render_template('canchas.html', canchas=canchas)

@app.route('/canchas/nueva', methods=['GET', 'POST'])
def nueva_cancha():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            tipo = request.form['tipo']
            ubicacion = request.form['ubicacion']

            nueva = Cancha(nombre=nombre, tipo=tipo, ubicacion=ubicacion)
            db.session.add(nueva)
            db.session.commit()

            flash('✅ Cancha registrada con éxito', 'success')
            return redirect(url_for('listar_canchas'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al registrar cancha: {str(e)}', 'danger')

    return render_template('nueva_cancha.html')

@app.route('/reservas')
def listar_reservas():
    reservas = Reserva.query.order_by(Reserva.fecha.desc(), Reserva.hora_inicio).all()
    return render_template('reservas.html', reservas=reservas)

@app.route('/reservar', methods=['POST'])
def reservar():
    try:
        cliente_id = int(request.form['cliente_id'])
        cancha_id = int(request.form['cancha_id'])
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
        hora_fin = datetime.strptime(request.form['hora_fin'], '%H:%M').time()

        # Validación simple: no solapamiento exacto en la misma cancha (rango abierto-cerrado)
        conflictos = Reserva.query.filter(
            Reserva.id_cancha == cancha_id,
            Reserva.fecha == fecha,
            Reserva.hora_inicio < hora_fin,
            Reserva.hora_fin > hora_inicio
        ).all()
        if conflictos:
            registrar_auditoria('sistema', f'Intento crear reserva conflictiva (cliente {cliente_id})', 'fallido')
            flash('Error: la reserva entra en conflicto con otra existente.', 'danger')
            return redirect(url_for('index'))

        nueva = Reserva(
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            id_cliente=cliente_id,
            id_cancha=cancha_id
        )
        db.session.add(nueva)
        db.session.commit()
        registrar_auditoria('sistema', f'Reserva creada id:{nueva.id_reserva} cliente:{cliente_id} cancha:{cancha_id}', 'exitoso')
        flash('Reserva creada con éxito ✅', 'success')
    except Exception as e:
        db.session.rollback()
        registrar_auditoria('sistema', f'Error al crear reserva: {str(e)}', 'fallido')
        flash('Ocurrió un error al crear la reserva.', 'danger')
    return redirect(url_for('index'))

@app.route('/historial/<int:id_cliente>')
def historial_cliente(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)
    reservas = Reserva.query.filter_by(id_cliente=id_cliente).order_by(Reserva.fecha.desc()).all()
    return render_template('historial.html', cliente=cliente, reservas=reservas)

@app.route('/auditoria')
def ver_auditoria():
    logs = Auditoria.query.order_by(Auditoria.fecha.desc()).limit(200).all()
    return render_template('auditoria.html', logs=logs)

@app.route('/backup')
def backup():
    # crea carpeta backups si no existe
    backups_dir = os.path.join(BASE_DIR, 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dump_file = os.path.join(backups_dir, f'backup_{timestamp}.sql')
    # usar sqlite3 .dump para crear backup
    cmd = f"sqlite3 {DB_PATH} \".dump\" > {dump_file}"
    try:
        subprocess.check_call(cmd, shell=True)
        registrar_auditoria('sistema', f'Backup creado: {os.path.basename(dump_file)}', 'exitoso')
        return jsonify({'status':'ok','file':os.path.basename(dump_file)})
    except subprocess.CalledProcessError as e:
        registrar_auditoria('sistema', 'Backup fallido', 'fallido')
        return jsonify({'status':'error'}), 500

# API simple para verificar disponibilidad (JSON)
@app.route('/api/disponibilidad', methods=['GET'])
def api_disponibilidad():
    cancha_id = request.args.get('cancha_id', type=int)
    fecha_str = request.args.get('fecha')
    hora_inicio = request.args.get('hora_inicio')
    hora_fin = request.args.get('hora_fin')
    if not (cancha_id and fecha_str and hora_inicio and hora_fin):
        return jsonify({'error':'parámetros incompletos'}), 400
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    h1 = datetime.strptime(hora_inicio, '%H:%M').time()
    h2 = datetime.strptime(hora_fin, '%H:%M').time()
    conflictos = Reserva.query.filter(
        Reserva.id_cancha==cancha_id,
        Reserva.fecha==fecha,
        Reserva.hora_inicio < h2,
        Reserva.hora_fin > h1
    ).count()
    return jsonify({'disponible': conflictos==0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

