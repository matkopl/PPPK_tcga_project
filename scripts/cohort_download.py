import os
import requests
import gzip
import shutil
from minio import Minio
from dotenv import load_dotenv
from constants import COHORTS

load_dotenv()

client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)
bucket = os.getenv("MINIO_BUCKET")

if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

BASE_URL = "https://tcga.xenahubs.net/download/"
TARGET_FILENAME = "HiSeqV2.gz"
DATA_DIR = "data/batch"
os.makedirs(DATA_DIR, exist_ok=True)

success = []
fail = []

for cohort in COHORTS:
    filename = f"TCGA.{cohort}.sampleMap/{TARGET_FILENAME}"
    url = BASE_URL + filename
    gz_path = os.path.join(DATA_DIR, f"{cohort}.tsv.gz")
    tsv_path = os.path.join(DATA_DIR, f"{cohort}.tsv")

    try:
        print(f"Downloading {cohort} from {url}...")
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(gz_path, "wb") as f:
                f.write(response.content)
            print(f"Saved: {gz_path}")

            with gzip.open(gz_path, 'rb') as f_in, open(tsv_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            print(f"Decompressed to: {tsv_path}")

            client.fput_object(bucket, f"{cohort}.tsv", tsv_path)
            print(f"Uploaded to MiniO: {cohort}.tsv")

            success.append(cohort)
        else:
            print(f"Failed to download {cohort} (HTTP {response.status_code})")
            fail.append(cohort)
    except Exception as e:
        print(f"Error for {cohort}: {e}")
        fail.append(cohort)

log_path = os.path.join(DATA_DIR, "log.txt")
with open(log_path, "w") as log:
    log.write("Successful cohorts:\n")
    log.write("\n".join(success))
    log.write("\n\nFailed cohorts:\n")
    log.write("\n".join(fail))

print(f"Done. Success: {len(success)}, Fail: {len(fail)}")
print(f"Log written to {log_path}")
