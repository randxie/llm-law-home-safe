import json
import os
from typing import List

import nltk
import numpy as np
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import NodeWithScore
from nltk.tokenize import sent_tokenize
from rapidfuzz import fuzz
from tqdm import tqdm

from common import (CUSTOM_CONTRACTS_MD_DIR, RELEVANCE_JSON_FILE,
                    STANDARD_CONTRACTS_MD_DIR, STORAGE_DIR, get_parser,
                    setup_indexer)
from utils import get_sections

# Ensure that the necessary NLTK models and corpora are downloaded
nltk.download("punkt")


def split_text_every_n_sentences(text: str, n: int) -> List[str]:
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    # Split the list of sentences into chunks of 'n' sentences
    chunks = [" ".join(sentences[i:i + n]) for i in range(0, len(sentences), n)]

    return chunks


def get_retriever(top_k: int = 10) -> VectorIndexRetriever:
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)

    # load index
    index = load_index_from_storage(storage_context)

    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=top_k,
    )
    return retriever


def calculate_chunk_scores(chunks: List[str], retrieved_items: List[NodeWithScore]) -> np.ndarray:
    chunk_scores = [0.0] * len(chunks)
    for item in retrieved_items:
        for i, chunk in enumerate(chunks):
            if item.text in chunk:
                chunk_scores[i] += item.score
            else:
                chunk_scores[i] += item.score * (fuzz.ratio(item.text, chunk) / 100.0)

    return np.array(chunk_scores)


if __name__ == "__main__":
    setup_indexer(debug_log=False)

    parser = get_parser()
    args = parser.parse_args()
    custom_contract_chunks = get_sections(file_path=os.path.join(CUSTOM_CONTRACTS_MD_DIR, args.contract))
    standard_contract_chunks = get_sections(file_path=os.path.join(STANDARD_CONTRACTS_MD_DIR, args.standard))
    print(f"Number of chunks: {len(custom_contract_chunks)} for custom contract")
    print(f"Number of chunks: {len(standard_contract_chunks)} for standard contract")

    custom_contract_chunk_scores = []
    for section_title, section_text in tqdm(custom_contract_chunks.items()):
        split_texts = split_text_every_n_sentences(section_text, 3)
        print(f"Number of splitted paragraphes: {len(split_texts)}")

        retriever: VectorIndexRetriever = get_retriever()

        retrieve_items = retriever.retrieve(split_texts[0])

        # For each section, check the top related sections in the standard contract
        chunk_scores = calculate_chunk_scores(standard_contract_chunks, retrieve_items)

        for i, split_text in enumerate(split_texts[1:]):
            retrieve_items = retriever.retrieve(split_text)
            chunk_scores += calculate_chunk_scores(standard_contract_chunks, retrieve_items)

        custom_contract_chunk_scores.append({
            "section_title": section_title,
            "standard_contract_relevance": chunk_scores.tolist(),
        })

    with open(RELEVANCE_JSON_FILE, "w") as f:
        json.dump(custom_contract_chunk_scores, f)
