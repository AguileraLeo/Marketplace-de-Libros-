"""Pruebas del flujo crítico del MVP y de las reglas de permisos.

Ejecutar desde la raíz:  python -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from books_api import catalog_lookup  # noqa: E402
from store import (  # noqa: E402
    Condition,
    Delivery,
    InvalidTransition,
    OfferStatus,
    PermissionDenied,
    RequestStatus,
    Role,
    UserStatus,
    ValidationError,
    build_demo_store,
)


class StoreTestCase(unittest.TestCase):
    def setUp(self):
        self.store = build_demo_store(catalog_lookup)
        self.reader = self.store.authenticate("lector@demo.cl", "1234")
        self.reader2 = self.store.authenticate("maria@demo.cl", "1234")
        self.seller = self.store.authenticate("vendedor@demo.cl", "1234")
        self.seller2 = self.store.authenticate("pedro@demo.cl", "1234")
        self.admin = self.store.authenticate("admin@demo.cl", "admin")
        self.book = self.store.upsert_book(catalog_lookup("demo-quijote"))

    def new_request(self, **kw):
        data = dict(
            book_id=self.book.id, max_price="20000", accepted_condition=Condition.ANY,
            location="Concepción", delivery_preference=Delivery.ANY, notes="",
        )
        data.update(kw)
        return self.store.create_request(self.reader, **data)


class HappyPathTest(StoreTestCase):
    def test_full_flow(self):
        req = self.new_request()
        self.assertEqual(req.status, RequestStatus.PUBLISHED)
        self.assertIn(req, self.store.open_requests(self.seller))

        offer = self.store.create_offer(
            self.seller, req.id, "15990", Condition.USED, "Buen estado", "", "+56 9 1111", "", ""
        )
        self.assertEqual(req.status, RequestStatus.WITH_OFFERS)
        self.assertIn(offer, self.store.offers_for_request(self.reader, req.id))

        with self.assertRaises(PermissionDenied):  # contacto oculto antes de coordinar o aceptar
            self.store.offer_contact(self.reader, offer.id)

        other = self.store.create_offer(
            self.seller2, req.id, "18000", Condition.NEW, "", "", "", "p@demo.cl", ""
        )

        # 1. El lector acepta para coordinar (estado intermedio)
        self.store.accept_offer(self.reader, offer.id)
        self.assertEqual(offer.status, OfferStatus.IN_DEAL)
        self.assertEqual(other.status, OfferStatus.ON_HOLD)
        self.assertEqual(req.status, RequestStatus.IN_DEAL)
        # El contacto del vendedor ahora es visible para coordinar
        self.assertEqual(self.store.offer_contact(self.reader, offer.id).phone, "+56 9 1111")

        # 2. El lector confirma que la compra fue concretada con éxito
        self.store.confirm_deal(self.reader, offer.id)
        self.assertEqual(offer.status, OfferStatus.ACCEPTED)
        self.assertEqual(other.status, OfferStatus.REJECTED)
        self.assertEqual(req.status, RequestStatus.RESOLVED)
        self.assertNotIn(req, self.store.open_requests(self.seller))

    def test_seller_feed_excludes_already_offered(self):
        req = self.new_request()
        self.assertIn(req, self.store.open_requests(self.seller))

        offer = self.store.create_offer(
            self.seller, req.id, "1000", Condition.NEW, "", "", "1", "", ""
        )
        # El vendedor que ya ofertó deja de verla en el feed...
        self.assertNotIn(req, self.store.open_requests(self.seller))
        # ...pero otro vendedor sí la sigue viendo.
        self.assertIn(req, self.store.open_requests(self.seller2))

        # Si cancela su oferta, la solicitud vuelve a aparecer en su feed.
        self.store.cancel_offer(self.seller, offer.id)
        self.assertIn(req, self.store.open_requests(self.seller))


class ValidationTest(StoreTestCase):
    def test_request_requires_book_and_location(self):
        with self.assertRaises(ValidationError):
            self.new_request(book_id=None)
        with self.assertRaises(ValidationError):
            self.new_request(location=" ")

    def test_max_price_optional_but_numeric(self):
        self.assertIsNone(self.new_request(max_price="").max_price)
        with self.assertRaises(ValidationError):
            self.new_request(max_price="abc")

    def test_offer_needs_contact_and_price_and_allows_any_condition(self):
        req = self.new_request(accepted_condition=Condition.NEW)
        with self.assertRaises(ValidationError):
            self.store.create_offer(self.seller, req.id, "1000", Condition.NEW, "", "", "", "", "")
        with self.assertRaises(ValidationError):
            self.store.create_offer(self.seller, req.id, "", Condition.NEW, "", "", "1", "", "")
        # Flexibilidad: el vendedor puede ofrecer libro usado aunque el lector haya pedido nuevo
        offer = self.store.create_offer(self.seller, req.id, "1000", Condition.USED, "", "", "1", "", "")
        self.assertEqual(offer.book_condition, Condition.USED)

    def test_one_active_offer_per_seller_and_request(self):
        req = self.new_request()
        self.store.create_offer(self.seller, req.id, "1000", Condition.NEW, "", "", "1", "", "")
        with self.assertRaises(ValidationError):
            self.store.create_offer(self.seller, req.id, "900", Condition.NEW, "", "", "1", "", "")

    def test_register_rules(self):
        user = self.store.register("Ana", "ana@demo.cl", "abcd", Role.SELLER, "Concepción")
        self.assertEqual(user.role, Role.SELLER)
        with self.assertRaises(ValidationError):
            self.store.register("Ana", "ana@demo.cl", "abcd", Role.READER)
        with self.assertRaises(PermissionDenied):
            self.store.register("Eva", "eva@demo.cl", "abcd", Role.ADMIN)

    def test_seller_register_requires_location_reader_does_not(self):
        with self.assertRaises(ValidationError):
            self.store.register("Beto", "beto@demo.cl", "abcd", Role.SELLER)
        seller = self.store.register("Beto", "beto@demo.cl", "abcd", Role.SELLER, "Talcahuano")
        self.assertEqual(seller.location, "Talcahuano")
        reader = self.store.register("Cata", "cata@demo.cl", "abcd", Role.READER)
        self.assertEqual(reader.location, "")


class PermissionTest(StoreTestCase):
    def test_roles_are_enforced(self):
        req = self.new_request()
        with self.assertRaises(PermissionDenied):
            self.store.create_request(self.seller, self.book.id, "", Condition.ANY, "X", Delivery.ANY)
        with self.assertRaises(PermissionDenied):
            self.store.create_offer(self.reader, req.id, "1000", Condition.NEW, "", "", "1", "", "")
        with self.assertRaises(PermissionDenied):
            self.store.admin_stats(self.reader)

    def test_reader_cannot_touch_other_readers_requests(self):
        req = self.new_request()
        offer = self.store.create_offer(self.seller, req.id, "1000", Condition.NEW, "", "", "1", "", "")
        with self.assertRaises(PermissionDenied):
            self.store.get_request(self.reader2, req.id)
        with self.assertRaises(PermissionDenied):
            self.store.cancel_request(self.reader2, req.id)
        with self.assertRaises(PermissionDenied):
            self.store.accept_offer(self.reader2, offer.id)

    def test_seller_cannot_cancel_other_sellers_offer(self):
        req = self.new_request()
        offer = self.store.create_offer(self.seller, req.id, "1000", Condition.NEW, "", "", "1", "", "")
        with self.assertRaises(PermissionDenied):
            self.store.cancel_offer(self.seller2, offer.id)
        self.assertEqual(self.store.offers_for_request(self.seller2, req.id), [])

    def test_suspended_user_is_blocked(self):
        self.store.set_user_status(self.admin, self.seller.id, UserStatus.SUSPENDED)
        with self.assertRaises(PermissionDenied):
            self.store.authenticate("vendedor@demo.cl", "1234")
        with self.assertRaises(PermissionDenied):  # sesión abierta también queda bloqueada
            self.store.open_requests(self.seller)


class StateMachineTest(StoreTestCase):
    def test_cancel_request_cancels_active_offers(self):
        req = self.new_request()
        offer = self.store.create_offer(self.seller, req.id, "1000", Condition.NEW, "", "", "1", "", "")
        self.store.cancel_request(self.reader, req.id)
        self.assertEqual(req.status, RequestStatus.CANCELLED)
        self.assertEqual(offer.status, OfferStatus.CANCELLED)
        with self.assertRaises(InvalidTransition):
            self.store.cancel_request(self.reader, req.id)

    def test_cannot_offer_on_resolved_or_accept_twice(self):
        req = self.new_request()
        offer = self.store.create_offer(self.seller, req.id, "1000", Condition.NEW, "", "", "1", "", "")
        self.store.accept_offer(self.reader, offer.id)
        self.store.confirm_deal(self.reader, offer.id)
        with self.assertRaises(ValidationError):
            self.store.create_offer(self.seller2, req.id, "900", Condition.NEW, "", "", "1", "", "")
        with self.assertRaises(InvalidTransition):
            self.store.accept_offer(self.reader, offer.id)
        with self.assertRaises(InvalidTransition):
            self.store.cancel_offer(self.seller, offer.id)

    def test_deal_negotiation_and_desist_flow(self):
        req = self.new_request()
        offer1 = self.store.create_offer(self.seller, req.id, "10000", Condition.NEW, "", "", "1", "", "")
        offer2 = self.store.create_offer(self.seller2, req.id, "12000", Condition.USED, "", "", "2", "", "")

        # Aceptar oferta 1 para coordinar
        self.store.accept_offer(self.reader, offer1.id)
        self.assertEqual(req.status, RequestStatus.IN_DEAL)
        self.assertEqual(offer1.status, OfferStatus.IN_DEAL)
        self.assertEqual(offer2.status, OfferStatus.ON_HOLD)

        # Desistir de la coordinación
        self.store.cancel_deal(self.reader, offer1.id)
        self.assertEqual(offer1.status, OfferStatus.REJECTED)
        self.assertEqual(offer2.status, OfferStatus.PUBLISHED)
        self.assertEqual(req.status, RequestStatus.WITH_OFFERS)

        # Ahora el lector puede aceptar la oferta 2
        self.store.accept_offer(self.reader, offer2.id)
        self.assertEqual(offer2.status, OfferStatus.IN_DEAL)
        self.store.confirm_deal(self.reader, offer2.id)
        self.assertEqual(offer2.status, OfferStatus.ACCEPTED)
        self.assertEqual(req.status, RequestStatus.RESOLVED)

    def test_admin_moderation_traces_role_and_reason(self):
        req = self.new_request()
        self.store.cancel_request(self.admin, req.id, reason="Contenido inapropiado")
        self.assertEqual(req.status, RequestStatus.CANCELLED)
        self.assertEqual(req.canceled_by_role, Role.ADMIN)
        self.assertEqual(req.cancellation_reason, "Contenido inapropiado")
        self.assertTrue(any(e.action == "solicitud_cancelada" for e in self.store.admin_activity(self.admin)))


class AdminAuditTest(StoreTestCase):
    def test_activity_search_filters_entries(self):
        self.new_request()
        found = self.store.admin_activity(self.admin, text="solicitud_publicada")
        self.assertTrue(found)
        self.assertTrue(all("solicitud_publicada" in e.action for e in found))
        self.assertEqual(self.store.admin_activity(self.admin, text="no-existe-xyz"), [])

    def test_export_activity_log_writes_file(self):
        self.new_request()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "registro.log")
            result = self.store.export_activity_log(self.admin, path)
            self.assertTrue(os.path.exists(result))
            with open(result, encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("REGISTRO DE ACTIVIDAD", content)
            self.assertIn("SOLICITUD_PUBLICADA", content)

    def test_only_admin_can_export_activity(self):
        with self.assertRaises(PermissionDenied):
            self.store.export_activity_log(self.reader, "registro.log")


if __name__ == "__main__":
    unittest.main()
