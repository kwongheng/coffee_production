import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
from src.paths import PROCESSED_DIR

load_dotenv()

def get_engine() -> Engine:

    '''
    Depending on .env, it will load localhost or online DB
    priority is online DB
    '''
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if not DATABASE_URL:
        DB_USER = os.environ.get("DB_USER")
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        DB_HOST = os.environ.get("DB_HOST", "localhost")
        DB_PORT = os.environ.get("DB_PORT", "5432")
        DB_NAME = os.environ.get("DB_NAME")

        if not all([DB_USER, DB_PASSWORD, DB_NAME]):
            raise RuntimeError(
                "Set either DATABASE_URL, or DB_USER/DB_PASSWORD/DB_NAME in .env"
            )

        DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    else:
        DATABASE_URL = f"postgresql+psycopg2://{DATABASE_URL}"

    return create_engine(DATABASE_URL)


def load_file_to_postgres(file_name: str, table_name: str, engine: Engine, processed_dir=PROCESSED_DIR,
                           if_exists: str="replace") -> None:
    """
    Read a processed CSV and load it into a Postgres table.

    if_exists: 'replace' (drop & recreate), 'append', or 'fail'
    """
    df = pd.read_csv(processed_dir / file_name)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    print(f"Loaded {len(df)} rows into '{table_name}' from {file_name}")


# does nothing if called directly
if __name__ == "__main__":
    pass
