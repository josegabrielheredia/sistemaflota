from datetime import date
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from choferes.models import Chofer

from .admin import PagoAdmin
from .forms import PagoAdminForm
from .models import AvanceChofer, Pago


class AvancesChoferTests(TestCase):
    def setUp(self):
        self.chofer = Chofer.objects.create(
            nombre="Chofer Avance",
            cedula="002-0000000-2",
            licencia="LIC-002",
        )

    def test_avance_asigna_saldo_pendiente_por_defecto(self):
        avance = AvanceChofer.objects.create(
            chofer=self.chofer,
            fecha=date.today(),
            monto=Decimal("500.00"),
        )
        self.assertEqual(avance.saldo_pendiente, Decimal("500.00"))
        self.assertEqual(avance.estado, AvanceChofer.Estado.PENDIENTE)

    def test_descuento_de_avances_en_orden(self):
        avance_1 = AvanceChofer.objects.create(
            chofer=self.chofer,
            fecha=date(2026, 3, 1),
            monto=Decimal("500.00"),
            saldo_pendiente=Decimal("500.00"),
        )
        avance_2 = AvanceChofer.objects.create(
            chofer=self.chofer,
            fecha=date(2026, 3, 2),
            monto=Decimal("300.00"),
            saldo_pendiente=Decimal("300.00"),
        )
        pago_admin = PagoAdmin(Pago, admin.site)
        descontado = pago_admin._aplicar_descuento_avances(
            chofer_id=self.chofer.id,
            monto_pago=Decimal("600.00"),
        )

        avance_1.refresh_from_db()
        avance_2.refresh_from_db()
        self.assertEqual(descontado, Decimal("600.00"))
        self.assertEqual(avance_1.saldo_pendiente, Decimal("0.00"))
        self.assertEqual(avance_1.estado, AvanceChofer.Estado.LIQUIDADO)
        self.assertEqual(avance_2.saldo_pendiente, Decimal("200.00"))
        self.assertEqual(avance_2.estado, AvanceChofer.Estado.PENDIENTE)

    def test_formulario_pago_calcula_monto_neto(self):
        AvanceChofer.objects.create(
            chofer=self.chofer,
            fecha=date.today(),
            monto=Decimal("300.00"),
            saldo_pendiente=Decimal("300.00"),
        )
        form = PagoAdminForm(
            data={
                "chofer": str(self.chofer.id),
                "monto": "1000.00",
                "metodo": Pago.Metodo.CHEQUE,
                "descontar_avance_pendiente": "on",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            Decimal(str(form.fields["monto_neto_a_pagar"].initial)),
            Decimal("700.00"),
        )

    def test_guardar_pago_descuenta_y_marca_liquidado(self):
        AvanceChofer.objects.create(
            chofer=self.chofer,
            fecha=date.today(),
            monto=Decimal("300.00"),
            saldo_pendiente=Decimal("300.00"),
        )
        form = PagoAdminForm(
            data={
                "chofer": str(self.chofer.id),
                "monto": "1000.00",
                "metodo": Pago.Metodo.CHEQUE,
                "descontar_avance_pendiente": "on",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        pago = form.save(commit=False)

        user = get_user_model().objects.create_superuser(
            username="admin_test_pago",
            email="admin_test_pago@example.com",
            password="ClaveSegura2026!",
        )
        request = RequestFactory().post("/admin/pagos/pago/add/")
        request.user = user

        pago_admin = PagoAdmin(Pago, admin.site)
        pago_admin.save_model(request, pago, form, change=False)

        pago.refresh_from_db()
        avance = AvanceChofer.objects.get(chofer=self.chofer)
        self.assertEqual(pago.descuento_avances, Decimal("300.00"))
        self.assertTrue(pago.liquido_avances)
        self.assertEqual(avance.saldo_pendiente, Decimal("0.00"))
        self.assertEqual(avance.estado, AvanceChofer.Estado.LIQUIDADO)
