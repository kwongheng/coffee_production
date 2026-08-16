import pandas as pd
from src.paths import RAW_DIR, PROCESSED_DIR
import re

'''
Define all transforms to datasets here
Update TRANSFORM_REGISTRY accordingly
'''

def normalize_column_names(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    """
    Strips whitespace, replaces 'YYYY/YY' season patterns with 'YYYY',
    lowercases, and replaces spaces with underscores.
    """
    print(f"{file_name}: Normalizing column headers...")

    def clean_header(col: str) -> str:
        col = col.strip()

        # Convert '1990/91' -> '1990'
        if re.fullmatch(r"\d{4}/\d{2}", col):
            col = col.split("/")[0]

        # Standardize to lower_snake_case
        return col.lower().replace(" ", "_")

    # do a callback by passing columns to clean_header function
    return df.rename(columns=clean_header)


def normalize_column_dtype(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    """
    Cast float to int, so that all volumes are in int
    """
    print(f"{file_name}: Normalizing column datatype...")

    # Identify columns whose names match the 4-digit year pattern
    target_cols = [
        col for col in df.columns if re.fullmatch(r"\d{4}", str(col).strip())
    ]

    # Filter for columns that are actually float data types
    float_target_cols = [
        col for col in target_cols if pd.api.types.is_float_dtype(df[col])
    ]

    # Cast those specific columns to integer
    if float_target_cols:
        df[float_target_cols] = df[float_target_cols].astype("int64")

    return df


def normalize_country_names(df, file_name):
    '''
    The names for some country don't match the ISO country names
    This need to be manually found by comparing missing country codes
    We need to clean this first before we can add country codes

    Also remove any leading and lagging spaces from country names
    '''
    print(f'{file_name}: Renaming countries to match ISO standards...')

    countries_to_rename = [('Bolivia (Plurinational State of)', 'Bolivia'),
                           ('Tanzania', 'Tanzania, United Republic of'),
                           ('Democratic Republic of Congo', 'Congo, the Democratic Republic of the'),
                           ('Trinidad & Tobago', 'Trinidad and Tobago'),
                           ('Viet Nam', 'Vietnam'),
                           ('United States of America', 'United States Of America'),
                           ('Russian Federation', 'Russia'),
                           ('Czechia','Czech Republic')]

    rename_map = dict(countries_to_rename)
    df['country'] = df['country'].str.strip().replace(rename_map)

    return df


def normalize_bel_lux_data(df, file_name):
    """
    Fills in missing Belgium and Luxembourg coffee consumption values for 1990-1998
    using a constant ratio derived from the 1999-2019 overlap window, splitting the
    Belgium/Luxembourg combined values so that Belgium + Luxembourg == Belgium/Luxembourg
    for each missing year.

    Finally remove the BLEU row as they are no longer required
    """

    print(f"{file_name}: Filling missing values for Belgium/Luxembourg...")

    df = df.copy()

    ratio_years = [str(c) for c in range(1999, 2020)]
    missing_years = [str(c) for c in range(1990, 1999)]
    df[ratio_years + missing_years] = df[ratio_years + missing_years]

    belgium_mask = df["country"] == "Belgium"
    lux_mask = df["country"] == "Luxembourg"
    bleu_mask = df["country"] == "Belgium/Luxembourg"

    if not belgium_mask.any() or not lux_mask.any() or not bleu_mask.any():
        raise ValueError("Could not find one or more of the required country rows.")

    belgium_idx = df.index[belgium_mask][0]
    lux_idx = df.index[lux_mask][0]
    bleu_idx = df.index[bleu_mask][0]

    # Get the total sum for each country to create the ratio
    belgium_total = df.loc[belgium_idx, ratio_years].sum()
    lux_total = df.loc[lux_idx, ratio_years].sum()

    denom = belgium_total + lux_total
    if denom == 0:
        raise ValueError("Cannot compute ratio: Belgium and Luxembourg totals are both zero "
                         "in the 1999-2019 window.")

    belgium_ratio = belgium_total / denom

    # backfill the missing values here
    for year in missing_years:
        combined_val = df.loc[bleu_idx, year]
        if pd.isna(combined_val):
            continue

        # the columns are in int64, we need to keep that in mind
        combined_val = int(combined_val)
        belgium_val = int(round(combined_val * belgium_ratio))
        lux_val = combined_val - belgium_val  # exact remainder -> guarantees the sum

        df.loc[belgium_idx, year] = belgium_val
        df.loc[lux_idx, year] = lux_val

    # removes data from BLEU row
    df.drop(bleu_idx, inplace=True)

    return df


def join_country_codes(df: pd.DataFrame, file_name: str, raw_dir=RAW_DIR) -> pd.DataFrame:
    '''
    Joins country codes to coffee data, so the coffee dataset will have country codes
    '''

    print(f"{file_name}: Joining country codes with table...")

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

    # Sanity check to ensure that there are no null country_codes
    if new_df["country_code"].isna().sum() > 0:
        raise ValueError(f"{file_name}: Some country codes are null!")

    # this will move country_code to index 0, if not ends up in last index
    cols = ['country_code'] + [c for c in new_df.columns if c != 'country_code']

    return new_df[cols]


# update this dict with new functions here
TRANSFORM_REGISTRY = {
    "normalize_column_names":normalize_column_names,
    "normalize_column_dtype": normalize_column_dtype,
    "normalize_country_names": normalize_country_names,
    "normalize_bel_lux_data": normalize_bel_lux_data,
    "join_country_codes": join_country_codes
}


def apply_transforms(df: pd.DataFrame, file_name: str, transform_names: list[str]) -> pd.DataFrame:
    """Apply the required transforms and check for invalid functions"""
    for name in transform_names:
        func = TRANSFORM_REGISTRY.get(name)
        if func is None:
            raise ValueError(f"Unknown transform: {name!r}")
        df = func(df, file_name)
    return df


def transform_file(file_name: str, transform_names: list[str], raw_dir= RAW_DIR,
                    processed_dir = PROCESSED_DIR) -> None:
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
