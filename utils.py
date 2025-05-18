import os
import pandas as pd

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

def load_all_data(location, date):
    base_path = f"./toast_exports/{location}/{date}"
    data = {
        "AllItemsReport": load_csv_if_exists(os.path.join(base_path, "AllItemsReport.csv")),
        "CheckDetails": load_csv_if_exists(os.path.join(base_path, "CheckDetails.csv")),
        "ItemSelectionDetails": load_csv_if_exists(os.path.join(base_path, "ItemSelectionDetails.csv")),
        "KitchenTimings": load_csv_if_exists(os.path.join(base_path, "KitchenTimings.csv")),
        "MenuExport": load_json_if_exists(os.path.join(base_path, "MenuExport.json")),
        "ModifiersSelectionDetails": load_csv_if_exists(os.path.join(base_path, "ModifiersSelectionDetails.csv")),
        "OrderDetails": load_csv_if_exists(os.path.join(base_path, "OrderDetails.csv")),
        "TimeEntries": load_csv_if_exists(os.path.join(base_path, "TimeEntries.csv")),
    }
    return data
