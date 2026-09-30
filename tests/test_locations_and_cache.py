"""Pruebas de la Fase 2: Servicios, búsqueda, caché de portadas y normalización de ubicaciones."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from books_api import (
    CACHE_DIR,
    get_cover_cache_path,
    is_cover_cached,
    prefetch_covers,
    search_books,
)
from locations import (
    CHILE_LOCATIONS,
    normalize_location_name,
    proximity_label,
    search_locations,
)


class LocationsTest(unittest.TestCase):
    def test_locations_catalog_not_empty(self):
        self.assertGreater(len(CHILE_LOCATIONS), 50)

    def test_search_locations_case_and_accent_insensitive(self):
        # Búsqueda con y sin tilde
        res_tilde = search_locations("Concepción")
        res_no_tilde = search_locations("concepcion")
        self.assertIn("Concepción (Biobío)", res_tilde)
        self.assertIn("Concepción (Biobío)", res_no_tilde)

    def test_search_locations_substring(self):
        res = search_locations("valp")
        self.assertTrue(any("Valparaíso" in r for r in res))

    def test_normalize_location_name(self):
        norm = normalize_location_name("concepcion")
        self.assertEqual(norm, "Concepción (Biobío)")

    def test_proximity_label_same_comuna(self):
        self.assertEqual(proximity_label("Concepción", "Concepción (Biobío)"), "Misma comuna")

    def test_proximity_label_same_region(self):
        self.assertEqual(proximity_label("Concepción", "Talcahuano (Biobío)"), "Misma región")

    def test_proximity_label_other_region(self):
        self.assertEqual(proximity_label("Concepción", "Santiago (Metropolitana)"), "Otra región (Metropolitana)")

    def test_proximity_label_missing_data(self):
        self.assertEqual(proximity_label("", "Santiago (Metropolitana)"), "")
        self.assertEqual(proximity_label("Concepción", ""), "")
        norm_stgo = normalize_location_name("santiago")
        self.assertEqual(norm_stgo, "Santiago (Metropolitana)")


class CoverCacheTest(unittest.TestCase):
    def test_get_cover_cache_path(self):
        url = "https://covers.openlibrary.org/b/isbn/9788445000663-M.jpg"
        path = get_cover_cache_path(url)
        self.assertIsNotNone(path)
        self.assertTrue(path.startswith(CACHE_DIR))
        self.assertTrue(path.endswith(".jpg"))

    def test_empty_url_returns_none(self):
        self.assertIsNone(get_cover_cache_path(""))
        self.assertFalse(is_cover_cached(""))

    def test_search_books_local_fallback_and_prefetch(self):
        results, origin = search_books("quijote", mode="titulo")
        self.assertGreater(len(results), 0)
        self.assertTrue(any("Quijote" in b["title"] for b in results))


if __name__ == "__main__":
    unittest.main()
