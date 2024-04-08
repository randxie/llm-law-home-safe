import os

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from common import STANDARD_CONTRACTS_MD_DIR, setup_indexer

if __name__ == "__main__":
    setup_indexer(debug_log=True)
    print("Starting to build index")

    documents = SimpleDirectoryReader(STANDARD_CONTRACTS_MD_DIR).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()
    print("Index built")
