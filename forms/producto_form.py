"""Formulario reutilizable para registrar o editar productos."""

from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Regexp


class ProductoForm(FlaskForm):
    """Valida la información principal de un producto."""

    codigo = StringField(
        "Código",
        validators=[
            DataRequired(message="El código es obligatorio."),
            Regexp(r"^PRO-\d{3}$", message="Use el formato PRO-000."),
        ],
        render_kw={"placeholder": "Ejemplo: PRO-007", "maxlength": 7},
    )
    nombre = StringField(
        "Nombre del producto",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, max=80, message="Ingrese entre 3 y 80 caracteres."),
        ],
        render_kw={"placeholder": "Ejemplo: Monitor de 24 pulgadas"},
    )
    categoria = SelectField(
        "Categoría",
        choices=[
            ("", "Seleccione una categoría"),
            ("Laptops y computadoras", "Laptops y computadoras"),
            ("Accesorios tecnológicos", "Accesorios tecnológicos"),
            ("Componentes informáticos", "Componentes informáticos"),
        ],
        validators=[DataRequired(message="Seleccione una categoría.")],
    )
    descripcion = TextAreaField(
        "Descripción",
        validators=[
            DataRequired(message="La descripción es obligatoria."),
            Length(min=10, max=250, message="Ingrese entre 10 y 250 caracteres."),
        ],
        render_kw={"rows": 4, "placeholder": "Describa las características principales"},
    )
    precio = DecimalField(
        "Precio (USD)",
        places=2,
        validators=[
            DataRequired(message="El precio es obligatorio."),
            NumberRange(min=0.01, max=100000, message="Ingrese un precio mayor que 0."),
        ],
        render_kw={"placeholder": "0.00", "min": "0.01", "step": "0.01"},
    )
    stock = IntegerField(
        "Existencias",
        validators=[
            InputRequired(message="Las existencias son obligatorias."),
            NumberRange(min=0, max=9999, message="Ingrese un valor entre 0 y 9999."),
        ],
        render_kw={"placeholder": "0", "min": 0, "max": 9999},
    )
    submit = SubmitField("Guardar producto")
