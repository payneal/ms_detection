import unittest
import pathlib
from medicalFormatChanger import MedicalFormatChanger

class TestMedicalFormatChanger(unittest.TestCase):
    def setUp(self):
        self.converter = MedicalFormatChanger()
        self.test_nii_path = pathlib.Path("./data/test_image.nii.gz").resolve()
        self.output_dir = pathlib.Path("./data/test_output_images").resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # Clean up test files
        for file in self.output_dir.iterdir():
            file.unlink()
        self.output_dir.rmdir()

    def test_convert_nii_to_image(self):
        output_images = self.converter.convert_nii_to_image(
            nii_path=self.test_nii_path,
            out_dir=self.output_dir,
            plane="axial",
            output_format="png",
            normalize=True,
            percentile_clip=(1, 99)
        )

        self.assertIsInstance(output_images, list)
        self.assertGreater(len(output_images), 0)

        for img_path in output_images:
            self.assertTrue(img_path.exists())
            with open(img_path, "rb") as f:
                header = f.read(8)
                self.assertTrue(header.startswith(b"\x89PNG\r\n\x1a\n"))    


    def test_dicom_to_nifti(self):
        test_dicom_dir = pathlib.Path("./data/test_dicom_series").resolve()
        output_nifti_path = pathlib.Path("./data/test_output.nii.gz").resolve()

        nifti_path = self.converter.dicom_to_nifti(test_dicom_dir, output_nifti_path)
        self.assertTrue(nifti_path.exists())
        self.assertEqual(nifti_path.suffix, ".gz")


if __name__ == "__main__":
   unittest.main()