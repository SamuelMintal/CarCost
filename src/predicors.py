import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
import tensorflow as tf

from csv_preprocessor import CsvPreprocessor



class K_nearest_neighbours:
        
    # Returns Euclidean distance between 2 dataframe entries ~ vehicles
    @staticmethod
    def _distance(elem_1: pd.DataFrame, elem_2: pd.DataFrame):
        dist = 0

        for key in elem_1.keys():
            if(key == "price"):
                continue

            if(key == "year" or key == "km" or key == "kw"):
                weight = 1
            else:
                weight = 0.1            

            dist += weight * abs(elem_1[key] - elem_2[key])

        return dist
    
    # Preprocesses the data
    # Returns df of car_to_predict and csv_file
    @staticmethod
    def _preprocess_data(car_to_predict: dict, csv_file_path: str):
        new_file_name = CsvPreprocessor.prefix_file_name_of(csv_file_path)

        curr_path = CsvPreprocessor.drop_null_containing_rows(csv_file_path, new_file_name)
        curr_path = CsvPreprocessor.add_car_to_predict(curr_path, car_to_predict)
        curr_path = CsvPreprocessor.normalize_columns(curr_path)
        curr_path = CsvPreprocessor.one_hot_encode_columns(curr_path)
        curr_path, car_df = CsvPreprocessor.take_out_car_to_predict(curr_path)

        return (car_df, CsvPreprocessor._get_df(curr_path))

    # Returns array of k dictionaries
    # with keys: dist, price
    @staticmethod
    def _get_closest_k_neighbours(car_df: pd.DataFrame, data_df: pd.DataFrame, k) -> np.array:
        
        def comparator(elem):
            return elem["dist"]

        res = []
        for _, data_entry in data_df.iterrows():
            res.append({
                "dist": K_nearest_neighbours._distance(car_df.iloc[0], data_entry),
                "price": data_entry["price"]
            })

        # Now I have to sort the array based on distance
        res.sort(key=lambda x: x.get("dist"), reverse=True)

        return np.array(res)[-k:]
    
    # Returns expected price from the neighbours array
    @staticmethod
    def _infer_price_from(neighbours: np.array, mode: str):
        
        match mode:
            case "AVG":
                return np.average([elem["price"] for elem in neighbours])
            case "WEIGHTED":
                dist_sum = np.sum([elem["dist"] for elem in neighbours])

                if(dist_sum == 0):
                    return neighbours[0]["price"]
                else:
                    return np.sum([(elem["dist"] / dist_sum) * elem["price"] for elem in neighbours])
            

    @staticmethod
    def predict_price_of(car_to_predict: dict, csv_file_path: str, infer_mode="WEIGHTED", k=3):

        # Firstly preprocess car_to_predict together with specified csv
        car_df, data_df = K_nearest_neighbours._preprocess_data(car_to_predict, csv_file_path)

        # Now get the closest k neighbours from the sepcifies dataset 
        k_nearest_neighbours = K_nearest_neighbours._get_closest_k_neighbours(car_df, data_df, k)

        # Infer price based on the found closest k neighbours
        expected_price = K_nearest_neighbours._infer_price_from(k_nearest_neighbours, infer_mode)

        # Return infered price
        return expected_price


class Neural_network_predictor:
    
    # neurons_layers is an array which whose len is number of layers and [i] is number of neurons in i-th layer
    def __init__(self, neurons_layers, n_epochs, csv_file_path) -> None:
        self.neurons_layers = neurons_layers
        self.n_epochs = n_epochs
        self.csv_file_path = csv_file_path
        
        self.trained = False
        self.model = None

    # Preprocesses the data
    # Returns df of car_to_predict and csv_file
    @staticmethod
    def _preprocess_data(car_to_predict: dict, csv_file_path: str):
        new_file_name = CsvPreprocessor.prefix_file_name_of(csv_file_path)

        curr_path = CsvPreprocessor.drop_null_containing_rows(csv_file_path, new_file_name)
        curr_path = CsvPreprocessor.add_car_to_predict(curr_path, car_to_predict)
        curr_path = CsvPreprocessor.normalize_columns(curr_path)
        curr_path = CsvPreprocessor.one_hot_encode_columns(curr_path)
        curr_path, car_df = CsvPreprocessor.take_out_car_to_predict(curr_path)

        return (car_df, CsvPreprocessor._get_df(curr_path))

    def _set_specified_model(self, inputs_shape):
        
        inputs = tf.keras.Input(shape=inputs_shape)

        x = inputs
        for n_neurons in self.neurons_layers:
            x = tf.keras.layers.Dense(units=n_neurons, activation="relu")(x)

        outputs = tf.keras.layers.Dense(units=1, activation=None)(x)

        self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(
                learning_rate=tf.keras.optimizers.schedules.CosineDecay(
                    0.001, self.n_epochs,
                )
            ),
            loss="mse",
            metrics=["mae"]
        )


    # Trains self.model
    def _train_network(self, dataset: np.array, targets: np.array):

        self.model.fit(dataset, targets, epochs=self.n_epochs)
        self.trained = True
        
    def predict_price_of(self, car_to_predict, retrain=False):

        if(not self.trained or retrain):
            # Firstly preprocess car_to_predict together with specified csv
            car_df, data_df = Neural_network_predictor._preprocess_data(car_to_predict, self.csv_file_path)
            inputs_shape = np.array(car_df).shape

            # Now set and train the network on the dataset 
            self._set_specified_model(inputs_shape)

            prices = data_df.pop("price")
            self._train_network(np.array(data_df), np.array(prices))

        # Infer price based on the trained NN
        expected_price = self.model([np.array(car_df)])[0]

        # Return infered price
        return expected_price



def main():
    # Usage example

    # True params from dataset
    # 2775	2007	Manuál	Diesel	190857	51
    sample_car = {
          "price": None,
          "year": 2007, 
          "trans": "Manuál", 
          "fuel": "Diesel", 
          "km": 190857, 
          "kw": 51,
    }
    abs_path = "C:/Users/samue/Desktop/Skola/others/CarCost/data/Škoda_Fabia (Všetky modely).csv"

    predicted_price = K_nearest_neighbours.predict_price_of(sample_car, abs_path, infer_mode="WEIGHTED", k=5)
    print(f"Predicted price with infer_mode=WEIGHTED and k=5 is {predicted_price}")

    predicted_price = K_nearest_neighbours.predict_price_of(sample_car, abs_path, infer_mode="AVG", k=5)
    print(f"Predicted price with infer_mode=AVG and k=5 is {predicted_price}")

if __name__ == "__main__":
    main()