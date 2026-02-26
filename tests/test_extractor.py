from app.extractor import extract_commitments

# Read from sample transcript
with open("sample_transcripts/product_planning.txt", "r") as f:
    transcript = f.read()

commitments = extract_commitments(transcript)

print(f"\nExtracted {len(commitments)} commitments:\n")
for c in commitments:
    print(f"Task: {c.task}")
    print(f"Owner: {c.owner}")
    print(f"Deadline: {c.deadline}")
    print(f"Priority: {c.priority}")
    print(f"Vague: {c.is_vague}")
    print("---")