import unittest
from msDetection import MSDection

class TestMSDetection(unittest.TestCase):
    def setUp(self):
        self.detector = MSDection()

    def test_detect_empty_data(self):
        data = []
        result = self.detector.detect(data)
        self.assertIn("detections", result)
        self.assertEqual(len(result["detections"]), 0)

    def test_detect_sample_data(self):
        data = [1, 2, 3]  # Sample input data
        result = self.detector.detect(data)
        self.assertIn("detections", result)
        # Further assertions can be added based on expected behavior

if __name__ == '__main__':
    unittest.main()