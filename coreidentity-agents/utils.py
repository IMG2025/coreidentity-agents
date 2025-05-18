import os
import pandas as pd
import json

def load_csv_if_exists(path):
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            print(f"⚠️ Error loading {path}: {e}")
    return pd.DataFrame()

def load_json_if_exists(path):
    if os.path.exists(path):
        try:
            return pd.read_json(path)
        except Exception as e:
            print(f"⚠️ Error loading {path}: {e}")
    return {}

def load_all_data(data_dir="./toast_exports"):
    data = {}

    for location in os.listdir(data_dir):
        loc_path = os.path.join(data_dir, location)
        if not os.path.isdir(loc_path):
            continue
        data[location] = {}

        for date in os.listdir(loc_path):
            date_path = os.path.join(loc_path, date)
            if not os.path.isdir(date_path):
                continue

            data[location][date] = {
                "AllItemsReport": load_csv_if_exists(os.path.join(date_path, "AllItemsReport.csv")),
                "CheckDetails": load_csv_if_exists(os.path.join(date_path, "CheckDetails.csv")),
                "OrderDetails": load_csv_if_exists(os.path.join(date_path, "OrderDetails.csv")),
                "KitchenTimings": load_csv_if_exists(os.path.join(date_path, "KitchenTimings.csv")),
                "TimeEntries": load_csv_if_exists(os.path.join(date_path, "TimeEntries.csv")),
                "ItemSelectionDetails": load_csv_if_exists(os.path.join(date_path, "ItemSelectionDetails.csv")),
                "ModifiersSelectionDetails": load_csv_if_exists(os.path.join(date_path, "ModifiersSelectionDetails.csv")),
                "MenuExportV2": load_json_if_exists(
                    next((f for f in [
                        os.path.join(date_path, "MenuExportV2.json"),
                        *[f for f in os.listdir(date_path) if f.startswith("MenuExportV2") and f.endswith(".json")]
                    ] if os.path.exists(f)), "")
                ),
                "MenuExport": load_json_if_exists(
                    next((f for f in [
                        os.path.join(date_path, "MenuExport.json"),
                        *[f for f in os.listdir(date_path) if f.startswith("MenuExport") and f.endswith(".json")]
                    ] if os.path.exists(f)), "")
                )
            }

    return data
