import json
import os
from typing import List

from jinja2 import Template
from openai import OpenAI
from tqdm import tqdm

from common import (CUSTOM_CONTRACTS_MD_DIR, RELEVANCE_JSON_FILE, RISK_ANALYSIS_JSON_FILE, STANDARD_CONTRACTS_MD_DIR,
                    get_parser)
from utils import get_sections

SYSTEM_MSG = "You are an experienced real-estate lawyer to help a home buyer analyze the risk in their home purchase contract"
INSTRUCTION = """You are provided with a section in a home purchase contract. You need to analyze the risk in the section based on the reference sections from standard home purchase contract from California Association of Realtor.

You can trust the reference sections from the standard contract because that is the industry standard and has been reviewed by legal experts. 

### Section to analyze
{{ cur_contract_section }}
### End of section

### Reference sections from standard contract (separated by ---)
{{ standard_contract_info }}
### End of reference sections

Output a json with the following format: {"explanation": "<explanation>", "risk": "<risk_level>"}
The risk level should be an integer from 1 to 5, where 1 is the lowest risk and 5 is the highest risk.
If the risk level is moderate, you don't need to provide an explanation. Keep you explanation concise and easy for non-legal people to understand.
Use your own experience and only set higher risk level to those unusual terms. If a term involves a common practice in the industry or similar to the standard contract, it should be considered as low risk and assign score to 1. Make sure your analysis is mutually beneficial to both parties.
"""

TEMPL = Template(INSTRUCTION)


def get_risk_analysis(
    cur_contract_section: str,
    all_standard_sections: List[str],
    relevance: List[float],
    k: int = 3,
) -> dict:
    # sort all_standard_sections by relevance
    all_standard_sections = sorted(
        zip(all_standard_sections, relevance),
        key=lambda x: x[1],
        reverse=True,
    )
    top_k_sections = [x[0] for x in all_standard_sections[:k]]

    standard_contract_info = "---\n".join(top_k_sections)
    instruction = TEMPL.render(
        cur_contract_section=cur_contract_section,
        standard_contract_info=standard_contract_info,
    )
    client = OpenAI()
    risk_analysis = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_MSG
            },
            {
                "role": "user",
                "content": instruction
            },
        ],
        response_format={"type": "json_object"},
    )

    return risk_analysis


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    custom_contract_chunks = get_sections(file_path=os.path.join(CUSTOM_CONTRACTS_MD_DIR, args.contract))
    standard_contract_chunks = get_sections(file_path=os.path.join(STANDARD_CONTRACTS_MD_DIR, args.standard))
    relevances = json.load(open(RELEVANCE_JSON_FILE, "rb"))

    results = []
    for idx in tqdm(range(len(custom_contract_chunks))):
        relevance = relevances[idx]["standard_contract_relevance"]
        section_title = relevances[idx]["section_title"]
        cur_contract_section = custom_contract_chunks[section_title]
        resp = get_risk_analysis(
            cur_contract_section,
            standard_contract_chunks,
            relevance=relevance,
            k=5,
        )
        risk_analysis = json.loads(resp.choices[0].message.content)
        risk_analysis["section_title"] = section_title

        results.append(risk_analysis)

    with open(RISK_ANALYSIS_JSON_FILE, "w") as f:
        json.dump(results, f)
