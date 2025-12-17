import unittest
import pathlib
from msDetection import MSDection

class TestMSDetection(unittest.TestCase):
    def setUp(self):
        self.detector = MSDection(
            dicom_path=pathlib.Path("./data/dicom").resolve(), 
            nifti_output_path=pathlib.Path("./data/nifti").resolve())


    def tearDown(self):
        # Clean up test files
        for file in self.detector.nifti_output_path.iterdir(): file.unlink()   

        # delete csv file if created
        csv_file = pathlib.Path("scan_manifest.csv")
        if csv_file.exists(): csv_file.unlink()  
        
        # reset detector
        self.detector = None
        return super().tearDown()       
    

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