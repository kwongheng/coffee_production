from src.extract import extract_from_kaggle, extract_from_url
from src.transform import transform_file
from src.load import get_engine, load_file_to_postgres
import yaml
import pandas as pd

CONFIG_FILE = "config.yaml"

def convert_yaml_to_df(yaml_file):

    with open('config.yaml') as f:
        data = yaml.safe_load(f)

    rows = []
    for source_type in ('kaggle_sources', 'url_sources'):
        for name, cfg in data.get(source_type, {}).items():
            row = {'source_type': source_type, 'source_name': name}
            for k, v in cfg.items():
                row[k] = ', '.join(v) if isinstance(v, list) else v
            rows.append(row)

    df = pd.DataFrame(rows)

    return df

def main():

    config = convert_yaml_to_df(CONFIG_FILE)

    # EXTRACT
    print('\nStarting extraction')
    print('*' * 30)

    #for _, source in config["kaggle_sources"].items():
    for _, row in config[config['source_type']=='kaggle_sources'].iterrows():

        new_file_name = None if pd.isna(row["new_file_name"]) else row["new_file_name"]

        extract_from_kaggle(
            kaggle_path=row["dataset_path"],
            file_name=row["file_name"],
            new_file_name=new_file_name
        )

    for _, row in config[config['source_type'] == 'url_sources'].iterrows():

        storage_options = {} if pd.isna(row["storage_options"]) else row["storage_options"]

        extract_from_url(
            url=row["url_path"],
            file_name=row["file_name"],
            storage_options=storage_options
        )

    # TRANSFORM
    print('\nStarting transform')
    print('*'*30)

    all_sources = config[config['source_type'].isin(['url_sources', 'kaggle_sources'])]
    for _, row in all_sources.iterrows():
        # transforms is flattened to strings, convert it back to list
        transform_names = row['transforms'].split(', ') if pd.notna(row['transforms']) else []
        transform_file(row['file_name'], transform_names)

    # LOAD
    print('\nStarting load to database')
    print('*' * 30)
    engine = get_engine()

    all_tables = config[config['source_type'].isin(['url_sources', 'kaggle_sources']) & pd.notna(config['table_name'])]
    for _, row in all_tables.iterrows():
        load_file_to_postgres(row['file_name'], row['table_name'], engine)

if __name__ == "__main__":
    main()

