import streamlit as st
import time
import re
from datetime import datetime
import base64

# Try to import openai
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# --- CONFIGURATION & BRANDING ---
st.set_page_config(
    page_title="Wells Fargo Compass",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SYSTEM PROMPT (The Master Prompt for AI Generation) ---
SYSTEM_PROMPT = """### SYSTEM PROMPT: INTERNAL COMMS & COMPLIANCE SPECIALIST

**ROLE:**
You are the Senior Internal Communications Strategist for Wells Fargo. Your goal is to draft high-quality, publishing-ready internal content that aligns strictly with the bank's strategic voice and regulatory environment.

**CORE VOICE & TONE:**
* **Professional & Grounded:** We are confident but never arrogant. Use clear, active verbs.
* **Empathetic & Inclusive:** We speak *to* employees, not *at* them. Acknowledge challenges where necessary.
* **Concise:** Banking professionals are busy. Get to the point. Avoid corporate fluff ("synergy," "paradigm shift").
* **Transparency:** If news is bad, state it clearly without euphemisms.

**STRICT REGULATORY GUARDRAILS (NON-NEGOTIABLE):**
1.  **No Promissory Language:** NEVER use words like "guarantee," "promise," "ensure," or "certainty" regarding financial outcomes or job security.
2.  **No Financial Advice:** Do not interpret market data as investment advice for employees.
3.  **Future-Looking Statements:** When discussing future projects, always use qualifying language (e.g., "We aim to," "Our goal is," "Subject to approval").
4.  **Data Privacy:** Never request or generate specific PII (Personally Identifiable Information) or specific customer account numbers.

**FORMATTING RULES:**
* Use **Bold** for key takeaways.
* Use bullet points for lists of 3 or more items.
* Subject lines must be punchy and under 50 characters.

**TASK:**
The user will provide a rough set of notes or a topic. You will transform this into a polished internal communication piece (email, memo, or intranet post).

**CRITICAL CHECK BEFORE OUTPUT:**
Before finalizing your response, silently review your draft against the "Regulatory Guardrails" above. If you find a violation, rewrite the sentence immediately.
"""

# --- UTILS ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    if bin_str:
        st.markdown(f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        ''', unsafe_allow_html=True)

# Apply background
set_background('background.png')

# Load logo
logo_b64 = get_base64_of_bin_file("wf_box_logo.png")

# WELLS FARGO THEME INJECTION
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        
        html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
        
        :root {
            --wf-red: #CD1409;
            --wf-gold: #FFC220;
            --wf-gray: #3B3B3B;
            --wf-light-gray: #F4F4F4;
        }

        .header-bar {
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 1.5rem;
            border-bottom: 4px solid var(--wf-red);
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header-logo { height: 45px; width: auto; margin-right: 15px; }
        .header-title { font-size: 1.2rem; font-weight: 700; color: var(--wf-gray); }
        .header-subtitle { font-size: 0.85rem; color: #777; }

        [data-testid="stSidebar"] {
            background-color: rgba(244, 244, 244, 0.95);
            backdrop-filter: blur(10px);
            border-right: 1px solid #ddd;
        }

        div.stButton > button:first-child {
            background-color: var(--wf-red);
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
        }
        div.stButton > button:first-child:hover { background-color: #a00e05; }

        .status-badge { padding: 5px 10px; border-radius: 6px; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
        .status-draft { background-color: #e0e0e0; color: #333; }
        .status-pending { background-color: var(--wf-gold); color: #333; }
        .status-approved { background-color: #2e7d32; color: white; }
        .status-rejected { background-color: var(--wf-red); color: white; }

        .compliance-alert {
            background-color: #ffebee;
            border-left: 5px solid var(--wf-red);
            padding: 12px 16px;
            color: var(--wf-red);
            margin: 12px 0;
            font-weight: 600;
            border-radius: 0 8px 8px 0;
        }

        h1, h2, h3, h4, p, span, div { color: var(--wf-gray); }
        
        .draft-preview {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 2rem;
            border: 1px solid #ddd;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- MOCK DATABASE (SESSION STATE) ---
if "drafts" not in st.session_state:
    st.session_state.drafts = []
if "user_role" not in st.session_state:
    st.session_state.user_role = "Associate"
if "active_draft" not in st.session_state:
    st.session_state.active_draft = None # Stores the currently viewed draft
if "api_mode" not in st.session_state:
    st.session_state.api_mode = "Demo"

# --- HELPER FUNCTIONS ---

SCENARIOS = {
    "🌩️ Crisis: Weather Closure": "Notify Charlotte employees of an early office closure due to incoming severe weather.",
    "📈 Executive: Q3 Results": "Draft a CEO update on strong Q3 financial results, with gratitude to the team.",
    "📋 Policy: Hybrid Work": "Communicate the new 3-day in-office hybrid policy starting next month.",
}

def generate_ai_draft(topic, api_key=None):
    """Generates draft using Mock or Live OpenAI API"""
    
    # --- LIVE MODE ---
    if st.session_state.api_mode == "Live" and api_key and OpenAI:
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": topic}
                ],
                temperature=0.7
            )
            body = response.choices[0].message.content
            # Extract title from first line if it looks like a subject
            lines = body.split('\n')
            title = lines[0].replace("**Subject:**", "").replace("Subject:", "").strip()[:50] if "Subject" in lines[0] else "Draft Communication"
            return {"title": title, "body": body, "flags": check_compliance(body)}
        except Exception as e:
            return {"title": "API Error", "body": str(e), "flags": []}
    
    # --- DEMO MODE (Mock Responses aligned with System Prompt style) ---
    time.sleep(1.0)
    p = topic.lower()
    
    if "weather" in p or "closure" in p:
        return {
            "title": "Office Closure: Charlotte",
            "body": """**Subject:** Office Closure: Charlotte Campus

Team,

Due to **severe weather conditions**, we are closing the Charlotte office at **2:00 PM EST today**.

**Key Actions:**
* Complete urgent tasks and save your work
* Commute home safely while conditions allow
* Continue remotely if your role permits

Your safety is our priority. We aim to resume normal operations tomorrow, pending weather updates.

Stay safe.""",
            "flags": []
        }
    elif "q3" in p or "results" in p:
        return {
            "title": "Q3 Results Update",
            "body": """**Subject:** Q3 Results: Resilient Performance

Team,

I'm proud to share that we delivered **strong Q3 results**.

Our disciplined approach has paid off, demonstrating stability in a volatile market. This reflects your dedication to our customers and our mission.

**Key Highlights:**
* Consumer Banking showed solid growth
* Expense discipline remained strong
* Credit quality stayed resilient

We are well positioned for Q4. Thank you for your continued focus.

Best,
*Leadership*""",
            "flags": []
        }
    elif "hybrid" in p or "policy" in p:
        return {
            "title": "Hybrid Work Update",
            "body": """**Subject:** Hybrid Work Policy Update

Team,

Starting next month, we are shifting to a **3-days in office** hybrid model.

In-person collaboration strengthens our culture and drives innovation. We understand this requires adjustment, and we aim to support you through this transition.

**What This Means:**
* Core in-office days: Tuesday, Wednesday, Thursday
* Remote flexibility: Monday and Friday
* Work with your manager on specific arrangements

Thank you for your flexibility and commitment.""",
            "flags": []
        }
    elif "bonus" in p or "guarantee" in p:
        return {
            "title": "Compensation Update",
            "body": "We are pleased to announce that bonuses are **guaranteed** to increase this year for all staff.",
            "flags": ["guaranteed"]
        }
    else:
        return {
            "title": f"Update: {topic[:30]}",
            "body": f"""**Subject:** Internal Update

Team,

Regarding **{topic}**: We are moving forward as planned.

Further details will be shared via the intranet. Please reach out to your manager with questions.

Best regards.""",
            "flags": []
        }

def check_compliance(text):
    banned = ["guarantee", "promise", "always", "ensure", "never", "risk-free", "certainly"]
    found = [word for word in banned if word in text.lower()]
    return found

# --- UI LAYOUT ---

# 1. HEADER
if logo_b64:
    st.markdown(f'''
    <div class="header-bar">
        <div style="display:flex; align-items:center;">
            <img src="data:image/png;base64,{logo_b64}" class="header-logo">
            <div>
                <div class="header-title">COMPASS</div>
                <div class="header-subtitle">Internal Communications Workbench</div>
            </div>
        </div>
        <div style="font-size:0.85rem; color:#888;">Role: <b>{st.session_state.user_role}</b></div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown('<div class="header-bar"><span class="header-title">🏛️ WELLS FARGO | Compass</span></div>', unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.header("👤 User Profile")
    
    role_selection = st.radio("Simulate Role:", ["Associate (Writer)", "VP (Approver)"])
    if role_selection != st.session_state.user_role:
        st.session_state.user_role = role_selection
        st.session_state.active_draft = None
        st.rerun()

    st.info(f"Logged in as: **{st.session_state.user_role}**")
    
    st.markdown("---")
    st.caption("⚙️ API MODE")
    api_mode = st.radio("Backend:", ["Demo", "Live (OpenAI)"], horizontal=True)
    st.session_state.api_mode = "Live" if "Live" in api_mode else "Demo"
    
    api_key = ""
    if st.session_state.api_mode == "Live":
        api_key = st.text_input("OpenAI API Key", type="password")
        if not api_key:
            st.warning("Enter key for Live mode")
    
    st.markdown("---")
    
    # Pending Actions
    pending_count = sum(1 for d in st.session_state.drafts if d['status'] == 'Pending Review')
    if "VP" in st.session_state.user_role:
        if pending_count > 0:
            st.error(f"🔔 {pending_count} Pending Approval(s)")
        else:
            st.success("✅ All Caught Up")
    
    # Scenario Library for Writers
    if "Associate" in st.session_state.user_role:
        st.markdown("---")
        st.caption("⚡ QUICK SCENARIOS")
        for label, prompt in SCENARIOS.items():
            if st.button(label, use_container_width=True):
                st.session_state.scenario_prompt = prompt
                st.rerun()

# 3. MAIN WORKSPACE

# SCENARIO A: WRITER VIEW
if "Associate" in st.session_state.user_role:
    
    # INPUT AREA
    st.subheader("🖊️ Create New Communication")
    
    default_prompt = st.session_state.get("scenario_prompt", "")
    topic_input = st.text_area("What do you need to write?", value=default_prompt, height=100, placeholder="Ex: Update the team on the delayed Q3 migration...")
    
    if default_prompt:
        st.session_state.scenario_prompt = ""

    col_gen, col_clear = st.columns([1, 4])
    with col_gen:
        if st.button("✨ Generate Draft", type="primary"):
            with st.spinner("Consulting Brand Guidelines..."):
                draft_data = generate_ai_draft(topic_input, api_key if st.session_state.api_mode == "Live" else None)
                
                flags = check_compliance(draft_data['body'])
                
                new_draft = {
                    "id": len(st.session_state.drafts) + 1,
                    "title": draft_data['title'],
                    "body": draft_data['body'],
                    "status": "Draft",
                    "flags": flags,
                    "timestamp": datetime.now().strftime("%H:%M")
                }
                st.session_state.drafts.insert(0, new_draft)
                st.session_state.active_draft = new_draft # OPEN IMMEDIATELY
                st.rerun()

    # --- DRAFT PREVIEW AREA (Main Window) ---
    if st.session_state.active_draft:
        draft = st.session_state.active_draft
        
        st.markdown("---")
        st.subheader(f"📄 {draft['title']}")
        
        badge_class = "status-draft"
        if draft['status'] == "Pending Review": badge_class = "status-pending"
        if draft['status'] == "Approved": badge_class = "status-approved"
        if draft['status'] == "Rejected": badge_class = "status-rejected"
        st.markdown(f"<span class='status-badge {badge_class}'>{draft['status']}</span>", unsafe_allow_html=True)
        
        # Editable Content
        edited_body = st.text_area("Draft Content", value=draft['body'], height=350, key="draft_editor")
        draft['body'] = edited_body # Save edits
        
        # Real-time Compliance
        live_flags = check_compliance(edited_body)
        if live_flags:
            st.markdown(f"<div class='compliance-alert'>🚨 Compliance Issues: {', '.join(live_flags)}</div>", unsafe_allow_html=True)
        else:
            st.success("✅ Compliance Check Passed")
        
        # Copy Function
        with st.expander("📋 Copy Text"):
            st.code(edited_body, language="markdown")
        
        # Actions
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if draft['status'] == "Draft" and not live_flags:
                if st.button("🚀 Submit for Approval", type="primary"):
                    draft['status'] = "Pending Review"
                    st.toast("Sent to Supervisor!", icon="✅")
                    st.session_state.active_draft = None
                    time.sleep(1)
                    st.rerun()
        with col2:
            if st.button("❌ Discard"):
                st.session_state.drafts.remove(draft)
                st.session_state.active_draft = None
                st.rerun()
    
    # --- DRAFTS LIST (Sidebar-like in main view) ---
    st.markdown("---")
    st.markdown("### 📂 Your Drafts")
    if not st.session_state.drafts:
        st.caption("No drafts yet. Generate one above!")
    
    for d in st.session_state.drafts:
        with st.container(border=True):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.markdown(f"**{d['title']}**")
                st.caption(f"{d['timestamp']} | {d['status']}")
            with cols[1]:
                badge = f"<span class='status-badge status-{d['status'].lower().replace(' ', '-')}'>{d['status']}</span>"
                st.markdown(badge, unsafe_allow_html=True)
            with cols[2]:
                if st.button("Open", key=f"open_{d['id']}"):
                    st.session_state.active_draft = d
                    st.rerun()


# SCENARIO B: APPROVER VIEW
else:
    st.subheader("✅ Approval Queue (Supervisor Mode)")
    
    pending_drafts = [d for d in st.session_state.drafts if d['status'] == "Pending Review"]
    
    if not pending_drafts:
        st.success("You're all caught up! No pending approvals.")
    
    for draft in pending_drafts:
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"### {draft['title']}")
                st.caption(f"Submitted at {draft['timestamp']} by Associate")
                st.text_area("Content Preview", draft['body'], height=250, disabled=True, key=f"preview_{draft['id']}")
                
                with st.expander("📋 Copy Text"):
                    st.code(draft['body'], language="markdown")
                
                st.info("🤖 **AI Compliance Check:** Tone is compliant. No red-flag keywords detected.")
                
            with cols[1]:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Approve & Publish", key=f"app_{draft['id']}", type="primary"):
                    draft['status'] = "Approved"
                    st.balloons()
                    st.toast("Approved & Published!", icon="🎉")
                    time.sleep(1)
                    st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌ Request Changes", key=f"rej_{draft['id']}"):
                    draft['status'] = "Rejected"
                    st.toast("Returned to writer.", icon="⚠️")
                    time.sleep(1)
                    st.rerun()
