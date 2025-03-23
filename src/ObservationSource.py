from enum import Enum

class ObservationSource(Enum):
    
    KEPLER = "Kepler"
    TESS = "TESS"
    K2 = "K2"
    CHEOPS = "CHEOPS"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, label):
        label = label.upper() 
        if label == "KEPLER":
            return cls.KEPLER
        elif label == "TESS":
            return cls.TESS
        elif label == "K2":
            return cls.K2
        elif label == "CHEOPS":
            return cls.CHEOPS
        else:
            raise ValueError(f"Geçersiz gözlem kaynağı: {label}")

if __name__ == "__main__":
    kaynak = ObservationSource.KEPLER
    print(kaynak) 
    print(kaynak.value)  

    kaynak2 = ObservationSource.from_string("tess")
    print(kaynak2)  # TESS

    # Geçersiz bir değer denerseniz hata oluşur
    # kaynak3 = ObservationSource.from_string("Spitzer")  # ValueError: Geçersiz gözlem kaynağı: Spitzer