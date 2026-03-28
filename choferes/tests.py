from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Chofer, Conduce


class ConduceValidationTests(TestCase):
    def setUp(self):
        self.chofer = Chofer.objects.create(
            nombre="Chofer Prueba",
            cedula="001-0000000-1",
            licencia="LIC-001",
        )

    def test_numero_se_normaliza_a_mayusculas(self):
        conduce = Conduce.objects.create(
            numero=" abc-123 ",
            chofer=self.chofer,
            fecha=date.today(),
        )
        self.assertEqual(conduce.numero, "ABC-123")

    def test_no_permite_conduce_duplicado_por_numero(self):
        Conduce.objects.create(
            numero="ABC-123",
            chofer=self.chofer,
            fecha=date.today(),
        )

        duplicado = Conduce(
            numero=" abc-123 ",
            chofer=self.chofer,
            fecha=date.today(),
        )
        with self.assertRaises(ValidationError) as ctx:
            duplicado.full_clean()

        self.assertIn("numero", ctx.exception.message_dict)
