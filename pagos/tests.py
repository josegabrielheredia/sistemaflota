from datetime import date
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from choferes.models import Chofer, Conduce

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
        self.chofer_otro = Chofer.objects.create(
            nombre="Chofer Secundario",
            cedula="002-0000000-3",
            licencia="LIC-003",
        )
        self.conduce_1 = Conduce.objects.create(
            numero="COND-001",
            chofer=self.chofer,
            fecha=date(2026, 3, 1),
            monto_generado=Decimal("15000.00"),
        )
        self.conduce_2 = Conduce.objects.create(
            numero="COND-002",
            chofer=self.chofer,
            fecha=date(2026, 3, 2),
            monto_generado=Decimal("18000.00"),
        )
        self.conduce_otro = Conduce.objects.create(
            numero="COND-003",
            chofer=self.chofer_otro,
            fecha=date(2026, 3, 3),
            monto_generado=Decimal("12000.00"),
        )

    def test_suministro_asigna_saldo_pendiente_por_defecto(self):
        avance = AvanceChofer.objects.create(
            chofer=self.chofer,
            fecha=date.today(),
            galones=Decimal("50.00"),
            precio_por_galon=Decimal("10.00"),
            monto=Decimal("0.00"),
        )
        self.assertEqual(avance.saldo_pendiente, Decimal("500.00"))
        self.assertEqual(avance.estado, AvanceChofer.Estado.PENDIENTE)

    def test_descuento_de_suministro_en_orden(self):
        avance_1 = AvanceChofer.objects.create(
            chofer=self.chofer,
            fecha=date(2026, 3, 1),
            galones=Decimal("50.00"),
            precio_por_galon=Decimal("10.00"),
            monto=Decimal("0.00"),
            saldo_pendiente=Decimal("500.00"),
        )
        avance_2 = AvanceChofer.objects.create(
            chofer=self.chofer,
            fecha=date(2026, 3, 2),
            galones=Decimal("30.00"),
            precio_por_galon=Decimal("10.00"),
            monto=Decimal("0.00"),
            saldo_pendiente=Decimal("300.00"),
        )
        pago_admin = PagoAdmin(Pago, admin.site)
        descontado = pago_admin._aplicar_descuento_combustible(
            chofer_id=self.chofer.id,
            monto_cobrar=Decimal("600.00"),
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
            galones=Decimal("30.00"),
            precio_por_galon=Decimal("10.00"),
            monto=Decimal("0.00"),
            saldo_pendiente=Decimal("300.00"),
        )
        form = PagoAdminForm(
            data={
                "chofer": str(self.chofer.id),
                "monto": "1000.00",
                "metodo": Pago.Metodo.CHEQUE,
                "numero_cheque": "CHQ-001",
                "numero_recibo_pago": "REC-100",
                "descontar_suministro_combustible": "on",
                "monto_a_cobrar_combustible": "300.00",
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
            galones=Decimal("30.00"),
            precio_por_galon=Decimal("10.00"),
            monto=Decimal("0.00"),
            saldo_pendiente=Decimal("300.00"),
        )
        form = PagoAdminForm(
            data={
                "chofer": str(self.chofer.id),
                "monto": "1000.00",
                "metodo": Pago.Metodo.CHEQUE,
                "numero_cheque": "CHQ-002",
                "numero_recibo_pago": "REC-101",
                "descontar_suministro_combustible": "on",
                "monto_a_cobrar_combustible": "300.00",
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

    def test_guardar_pago_con_cuota_parcial_deja_saldo_pendiente(self):
        AvanceChofer.objects.create(
            chofer=self.chofer,
            fecha=date.today(),
            galones=Decimal("50.00"),
            precio_por_galon=Decimal("10.00"),
            monto=Decimal("0.00"),
            saldo_pendiente=Decimal("500.00"),
        )
        form = PagoAdminForm(
            data={
                "chofer": str(self.chofer.id),
                "monto": "1000.00",
                "metodo": Pago.Metodo.TRANSFERENCIA,
                "descontar_suministro_combustible": "on",
                "monto_a_cobrar_combustible": "200.00",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        pago = form.save(commit=False)

        user = get_user_model().objects.create_superuser(
            username="admin_test_pago_parcial",
            email="admin_test_pago_parcial@example.com",
            password="ClaveSegura2026!",
        )
        request = RequestFactory().post("/admin/pagos/pago/add/")
        request.user = user

        pago_admin = PagoAdmin(Pago, admin.site)
        pago_admin.save_model(request, pago, form, change=False)

        pago.refresh_from_db()
        avance = AvanceChofer.objects.get(chofer=self.chofer)
        self.assertEqual(pago.descuento_avances, Decimal("200.00"))
        self.assertFalse(pago.liquido_avances)
        self.assertEqual(avance.saldo_pendiente, Decimal("300.00"))
        self.assertEqual(avance.estado, AvanceChofer.Estado.PENDIENTE)

    def test_formulario_exige_numero_cheque_si_metodo_es_cheque(self):
        form = PagoAdminForm(
            data={
                "chofer": str(self.chofer.id),
                "monto": "1000.00",
                "metodo": Pago.Metodo.CHEQUE,
                "numero_cheque": "",
                "numero_recibo_pago": "REC-001",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("numero_cheque", form.errors)

    def test_formulario_limpia_numero_cheque_si_metodo_no_es_cheque(self):
        form = PagoAdminForm(
            data={
                "chofer": str(self.chofer.id),
                "monto": "1000.00",
                "metodo": Pago.Metodo.EFECTIVO,
                "numero_cheque": "CHQ-999",
                "numero_recibo_pago": "REC-002",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data.get("numero_cheque"), "")

    def test_formulario_permite_varios_conduces_mismo_chofer(self):
        form = PagoAdminForm(
            data={
                "chofer": str(self.chofer.id),
                "conduces": [str(self.conduce_1.id), str(self.conduce_2.id)],
                "monto": "1000.00",
                "metodo": Pago.Metodo.EFECTIVO,
                "numero_recibo_pago": "REC-003",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_formulario_bloquea_conduces_de_otro_chofer(self):
        form = PagoAdminForm(
            data={
                "chofer": str(self.chofer.id),
                "conduces": [str(self.conduce_1.id), str(self.conduce_otro.id)],
                "monto": "1000.00",
                "metodo": Pago.Metodo.EFECTIVO,
                "numero_recibo_pago": "REC-004",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("conduces", form.errors)
