import unittest
import os
import time

from . import fixture_path, compare_files

from enebootools import mergetool

class TestMergeTool(unittest.TestCase):
    """TestPNBuffer Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        
        

    def test_file_py(self) -> None:
        """Basic test."""

        fichero_base = fixture_path('base.py')
        fichero_patch = fixture_path('base_patch.py')
        fichero_resultado = fixture_path('base_result.py')
        fichero_resultado_ok = fixture_path('base_result_ok.py')

        tool_interface = mergetool.MergeToolInterface()
        tool_interface.verbosity=100
        tool_interface.set_output_file(fichero_resultado)
        self.assertTrue(tool_interface.do_file_patch("PY",fichero_base,fichero_patch))
        tool_interface.output.close()   
        self.assertTrue(compare_files(fichero_resultado, fichero_resultado_ok))
    
    def test_file_def_py(self) -> None:
        """Basic test."""

        fichero_base = fixture_path('base_def.py')
        fichero_patch = fixture_path('base_def_patch.py')
        fichero_resultado = fixture_path('base_def_result.py')
        fichero_resultado_ok = fixture_path('base_def_result_ok.py')

        tool_interface = mergetool.MergeToolInterface()
        tool_interface.verbosity=100
        tool_interface.set_output_file(fichero_resultado)
        
        self.assertTrue(tool_interface.do_file_patch("PY",fichero_base,fichero_patch))
        tool_interface.output.close()
        self.assertTrue(compare_files(fichero_resultado, fichero_resultado_ok))
    
    def test_file_model_py(self) -> None:
        """Basic test."""

        fichero_base = fixture_path('base_model.py')
        fichero_patch = fixture_path('base_model_patch.py')
        fichero_resultado = fixture_path('base_model_result.py')
        fichero_resultado_ok = fixture_path('base_model_result_ok.py')

        tool_interface = mergetool.MergeToolInterface()
        tool_interface.verbosity=100
        tool_interface.set_output_file(fichero_resultado)
        self.assertTrue(tool_interface.do_file_patch("PY",fichero_base,fichero_patch))
        tool_interface.output.close()
        self.assertTrue(compare_files(fichero_resultado, fichero_resultado_ok))
    
    
    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        
        #file_names_list = ['base_result.py','base_def_result.py','base_models_result.py']
        #for file_name in file_names_list:
        #    file_path = fixture_path(file_name)
        #    if os.path.exists(file_path):
        #        print("Borrando", file_name, os.stat(file_path).st_size)
        #        os.remove(file_path)
