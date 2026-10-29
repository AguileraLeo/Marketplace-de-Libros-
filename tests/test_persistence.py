import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from books_api import catalog_lookup
from services.persistence import load_store, save_store
from store import build_demo_store


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


if __name__ == "__main__":
    unittest.main()
