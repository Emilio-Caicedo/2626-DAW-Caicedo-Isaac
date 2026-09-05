"""Formulario reutilizable para registrar o editar proveedores."""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Regexp


class ProveedorForm(FlaskForm):
    """Valida los datos comerciales de un proveedor."""

    codigo = StringField(
        "Código",
        validators=[
            DataRequired(message="El código es obligatorio."),
            Regexp(r"^PRV-\d{3}$", message="Use el formato PRV-000."),
        ],
        render_kw={"placeholder": "Ejemplo: PRV-004", "maxlength": 7},
    )
    nombre = StringField(
        "Nombre del proveedor",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, max=100, message="Ingrese entre 3 y 100 caracteres."),
        ],
        render_kw={"placeholder": "Nombre comercial"},
    )
    categoria = TextAreaField(
        "Productos que distribuye",
        validators=[
            DataRequired(message="La categoría es obligatoria."),
            Length(min=10, max=180, message="Ingrese entre 10 y 180 caracteres."),
        ],
        render_kw={"rows": 3, "placeholder": "Ejemplo: Computadoras, periféricos y accesorios"},
    )
    correo = StringField(
        "Correo electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingrese un correo electrónico válido."),
            Length(max=120, message="El correo no debe superar 120 caracteres."),
        ],
        render_kw={"placeholder": "ventas@proveedor.com", "type": "email"},
    )
    ciudad = StringField(
        "Ciudad",
        validators=[
            DataRequired(message="La ciudad es obligatoria."),
            Length(min=2, max=60, message="Ingrese entre 2 y 60 caracteres."),
        ],
        render_kw={"placeholder": "Ejemplo: Quito"},
    )
    entrega_dias = IntegerField(
        "Tiempo estimado de entrega (días)",
        validators=[
            DataRequired(message="El tiempo de entrega es obligatorio."),
            NumberRange(min=1, max=60, message="Ingrese un valor entre 1 y 60 días."),
        ],
        render_kw={"placeholder": "3", "min": 1, "max": 60},
    )
    submit = SubmitField("Guardar proveedor")
