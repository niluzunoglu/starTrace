import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.impute import SimpleImputer 

from Constants import EXOPLANET_DATA_FILE, MERGED_CSV_PATH
from ExoplanetData import ExoplanetData
from ObservationSource import ObservationSource

class ExoplanetModelTrainer:

    def __init__(self, dataframe: pd.DataFrame, target_column: str, 
                 use_statistical: bool = True, use_fourier: bool = True, 
                 use_wavelet: bool = True, use_manual: bool = True,
                 feature_columns: list = ['koi_period', 'koi_depth', 'koi_impact', 'koi_duration', 'koi_steff', 'koi_srad'],
                 test_size: float = 0.2, validation_size: float = 0.2, random_state: int = 42,
                 hidden_layer_sizes: tuple = (100,), activation: str = 'relu', solver: str = 'adam', learning_rate: str = 'constant',
                 learning_rate_init: float = 0.001, max_iter: int = 300, output_dir: str = "../reports", use_feature_extraction: bool = False):

        self.df = dataframe
        self.target_column = target_column
        self.use_statistical = use_statistical
        self.use_fourier = use_fourier
        self.use_wavelet = use_wavelet
        self.use_manual = use_manual
        self.feature_columns = feature_columns 
        self.test_size = test_size
        self.validation_size = validation_size
        self.random_state = random_state
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation
        self.solver = solver
        self.learning_rate = learning_rate
        self.learning_rate_init = learning_rate_init
        self.max_iter = max_iter
        self.use_feature_extraction = use_feature_extraction
        self.output_dir = output_dir
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join(self.output_dir, self.timestamp)
        os.makedirs(self.run_dir, exist_ok=True)
        self.X_train, self.X_val, self.X_test, self.y_train, self.y_val, self.y_test = self._prepare_data()
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_val_scaled = self.scaler.transform(self.X_val)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        self.model = MLPClassifier(random_state=self.random_state, hidden_layer_sizes=self.hidden_layer_sizes,
                                    activation=self.activation, solver=self.solver, learning_rate=self.learning_rate,
                                    learning_rate_init=self.learning_rate_init, max_iter=self.max_iter)
        self.train_accuracies = []
        self.val_accuracies = []
        self.test_accuracies = []
        
    def _prepare_data(self) -> tuple:

        if self.use_feature_extraction:

            X = pd.DataFrame(index=self.df.index)
            print("X \n",X.head())

            if self.use_statistical:
                X = X.join(self.df.extract_statistical_features(self.feature_columns))
            if self.use_fourier:
                X = X.join(self.df.extract_fourier_features(self.feature_columns))
            if self.use_wavelet:
                X = X.join(self.df.extract_wavelet_features(self.feature_columns))
            if self.use_manual:
                X = X.join(self.df.extract_manual_features())
            
            imputer = SimpleImputer(strategy='mean')
            X = imputer.fit_transform(X)

        X = self.df.drop([self.target_column, "id"], axis=1)
    
        y = self.df[self.target_column]

        print("✅ X (özellikler) boyutu:", len(X))
        print("✅ y (etiketler) boyutu:", len(y))

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=self.random_state, shuffle=False)
        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=self.validation_size / (1 - self.test_size), random_state=self.random_state, shuffle = False)
        return X_train, X_val, X_test, y_train, y_val, y_test

    def train_model(self):

        for epoch in range(self.max_iter):
            self.model.partial_fit(self.X_train_scaled, self.y_train, classes=pd.unique(self.y_train))  # classes parametresi eklendi
            
            y_train_pred = self.model.predict(self.X_train_scaled)
            train_accuracy = accuracy_score(self.y_train, y_train_pred)
            self.train_accuracies.append(train_accuracy)
            
            y_val_pred = self.model.predict(self.X_val_scaled)
            val_accuracy = accuracy_score(self.y_val, y_val_pred)
            self.val_accuracies.append(val_accuracy)
            
            y_test_pred = self.model.predict(self.X_test_scaled)
            test_accuracy = accuracy_score(self.y_test, y_test_pred)
            self.test_accuracies.append(test_accuracy)

            print(f"Epoch {epoch+1}/{self.max_iter}, Train Accuracy: {train_accuracy:.4f}, Validation Accuracy: {val_accuracy:.4f}, Test Accuracy: {test_accuracy:.4f}")

    def evaluate_train_set(self):
        y_pred = self.model.predict(self.X_train_scaled)
        accuracy = accuracy_score(self.y_train, y_pred)
        report = classification_report(self.y_train, y_pred)
        cm = confusion_matrix(self.y_train, y_pred)
        return accuracy, report, cm

    def evaluate_model(self):
        y_pred = self.model.predict(self.X_test_scaled)
        accuracy = accuracy_score(self.y_test, y_pred)
        report = classification_report(self.y_test, y_pred)
        cm = confusion_matrix(self.y_test, y_pred)
        return accuracy, report, cm
    
    def evaluate_validation_set(self):
        y_pred = self.model.predict(self.X_val_scaled)
        accuracy = accuracy_score(self.y_val, y_pred)
        report = classification_report(self.y_val, y_pred)
        cm = confusion_matrix(self.y_val, y_pred)
        return accuracy, report, cm
    
    def save_results(self, test_accuracy: float, test_report: str, test_cm: list, val_accuracy: float, val_report: str, val_cm: list, train_accuracy: float, train_report: str, train_cm: list):         # Metin dosyasına model yapısını ve sonuçları kaydet
        model_summary_path = os.path.join(self.run_dir, "model_summary.txt")
        with open(model_summary_path, "w") as f:
            f.write(f"Model Yapısı:\n")
            f.write(f"Hidden Layer Sizes: {self.hidden_layer_sizes}\n")
            f.write(f"Activation Function: {self.activation}\n")
            f.write(f"Solver: {self.solver}\n")
            f.write(f"Learning Rate: {self.learning_rate}\n")
            f.write(f"Learning Rate Init: {self.learning_rate_init}\n")
            f.write(f"Max Iterations: {self.max_iter}\n")
            f.write(f"\nSon Epoch Train Seti Doğruluğu: {self.train_accuracies[-1]}\n")
            f.write(f"\nSon Epoch Test Seti Doğruluğu: {test_accuracy}\n")
            f.write(f"Test Seti Sınıflandırma Raporu:\n{test_report}\n")
            f.write(f"\nSon Epoch Validation Seti Doğruluğu: {val_accuracy}\n")
            f.write(f"Validation Seti Sınıflandırma Raporu:\n{val_report}\n")
            f.write(f"Test Size: {self.test_size}\n")
            f.write(f"Validation Size: {self.validation_size}\n")
            f.write(f"Random State: {self.random_state}\n")
            f.write(f"\nSon Epoch Train Seti Doğruluğu: {self.train_accuracies[-1]}\n")
            f.write(f"\nSon Epoch Test Seti Doğruluğu: {self.test_accuracies[-1]}\n")

        plt.figure(figsize=(12, 6))
        plt.plot(self.train_accuracies, label='Train Accuracy', color='red')
        plt.plot(self.val_accuracies, label='Validation Accuracy', color='green')
        plt.xlabel('Epoch')
        plt.ylabel('Doğruluk')
        plt.title('Epoch\'a Göre Train ve Validation Doğruluğu')
        plt.legend()
        plt.grid(True)
        accuracy_plot_path = os.path.join(self.run_dir, "accuracy_vs_epoch.png")
        plt.savefig(accuracy_plot_path)
        plt.plot(self.test_accuracies, label="Test Accuracy", color="blue") #test verisi eklendi
        plt.title('Epoch\'a Göre Train, Validation ve Test Doğruluğu')
        plt.close()

        self._plot_confusion_matrix(test_cm, "Test Confusion Matrix", os.path.join(self.run_dir, "test_confusion_matrix.png"))
        self._plot_confusion_matrix(val_cm, "Validation Confusion Matrix", os.path.join(self.run_dir, "validation_confusion_matrix.png"))
        self._plot_confusion_matrix(train_cm, "Train Confusion Matrix", os.path.join(self.run_dir, "train_confusion_matrix.png"))

    def _plot_confusion_matrix(self, cm: list, title: str, filepath: str):
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
        plt.title(title)
        plt.ylabel('Gerçek Etiketler')
        plt.xlabel('Tahmin Edilen Etiketler')
        plt.savefig(filepath)
        plt.close()

    def get_model(self):
        return self.model

    def get_test_data(self):
        return self.X_test_scaled, self.y_test

