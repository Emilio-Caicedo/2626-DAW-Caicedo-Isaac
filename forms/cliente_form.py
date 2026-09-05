"""Formulario reutilizable para registrar o editar clientes."""

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp


class ClienteForm(FlaskForm):
    """Valida la información de contacto de un cliente."""

    codigo = StringField(
        "Código",
        validators=[
            DataRequired(message="El código es obligatorio."),
            Regexp(r"^CLI-\d{3}$", message="Use el formato CLI-000."),
        ],
        render_kw={"placeholder": "Ejemplo: CLI-005", "maxlength": 7},
    )
    nombre = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=5, max=100, message="Ingrese entre 5 y 100 caracteres."),
        ],
        render_kw={"placeholder": "Nombres y apellidos"},
    )
    tipo = SelectField(
        "Tipo de cliente",
        choices=[
            ("", "Seleccione un tipo"),
            ("Estudiante", "Estudiante"),
            ("Profesional", "Profesional"),
            ("Emprendimiento", "Emprendimiento"),
            ("Empresa", "Empresa"),
        ],
        validators=[DataRequired(message="Seleccione un tipo de cliente.")],
    )
    correo = StringField(
        "Correo electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingrese un correo electrónico válido."),
            Length(max=120, message="El correo no debe superar 120 caracteres."),
        ],
        render_kw={"placeholder": "nombre@ejemplo.com", "type": "email"},
    )
    ciudad = StringField(
        "Ciudad",
        validators=[
            DataRequired(message="La ciudad es obligatoria."),
            Length(min=2, max=60, message="Ingrese entre 2 y 60 caracteres."),
        ],
        render_kw={"placeholder": "Ejemplo: Puyo"},
    )
    submit = SubmitField("Guardar cliente")
