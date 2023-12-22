"""This script processes the translations file  and creates a json file for each language."""

# Global imports

import pandas as pd


FILE_PATH = "app/languages/language_6person.xlsx"


class Translator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path, sheet_name="Sheet1", header=0)

    def parse_file(self):
        """Parses the file and creates a dictionary with the translations."""
        # Drop rows with NaN values
        self.df.dropna(inplace=True, how="all")

    def get_languages(self):
        """Gets the languages from the file."""
        columns = self.df.columns
        self.languages = [column for column in columns if len(column) == 2]
