# Script opcional para crear backups (usa sqlite3 .dump)
import os, subprocess
from datetime import datetime
BASE = os.path.abspath(os.path.dirname(__file__))
DB = os.path.join(BASE, 'database.db')
OUT = os.path.join(BASE, 'backups')
os.makedirs(OUT, exist_ok=True)
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
dump = os.path.join(OUT, f'backup_{ts}.sql')
cmd = f'sqlite3 "{DB}" ".dump" > "{dump}"'
print('Ejecutando:', cmd)
r = subprocess.call(cmd, shell=True)
if r == 0:
    print('Backup creado en', dump)
else:
    print('Error al crear backup. Asegúrate de tener sqlite3 disponible.')
