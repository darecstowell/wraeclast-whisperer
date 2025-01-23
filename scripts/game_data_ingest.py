"""
This script reads JSON files from the data/game_data folder and inserts them into a PostgreSQL database.
Each JSON file is treated as a separate table, with each object in the array as a row.

Compatible data from -  https://github.com/adainrivers/poe2-data/tree/main/data
"""

import json
from pathlib import Path

from settings import DATABASE_URL
from sqlalchemy import JSON, Column, MetaData, Table, create_engine

# Initialize SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()


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

    table_name = f"gamedata_{table_name}"

    # Create table if it doesn't exist
    table = Table(table_name, metadata, Column("data", JSON), extend_existing=True)

    metadata.create_all(engine)

    # Insert/Update data
    with engine.connect() as conn:
        # Clear existing data
        conn.execute(table.delete())
        # Insert each object as a row
        for item in data_array:
            conn.execute(table.insert().values(data=item))
        conn.commit()


def main():
    # Set path to data folder
    data_folder = Path("/usr/src/app/data/game_data")

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

        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {json_file.name}")
        except Exception as e:
            print(f"Error processing {json_file.name}: {str(e)}")


if __name__ == "__main__":
    main()
