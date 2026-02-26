from app.memory import init_db, save_meeting, save_commitments, get_all_commitments, search_similar_commitments
from app.schemas import Commitment

# Initialize DB
init_db()

# Create a meeting
meeting_id = save_meeting("Q3 Planning")
print(f"Meeting created: {meeting_id}")

# Create sample commitments
commitments = [
    Commitment(task="Finish API documentation", owner="Abhishek", deadline="next Friday", priority="high", is_vague=False),
    Commitment(task="Review marketing budget", owner="Geetu", deadline=None, priority="medium", is_vague=True),
    Commitment(task="Deploy staging environment", owner="Rishabh", deadline="tomorrow", priority="high", is_vague=False),
]

# Save them
save_commitments(meeting_id, "Q3 Planning", commitments)
print("Commitments saved.")

# Retrieve all
all_commitments = get_all_commitments()
print(f"\nTotal commitments in DB: {len(all_commitments)}")
for c in all_commitments:
    print(f"  - {c['task']} | Owner: {c['owner']} | Status: {c['status']}")

# Test semantic search
print("\nSemantic search: 'who is responsible for documentation?'")
results = search_similar_commitments("who is responsible for documentation?")
print(f"  Found: {results['documents']}")