if __name__ == "__main__":

    try:

        merged_exoplanet_data = ExoplanetData(file_path=MERGED_CSV_PATH, observation_source=ObservationSource.from_string("MERGED"))
        target_column = 'disposition'

        #feature_columns = ['koi_period', 'koi_depth', 'koi_impact', 'koi_duration', 'koi_steff', 'koi_srad']

        feature_columns = [
            "id",
            "period",
            "duration"
            "depth",
            "steff",
            "srad",
            "slogg",
            "model_snr",
            "ra",
            "dec"
        ]
        
        data = merged_exoplanet_data.get_dataframe_with_columns([target_column] + feature_columns)
        data = data.dropna()
        merged_exoplanet_data.update_data(data)
        merged_exoplanet_data.show_target_distribution()

        data[target_column] = data[target_column].astype('category').cat.codes

        trainer = ExoplanetModelTrainer(dataframe=data, 
                                        target_column=target_column,
                                        use_statistical=True, 
                                        use_fourier=True, 
                                        use_wavelet=True, 
                                        use_manual=True,
                                        feature_columns=feature_columns, 
                                        test_size=0.2, 
                                        validation_size=0.2, 
                                        random_state=42,
                                        hidden_layer_sizes=(128,64),
                                        activation='relu', 
                                        solver='adam', 
                                        learning_rate='adaptive',
                                        learning_rate_init=0.01, 
                                        max_iter=500,
                                        use_feature_extraction=False)

        trainer.train_model()

        accuracy, report, test_cm = trainer.evaluate_model()
        val_accuracy, val_report, val_cm = trainer.evaluate_validation_set()
        train_accuracy, train_report, train_cm = trainer.evaluate_train_set()

        trainer.save_results(accuracy, report, test_cm, val_accuracy, val_report, val_cm, train_accuracy, train_report, train_cm)

        print(f"Model Doğruluğu (Train Seti): {train_accuracy}")
        print(f"Model Doğruluğu (Test Seti): {accuracy}")
        print("Sınıflandırma Raporu (Test Seti):\n", report)
        print(f"Model Doğruluğu (Validation Seti): {val_accuracy}")
        print("Sınıflandırma Raporu (Validation Seti):\n", val_report)
        print(f"Raporlar {trainer.run_dir} dizinine kaydedildi.")

    except FileNotFoundError:
        print(f"{EXOPLANET_DATA_FILE} dosyası bulunamadı.")
    except KeyError as e:
        print(f"Sütun hatası: {e}. Lütfen sütun adlarını kontrol edin.")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")