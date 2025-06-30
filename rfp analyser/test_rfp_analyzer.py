import requests
import os
from pathlib import Path

def test_rfp_analyzer():
    # Test file path
    test_pdf = "test_rfp.pdf"  # Replace with your test RFP PDF
    
    if not os.path.exists(test_pdf):
        print(f"Please place a test RFP PDF file named '{test_pdf}' in the current directory")
        return

    # Base URL
    base_url = "http://localhost:8000"

    # Test document analysis
    print("\nTesting document analysis...")
    with open(test_pdf, "rb") as f:
        files = {"file": (test_pdf, f, "application/pdf")}
        response = requests.post(f"{base_url}/analyze", files=files)
        print(f"Analysis response: {response.json()}")

    # Test query
    print("\nTesting query functionality...")
    test_questions = [
        "What is the scope of work?",
        "What are the technical requirements?",
        "What is the budget for this project?",
        "What are the evaluation criteria?"
    ]

    for question in test_questions:
        response = requests.post(
            f"{base_url}/query",
            json={"question": question}
        )
        print(f"\nQ: {question}")
        print(f"A: {response.json()['answer']}")

    # Test summary
    print("\nTesting summary generation...")
    response = requests.get(f"{base_url}/summary")
    summary = response.json()
    
    print("\nRFP Summary:")
    for section, content in summary.items():
        print(f"\n{section}:")
        print(content)

if __name__ == "__main__":
    test_rfp_analyzer() 