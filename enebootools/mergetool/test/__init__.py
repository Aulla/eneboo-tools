"""Test for database package."""

import os
import time


def fixture_path(*path: str) -> str:
    """
    Get fixture path for this test folder.
    """
    basedir = os.path.realpath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, "fixtures", *path)
    return filepath

def compare_files(file_name_1, file_name_2):
    file_1 = open(file_name_1, 'rb')
    data_file_1 = file_1.read()
    file_1.close()

    file_2 = open(file_name_2, 'rb')
    data_file_2 = file_2.read()
    file_2.close()

    return data_file_1 == data_file_2


