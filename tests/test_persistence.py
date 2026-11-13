import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.persistence import load_store, migrate_legacy_data_file, save_store
from models.store import build_demo_store
from services.books_api import catalog_lookup


class PersistenceTest(unittest.TestCase):
    def test_migrate_legacy_data_file(self):
        with tempfile.TemporaryDirectory() as d:
            legacy_path = os.path.join(d, "data.json")
            new_path = os.path.join(d, "data", "user", "data.json")
            with open(legacy_path, "w", encoding="utf-8") as file:
                file.write("legacy")

            migrate_legacy_data_file(legacy_path, new_path)

            with open(new_path, encoding="utf-8") as file:
                self.assertEqual(file.read(), "legacy")
            self.assertFalse(os.path.exists(legacy_path))

    def test_migration_does_not_overwrite_existing_data(self):
        with tempfile.TemporaryDirectory() as d:
            legacy_path = os.path.join(d, "data.json")
            new_path = os.path.join(d, "data", "user", "data.json")
            os.makedirs(os.path.dirname(new_path))
            with open(legacy_path, "w", encoding="utf-8") as file:
                file.write("legacy")
            with open(new_path, "w", encoding="utf-8") as file:
                file.write("current")

            migrate_legacy_data_file(legacy_path, new_path)

            with open(new_path, encoding="utf-8") as file:
                self.assertEqual(file.read(), "current")
            self.assertTrue(os.path.exists(legacy_path))

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
