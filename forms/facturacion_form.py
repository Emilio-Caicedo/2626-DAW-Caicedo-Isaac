"""Formulario reutilizable para registrar o editar comprobantes."""

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Regexp


class FacturacionForm(FlaskForm):
    """Valida los datos necesarios para generar un comprobante."""

    numero = StringField(
        "Número del comprobante",
        validators=[
            DataRequired(message="El número es obligatorio."),
            Regexp(r"^FAC-\d{4}$", message="Use el formato FAC-0000."),
        ],
        render_kw={"placeholder": "Ejemplo: FAC-0002", "maxlength": 8},
    )
    fecha = DateField(
        "Fecha",
        format="%Y-%m-%d",
        validators=[DataRequired(message="Seleccione una fecha válida.")],
    )
    cliente_codigo = SelectField(
        "Cliente",
        choices=[],
        validators=[DataRequired(message="Seleccione un cliente.")],
    )
    producto_codigo = SelectField(
        "Producto disponible",
        choices=[],
        validators=[DataRequired(message="Seleccione un producto.")],
    )
    cantidad = IntegerField(
        "Cantidad",
        validators=[
            DataRequired(message="La cantidad es obligatoria."),
            NumberRange(min=1, max=100, message="Ingrese una cantidad entre 1 y 100."),
        ],
        render_kw={"placeholder": "1", "min": 1, "max": 100},
    )
    submit = SubmitField("Generar comprobante")
