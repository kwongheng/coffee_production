from pathlib import Path

import pandas as pd

# Project root = one level up from this file's directory (src/ -> project/)
# avoid using relative paths like ../data/raw/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# we are using pathlib object not strings
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

def clean_columns(df, file_name):
    """
    Replace spaces with underscores
    For nnnn/nnnn from year column like 2019/20, we take 2019
    Update all columsn to lowercase
    """
    new_cols = {}

    print(f'{file_name}: Cleaning columns in...')
    for col in df.columns:
        c = col.strip()
        # important to check that we are dealing with nnnn/nn format
        if "/" in c and c[0].isdigit():
            c = c.split('/')[0][:2] + c.split('/')[1]
        else:
            c = c.strip().lower().replace(" ", "_")
        new_cols[col] = c
    df = df.rename(columns=new_cols)

    return df

def clean_country_codes(df, file_name):
    '''
    The names for some country don't match the ISO country names
    This need to be manually found by comparing missing country codes
    We need to clean this first before we can add country codes
    '''
    countries_to_rename = [('Bolivia (Plurinational State of)', 'Bolivia'),
                           ('Tanzania', 'Tanzania, United Republic of'),
                           ('Democratic Republic of Congo', 'Congo, the Democratic Republic of the'),
                           ('Trinidad & Tobago', 'Trinidad and Tobago'),
                           ('Viet Nam', 'Vietnam')]

    print(f'{file_name}: Renaming countries to match ISO standards...')
    rename_map = dict(countries_to_rename)
    df['country'] = df['country'].replace(rename_map)

    return df

def join_country_codes(df, file_name, raw_dir=DEFAULT_RAW_DIR, **kwargs):
    '''
    Joins country codes to coffee data
    '''

    print(f'{file_name}: Joining country codes with table...')

    # read country and country codes, drop other columns
    cc_df = pd.read_csv(raw_dir / "country_codes.csv")
    cc_df = cc_df.rename(columns={
        'English short name lower case': 'country',
        'Alpha-3 code': 'country_code'
    })
    cc_df = cc_df[['country', 'country_code']]

    new_df = df.merge(
        cc_df,
        left_on='country',
        right_on='country',
        how='left'
    )

    # this will move country_code to index 0, if not ends up in last index
    cols = ['country_code'] + [c for c in new_df.columns if c != 'country_code']
    new_df = new_df[cols]

    return new_df

def reduce_co2_data(df, file_name):
    return df

TRANSFORM_REGISTRY = {
    "clean_columns": clean_columns,
    "clean_country_codes": clean_country_codes,
    "join_country_codes": join_country_codes,
    "reduce_co2_data": reduce_co2_data,
}

def apply_transforms(df, file_name, transform_names):
    """Apply the required transforms and check for invalid functions"""
    for name in transform_names:
        func = TRANSFORM_REGISTRY.get(name)
        if func is None:
            raise ValueError(f"Unknown transform: {name!r}")
        df = func(df, file_name)
    return df

def transform_file(file_name, transform_names, raw_dir= DEFAULT_RAW_DIR,
                    processed_dir = DEFAULT_PROCESSED_DIR):
    """loop all required transforms, apply transforms and finally saved to processed folder"""
    try:
        df = pd.read_csv(raw_dir / file_name)
        if transform_names:
            df = apply_transforms(df, file_name, transform_names)
        df.to_csv(processed_dir / file_name, index=False)
    except FileNotFoundError:
        print(f"File {raw_dir / file_name} not found")


# does nothing if called directly
if __name__ == "__main__":
    pass
