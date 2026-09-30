"""Modelos ligeros utilizados por la autenticación de EmiTech Store."""

from flask_login import UserMixin


class Usuario(UserMixin):
    """Representa un registro de PostgreSQL para Flask-Login."""

    def __init__(self, id_usuario, usuario, nombre_completo):
        self.id_usuario = int(id_usuario)
        self.usuario = usuario
        self.nombre_completo = nombre_completo

    def get_id(self):
        """Flask-Login almacena este identificador en la sesión."""
        return str(self.id_usuario)

    @classmethod
    def desde_fila(cls, fila):
        """Construye el usuario a partir de una fila de PostgreSQL."""
        if fila is None:
            return None
        return cls(
            id_usuario=fila["id_usuario"],
            usuario=fila["usuario"],
            nombre_completo=fila["nombre_completo"],
        )
