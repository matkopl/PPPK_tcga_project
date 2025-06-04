import os
import io
import pandas as pd
from pymongo import MongoClient
from minio import Minio
from dotenv import load_dotenv
from constants import GENES_OF_INTEREST

load_dotenv()

minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)

bucket = os.getenv("MINIO_BUCKET")

mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client[os.getenv("MONGO_DB")]
col = db[os.getenv("MONGO_COLLECTION")]

objects = minio_client.list_objects(bucket)
inserted = 0
skipped = 0

for obj in objects:
    if not obj.object_name.endswith(".tsv"):
        continue

    cohort = obj.object_name.replace(".tsv", "")
    print(f"Processing {obj.object_name} (cohort: {cohort})")

    try:
        response = minio_client.get_object(bucket, obj.object_name)
        content = io.BytesIO(response.read())
        df = pd.read_csv(content, sep="\t", index_col=0)
        df = df.transpose()

        genes_present = list(set(GENES_OF_INTEREST) & set(df.columns))
        if not genes_present:
            print(f"No target genes in {cohort}, skipping.")
            skipped += 1
            continue

        for pid, row in df.iterrows():
            document = {
                "patient_id": pid,
                "cancer_cohort": cohort,
                "genes": {g: row[g] for g in genes_present if pd.notna(row[g])}
            }
            col.insert_one(document)
            inserted += 1

        print(f"Inserted {len(df)} patients from {cohort}")

    except Exception as e:
        print(f"Failed to process {obj.object_name}: {e}")
        skipped += 1

print(f"Done. Inserted: {inserted} patients. Skipped: {skipped} cohorts.")
