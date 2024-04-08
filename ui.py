import json
import os

import gradio as gr

from common import CUSTOM_CONTRACTS_MD_DIR, RISK_ANALYSIS_JSON_FILE, get_parser
from utils import get_sections

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    custom_contract_chunks = get_sections(file_path=os.path.join(CUSTOM_CONTRACTS_MD_DIR, args.contract))
    risk_reports = json.load(open(RISK_ANALYSIS_JSON_FILE))

    all_text = []
    for idx, (section_title, section_text) in enumerate(custom_contract_chunks.items()):
        risk_report = risk_reports[idx]
        assert risk_report["section_title"] == section_title

        cur_text = f"{section_title}\n\n{section_text}\n\n"

        explanation = None
        if int(risk_report["risk"]) >= 4:
            cur_text = f'<div style="color: red; border: 2px solid orange; padding: 10px; margin: 10px 0; display: inline-block;"> {cur_text} </div>'
            explanation = (f'<div style="color: orange;"> {risk_report["explanation"]} </div>')

        all_text.append(cur_text)
        if explanation:
            all_text.append(explanation)

    full_text = "\n\n".join(all_text)

    with gr.Blocks() as demo:
        gr.Markdown(full_text)

    demo.launch()
