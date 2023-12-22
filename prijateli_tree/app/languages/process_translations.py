"""This script processes the translations file  and creates a json file for each language."""

# Global imports

import pandas as pd


FILE_PATH = "C:/Users/fdmol/Desktop/Prijateli-project/language_6person.xlsx"


class Translator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path, sheet_name="Sheet1", header=0)

    def parse_file(self):
        """Parses the file and creates a dictionary with the translations."""
        # Drop rows with NaN values
        self.df.dropna(inplace=True, how="all")

    def get_languages_and_sections(self):
        """Gets the languages from the file."""
        columns = self.df.columns
        self.languages = [column for column in columns if len(column) == 2]
        self.game_sections = self.df.loc[:, "game_section"].unique()

    def generate_dict(self):
        """Generates a dictionary with the translations."""
        self.parse_file()
        self.get_languages()

        # Create a dictionary for each language
        self.translations = {}
        for language in self.languages:
            self.translations[language] = {}

        # Get the translations


if __name__ == "__main__":
    translator = Translator(FILE_PATH)
    translator.generate_dict()

    print(translator.translations)
