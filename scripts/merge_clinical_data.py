import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
col = db[os.getenv("MONGO_COLLECTION")]

clinical_path = "data/TCGA_clinical_survival_data.tsv"
clinical = pd.read_csv(clinical_path, sep="\t", index_col="bcr_patient_barcode")

updated = 0
not_found = 0

for patient in col.find():
    pid = patient["patient_id"]
    base_pid = pid[:12]
    if base_pid in clinical.index:
        row = clinical.loc[base_pid]
        update_fields = {
            "DSS": int(row["DSS"]) if not pd.isna(row["DSS"]) else None,
            "OS": int(row["OS"]) if not pd.isna(row["OS"]) else None,
            "clinical_stage": row["clinical_stage"] if pd.notna(row["clinical_stage"]) else None
        }
        col.update_one({"_id": patient["_id"]}, {"$set": update_fields})
        updated += 1
    else:
        not_found += 1

print(f"Clinical data merged. Updated: {updated}, Not found: {not_found}")
