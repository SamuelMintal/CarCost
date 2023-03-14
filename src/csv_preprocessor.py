import pandas as pd
import os

class CsvPreprocessor:   

     @staticmethod
     def prefix_file_name_of(from_path, prefix="Augmented_"):
          SEPARATOR = "/"
          return prefix + from_path.split(SEPARATOR)[-1]

     @staticmethod
     def _get_df(file_path):
          if(file_path is None):
               return
          
          return pd.read_csv(file_path)

     # returns path to which it saved file
     @staticmethod
     def _save_df(df, file_path, save_name):

          if(save_name == None):
               df.to_csv(file_path, header=True, index=False)
               return file_path
          else:
               SEPARATOR = "/"
               old_path = file_path.split(SEPARATOR)
               new_path = SEPARATOR.join(old_path[:-1]) + "/" + save_name
               df.to_csv(new_path, header=True, index=False)
               return new_path
          

     # Drops rows which conatins at least one null
     # Returns file path to the saved file
     @staticmethod
     def drop_null_containing_rows(file_path, save_name=None):          
          df = CsvPreprocessor._get_df(file_path)
          df = df.dropna()          
          return CsvPreprocessor._save_df(df, file_path, save_name)
          

     # Normalizes sepcified column values to [0,1] region
     # Returns file path to the saved file
     @staticmethod
     def normalize_columns(file_path, save_name=None, normalize_columns=["year", "km", "kw"]):
          df = CsvPreprocessor._get_df(file_path)

          if(normalize_columns != None):
               for column_name in normalize_columns:
                    df[column_name] = (df[column_name] - df[column_name].min()) / (df[column_name].max() - df[column_name].min())    

          return CsvPreprocessor._save_df(df, file_path, save_name)

     # one hot encodes specified column values
     # Returns file path to the saved file
     @staticmethod
     def one_hot_encode_columns(file_path, save_name=None, one_hot_columns=["trans", "fuel"]):          
          df = CsvPreprocessor._get_df(file_path)

          # One hot encode specified columns
          for col_name in one_hot_columns:
               # Get the one hot encoded columns
               one_hot_encoded = pd.get_dummies(df[col_name])
               # Drop the original column which we onehot encoded
               df = df.drop(columns=col_name)

               # Concatenate the together
               df = pd.concat([df, one_hot_encoded], axis=1)

          return CsvPreprocessor._save_df(df, file_path, save_name)
     
     # Adds the car which price we will be predicting to the dataframe
     # WARNING: Sets the car's price to None -> if we will call this before 
     # drop_null_containing_rows our car will be drop
     @staticmethod
     def add_car_to_predict(file_path, car_dict, save_name=None):
          df = CsvPreprocessor._get_df(file_path)
          SPECIAL_COLUMN_NAME = "IsCarToPredict"

          # Add column which will make it stand apart from the rest of the dataset
          car_dict[SPECIAL_COLUMN_NAME] = True

          # Now add the same column to the rest of the dataset 
          # but with different value
          df[SPECIAL_COLUMN_NAME] = False

          # Now append the car to the augmented df
          df = df.append(car_dict, ignore_index=True)

          return CsvPreprocessor._save_df(df, file_path, save_name)
     
     # Takes the car to predict from the dataset and returns it with the file path,
     # it also deletes column SPECIAL_COLUMN_NAME both from df and car
     @staticmethod
     def take_out_car_to_predict(file_path, save_name=None):
          df = CsvPreprocessor._get_df(file_path)
          SPECIAL_COLUMN_NAME = "IsCarToPredict"

          car_df = df[df[SPECIAL_COLUMN_NAME]].drop(columns=[SPECIAL_COLUMN_NAME])
          df = df[~df[SPECIAL_COLUMN_NAME]].drop(columns=[SPECIAL_COLUMN_NAME])

          return CsvPreprocessor._save_df(df, file_path, save_name), car_df



"""
def main():
     # Usage example
     sample_car = {
          "price": None,
          "year": 2014, 
          "trans": "Automat", 
          "fuel": "Diesel", 
          "km": 356000, 
          "kw": 77.0,
     }
     abs_path = "C:/Users/samue/Desktop/Skola/others/CarCost/data/Audi_e-tron.csv"
     new_file_name = CsvPreprocessor.prefix_file_name_of(abs_path)

     curr_path = CsvPreprocessor.drop_null_containing_rows(abs_path, new_file_name)
     curr_path = CsvPreprocessor.add_car_to_predict(curr_path, sample_car)
     curr_path = CsvPreprocessor.normalize_columns(curr_path)
     curr_path = CsvPreprocessor.one_hot_encode_columns(curr_path)

     curr_path, car_df = CsvPreprocessor.take_car_to_predict(curr_path)
     print(car_df)
     

if __name__ == "__main__":
     main()
#"""