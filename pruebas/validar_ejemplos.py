#!/usr/bin/env python3
"""Pruebas auxiliares reproducibles fuera de Android; no sustituyen el APK real."""
from pathlib import Path
import json, re, sqlite3
import cv2
BASE=Path(__file__).resolve().parent.parent
DB_FILE=BASE/'android/app/src/main/java/ar/edu/et35/panolapp/data/PanolDb.java'
src=DB_FILE.read_text(encoding='utf-8')
blocks=re.findall(r'db\.execSQL\((.*?)\);',src,re.DOTALL)
assert len(blocks)>=4, f'Esperábamos tablas e índices, encontramos {len(blocks)}'
statements=[]
for block in blocks:
    lit=re.findall(r'"(?:\\.|[^"\\])*"',block)
    statements.append(''.join(json.loads(s) for s in lit))
con=sqlite3.connect(':memory:')
con.execute('PRAGMA foreign_keys = ON')
for statement in statements:con.execute(statement)
assert set(r[0] for r in con.execute('SELECT name FROM sqlite_master WHERE type="table"'))>= {'tablets','movimientos'}

def insert(serial='TAB-001',state='EN_PANOL',legajo='',tarea=''):
    con.execute('INSERT INTO tablets VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
      (serial,'Snapdragon 680',4,64,10.1,'USB-C','Wi-Fi',state,legajo,tarea,0,0))

def reject(action,msg):
    try:action()
    except sqlite3.IntegrityError:print('OK',msg)
    else:raise AssertionError('Debió rechazarse '+msg)
insert();print('OK insert equipo válido')
reject(lambda:insert(),'serie duplicada')
reject(lambda:insert('TAB-002','ESTADO_DESCONOCIDO'),'estado no permitido')
reject(lambda:insert('TAB-002','EN_USO_EXTERNO','EMP-123',''),'Home Office sin tarea')
reject(lambda:insert('TAB-002','EN_USO_LOCAL','',''),'prestado sin legajo')
reject(lambda:con.execute("INSERT INTO movimientos(serial,tipo,hacia_estado,metodo_identificacion,fecha) VALUES('NO_EXISTE','ALTA','EN_PANOL','QR',0)"),'FK historial/serie')
con.execute("INSERT INTO movimientos(serial,tipo,hacia_estado,metodo_identificacion,fecha) VALUES('TAB-001','ALTA','EN_PANOL','QR',0)")
assert con.execute('SELECT count(*) FROM movimientos').fetchone()[0]==1
print('OK movimiento válido con FK')

items=json.loads((BASE/'etiquetas/inventario_ejemplo.json').read_text(encoding='utf-8'))
for item in items:
    serial=item['serial']
    as_text=(BASE/f'etiquetas/{serial}.txt').read_text(encoding='utf-8').strip()
    assert json.loads(as_text)==item
    arr=cv2.imread(str(BASE/f'etiquetas/{serial}.png'))
    # OpenCV es muy sensible al tamaño del render para algunas versiones de QR.
    arr=cv2.resize(arr,(700,700),interpolation=cv2.INTER_NEAREST)
    value,_,_=cv2.QRCodeDetector().detectAndDecode(arr)
    assert value and json.loads(value)['serial']==serial, serial+' QR ilegible para la herramienta auxiliar'
    print('OK QR real',serial)
print('VERIFICACIONES AUXILIARES FINALIZADAS')
