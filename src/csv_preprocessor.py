import pandas as pd
import os

class Csv_preprocessor:
    def __init__(self, csv_file_path) -> None:
        self.file_path = csv_file_path

    # Drops rows whose columns
    def drop_invalid_columns(self, safe_name=None):
        if(self.file_path is None):
                return
        
        df = pd.read_csv(self.file_path)
        df = df.dropna()

        if(safe_name == None):
             df.to_csv(self.file_path)
        else:
             df.to_csv(os.getcwd + "/" + safe_name + ".csv")
