# Reserva de Canchas - App (SQLite, Flask, Bootstrap)

Aplicación web sencilla para gestionar clientes, canchas y reservas.
- SQLite como BD (archivo database.db)
- Flask + SQLAlchemy
- Frontend con Bootstrap via CDN
- Auditoría de operaciones y script de backup
- No incluye sistema de login (según solicitud)

## Cómo ejecutar
1. Crear entorno virtual:
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt

2. Inicializar la base de datos y ejecutar:


flask run

o


python app.py

3. Abrir en el navegador: http://127.0.0.1:5000

4.erifica que existan clientes y canchas:




Ir a http://127.0.0.1:5000/clientes y crear un cliente si no hay ninguno.


Ir a http://127.0.0.1:5000/canchas y crear una cancha si no hay ninguna.




5.Ve a la página principal de reservas:
http://127.0.0.1:5000/


Llena el formulario con los datos:




Cliente (ID): escribe el ID de un cliente existente.


Cancha: selecciona una cancha.


Fecha: selecciona la fecha.


Hora inicio: por ejemplo 10:00.


Hora fin: por ejemplo 11:00.




6.Haz clic en "Reservar".
Si todo está bien, verás el mensaje "Reserva creada con éxito".
Si hay conflicto de horario, aparecerá un mensaje de error.


Para ver las reservas registradas:
http://127.0.0.1:5000/reservas


Para ver el historial de un cliente:
http://127.0.0.1:5000/historial/1 (cambia el número por el ID del cliente).

