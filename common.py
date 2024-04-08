import argparse
import logging
import os
import sys

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

STORAGE_DIR = "storage"
CUSTOM_CONTRACTS_DIR = "custom_contracts"
STANDARD_CONTRACTS_DIR = "standard_contracts"
CUSTOM_CONTRACTS_MD_DIR = os.path.join(STORAGE_DIR, CUSTOM_CONTRACTS_DIR)
STANDARD_CONTRACTS_MD_DIR = os.path.join(STORAGE_DIR, STANDARD_CONTRACTS_DIR)
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

RELEVANCE_JSON_FILE = os.path.join(STORAGE_DIR, "relevance.json")
RISK_ANALYSIS_JSON_FILE = os.path.join(STORAGE_DIR, "risk_analysis.json")


def setup_indexer(debug_log: bool = False):
    if debug_log:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    embed_model = OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=10)
    Settings.embed_model = embed_model


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=str, default="contract.md")
    parser.add_argument("--standard", type=str, default="2020_residential_pa.md")
    return parser
