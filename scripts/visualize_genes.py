from pymongo import MongoClient
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
col = client[os.getenv("MONGO_DB")][os.getenv("MONGO_COLLECTION")]

def visualize(patient_id):
    data = col.find_one({"patient_id": patient_id})
    if not data:
        print(f"Patient {patient_id} not found.")
        print("Available sample IDs:")
        for doc in col.find().limit(5):
            print("-", doc["patient_id"])
        return

    genes = data["genes"]
    plt.figure(figsize=(10, 5))
    plt.bar(genes.keys(), genes.values(), color="skyblue")
    plt.xticks(rotation=45)
    plt.title(f"Gene Expression for {patient_id}")
    plt.xlabel("Genes")
    plt.ylabel("Expression Level")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    pid = input("Enter patient ID (e.g. TCGA-OR-A5LC-01): ").strip()
    visualize(pid)
