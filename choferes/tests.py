from datetime import date, timedelta

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


class ChoferDocumentosEstadoTests(TestCase):
    def test_estado_licencia_vencida(self):
        chofer = Chofer.objects.create(
            nombre="Chofer Licencia",
            cedula="001-0000000-9",
            licencia="LIC-999",
            vencimiento_licencia=date.today() - timedelta(days=1),
        )
        self.assertEqual(chofer.estado_licencia(), "Vencido")

    def test_estado_documentos_vigentes(self):
        chofer = Chofer.objects.create(
            nombre="Chofer Vigente",
            cedula="001-0000000-8",
            licencia="LIC-998",
            rntt=True,
            seguro_ley=True,
            vencimiento_licencia=date.today() + timedelta(days=30),
            vencimiento_carnet_rntt=date.today() + timedelta(days=45),
            vencimiento_seguro_ley=date.today() + timedelta(days=60),
        )
        self.assertEqual(chofer.estado_licencia(), "Vigente")
        self.assertEqual(chofer.estado_carnet_rntt(), "Vigente")
        self.assertEqual(chofer.estado_seguro_ley(), "Vigente")

    def test_estado_documento_no_aplica_si_no_corresponde(self):
        chofer = Chofer.objects.create(
            nombre="Chofer No Aplica",
            cedula="001-0000000-7",
            licencia="LIC-997",
            rntt=False,
            seguro_ley=False,
        )
        self.assertEqual(chofer.estado_carnet_rntt(), "No aplica")
        self.assertEqual(chofer.estado_seguro_ley(), "No aplica")
