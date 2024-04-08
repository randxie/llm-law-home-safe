import glob
import os
import pickle

from dotenv import load_dotenv
from llama_parse import LlamaParse
from common import (
    STORAGE_DIR,
    STANDARD_CONTRACTS_DIR,
    LLAMA_CLOUD_API_KEY,
    CUSTOM_CONTRACTS_DIR,
)

load_dotenv()

if __name__ == "__main__":
    result_type = "markdown"  # "markdown" and "text" are available
    parser = LlamaParse(
        api_key=LLAMA_CLOUD_API_KEY,
        result_type=result_type,
    )

    for pdf_dir in [STANDARD_CONTRACTS_DIR, CUSTOM_CONTRACTS_DIR]:
        doc_names = glob.glob(f"{pdf_dir}/*.pdf")

        target_dir = os.path.join(STORAGE_DIR, pdf_dir)
        os.makedirs(target_dir, exist_ok=True)

        for doc_name in doc_names:
            print(f"Parsing pdf: {doc_name}")

            # remove extension and keep the base part
            doc_basename = os.path.basename(doc_name).split(".")[0]
            target_pkl = f"{target_dir}/{doc_basename}.pkl"
            if os.path.exists(target_pkl):
                print(f"File {target_pkl} exists, skipping...")
                continue

            documents = parser.load_data(doc_name)
            pickle.dump(documents, open(target_pkl, "wb"))

            # write text into a markdown file
            if result_type == "markdown":
                output_name = f"{target_dir}/{doc_basename}.md"
            else:
                output_name = f"{target_dir}/{doc_basename}.txt"

            with open(output_name, "w") as f:
                f.write(documents[0].text)
