from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
load_lab_env(ROOT)

st.set_page_config(
    page_title="IT Helpdesk Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Design System based on ui-ux-pro-max and specified palette
# Background: #FFFFFF (main), #F0F7FC (secondary)
# Surface/Card: #E3F0FA
# Border: #CFE3F2
# Primary: #4A9FE0
# Primary hover: #2E7DC4
# Text primary: #1E2A38
# Text secondary: #5C7288
# Accent: #7ED6C4
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1E2A38;
}

.stApp {
    background: linear-gradient(180deg, #FFFFFF 0%, #F0F7FC 100%);
}

section[data-testid="stSidebar"] {
    background-color: #F0F7FC;
    border-right: 1px solid #CFE3F2;
}

/* Header & Card styles */
.header-container {
    background: linear-gradient(135deg, #FFFFFF 0%, #E3F0FA 100%);
    border: 1px solid #CFE3F2;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(74, 159, 224, 0.08);
}
.header-title {
    color: #1E2A38;
    font-size: 24px;
    font-weight: 700;
    margin: 0;
}
.header-caption {
    color: #5C7288;
    font-size: 13px;
    margin-top: 4px;
}

/* Chat Bubbles */
div[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 10px;
    border: 1px solid #CFE3F2;
    background: #FFFFFF;
}

div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
    border-left: 4px solid #4A9FE0;
}

div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
    background: #F8FBFE;
    border-right: 4px solid #7ED6C4;
}

/* Buttons */
.stButton > button {
    background-color: #4A9FE0 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background-color: #2E7DC4 !important;
    transform: translateY(-1px);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Tải cấu hình và artifacts
SYSTEM_PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
tool_decls = load_tool_declarations(TOOLS_PATH)
openai_tools = to_openai_tools(tool_decls)

# --- SIDEBAR: Quản lý cấu hình & Transcript ---
with st.sidebar:
    st.markdown("### ⚙️ Cấu hình Agent")
    provider_name = st.selectbox(
        "Provider",
        ["gemini", "openrouter", "openai", "anthropic"],
        index=0,
    )
    version_label = st.selectbox(
        "Version",
        ["v0", "v1", "v2", "v3"],
        index=3,
    )
    selected_model = None

    artifact_ver = build_artifact_version(version_label, SYSTEM_PROMPT_PATH, TOOLS_PATH)

    st.markdown("---")
    st.markdown("### 📦 Artifact Version Active")
    st.code(artifact_ver.artifact_version, language="text")

    if st.button("🔄 Reset Cuộc Trò Chuyện"):
        st.session_state.messages = []
        st.session_state.pop("transcript_path", None)
        st.session_state.pop("transcript", None)
        st.rerun()

    st.markdown("---")
    st.markdown("### 📄 Transcript Log")
    if "transcript_path" in st.session_state:
        trans_file: Path = st.session_state["transcript_path"]
        st.caption(f"Đang lưu: `{trans_file.name}`")
        if trans_file.exists():
            st.download_button(
                label="📥 Tải transcript JSON",
                data=trans_file.read_text(encoding="utf-8"),
                file_name=trans_file.name,
                mime="application/json",
            )

# Header giao diện
st.markdown(
    f"""
    <div class="header-container">
        <div class="header-title">🛠️ IT Helpdesk Agent</div>
        <div class="header-caption">Artifact Version Active: <code>{artifact_ver.artifact_version}</code></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Khởi tạo session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "transcript" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        safe_slug(version_label),
        safe_slug(provider_name),
        timestamp,
    ])
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state["transcript_path"] = transcript_path
    st.session_state["transcript"] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_ver),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tools" in msg and msg["tools"]:
            with st.expander("🔍 Chi tiết Tool Calling Traces"):
                st.json(msg["tools"])

# Nhận câu hỏi mới
if prompt := st.chat_input("Nhập yêu cầu hỗ trợ IT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    provider = make_provider(provider_name)
    chat_history = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        chat_history.append({"role": m["role"], "content": m["content"]})

    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.messages) // 2 + 1,
        "started_at": now_iso(),
        "user": prompt,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        with st.spinner("Agent đang xử lý và kích hoạt tools..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=chat_history,
                    tools=openai_tools,
                    model=selected_model,
                    max_tool_rounds=4,
                )
                reply = result.get("assistant_text", "")
                # Format response cleanly if model output is raw JSON string with 'reply'
                try:
                    parsed_json = json.loads(reply.strip())
                    if isinstance(parsed_json, dict) and "reply" in parsed_json:
                        reply = parsed_json["reply"]
                except Exception:
                    pass

                tool_events = result.get("tool_events", [])
                turn_record.update(result)

                st.markdown(reply)
                if tool_events:
                    with st.expander("🔍 Chi tiết Tool Calling Traces"):
                        st.json(tool_events)

            except Exception as exc:
                reply = f"Lỗi thực thi: {type(exc).__name__}: {str(exc)}"
                tool_events = []
                turn_record.update({
                    "status": "provider_error",
                    "error": reply,
                })
                st.error(reply)

    turn_record["ended_at"] = now_iso()
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "tools": tool_events,
    })

    # Tự động ghi nhận và lưu transcript ra file
    st.session_state["transcript"]["turns"].append(turn_record)
    write_transcript(st.session_state["transcript_path"], st.session_state["transcript"])
