import errno
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.persistence import load_store, save_store
from models.store import build_demo_store
from services.books_api import catalog_lookup


class PersistenceTest(unittest.TestCase):
    def test_guardar_y_recuperar(self):
        store = build_demo_store(catalog_lookup)
        user = store.register("Ana Ñuñez", "ana@demo.cl", "clave1", "lector")
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.json")
            self.assertIsNone(load_store(path))  # primera vez: no hay archivo
            save_store(store, path)
            loaded = load_store(path)
        self.assertEqual(loaded.user(user.id).name, "Ana Ñuñez")
        self.assertEqual(loaded.authenticate("ana@demo.cl", "clave1").id, user.id)
        self.assertEqual(len(loaded.offers), len(store.offers))
        self.assertGreater(loaded.add_user("X", "x@x.cl", "1234", "lector").id, user.id)  # ids no se repiten

    def test_json_corrupto_no_se_pierde(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.json")
            with open(path, "w") as f:
                f.write("{roto")
            self.assertIsNone(load_store(path))
            self.assertTrue(os.path.exists(path + ".corrupto"))

    def test_json_con_estructura_inesperada_se_respalda(self):
        """Auditoría H13: JSON válido pero que no es un data.json (lista, número, null...)."""
        for contenido in ("[1, 2]", "null", "42", '"texto"', '{"users": ["x"]}', '{"users": 5}'):
            with self.subTest(contenido=contenido), tempfile.TemporaryDirectory() as d:
                path = os.path.join(d, "data.json")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(contenido)
                self.assertIsNone(load_store(path))  # la app arranca con datos de demo, sin caerse
                with open(path + ".corrupto", encoding="utf-8") as f:
                    self.assertEqual(f.read(), contenido)  # el archivo original se conserva intacto

    def test_fallo_de_escritura_no_estropea_lo_ya_guardado(self):
        """Auditoría H08: si el disco falla al guardar, el error sube (la app lo informa) y el último
        data.json queda intacto, que es el estado al que vuelve la app."""
        store = build_demo_store(catalog_lookup)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.json")
            save_store(store, path)
            with open(path, encoding="utf-8") as f:
                antes = f.read()
            store.register("Nueva", "nueva@demo.cl", "1234", "lector")  # cambio que no alcanza a guardarse
            disco_lleno = OSError(errno.ENOSPC, "No space left on device")
            with mock.patch("services.persistence.json.dump", side_effect=disco_lleno):
                with self.assertRaises(OSError):
                    save_store(store, path)
            with open(path, encoding="utf-8") as f:
                self.assertEqual(f.read(), antes)
            recargado = load_store(path)
        self.assertIsNone(recargado.find_user_by_email("nueva@demo.cl"))
        self.assertEqual(len(recargado.users), len(store.users) - 1)

    def test_contacto_por_oferta_se_guarda_y_un_json_anterior_carga_igual(self):
        """SPEC-011: la copia del contacto de cada oferta sobrevive a guardar y cargar; un data.json
        de antes (sin la tabla offer_contacts) carga y usa el contacto del perfil."""
        import json
        store = build_demo_store(catalog_lookup)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.json")
            save_store(store, path)
            self.assertEqual(load_store(path).offer_contacts, store.offer_contacts)
            with open(path, encoding="utf-8") as f:
                datos = json.load(f)
            del datos["offer_contacts"]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(datos, f)
            anterior = load_store(path)
        self.assertEqual(anterior.offer_contacts, {})
        lector = anterior.authenticate("lector@demo.cl", "1234")
        oferta = next(iter(anterior.offers.values()))
        anterior.accept_offer(lector, oferta.id)
        self.assertEqual(anterior.offer_contact(lector, oferta.id).phone, anterior.contacts[oferta.seller_id].phone)


if __name__ == "__main__":
    unittest.main()
