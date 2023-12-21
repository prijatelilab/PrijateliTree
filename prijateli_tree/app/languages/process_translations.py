"""This script processes the translations file  and creates a json file for each language."""

# Global imports

import json
import pandas as pd

FILE_PATH = "app/languages/language_6person.xlsx"


class Translator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path, sheet_name="Sheet1", header=0)
