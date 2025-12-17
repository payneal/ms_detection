import os
import tempfile
import unittest
import urllib.parse

# IMPORTANT: set env BEFORE importing app so IMAGE_ROOT picks it up
# (If you already imported app elsewhere, run tests in a fresh process.)

class TestFlaskGraphQL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.image_root = os.path.join(cls.tmpdir.name, "data", "images")
        os.makedirs(cls.image_root, exist_ok=True)

        os.environ["IMAGE_ROOT"] = cls.image_root

        # Import after env var is set
        from app import app as flask_app
        cls.app = flask_app
        cls.app.config.update(TESTING=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()

    def _write_min_png(self, file_path: str):
        # Minimal PNG signature + some bytes
        png_bytes = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 32)
        with open(file_path, "wb") as f:
            f.write(png_bytes)

    def test_graphql_get_up(self):
        resp = self.client.get("/graphql")
        self.assertEqual(resp.status_code, 200)
        body = resp.data.lower()
        self.assertTrue(b"<html" in body or b"graphiql" in body)

    def test_graphql_post_returns_image_url(self):
        payload = {
            "query": "query($p: String!){ imageUrl(path: $p) }",
            "variables": {"p": "slice_001.png"},
        }
        resp = self.client.post("/graphql", json=payload)
        self.assertEqual(resp.status_code, 200)

        data = resp.get_json()
        self.assertIn("data", data)
        self.assertIn("imageUrl", data["data"])

        url = data["data"]["imageUrl"]
        self.assertIn("/img", url)
        self.assertIn("path=", url)

    def test_img_endpoint_serves_png(self):
        img_path = os.path.join(self.image_root, "slice_001.png")
        self._write_min_png(img_path)

        resp = self.client.get("/img?path=" + urllib.parse.quote("slice_001.png"))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertTrue(resp.headers.get("Content-Type", "").startswith("image/"))

    def test_img_endpoint_404_when_missing(self):
        resp = self.client.get("/img?path=does_not_exist.png")
        self.assertEqual(resp.status_code, 404)

    def test_img_endpoint_415_for_non_image_extension(self):
        bad_path = os.path.join(self.image_root, "not_allowed.txt")
        with open(bad_path, "w") as f:
            f.write("nope")

        resp = self.client.get("/img?path=not_allowed.txt")
        self.assertEqual(resp.status_code, 415)

    def test_img_endpoint_blocks_path_traversal(self):
        resp = self.client.get("/img?path=../secrets.png")
        self.assertIn(resp.status_code, (400, 404))


if __name__ == "__main__":
    unittest.main()
