"""
This script reads JSON files from the data/game_data folder and inserts them into a PostgreSQL database.
Each JSON file is treated as a separate table, with each object in the array as a row.

Compatible data from -  https://github.com/adainrivers/poe2-data/tree/main/data
"""

import json
from pathlib import Path
from typing import Any

from pgvector.sqlalchemy import Vector
from settings import DATABASE_URL, GAME_DATA_VECTOR_DIM
from sqlalchemy import JSON, Column, Integer, MetaData, Table, Text, create_engine

engine = create_engine(DATABASE_URL)
metadata = MetaData()

GAME_DATA_FOLDER = Path("/usr/src/app/data/game_data")
TABLE_PREFIX = "gamedata_"


def flatten_json(data: dict[str, Any], prefix: str = "") -> str:
    """Convert nested JSON to flat searchable text"""
    items = []
    for k, v in data.items():
        new_key = f"{prefix}{k}" if prefix else k
        if isinstance(v, dict):
            items.append(flatten_json(v, f"{new_key}_"))
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    items.append(flatten_json(item, f"{new_key}_"))
                else:
                    items.append(str(item))
        else:
            items.append(f"{new_key}:{str(v)}")
    return " ".join(items)


def read_json_file(file_path):
    """Read JSON file and return contents"""
    with open(file_path) as f:
        return json.load(f)


def create_or_update_table(table_name, data_array):
    """Create or update table with JSON data array"""
    # Skip if array is empty
    if not data_array:
        print(f"Skipping {table_name} - empty array")
        return

    table_name = f"{TABLE_PREFIX}{table_name}"

    # Create table with id and searchable_data columns
    table = Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("data", JSON),
        Column("searchable_data", Text),
        Column("embedding", Vector(GAME_DATA_VECTOR_DIM)),
        extend_existing=True,
    )
    metadata.create_all(engine)

    # Insert/Update data with flattened searchable text
    with engine.connect() as conn:
        for item in data_array:
            searchable = flatten_json(item)
            conn.execute(table.insert().values(data=item, searchable_data=searchable))
        conn.commit()


def main():
    # Set path to data folder
    data_folder = Path(GAME_DATA_FOLDER)

    # Process each JSON file
    for json_file in data_folder.glob("*.json"):
        try:
            table_name = json_file.stem  # Get filename without extension
            data_array = read_json_file(json_file)

            if isinstance(data_array, list):
                create_or_update_table(table_name, data_array)
                print(f"Processed {json_file.name} - {len(data_array)} rows")
            else:
                print(f"Skipping {json_file.name} - not an array")
            # ONLY RUN ONCE FOR TESTING
            break
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {json_file.name}")
        except Exception as e:
            print(f"Error processing {json_file.name}: {str(e)}")


if __name__ == "__main__":
    main()
