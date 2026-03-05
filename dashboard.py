import streamlit as st
import requests

API_URL = "https://commitiq-api-txrx.onrender.com/api/v1"  #"http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="CommitIQ",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 CommitIQ")
st.caption("Cross-Meeting Execution Intelligence Engine")
st.divider()

# ─── Tabs ─────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Health Score",
    "📥 Ingest Meeting",
    "📋 Commitments",
    "💬 Ask CommitIQ"
])


# ─── Tab 1: Health Score ──────────────────────────────────────

with tab1:
    st.subheader("Execution Health Score")

    if st.button("Refresh Score"):
        response = requests.get(f"{API_URL}/health-score")
        data = response.json()

        score = data["health_score"]
        label = data["health_label"]
        total = data["total_commitments"]
        risks = data["total_risks"]

        # Color based on label
        if label == "Healthy":
            color = "green"
        elif label == "At Risk":
            color = "orange"
        else:
            color = "red"

        st.markdown(
            f"<h1 style='color:{color}; font-size:80px'>{score}</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h3 style='color:{color}'>{label}</h3>",
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        col1.metric("Total Commitments", total)
        col2.metric("Active Risk Flags", risks)

        # Show risks
        st.divider()
        st.subheader("Active Risk Flags")
        risks_response = requests.get(f"{API_URL}/risks")
        risks_data = risks_response.json()

        if risks_data["total_risks"] == 0:
            st.success("No risks detected.")
        else:
            for risk in risks_data["risks"]:
                if risk["severity"] == "high":
                    st.error(f"🔴 {risk['type'].upper()} — {risk['insight']}")
                else:
                    st.warning(f"🟡 {risk['type'].upper()} — {risk['insight']}")


# ─── Tab 2: Ingest Meeting ────────────────────────────────────

with tab2:
    st.subheader("Ingest a Meeting Transcript")

    meeting_title = st.text_input(
        "Meeting Title",
        placeholder="e.g. Q3 Product Planning"
    )

    transcript = st.text_area(
        "Paste Meeting Transcript",
        height=200,
        placeholder="Paste raw meeting transcript or notes here..."
    )

    if st.button("Extract Commitments"):
        if not meeting_title or not transcript:
            st.warning("Please enter both meeting title and transcript.")
        else:
            with st.spinner("Extracting commitments..."):
                response = requests.post(
                    f"{API_URL}/ingest",
                    json={
                        "meeting_title": meeting_title,
                        "content": transcript
                    }
                )
                data = response.json()

            # Health Score
            score = data["health_score"]
            label = data["health_label"]

            if label == "Healthy":
                color = "green"
            elif label == "At Risk":
                color = "orange"
            else:
                color = "red"

            st.markdown(
                f"<h2 style='color:{color}'>Health Score: {score} — {label}</h2>",
                unsafe_allow_html=True
            )

            st.success(f"Extracted {data['commitments_extracted']} commitments")

            # Commitments
            st.subheader("Extracted Commitments")
            for c in data["commitments"]:
                with st.expander(f"📌 {c['task']}"):
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Owner:** {c['owner'] or '⚠️ Unassigned'}")
                    col2.write(f"**Deadline:** {c['deadline'] or '⚠️ Not set'}")
                    col3.write(f"**Priority:** {c['priority']}")
                    if c["is_vague"]:
                        st.warning("⚠️ This commitment is vague")

            # Risk Flags
            if data["risk_flags"]:
                st.subheader("Risk Flags")
                for flag in data["risk_flags"]:
                    if flag["severity"] == "high":
                        st.error(f"🔴 {flag['insight']}")
                    else:
                        st.warning(f"🟡 {flag['insight']}")


# ─── Tab 3: Commitments ───────────────────────────────────────

with tab3:
    st.subheader("All Commitments")

    owner_filter = st.text_input(
        "Filter by Owner",
        placeholder="e.g. Abhishek (leave empty for all)"
    )

    if st.button("Load Commitments"):
        url = f"{API_URL}/commitments"
        if owner_filter:
            url += f"?owner={owner_filter}"

        response = requests.get(url)
        data = response.json()

        st.write(f"**Total:** {data['total']} commitments")

        for c in data["commitments"]:
            with st.expander(f"📌 {c['task']}"):
                col1, col2, col3 = st.columns(3)
                col1.write(f"**Owner:** {c['owner'] or '⚠️ Unassigned'}")
                col2.write(f"**Deadline:** {c['deadline'] or '⚠️ Not set'}")
                col3.write(f"**Status:** {c['status']}")
                st.write(f"**Meeting:** {c['meeting_title']}")
                st.write(f"**Priority:** {c['priority']}")


# ─── Tab 4: Ask CommitIQ ──────────────────────────────────────

with tab4:
    st.subheader("Ask CommitIQ")
    st.caption("Ask anything about your commitments across all meetings")

    question = st.text_input(
        "Your Question",
        placeholder="e.g. What has Abhishek committed to this month?"
    )

    if st.button("Ask"):
        if not question:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": question}
                )
                data = response.json()

            st.markdown("### Answer")
            st.success(data["answer"])
