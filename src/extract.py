from pathlib import Path
import pandas as pd
import kagglehub
from kagglehub import KaggleDatasetAdapter
from src.paths import RAW_DIR

def extract_from_kaggle(kaggle_path: str, file_name: str, new_file_name: str = '') -> None:

    # Load data from kaggle
    print(f'extracting from kaggle: {kaggle_path}/{file_name}')
    df = kagglehub.dataset_load(
      KaggleDatasetAdapter.PANDAS,
      kaggle_path,
      file_name,
    )

    # if new file name, save with that new name
    file_to_save = new_file_name or file_name

    print(f'saving file to: {RAW_DIR}/{file_to_save}')
    df.to_csv(RAW_DIR / file_to_save, index=False)


def extract_from_url(url: str, file_name: str, storage_options: dict) -> None:

    print(f'extracting from url: {url}')
    df = pd.read_csv(url, storage_options=storage_options)

    print(f'saving file to: {RAW_DIR}/{file_name}')
    df.to_csv(RAW_DIR / file_name, index=False)

# does nothing if called directly
if __name__ == "__main__":
    pass

