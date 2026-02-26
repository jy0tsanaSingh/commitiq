from app.memory import init_db, save_meeting, save_commitments
from app.risk_engine import detect_risks, calculate_health_score
from app.schemas import Commitment

# Setup
init_db()
meeting_id = save_meeting("Risk Test Meeting")

commitments = [
    Commitment(task="Finish API documentation", owner="Abhishek", deadline="next Friday", priority="high", is_vague=False),
    Commitment(task="Review marketing budget", owner="Geetu", deadline=None, priority="medium", is_vague=True),
    Commitment(task="Follow up with client", owner=None, deadline=None, priority="medium", is_vague=False),
    Commitment(task="Deploy staging environment", owner="Rishabh", deadline="tomorrow", priority="high", is_vague=False),
]

save_commitments(meeting_id, "Risk Test Meeting", commitments)

# Detect risks — pass meeting_id so repeated_topic is accurate
flags = detect_risks(commitments, meeting_id=meeting_id)
score, label = calculate_health_score(flags)

print(f"\nHealth Score: {score} — {label}")
print(f"Total Risk Flags: {len(flags)}\n")

for flag in flags:
    print(f"Type: {flag.type}")
    print(f"Severity: {flag.severity}")
    print(f"Insight: {flag.insight}")
    print("---")