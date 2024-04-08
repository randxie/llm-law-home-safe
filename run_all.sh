echo "Parsing pdf files to markdown"
python parse_pdf.py 

echo "Build index using the processed markdown files"
python build_index.py

echo "Calculate revelance score for custom contract"
python cal_relevance.py

echo "Generate risk report"
python gen_risk_report.py
