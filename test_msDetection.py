import unittest
import pathlib
from msDetection import MSDection
from libary.util.medicalFormatChanger import MedicalFormatChanger

class TestMSDetection(unittest.TestCase):
    def setUp(self):
        self .changer = MedicalFormatChanger()
        self.detector = MSDection(
            dicom_path=pathlib.Path("./data/dicom").resolve(), 
            nifti_output_path=pathlib.Path("./data/nifti").resolve(), 
            image_output_path=pathlib.Path("./data/images").resolve())  


    def tearDown(self):
        # Clean up test files
        for file in self.detector.nifti_output_path.iterdir(): file.unlink()   

        # delete csv file if created
        csv_file = pathlib.Path("scan_manifest.csv")
        if csv_file.exists(): csv_file.unlink()  
        
        # clean up created images
        for file in self.detector.image_output_path.iterdir(): file.unlink()

        # reset detector
        self.detector = None
        return super().tearDown()       
    

    def image_conversion_test(self, path):
        with open(path, "rb") as f:
            header = f.read(8)

        # PNG signature
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            is_png = True
            is_jpeg = False

        # JPEG signature
        elif header.startswith(b"\xff\xd8"):
            is_png = False
            is_jpeg = True

        else:
            is_png = is_jpeg = False

        return (is_png or is_jpeg)


    def test_pipe_line(self):
        
        # ingest_and_harmonize
        records = self.detector.ingest_and_harmonize()
        self.assertIsNotNone(records)
        # confirm this is a dataframe with expected columns
        expected_columns = {"patient_id", "date", "series_name", "nifti_path", "voxel_x", "voxel_y", "voxel_z", "shape"}
        self.assertTrue(set(records.columns).issuperset(expected_columns))  

        # check .gz files are created in nifti_output_path  
        nifti_files = list(self.detector.nifti_output_path.glob("*.nii.gz"))  
        self.assertGreater(len(nifti_files), 0)
      
        # check .nii file to jpeg conversion
        jpeg_location = self.changer.convert_nii_to_image(nifti_files[0], "./data/images/")
        self.assertTrue(self.image_conversion_test(jpeg_location[0]))

        # check what this is ... go through all templates later 
        # self.changer.convert_nii_to_image("./data/templates/MNI152_T1_1mm.nii.gz", "./data/hold/")

        # preprocess_and_register
        preproc_df = self.detector.preprocess_and_register()
        self.assertTrue(preproc_df)
    
    
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