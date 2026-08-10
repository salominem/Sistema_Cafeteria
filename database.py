import hashlib
from peewee import (
    SqliteDatabase, Model, CharField, FloatField, 
    ForeignKeyField, IntegerField, DateTimeField, BooleanField
)
import datetime

db = SqliteDatabase('bar_system.db')


class BaseModel(Model):
    class Meta:
        database = db


class Usuario(BaseModel):
    username = CharField(unique=True)
    password_hash = CharField()
    rol = CharField(default="Admin")


class Categoria(BaseModel):
    nombre = CharField(unique=True)


class Producto(BaseModel):
    nombre = CharField()
    precio = FloatField()
    categoria = ForeignKeyField(Categoria, backref='productos', null=True, on_delete='SET NULL')


class Mesa(BaseModel):
    numero = IntegerField(unique=True)
    estado = CharField(default="Libre")  # "Libre" o "Ocupada"


class PedidoMesa(BaseModel):
    mesa = ForeignKeyField(Mesa, backref='pedidos', on_delete='CASCADE')
    producto = ForeignKeyField(Producto, backref='pedidos_activos', on_delete='CASCADE')
    cantidad = IntegerField(default=1)


class Venta(BaseModel):
    fecha = DateTimeField(default=datetime.datetime.now)
    mesa_numero = IntegerField()
    total = FloatField()
    metodo_pago = CharField(default="Efectivo")
    cerrado = BooleanField(default=False)


class CierreCaja(BaseModel):
    fecha = DateTimeField(default=datetime.datetime.now)
    turno = CharField()
    total_efectivo = FloatField()
    total_mp = FloatField()
    total_tarjeta = FloatField()
    total_general = FloatField()


def hash_password(password: str) -> str:
    """Genera un hash SHA-256 para la contraseña."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def inicializar_bd():
    db.connect(reuse_if_open=True)
    db.create_tables([
        Usuario, Categoria, Producto, Mesa, 
        PedidoMesa, Venta, CierreCaja
    ])

    # Crear usuario administrador por defecto si no existe ningún usuario
    if Usuario.select().count() == 0:
        Usuario.create(
            username="admin",
            password_hash=hash_password("admin123"),
            rol="Admin"
        )
        print("-> Usuario Administrador por defecto creado (admin / admin123)")

    # Crear categorías básicas si está vacía
    if Categoria.select().count() == 0:
        Categoria.create(nombre="General")

    # Crear 8 mesas por defecto si no existen
    if Mesa.select().count() == 0:
        for i in range(1, 9):
            Mesa.create(numero=i, estado="Libre")