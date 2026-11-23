# -*- coding: utf-8 -*-
"""Streamlit interface for NexRAG. Run with ``streamlit run app.py``."""

import os
import re
import base64
import hashlib
import hmac
import smtplib
import ssl
from email.message import EmailMessage
from io import BytesIO
import sqlite3
import tempfile
import textwrap
import uuid
from datetime import datetime
from html import escape, unescape
from pathlib import Path
from urllib.parse import quote
from zipfile import ZIP_DEFLATED, ZipFile

import streamlit as st
from dotenv import load_dotenv
from theme import apply_theme

# Environment settings must be loaded before rag_engine imports ChromaDB.
load_dotenv(Path(__file__).resolve().parent / ".env")


def get_setting(name, default=""):
    """Read a setting from Streamlit secrets first, then the local environment."""
    try:
        value = st.secrets.get(name, None)
    except Exception:
        # Streamlit raises when no secrets file or cloud secrets are configured.
        value = None
    if value is None:
        value = os.getenv(name, default)
    return str(value).strip() if value is not None else default

from rag_engine import EnhancedRAGv3  # noqa: E402


APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets"

st.set_page_config(
    page_title="NexRAG | Document Intelligence",
    page_icon=str(ASSET_DIR / "nexrag-mark.svg"),
    layout="wide",
    initial_sidebar_state="collapsed",
)


NAV_ITEMS = ["Home", "History", "Tools", "Overview", "Contact"]
NAV_LABELS = {
    "Home": "Home",
    "Overview": "Overview",
    "Tools": "Tools",
    "History": "History",
    "Contact": "Contact",
}


def initialize_state():
    defaults = {
        "rag_system": None,
        "init_status": "Waiting for configuration",
        "init_attempted": False,
        "chat_history": [],
        "chat_sessions": [],
        "active_chat_id": None,
        "summary": None,
        "summary_metadata": "",
        "upload_status": "",
        "attached_uploads_processed": set(),
        "pending_composer_uploads": [],
        "composer_upload_feedback": [],
        "composer_upload_generation": {},
        "navigation": "Home",
        "navigation_expanded": True,
        "nx_theme": "dark",
        "history_search": "",
        "history_notice": None,
        "pending_question": None,
        "pending_question_options": None,
        "workspace_notice": "",
        "use_hyde": False,
        "use_multi_query": True,
        "tool_summaries": {},
        "tool_images_zip": None,
        "tool_images_file": None,
        "tool_images_count": 0,
        "tool_notice": None,
        "tool_notice_file": None,
        "account_email": None,
        "account_name": None,
        "contact_mailto": None,
        "contact_notice": None,
        "contact_notice_kind": "info",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if st.session_state.chat_history and not st.session_state.chat_sessions:
        chat_id = uuid.uuid4().hex
        messages = []
        for old_item in st.session_state.chat_history:
            item = dict(old_item)
            item["chat_id"] = chat_id
            messages.append(item)
        first_question = messages[0].get("question", "Saved conversation") if messages else "Saved conversation"
        st.session_state.chat_sessions = [{
            "id": chat_id,
            "title": str(first_question)[:72],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "messages": messages,
        }]
        st.session_state.chat_history = messages
        st.session_state.active_chat_id = chat_id
    if st.session_state.get("navigation_version") != 6:
        if st.session_state.navigation == "Overview":
            st.session_state.navigation = "Home"
        elif st.session_state.navigation == "Guide":
            st.session_state.navigation = "Overview"
        elif st.session_state.navigation == "Summarization":
            st.session_state.navigation = "History"
        elif st.session_state.navigation == "Chat":
            st.session_state.navigation = "Home"
        elif st.session_state.navigation == "Documents":
            st.session_state.navigation = "Tools"
        st.session_state.navigation_version = 6
    if st.session_state.get("retrieval_defaults_version") != 1:
        st.session_state.use_hyde = False
        st.session_state.use_multi_query = True
        st.session_state.retrieval_defaults_version = 1


ACCOUNT_DB_PATH = APP_DIR / ".nexrag_accounts.sqlite3"
PASSWORD_HASH_ROUNDS = 310_000


def _account_connection():
    ACCOUNT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(ACCOUNT_DB_PATH, timeout=10)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS accounts ("
        "email TEXT PRIMARY KEY COLLATE NOCASE, display_name TEXT NOT NULL, "
        "password_hash TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    connection.commit()
    return connection


def _hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ROUNDS)
    return f"pbkdf2_sha256${PASSWORD_HASH_ROUNDS}${salt.hex()}${digest.hex()}"


def _verify_password(password, stored_hash):
    try:
        algorithm, rounds, salt_hex, digest_hex = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(rounds)
        ).hex()
        return hmac.compare_digest(candidate, digest_hex)
    except (AttributeError, TypeError, ValueError):
        return False


def create_local_account(email, display_name, password):
    email = email.strip().casefold()
    connection = _account_connection()
    try:
        connection.execute(
            "INSERT INTO accounts (email, display_name, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (email, display_name.strip(), _hash_password(password), datetime.now().isoformat(timespec="seconds")),
        )
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        connection.close()


def authenticate_local_account(email, password):
    email = email.strip().casefold()
    connection = _account_connection()
    try:
        row = connection.execute(
            "SELECT email, display_name, password_hash FROM accounts WHERE email = ?", (email,)
        ).fetchone()
    finally:
        connection.close()
    if not row or not _verify_password(password, row[2]):
        return None
    return {"email": row[0], "name": row[1]}


def engine_is_ready():
    engine = st.session_state.get("rag_system")
    return engine is not None and bool(getattr(engine, "is_initialized", False))


def document_count():
    engine = st.session_state.get("rag_system")
    return len(getattr(engine, "pdf_metadata", {}) or {}) if engine else 0


def chunk_count():
    engine = st.session_state.get("rag_system")
    return len(getattr(engine, "documents", []) or []) if engine else 0


def has_loaded_documents():
    return document_count() > 0


def initialize_system():
    """Load the existing engine once per session from environment secrets."""
    existing = st.session_state.get("rag_system")
    if existing is not None and bool(getattr(existing, "is_initialized", False)):
        return "Models already loaded."
    api_key = get_setting("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY is missing. Add it to Streamlit secrets or your local .env file."
    try:
        engine = EnhancedRAGv3(api_key)
        status = engine.load_models()
        st.session_state.rag_system = engine
        return status
    except Exception as exc:
        return f"Initialization failed: {exc}"


def upload_and_process(rag_system, pdf_path, use_semantic):
    if rag_system is None or not getattr(rag_system, "is_initialized", False):
        return "The system is not ready yet."
    try:
        result = rag_system.ingest_pdf(pdf_path, use_semantic_chunking=use_semantic)
        if Path(pdf_path).name in getattr(rag_system, "pdf_metadata", {}):
            pdf_files = getattr(rag_system, "pdf_files", None)
            if not isinstance(pdf_files, dict):
                pdf_files = {}
            pdf_files[Path(pdf_path).name] = Path(pdf_path).read_bytes()
            rag_system.pdf_files = pdf_files
        return result
    except Exception as exc:
        return f"Error: {exc}"


def ask_question(rag_system, query, use_hyde, use_multi_query):
    if rag_system is None:
        return "The system is not ready yet.", "", ""
    try:
        return rag_system.chat(query, use_hyde=use_hyde, use_multi_query=use_multi_query)
    except Exception as exc:
        return f"Error: {exc}", "", ""


def clean_answer_text(answer):
    """Keep source references in the optional source panel, not in the answer."""
    answer = re.sub(r"\s*\[sources?\s+[^\]]+\]", "", str(answer), flags=re.IGNORECASE)
    answer = re.sub(r"[ \t]+([,.;:!?])", r"\1", answer)
    answer = re.sub(r"[ \t]{2,}", " ", answer)
    return answer.strip()


def format_sources_for_display(citations, engine=None):
    """Refresh saved source markup into the compact page/excerpt format."""
    citations = str(citations or "")
    if 'class="nx-source-row nx-source-row-v2"' in citations:
        return citations

    plain = unescape(re.sub(r"<[^>]+>", " ", citations))
    plain = re.sub(r"\s+", " ", plain).strip()
    page_matches = list(re.finditer(r"\bPage\s+(\d+)\b", plain, flags=re.IGNORECASE))
    documents = getattr(engine, "documents", []) if engine is not None else []
    if page_matches and documents:
        page_groups = {}
        for doc in documents:
            metadata = doc.metadata
            page_index = metadata.get("page")
            pdf_id = metadata.get("pdf_id")
            if page_index is None or not pdf_id:
                continue
            try:
                page_number = int(page_index) + 1
            except (TypeError, ValueError):
                continue
            page_groups.setdefault(page_number, {})[pdf_id] = doc

        page_occurrences = {}
        refreshed = []
        for match in page_matches:
            page = int(match.group(1))
            candidates = sorted(
                page_groups.get(page, {}).values(),
                key=lambda doc: str(doc.metadata.get("pdf_name", "")).casefold(),
            )
            if not candidates:
                continue
            occurrence = page_occurrences.get(page, 0)
            doc = candidates[min(occurrence, len(candidates) - 1)]
            page_occurrences[page] = occurrence + 1
            pdf_id = doc.metadata.get("pdf_id")
            page_index = doc.metadata.get("page")
            page_text = "\n".join(
                chunk.page_content for chunk in documents
                if chunk.metadata.get("pdf_id") == pdf_id
                and chunk.metadata.get("page") == page_index
            ) or doc.page_content
            words = re.sub(r"\s+", " ", str(page_text)).split()
            if len(words) > 4:
                excerpt = f"{' '.join(words[:2])} ... {' '.join(words[-2:])}"
            else:
                excerpt = " ".join(words)
            refreshed.append(
                f'<div class="nx-source-row nx-source-row-v2">'
                f'<b>Page {page}:</b> {escape(excerpt)}</div>'
            )
        if refreshed:
            return "".join(refreshed)

    rows = []
    for index, page_match in enumerate(page_matches):
        next_start = page_matches[index + 1].start() if index + 1 < len(page_matches) else len(plain)
        section = plain[page_match.end():next_start]
        start_match = re.search(r"\bStart:\s*(.*?)(?=\bEnd:|$)", section, flags=re.IGNORECASE)
        end_match = re.search(r"\bEnd:\s*(.*)$", section, flags=re.IGNORECASE)
        if start_match:
            start_text = start_match.group(1).strip()
        else:
            start_text = re.sub(r"^.*?(?:Relevance:[^)]*\)|Document Header)\s*", "", section, flags=re.IGNORECASE)
            start_text = re.sub(r"^.*?:\s*", "", start_text)
        start_text = re.sub(r"(?:\.{2,}|…)", " ", start_text)
        first_words = re.sub(r"\s+", " ", start_text).split()[:2]
        end_text = end_match.group(1).strip() if end_match else start_text
        end_text = re.sub(r"(?:\.{2,}|…)", " ", end_text)
        end_words = re.sub(r"\s+", " ", end_text).split()[-2:]
        if not first_words:
            continue
        excerpt = " ".join(first_words)
        if end_words:
            excerpt += f" ... {' '.join(end_words)}"
        rows.append((int(page_match.group(1)), excerpt))

    rows.sort(key=lambda row: row[0])
    return "".join(
        f'<div class="nx-source-row nx-source-row-v2"><b>Page {page}:</b> {escape(excerpt)}</div>'
        for page, excerpt in rows
    ) or citations


def summarize_doc(rag_system):
    try:
        return rag_system.summarize_document()
    except Exception as exc:
        return f"Error: {exc}", ""


def summarize_selected_pdf(rag_system, pdf_name):
    """Summarize only the indexed chunks belonging to the selected PDF."""
    chunks = [
        doc for doc in getattr(rag_system, "documents", [])
        if doc.metadata.get("pdf_name") == pdf_name
    ]
    if not chunks:
        return f"No indexed content found for {pdf_name}.", ""

    summaries = []
    for start in range(0, len(chunks), 10):
        section = "\n\n---\n\n".join(doc.page_content for doc in chunks[start:start + 10])
        try:
            response = rag_system.llm.invoke(
                f"Summarize this section of {pdf_name} in 3-5 concise factual bullet points.\n\n{section}"
            )
            summaries.append(response.content)
        except Exception as exc:
            return f"Error summarizing {pdf_name}: {exc}", ""

    try:
        response = rag_system.llm.invoke(
            f"Create a clear summary of the single PDF named {pdf_name}. Include its purpose, main topics, "
            "key findings or arguments, and overall takeaway. Start with a direct 2-3 sentence overview, "
            "then use concise headings and bullets. Avoid generic introductions and repetition.\n\n"
            + "\n\n".join(summaries)
        )
        info = getattr(rag_system, "pdf_metadata", {}).get(pdf_name, {})
        metadata = f"**File:** {pdf_name}  \n**Pages:** {info.get('pages', 'Unknown')}  \n**Chunks summarized:** {len(chunks)}"
        return response.content, metadata
    except Exception as exc:
        return f"Error summarizing {pdf_name}: {exc}", ""


def navigate_to(page):
    st.session_state.navigation = page


def toggle_navigation():
    st.session_state.navigation_expanded = not st.session_state.get("navigation_expanded", True)


def toggle_theme():
    st.session_state.nx_theme = "light" if st.session_state.nx_theme == "dark" else "dark"


def start_new_chat():
    st.session_state.active_chat_id = None
    st.session_state.pending_question = None
    st.session_state.pending_question_options = None
    st.session_state.navigation = "Home"


def open_saved_chat(chat_id):
    st.session_state.active_chat_id = chat_id
    st.session_state.navigation = "Home"


def delete_saved_chat(chat_id):
    deleted = next((chat for chat in st.session_state.chat_sessions if chat["id"] == chat_id), None)
    st.session_state.chat_sessions = [chat for chat in st.session_state.chat_sessions if chat["id"] != chat_id]
    st.session_state.chat_history = [item for item in st.session_state.chat_history if item.get("chat_id") != chat_id]
    if st.session_state.active_chat_id == chat_id:
        st.session_state.active_chat_id = None
    if deleted:
        st.toast(f"Deleted chat: {deleted.get('title', 'Conversation')}", icon="🗑️")
    st.session_state.navigation = "History"


def remove_history_document(pdf_name):
    engine = st.session_state.get("rag_system")
    if engine is None:
        st.session_state.history_notice = ("error", "The RAG engine is not ready; the file was not removed.")
        return

    result = engine.remove_document(pdf_name)
    if str(result).lower().startswith("error:"):
        st.session_state.history_notice = ("error", result)
        return

    st.session_state.summary = None
    st.session_state.summary_metadata = ""
    st.session_state.tool_summaries.pop(pdf_name, None)
    if st.session_state.tool_images_file == pdf_name:
        st.session_state.tool_images_zip = None
        st.session_state.tool_images_file = None
        st.session_state.tool_images_count = 0
    if st.session_state.tool_notice_file == pdf_name:
        st.session_state.tool_notice = None
        st.session_state.tool_notice_file = None
    st.session_state.attached_uploads_processed = {
        signature for signature in st.session_state.attached_uploads_processed
        if pdf_name not in signature
    }
    st.session_state.history_notice = ("success", result)


def set_pending_question(query):
    st.session_state.pending_question = query
    st.session_state.pending_question_options = {
        "hyde": st.session_state.get("use_hyde", False),
        "multi_query": st.session_state.get("use_multi_query", True),
    }
    st.session_state.navigation = "Home"




def start_document_analysis():
    if not has_loaded_documents():
        st.session_state.workspace_notice = "Add a PDF with the + button on Home before starting an analysis."
        st.session_state.navigation = "Home"
        return
    set_pending_question("Analyze the key themes across my documents.")


def submit_composer(message_key):
    question = st.session_state.get(message_key, "").strip()
    if not question:
        return
    st.session_state[message_key] = ""
    if not has_loaded_documents():
        st.session_state.workspace_notice = "Add a PDF with the + button before asking a question."
        st.session_state.navigation = "Home"
        return
    set_pending_question(question)


def render_brand():
    logo = (ASSET_DIR / "nexrag-mark.svg").read_text(encoding="utf-8")
    logo_data = base64.b64encode(logo.encode("utf-8")).decode("ascii")
    st.markdown(
        f'<style>.st-key-brand_toggle button::before {{ background-image: url("data:image/svg+xml;base64,{logo_data}"); }}</style>',
        unsafe_allow_html=True,
    )
    st.button(
        "Toggle navigation", key="brand_toggle", on_click=toggle_navigation,
        help="Show or hide the navigation menu",
    )


def render_sidebar():
    render_brand()
    if st.session_state.get("navigation_expanded", True):
        st.markdown('<div class="nx-eyebrow">Workspace</div>', unsafe_allow_html=True)
        for page in NAV_ITEMS:
            st.button(
                NAV_LABELS[page],
                type="primary" if st.session_state.navigation == page else "secondary",
                use_container_width=True,
                key=f"nav_{page}",
                on_click=navigate_to,
                args=(page,),
            )

        st.markdown('<div class="nx-rule"></div><div class="nx-eyebrow">Recent questions</div>', unsafe_allow_html=True)
        recent_questions = st.session_state.chat_history[-3:][::-1]
        if recent_questions:
            for item in recent_questions:
                st.markdown(
                    f'<div class="nx-recent">{escape(str(item.get("question", "")))}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Your recent questions will appear here.")

        status = st.session_state.init_status
        if engine_is_ready():
            st.markdown('<div class="nx-status"><span class="nx-dot"></span>System ready</div>', unsafe_allow_html=True)
        elif status.startswith("Initialization failed"):
            st.markdown('<div class="nx-status"><span class="nx-dot nx-dot-error"></span>Initialization error</div>', unsafe_allow_html=True)
            st.error(status)
            if st.button("Retry initialization", use_container_width=True, key="retry_init"):
                with st.spinner("Loading retrieval models..."):
                    st.session_state.init_status = initialize_system()
                st.rerun()
        elif "missing" in status.lower():
            st.markdown('<div class="nx-status"><span class="nx-dot nx-dot-wait"></span>Configuration needed</div>', unsafe_allow_html=True)
            st.caption(status)
        else:
            st.markdown('<div class="nx-status"><span class="nx-dot nx-dot-wait"></span>System initializing</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="nx-nav-collapsed-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    return st.session_state.navigation

def render_topbar(page):
    if page == "Home":
        crumb_col, theme_col, action_col = st.columns([1.8, .8, .8])
    else:
        crumb_col, control_col = st.columns([.8, 3.2])
    with crumb_col:
        st.markdown(
            f'<div class="nx-top-label">NEXRAG &nbsp;/&nbsp; {escape(page)}</div>',
            unsafe_allow_html=True,
        )
    if page == "Home":
        with theme_col:
            theme_label = "Light mode" if st.session_state.nx_theme == "dark" else "Dark mode"
            st.button(
                theme_label, type="secondary", use_container_width=True,
                key="theme_toggle", on_click=toggle_theme,
            )
        with action_col:
            st.button(
                "New chat", type="secondary", use_container_width=True,
                key="new_chat", on_click=start_new_chat,
            )
    elif page == "History":
        with control_col:
            st.text_input(
                "Search history", placeholder="Find a document or conversation...",
                label_visibility="collapsed", key="history_search",
            )


def render_header(eyebrow, title, subtitle, subtitle_align="center"):
    subtitle_class = " nx-subtitle-left" if subtitle and subtitle_align == "left" else ""
    subtitle_html = f'<div class="nx-subtitle{subtitle_class}">{escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="nx-eyebrow">{escape(eyebrow)}</div>'
        f'<div class="nx-title">{escape(title)}</div>{subtitle_html}',
        unsafe_allow_html=True,
    )


def render_composer(key_prefix, disabled=False, placeholder="Ask NexRAG about your documents…"):
    message_key = f"{key_prefix}_message"
    process_pending_composer_uploads(key_prefix)
    with st.container(key="prompt_card"):
        prompt_col, attach_col, send_col = st.columns([8.0, .65, .78])
        with prompt_col:
            st.text_input(
                "Message NexRAG", placeholder=placeholder,
                label_visibility="collapsed", key=message_key, disabled=disabled,
                on_change=submit_composer, args=(message_key,),
            )
        with attach_col:
            with st.container(key=f"{key_prefix}_attach"):
                generation = st.session_state.composer_upload_generation.get(key_prefix, 0)
                widget_key = f"{key_prefix}_attach_{generation}"
                st.file_uploader(
                    "Add PDF documents", type=["pdf"], accept_multiple_files=True,
                    label_visibility="collapsed", help="Choose PDF documents for this session",
                    key=widget_key, disabled=disabled,
                    on_change=queue_composer_uploads, args=(key_prefix, widget_key),
                )
        with send_col:
            st.button(
                "↑", type="primary", use_container_width=True, disabled=disabled,
                help="Send your question", key=f"{key_prefix}_send",
                on_click=submit_composer, args=(message_key,),
            )
    feedback = st.session_state.composer_upload_feedback
    if feedback:
        for kind, message in feedback:
            if kind == "success":
                st.success(message)
            elif kind == "warning":
                st.warning(message)
            else:
                st.error(message)
        st.session_state.composer_upload_feedback = []


def queue_composer_uploads(key_prefix, widget_key):
    """Queue selected PDFs and rotate the uploader key to reset the picker."""
    uploaded_files = st.session_state.get(widget_key) or []
    pending = st.session_state.pending_composer_uploads
    for uploaded_file in uploaded_files:
        data = uploaded_file.getvalue()
        pending.append({
            "key_prefix": key_prefix,
            "name": Path(uploaded_file.name).name or "document.pdf",
            "size": uploaded_file.size,
            "digest": hashlib.md5(data).hexdigest(),
            "data": data,
        })


def process_pending_composer_uploads(key_prefix):
    """Index files queued by a composer picker and retain a visible result."""
    pending = st.session_state.pending_composer_uploads
    selected = [item for item in pending if item["key_prefix"] == key_prefix]
    st.session_state.pending_composer_uploads = [item for item in pending if item["key_prefix"] != key_prefix]
    if not selected:
        return
    generations = st.session_state.composer_upload_generation
    generations[key_prefix] = generations.get(key_prefix, 0) + 1
    processed = st.session_state.attached_uploads_processed
    feedback = st.session_state.composer_upload_feedback
    for item in selected:
        safe_name = item["name"]
        signature = (safe_name, item["size"], item["digest"])
        if signature in processed:
            feedback.append(("warning", f"{safe_name} is already in your library."))
            continue
        try:
            with tempfile.TemporaryDirectory(prefix="nexrag_upload_") as folder:
                pdf_path = Path(folder) / safe_name
                pdf_path.write_bytes(item["data"])
                with st.spinner(f"Adding {safe_name} to your library…"):
                    result = upload_and_process(
                        st.session_state.rag_system, str(pdf_path), use_semantic=True
                    )
            engine = st.session_state.rag_system
            indexes_ready = (
                safe_name in getattr(engine, "pdf_metadata", {})
                and getattr(engine, "vector_db", None) is not None
                and getattr(engine, "bm25_retriever", None) is not None
            )
            if str(result).lstrip().lower().startswith("error:") or not indexes_ready:
                feedback.append(("error", f"Could not index {safe_name}: {result}"))
            elif str(result).lstrip().lower().startswith("notice:"):
                processed.add(signature)
                feedback.append(("warning", f"{safe_name} is already indexed and ready for questions."))
            else:
                processed.add(signature)
                feedback.append(("success", f"{safe_name} is indexed and ready for questions."))
        except Exception as exc:
            feedback.append(("error", f"Could not index {safe_name}: {exc}"))


def process_chat_question(question, use_hyde, use_multi_query):
    with st.spinner("Searching your documents and preparing an answer…"):
        answer, citations, metadata = ask_question(
            st.session_state.rag_system, question, use_hyde, use_multi_query
        )
    answer = clean_answer_text(answer)
    chat = next(
        (item for item in st.session_state.chat_sessions if item["id"] == st.session_state.active_chat_id),
        None,
    )
    if chat is None:
        chat = {
            "id": uuid.uuid4().hex,
            "title": question[:72],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "messages": [],
        }
        st.session_state.chat_sessions.append(chat)
        st.session_state.active_chat_id = chat["id"]
    message = {
        "chat_id": chat["id"],
        "question": question,
        "answer": answer,
        "citations": citations,
        "metadata": metadata,
    }
    chat["messages"].append(message)
    st.session_state.chat_history.append(message)


def render_feature_cards():
    cards = [
        ("01 / ASK", "Research chat", "Ask questions grounded in your PDFs, with source pages when you need them.", "Open chat", "Home"),
        ("02 / SYNTHESIZE", "Unified summary", "Summarize all documents in your active library.", "Summarize", "Summarization"),
        ("03 / ANALYZE", "Theme analysis", "Identify key themes across your document collection.", "Analyze library", "Analyze"),
        ("04 / TOOLS", "PDF tools", "Summarize selected PDFs or extract embedded images.", "Open tools", "Tools"),
    ]
    columns = st.columns(4)
    for column, (label, title, copy, action, destination) in zip(columns, cards):
        with column:
            st.markdown(
                f'<div class="nx-card"><div class="nx-card-label">{label}</div>'
                f'<div class="nx-card-title">{title}</div><div class="nx-card-copy">{copy}</div></div>',
                unsafe_allow_html=True,
            )
            if destination == "Analyze":
                st.button(action, use_container_width=True, key="card_analyze", on_click=start_document_analysis)
            else:
                st.button(
                    action, use_container_width=True, key=f"card_{destination}",
                    on_click=navigate_to, args=(destination,),
                )


def render_project_guide():
    apply_theme()
    render_header(
        "PROJECT GUIDE",
        "How NexRAG works",
        "A document research workspace that brings your PDFs together and answers questions with traceable sources.",
        subtitle_align="left",
    )
    st.markdown('<div class="nx-rule"></div><div class="nx-section-title">From PDF to cited answer</div>', unsafe_allow_html=True)
    steps = [
        ("01 / INGEST", "Add your PDFs", "Upload research papers or reports. NexRAG extracts text and document details, then divides content into searchable passages."),
        ("02 / RETRIEVE", "Find useful evidence", "Semantic and keyword search work together. Query expansion, result fusion, and reranking help surface relevant passages across your library."),
        ("03 / RESPOND", "Ask and verify", "Ask a question on Home. NexRAG gives a direct answer and keeps page excerpts available when you open Sources."),
        ("04 / SYNTHESIZE", "Review the whole library", "Generate a multi-document summary or ask for themes and comparisons across the PDFs you have loaded."),
    ]
    columns = st.columns(2)
    for index, (label, title, copy) in enumerate(steps):
        with columns[index % 2]:
            st.markdown(
                f'<div class="nx-card nx-guide-card"><div class="nx-card-label">{label}</div>'
                f'<div class="nx-card-title">{title}</div><div class="nx-card-copy">{copy}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown('<div class="nx-rule"></div><div class="nx-section-title">What powers it</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="nx-card nx-guide-summary"><svg class="nx-flow-diagram" viewBox="0 0 800 226" role="img" aria-labelledby="nx-flow-title nx-flow-desc">'
        '<title id="nx-flow-title">How NexRAG turns documents into cited answers</title>'
        '<desc id="nx-flow-desc">PDFs are extracted and embedded, hybrid semantic and keyword search finds evidence, a reranker prioritizes passages, and the language model creates an answer with citations.</desc>'
        '<defs><linearGradient id="nx-flow-line" x1="0" x2="1"><stop stop-color="#34d399" stop-opacity=".42"/><stop offset="1" stop-color="#a7f3d0" stop-opacity=".8"/></linearGradient>'
        '<linearGradient id="nx-flow-card" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#123d30" stop-opacity=".78"/><stop offset="1" stop-color="#10231f" stop-opacity=".72"/></linearGradient></defs>'
        '<path class="nx-flow-rail" d="M180 112H215M400 112H435M595 112H630"/>'
        '<circle class="nx-flow-pulse" cx="181" cy="112" r="3.5"/><circle class="nx-flow-pulse nx-flow-pulse-2" cx="401" cy="112" r="3.5"/><circle class="nx-flow-pulse nx-flow-pulse-3" cx="596" cy="112" r="3.5"/>'
        '<g class="nx-flow-node"><rect x="10" y="48" width="170" height="128" rx="20"/><path class="nx-flow-icon" d="M34 84h20l9 9v28H34V84Zm20 1v9h9M40 104h14m-14 7h14"/><text x="76" y="101" class="nx-flow-title">PDF library</text><text x="76" y="122" class="nx-flow-copy">Extract · chunk · embed</text><text x="76" y="143" class="nx-flow-copy">Session documents</text></g>'
        '<g class="nx-flow-node"><rect x="215" y="48" width="185" height="128" rx="20"/><circle class="nx-flow-icon" cx="244" cy="103" r="13"/><path class="nx-flow-icon" d="m254 113 9 9m-26-19h14m-14 7h9"/><text x="272" y="101" class="nx-flow-title">Hybrid search</text><text x="272" y="122" class="nx-flow-copy">Vector + BM25</text><text x="272" y="143" class="nx-flow-copy">HyDE · multi-query</text></g>'
        '<g class="nx-flow-node"><rect x="435" y="48" width="160" height="128" rx="20"/><path class="nx-flow-icon" d="M456 91h21m-21 10h16m-16 10h12m-12 10h8"/><circle class="nx-flow-icon-fill" cx="480" cy="91" r="3"/><circle class="nx-flow-icon-fill" cx="475" cy="101" r="3"/><circle class="nx-flow-icon-fill" cx="471" cy="111" r="3"/><text x="490" y="101" class="nx-flow-title">Reranking</text><text x="490" y="122" class="nx-flow-copy">Cross-encoder</text><text x="490" y="143" class="nx-flow-copy">Best evidence first</text></g>'
        '<g class="nx-flow-node"><rect x="630" y="48" width="160" height="128" rx="20"/><path class="nx-flow-icon" d="M650 89h26v24h-26zM655 96h16m-16 6h12m-12 6h8"/><path class="nx-flow-spark" d="m671 83 2 5 5 2-5 2-2 5-2-5-5-2 5-2z"/><text x="686" y="101" class="nx-flow-title">Answer</text><text x="686" y="122" class="nx-flow-copy">Groq language model</text><text x="686" y="143" class="nx-flow-copy">Grounded citations</text></g>'
        '<text x="400" y="207" text-anchor="middle" class="nx-flow-caption">Evidence moves through every step before NexRAG responds</text>'
        '</svg></div>',
        unsafe_allow_html=True,
    )


def render_overview():
    apply_theme()
    if st.session_state.workspace_notice:
        st.info(st.session_state.workspace_notice)
        st.session_state.workspace_notice = ""
    if not engine_is_ready():
        st.info(st.session_state.init_status)

    pending_question = st.session_state.pending_question
    if pending_question:
        options = st.session_state.pending_question_options or {}
        st.session_state.pending_question = None
        st.session_state.pending_question_options = None
        process_chat_question(
            pending_question,
            options.get("hyde", st.session_state.get("use_hyde", False)),
            options.get("multi_query", st.session_state.get("use_multi_query", True)),
        )

    active_chat = next(
        (item for item in st.session_state.chat_sessions if item["id"] == st.session_state.active_chat_id),
        None,
    )
    active_messages = active_chat["messages"] if active_chat else []
    if active_messages:
        with st.container(height=520, border=False, key="home_chat_transcript"):
            for item in active_messages:
                question = escape(str(item.get("question", ""))).replace("\n", "<br>")
                st.markdown(f'<div class="nx-user-question">{question}</div>', unsafe_allow_html=True)
                with st.chat_message("assistant", avatar=str(ASSET_DIR / "nexrag-mark.svg")):
                    st.markdown(clean_answer_text(item["answer"]))
                    if item.get("citations"):
                        with st.expander("Sources (pages)", expanded=False):
                            st.markdown(
                                format_sources_for_display(item["citations"], st.session_state.get("rag_system")),
                                unsafe_allow_html=True,
                            )
        st.markdown(
            '<style>@media (min-width: 701px) {'
            '.st-key-home_chat_input {position:fixed!important;z-index:100!important;'
            'left:calc(50% + 43px)!important;bottom:8px!important;transform:translateX(-50%);'
            'width:min(960px,calc(100vw - 140px))!important;padding:0!important;'
            'border:0!important;outline:0!important;box-shadow:none!important;background:transparent!important;}'
            '}.st-key-home_chat_transcript {scroll-behavior:smooth;}'
            '@media (max-width:700px) {'
            '.st-key-home_chat_input {position:fixed!important;z-index:100!important;'
            'left:14px!important;bottom:6px!important;transform:none;width:calc(100vw - 28px)!important;'
            'padding:0!important;border:0!important;outline:0!important;box-shadow:none!important;background:transparent!important;}'
            '}</style>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="nx-welcome"><div class="nx-eyebrow">YOUR DOCUMENT INTELLIGENCE WORKSPACE</div>'
            '<div class="nx-title">What would you like to understand?</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="nx-rag-stage" role="img" aria-label="PDF documents flow through hybrid retrieval into a grounded answer">'
            '<svg class="nx-rag-visual" viewBox="0 0 860 300" xmlns="http://www.w3.org/2000/svg">'
            '<title>NexRAG research flow</title><desc>Documents are extracted and searched with semantic and keyword retrieval before evidence is used to create a grounded answer.</desc>'
            '<defs>'
            '<radialGradient id="nx-core-glow" cx="34%" cy="28%"><stop stop-color="#d1fae5"/><stop offset=".22" stop-color="#6ee7b7"/><stop offset=".62" stop-color="#10a875"/><stop offset="1" stop-color="#063c32"/></radialGradient>'
            '<linearGradient id="nx-glass" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#1b5743" stop-opacity=".92"/><stop offset="1" stop-color="#0a211d" stop-opacity=".88"/></linearGradient>'
            '<filter id="nx-soft-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="7" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            '</defs>'
            '<ellipse class="nx-rag-halo" cx="430" cy="145" rx="340" ry="108"/>'
            '<path id="nx-flow-in" class="nx-rag-path" d="M190 142 C270 142 285 112 350 132"/>'
            '<path id="nx-flow-out" class="nx-rag-path" d="M510 140 C566 140 591 140 654 140"/>'
            '<g class="nx-doc-stack"><rect class="nx-doc-back" x="48" y="80" width="100" height="128" rx="13" transform="rotate(-9 98 144)"/>'
            '<rect class="nx-doc-front" x="82" y="67" width="104" height="136" rx="14"/>'
            '<path class="nx-doc-fold" d="M153 67v27h33"/><path class="nx-doc-line" d="M101 119h58M101 135h63M101 151h48M101 167h55"/>'
            '<circle class="nx-doc-mark" cx="108" cy="91" r="8"/><text class="nx-svg-label" x="68" y="240">PDF LIBRARY</text></g>'
            '<g class="nx-core-group"><ellipse class="nx-core-orbit" cx="430" cy="140" rx="119" ry="39" transform="rotate(-16 430 140)"/>'
            '<circle class="nx-core-sphere" cx="430" cy="140" r="69"/>'
            '<path class="nx-core-network" d="M394 119 421 102l29 12 22 28-26 28-36-5-20-24 27-29 7 45 26-43 22 28-56 23"/>'
            '<g class="nx-core-dots"><circle cx="394" cy="119" r="4"/><circle cx="421" cy="102" r="4"/><circle cx="450" cy="114" r="4"/><circle cx="472" cy="142" r="4"/><circle cx="446" cy="170" r="4"/><circle cx="410" cy="165" r="4"/><circle cx="390" cy="141" r="4"/><circle cx="428" cy="147" r="5"/></g>'
            '<text class="nx-svg-label" x="430" y="240" text-anchor="middle">HYBRID RETRIEVAL</text></g>'
            '<g class="nx-answer-card"><rect x="654" y="91" width="156" height="104" rx="17"/>'
            '<circle class="nx-answer-check" cx="684" cy="124" r="13"/><path class="nx-answer-tick" d="m678 124 4 4 8-9"/>'
            '<path class="nx-answer-line" d="M708 119h78M678 157h108M678 173h82"/>'
            '<text class="nx-svg-label" x="732" y="240" text-anchor="middle">GROUNDED ANSWER</text></g>'
            '<circle class="nx-flow-particle" r="5" filter="url(#nx-soft-glow)"><animateMotion dur="2.9s" repeatCount="indefinite"><mpath href="#nx-flow-in"/></animateMotion></circle>'
            '<circle class="nx-flow-particle nx-flow-particle-2" r="4" filter="url(#nx-soft-glow)"><animateMotion dur="3.4s" begin=".7s" repeatCount="indefinite"><mpath href="#nx-flow-out"/></animateMotion></circle>'
            '</svg></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="nx-home-powers" aria-label="NexRAG capabilities">'
            '<div class="nx-power-track" aria-hidden="true"></div>'
            '<div class="nx-power-chip"><span class="nx-power-dot"></span>Semantic + BM25</div>'
            '<div class="nx-power-chip"><span class="nx-power-dot"></span>HyDE + multi-query</div>'
            '<div class="nx-power-chip"><span class="nx-power-dot"></span>Cross-encoder reranking</div>'
            '<div class="nx-power-chip"><span class="nx-power-dot"></span>Multi-PDF context</div>'
            '<div class="nx-power-chip"><span class="nx-power-dot"></span>Source pages on demand</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    if active_messages:
        with st.container(key="home_chat_input"):
            render_composer(
                "overview_composer", disabled=not engine_is_ready(),
                placeholder="Ask a question about your documents…",
            )
    else:
        composer_cols = st.columns([.15, 1.0, .15])
        with composer_cols[1]:
            render_composer(
                "overview_composer", disabled=not engine_is_ready(),
                placeholder="Ask a question about your documents…",
            )

    if active_messages:
        return


def render_chat():
    apply_theme()
    render_header(
        "Research assistant",
        "Chat with your documents",
        "Ask focused questions and review the source citations behind each answer.",
    )
    st.write("")
    use_hyde = st.session_state.get("use_hyde", False)
    use_multi_query = st.session_state.get("use_multi_query", True)
    ready = engine_is_ready() and has_loaded_documents()
    if not engine_is_ready():
        st.info("NexRAG is initializing from your configured environment.")
    elif not has_loaded_documents():
        st.info("Add a PDF with the + button on Home to start a conversation.")

    pending_question = st.session_state.pending_question
    if pending_question:
        options = st.session_state.pending_question_options or {}
        st.session_state.pending_question = None
        st.session_state.pending_question_options = None
        process_chat_question(
            pending_question,
            options.get("hyde", use_hyde),
            options.get("multi_query", use_multi_query),
        )

    active_chat = next(
        (item for item in st.session_state.chat_sessions if item["id"] == st.session_state.active_chat_id),
        None,
    )
    active_messages = active_chat["messages"] if active_chat else []
    if not active_messages:
        st.markdown(
            '<div class="nx-empty"><div class="nx-empty-title">Ask a question grounded in your documents</div>'
            '<div class="nx-empty-copy">Choose a prompt or write your own question below.</div></div>',
            unsafe_allow_html=True,
        )
        suggestions = [
            "What are the main findings?",
            "Summarize the key arguments.",
            "Compare the documents’ conclusions.",
        ]
        descriptions = [
            "Surface the central results and takeaways.",
            "Bring together the authors’ main arguments.",
            "Compare conclusions across your document set.",
        ]
        with st.container(key="suggestions"):
            suggestion_cols = st.columns(3)
            for index, (column, question, description) in enumerate(zip(suggestion_cols, suggestions, descriptions)):
                with column:
                    with st.container(key=f"suggestion_card_{index}"):
                        if st.button(question, use_container_width=True, disabled=not ready, key=f"suggestion_{index}"):
                            process_chat_question(question, use_hyde, use_multi_query)
                            st.rerun()
                        st.caption(description)

    for item in active_messages:
        question = escape(str(item.get("question", ""))).replace("\n", "<br>")
        st.markdown(f'<div class="nx-user-question">{question}</div>', unsafe_allow_html=True)
        with st.chat_message("assistant", avatar=str(ASSET_DIR / "nexrag-mark.svg")):
            st.markdown(clean_answer_text(item["answer"]))
            if item.get("citations"):
                with st.expander("Sources (pages)", expanded=False):
                    st.markdown(
                        format_sources_for_display(item["citations"], st.session_state.get("rag_system")),
                        unsafe_allow_html=True,
                    )

    st.markdown('<div class="nx-rule"></div><div class="nx-eyebrow">YOUR DOCUMENTS, IN CONTEXT</div>', unsafe_allow_html=True)
    composer_cols = st.columns([.15, 1.0, .15])
    with composer_cols[1]:
        render_composer("chat_composer", disabled=not engine_is_ready(), placeholder="Ask a question about your PDFs…")


def render_document_library():
    engine = st.session_state.get("rag_system")
    metadata = getattr(engine, "pdf_metadata", {}) if engine else {}
    headers = getattr(engine, "doc_headers", {}) if engine else {}
    if not metadata:
        st.markdown(
            '<div class="nx-empty"><div class="nx-empty-title">Your library is ready for its first PDF</div>'
            '<div class="nx-empty-copy">Upload one or more documents to build this session’s research workspace.</div></div>',
            unsafe_allow_html=True,
        )
        return
    for name, info in metadata.items():
        safe_name = escape(str(name))
        info = info or {}
        header = headers.get(name, {}) or {}
        title = escape(str(header.get("title", "")))
        authors = escape(", ".join(header.get("authors", [])[:3])) if header.get("authors") else ""
        details = f"{info.get('pages', '—')} pages · {info.get('chunks', '—')} chunks"
        st.markdown(
            f'<div class="nx-card nx-card-compact">'
            f'<div class="nx-card-label">PDF DOCUMENT</div><div class="nx-card-title">▤ &nbsp;{safe_name}</div>'
            f'<div class="nx-card-copy">{details}{f"<br>{title}" if title else ""}{f"<br>{authors}" if authors else ""}</div></div>',
            unsafe_allow_html=True,
        )


def render_documents():
    apply_theme()
    render_header(
        "Knowledge base",
        "Your document library",
        "Upload PDFs and manage the documents available to NexRAG in this session.",
    )
    st.write("")
    if st.session_state.workspace_notice:
        st.info(st.session_state.workspace_notice)
        st.session_state.workspace_notice = ""
    uploaded_files = st.file_uploader(
        "Choose PDF documents", type=["pdf"], accept_multiple_files=True,
        help="Select one or more PDF files for this session’s knowledge base.", key="pdf_uploads",
    )
    semantic_chunking = st.checkbox("Use semantic chunking", value=True, key="semantic_chunking")
    add_col, spacer = st.columns([1, 2.5])
    with add_col:
        if st.button(
            f"Add {len(uploaded_files or [])} document{'s' if len(uploaded_files or []) != 1 else ''}",
            disabled=not uploaded_files or not engine_is_ready(), key="upload_documents",
        ):
            outcomes = []
            progress = st.progress(0)
            for index, uploaded_file in enumerate(uploaded_files):
                safe_name = Path(uploaded_file.name).name or "document.pdf"
                try:
                    with tempfile.TemporaryDirectory(prefix="nexrag_upload_") as folder:
                        pdf_path = Path(folder) / safe_name
                        pdf_path.write_bytes(uploaded_file.getvalue())
                        with st.spinner(f"Processing {safe_name}…"):
                            result = upload_and_process(
                                st.session_state.rag_system, str(pdf_path), semantic_chunking
                            )
                    outcomes.append(f"**{safe_name}** — {result}")
                except Exception as exc:
                    outcomes.append(f"**{safe_name}** — Error: {exc}")
                progress.progress((index + 1) / len(uploaded_files))
            st.session_state.upload_status = "\n\n".join(outcomes)
            st.rerun()
    if st.session_state.upload_status:
        st.info(st.session_state.upload_status)

    st.markdown('<div class="nx-rule"></div>', unsafe_allow_html=True)
    docs_col, actions_col = st.columns([2.6, 1])
    with docs_col:
        st.markdown(f'<div class="nx-section-title">Active documents · {document_count()}</div>', unsafe_allow_html=True)
        render_document_library()
    with actions_col:
        st.markdown(
            '<div class="nx-card nx-library-action"><div class="nx-card-label">LIBRARY ACTION</div>'
            '<div class="nx-card-title">Clear documents</div>'
            '<div class="nx-card-copy">Remove all indexed PDFs and retrieval data from this session.</div></div>',
            unsafe_allow_html=True,
        )
        confirm_clear = st.checkbox(
            "Confirm clear all", disabled=not engine_is_ready() or not has_loaded_documents(),
            key="confirm_clear",
        )
        if st.button(
            "Clear all documents", type="secondary", use_container_width=True,
            disabled=not engine_is_ready() or not has_loaded_documents() or not confirm_clear,
            key="clear_all_documents",
        ):
            with st.spinner("Clearing document library…"):
                result = st.session_state.rag_system.clear_all_documents()
            st.session_state.upload_status = str(result)
            st.session_state.summary = None
            st.session_state.summary_metadata = ""
            st.success(result)
            st.rerun()


def build_text_pdf(title, body_text):
    """Build a dependency-free PDF for a tool-generated report."""
    lines = str(body_text).splitlines()
    wrapped = []
    for line in lines:
        cleaned = re.sub(r"[*_`#]", "", line)
        wrapped.extend(textwrap.wrap(cleaned, width=88, break_long_words=True) if cleaned else [""])
    pages = [wrapped[index:index + 52] for index in range(0, max(1, len(wrapped)), 52)]
    objects = [None, b"<< /Type /Catalog /Pages 2 0 R >>"]
    page_ids = [3 + index * 2 for index in range(len(pages))]
    regular_font_id = 3 + len(pages) * 2
    bold_font_id = regular_font_id + 1
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("ascii"))
    for page_index, page_lines in enumerate(pages):
        page_id = page_ids[page_index]
        stream_id = page_id + 1
        commands = [
            f"BT /F2 16 Tf 54 790 Td ({_pdf_literal(title)}) Tj ET",
            f"BT /F1 9 Tf 54 772 Td (Page {page_index + 1} of {len(pages)}) Tj ET",
        ]
        y = 748
        for line in page_lines:
            font = "F1"
            size = 10
            commands.append(f"BT /{font} {size} Tf 54 {y} Td ({_pdf_literal(line)}) Tj ET")
            y -= 13
        stream = "\n".join(commands).encode("cp1252", "replace")
        objects.extend([
            (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
             f"/Resources << /Font << /F1 {regular_font_id} 0 R /F2 {bold_font_id} 0 R >> >> "
             f"/Contents {stream_id} 0 R >>").encode("ascii"),
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream",
        ])
    objects.extend([
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
    ])
    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id in range(1, len(objects)):
        offsets.append(len(pdf))
        pdf.extend(f"{object_id} 0 obj\n".encode("ascii"))
        pdf.extend(objects[object_id] + b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer\n<< /Size {len(objects)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii"))
    return bytes(pdf)


def extract_pdf_images(pdf_bytes):
    """Extract embedded figures while skipping page-sized and flat background images."""
    from pypdf import PdfReader
    from PIL import Image, ImageChops, ImageFilter

    def is_flat_background(image):
        width, height = image.size
        if width < 96 or height < 64:
            return False
        if "A" in image.getbands() and image.getchannel("A").getextrema()[0] < 255:
            return False

        sample = image.convert("RGB")
        sample.thumbnail((64, 64))
        softened = sample.filter(ImageFilter.GaussianBlur(radius=2))
        detail = ImageChops.difference(sample, softened).convert("L")
        detail_pixels = list(detail.getdata())
        if not detail_pixels:
            return True
        high_detail_ratio = sum(pixel > 18 for pixel in detail_pixels) / len(detail_pixels)
        return high_detail_ratio < 0.04

    output = BytesIO()
    count = 0
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for page_number, page in enumerate(PdfReader(BytesIO(pdf_bytes)).pages, 1):
            try:
                page_images = page.images
            except Exception:
                continue
            for image_number, image in enumerate(page_images, 1):
                try:
                    data = image.data
                    try:
                        with Image.open(BytesIO(data)) as decoded_image:
                            image_width, image_height = decoded_image.size
                            flat_background = is_flat_background(decoded_image)
                    except (OSError, ValueError):
                        image_width = image_height = 0
                        flat_background = False

                    if flat_background:
                        continue

                    page_width = abs(float(page.mediabox.width))
                    page_height = abs(float(page.mediabox.height))
                    if page_width and page_height and image_width and image_height:
                        image_ratio = image_width / image_height
                        page_ratio = page_width / page_height
                        direct_cover = (
                            abs(image_ratio / page_ratio - 1) <= 0.12
                            and image_width >= page_width * 0.82
                            and image_height >= page_height * 0.82
                        )
                        rotated_cover = (
                            abs(image_ratio / (1 / page_ratio) - 1) <= 0.12
                            and image_width >= page_height * 0.82
                            and image_height >= page_width * 0.82
                        )
                        if direct_cover or rotated_cover:
                            continue

                    image_name = Path(str(getattr(image, "name", ""))).name
                    extension = Path(image_name).suffix.lower()
                    if extension not in {".jpg", ".jpeg", ".png", ".jp2", ".tif", ".tiff", ".gif", ".bmp", ".webp"}:
                        extension = ".png" if data.startswith(b"\x89PNG") else ".jpg" if data.startswith(b"\xff\xd8") else ".bin"
                    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", Path(image_name).stem).strip("-")
                    stem = stem or f"image-{image_number}"
                    archive.writestr(f"page-{page_number:03d}/{stem}{extension}", data)
                    count += 1
                except Exception:
                    continue
    return (output.getvalue() if count else None), count


def render_account_section():
    if st.session_state.account_email:
        name = escape(str(st.session_state.account_name or ""))
        email = escape(str(st.session_state.account_email))
        st.markdown(
            '<div class="nx-account-card"><div class="nx-account-avatar">'
            f'{escape((st.session_state.account_name or st.session_state.account_email)[:1].upper())}'
            '</div><div><div class="nx-tool-kicker">SIGNED IN</div>'
            f'<div class="nx-tool-title">{name or email}</div>'
            f'<div class="nx-tool-copy">{email}</div></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign out", key="contact_sign_out"):
            st.session_state.account_email = None
            st.session_state.account_name = None
            st.rerun()
        return

    st.markdown(
        '<div class="nx-account-intro"><div class="nx-account-intro-icon" aria-hidden="true">&#9673;</div>'
        '<div><div class="nx-tool-kicker">YOUR PROFILE</div><div class="nx-account-intro-title">A familiar place to return to</div>'
        '<div class="nx-account-intro-copy">Create a local profile or sign in to the one you already use on this device.</div></div></div>',
        unsafe_allow_html=True,
    )
    create_tab, continue_tab = st.tabs(["Create account", "Sign in"])
    with create_tab:
        with st.form("contact_create_account"):
            display_name = st.text_input("Name", placeholder="Your name")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", help="Use at least 8 characters.")
            confirm_password = st.text_input("Confirm password", type="password")
            create_submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
        if create_submitted:
            normalized_email = email.strip().casefold()
            normalized_name = display_name.strip()
            if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized_email):
                st.error("Enter a valid email address.")
            elif not normalized_name:
                st.error("Enter your name.")
            elif len(password) < 8:
                st.error("Use a password with at least 8 characters.")
            elif password != confirm_password:
                st.error("The passwords do not match.")
            else:
                try:
                    if create_local_account(normalized_email, display_name, password):
                        st.session_state.account_email = normalized_email
                        st.session_state.account_name = normalized_name
                        st.rerun()
                    else:
                        st.error("An account already exists for that email. Continue with email to sign in.")
                except sqlite3.Error as exc:
                    st.error(f"Could not create the account: {exc}")

    with continue_tab:
        with st.form("contact_continue_email"):
            login_email = st.text_input("Email", placeholder="you@example.com", key="contact_login_email")
            login_password = st.text_input("Password", type="password", key="contact_login_password")
            login_submitted = st.form_submit_button("Continue", type="primary", use_container_width=True)
        if login_submitted:
            try:
                account = authenticate_local_account(login_email, login_password)
                if account:
                    st.session_state.account_email = account["email"]
                    st.session_state.account_name = account["name"]
                    st.rerun()
                st.error("We couldn’t sign you in with those details.")
            except sqlite3.Error as exc:
                st.error(f"Could not sign in: {exc}")


def render_contact():
    apply_theme()
    render_header("CONTACT", "Get in touch", "")
    contact_email = get_setting("CONTACT_EMAIL")
    contact_email_is_valid = bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", contact_email))
    smtp_host = get_setting("SMTP_HOST")
    smtp_sender = get_setting("SMTP_FROM_EMAIL") or get_setting("SMTP_USERNAME") or contact_email
    smtp_is_configured = bool(smtp_host and contact_email_is_valid and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", smtp_sender))

    contact_tab, account_tab = st.tabs(["Send a message", "Your account"])
    with contact_tab:
        left, right = st.columns([0.85, 1.15], gap="large")
        with left:
            st.markdown(
                '<div class="nx-contact-card"><div class="nx-contact-card-icon" aria-hidden="true">&#9993;</div>'
                '<div class="nx-tool-kicker">SUPPORT DESK</div>'
                '<div class="nx-tool-title">Let\'s make your workspace work better.</div>'
                '<div class="nx-tool-copy">Questions about setup, document processing, or your results? '
                'Send us a note and we\'ll help you find the next step.</div>'
                + (
                    '<div class="nx-contact-card-foot"><span>Sent from this form</span><span>Replies go to your inbox</span></div></div>'
                    if smtp_is_configured else
                    '<div class="nx-contact-card-foot"><span>Opens in your email app</span><span>You review before sending</span></div></div>'
                ),
                unsafe_allow_html=True,
            )
            if contact_email_is_valid:
                safe_email = escape(contact_email)
                mailto_email = quote(contact_email, safe="@.+-_")
                st.markdown(
                    f'<div class="nx-contact-email"><span>EMAIL</span>'
                    f'<a href="mailto:{mailto_email}">{safe_email}</a></div>',
                    unsafe_allow_html=True,
                )

        with right:
            with st.container(key="contact_form_panel"):
                st.markdown(
                    '<div class="nx-contact-form-heading"><div class="nx-tool-kicker">CONTACT FORM</div>'
                    '<div class="nx-contact-form-title">Send us a message</div>'
                    '<div class="nx-contact-form-copy">Share a little detail so we can point you in the right direction.</div></div>',
                    unsafe_allow_html=True,
                )
                with st.form("contact_message_form"):
                    sender_name = st.text_input("Your name", placeholder="Your name")
                    sender_email = st.text_input("Your email", placeholder="you@example.com")
                    subject = st.selectbox("What is this about?", ["General question", "Feedback", "Bug report", "Other"])
                    message = st.text_area("Message", placeholder="How can we help?", height=150, max_chars=3000)
                    submitted = st.form_submit_button(
                        "Send message", type="primary", use_container_width=True
                    )

                if submitted:
                    st.session_state.contact_mailto = None
                    st.session_state.contact_notice = None
                    st.session_state.contact_notice_kind = "info"
                    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", sender_email.strip()):
                        st.error("Enter a valid email address so we can reply.")
                    elif not message.strip():
                        st.error("Write a message before continuing.")
                    else:
                        body = (
                            f"From: {sender_name.strip() or 'NexRAG user'}\n"
                            f"Reply to: {sender_email.strip()}\n\n{message.strip()}"
                        )
                        if smtp_is_configured:
                            try:
                                email_message = EmailMessage()
                                email_message["Subject"] = f"[NexRAG] {subject}"
                                email_message["From"] = smtp_sender
                                email_message["To"] = contact_email
                                email_message["Reply-To"] = sender_email.strip()
                                email_message.set_content(body)

                                smtp_port = int(get_setting("SMTP_PORT", "587"))
                                use_ssl = get_setting("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes", "on"}
                                use_tls = get_setting("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
                                timeout = float(get_setting("SMTP_TIMEOUT", "15"))
                                context = ssl.create_default_context()
                                if use_ssl:
                                    mail_server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=timeout, context=context)
                                else:
                                    mail_server = smtplib.SMTP(smtp_host, smtp_port, timeout=timeout)
                                with mail_server:
                                    if use_tls and not use_ssl:
                                        mail_server.starttls(context=context)
                                    smtp_username = get_setting("SMTP_USERNAME")
                                    smtp_password = get_setting("SMTP_PASSWORD")
                                    if smtp_username:
                                        mail_server.login(smtp_username, smtp_password)
                                    mail_server.send_message(email_message)
                                st.session_state.contact_notice = "Message sent successfully."
                                st.session_state.contact_notice_kind = "success"
                            except (OSError, smtplib.SMTPException, ValueError) as exc:
                                st.session_state.contact_notice = f"Could not send the message: {exc}"
                                st.session_state.contact_notice_kind = "error"
                        else:
                            recipient = quote(contact_email, safe="@.+-_") if contact_email_is_valid else ""
                            st.session_state.contact_mailto = (
                                f"mailto:{recipient}?subject={quote('[NexRAG] ' + subject)}&body={quote(body)}"
                            )
                            st.session_state.contact_notice = "Message sent successfully."

                notice = st.session_state.contact_notice
                if notice:
                    if st.session_state.contact_notice_kind == "success":
                        st.success(notice)
                    elif st.session_state.contact_notice_kind == "error":
                        st.error(notice)
                    else:
                        st.info(notice)
                if st.session_state.contact_mailto:
                    st.link_button("Open email app", st.session_state.contact_mailto, type="primary", use_container_width=True)

    with account_tab:
        render_account_section()


def render_tools():
    apply_theme()
    render_header("PDF WORKSPACE", "Tools", "")
    st.write("")
    with st.expander("Retrieval options", expanded=False):
        st.checkbox("HyDE (sample-answer search)", key="use_hyde")
        st.caption("Uses a sample answer to find relevant passages.")
        st.checkbox("Multi-query search", key="use_multi_query")
        st.caption("Searches your question in a few different ways.")

    engine = st.session_state.get("rag_system")
    documents = list((getattr(engine, "pdf_metadata", {}) or {}).keys()) if engine else []
    if not documents:
        st.markdown(
            '<div class="nx-empty"><div class="nx-empty-title">Add a PDF to use these tools</div>'
            '<div class="nx-empty-copy">Use the + button on Home to add a document.</div></div>',
            unsafe_allow_html=True,
        )
        return

    if st.session_state.get("tools_selected_pdf") not in documents:
        st.session_state.tools_selected_pdf = documents[0]
    selected_pdf = st.selectbox("Select a PDF", documents, key="tools_selected_pdf")
    summary_column, images_column = st.columns(2)
    with summary_column:
        with st.container(key="tool_summary_card"):
            st.markdown(
                '<div class="nx-tool-art nx-tool-summary-art"><svg viewBox="0 0 100 78" aria-hidden="true">'
                '<path class="nx-tool-page-back" d="M27 12h35l12 12v42H27z"/><path class="nx-tool-page-front" d="M19 7h35l12 12v42H19z"/>'
                '<path class="nx-tool-page-fold" d="M54 7v13h12M28 34h28M28 43h25M28 52h18"/>'
                '<path class="nx-tool-spark" d="m77 9 3 7 7 3-7 3-3 7-3-7-7-3 7-3z"/></svg></div>'
                '<div class="nx-tool-kicker">TOOL 01</div><div class="nx-tool-title">File summary</div>'
                '<div class="nx-tool-copy">Summarize the selected PDF and download the result as a PDF.</div>',
                unsafe_allow_html=True,
            )
            if st.button("Summarize selected file", use_container_width=True, key="tool_summarize_pdf", disabled=not engine_is_ready()):
                try:
                    with st.spinner(f"Summarizing {selected_pdf}…"):
                        st.session_state.tool_summaries[selected_pdf] = summarize_selected_pdf(engine, selected_pdf)
                except Exception as exc:
                    st.session_state.tool_summaries[selected_pdf] = (f"Error: {exc}", "")
    with images_column:
        with st.container(key="tool_images_card"):
            st.markdown(
                '<div class="nx-tool-art nx-tool-images-art"><svg viewBox="0 0 100 78" aria-hidden="true">'
                '<rect class="nx-tool-image-frame" x="13" y="10" width="74" height="56" rx="10"/>'
                '<circle class="nx-tool-image-sun" cx="68" cy="26" r="7"/>'
                '<path class="nx-tool-image-land" d="m20 57 17-18 11 11 10-12 22 22H20z"/>'
                '<circle class="nx-tool-image-dot" cx="24" cy="17" r="2"/><circle class="nx-tool-image-dot" cx="78" cy="58" r="2"/></svg></div>'
                '<div class="nx-tool-kicker">TOOL 02</div><div class="nx-tool-title">Image extraction</div>'
                '<div class="nx-tool-copy">Collect detailed figures while skipping page-sized and flat background images.</div>',
                unsafe_allow_html=True,
            )
            if st.button("Extract images", use_container_width=True, key="tool_extract_images"):
                pdf_files = getattr(engine, "pdf_files", {}) if engine else {}
                pdf_bytes = pdf_files.get(selected_pdf)
                if not pdf_bytes:
                    st.session_state.tool_notice_file = selected_pdf
                    st.session_state.tool_notice = (
                        "This older library entry has no stored PDF data. Remove it from History > Files and add it again from Home."
                    )
                    st.session_state.tool_images_zip = None
                    st.session_state.tool_images_file = None
                else:
                    try:
                        with st.spinner(f"Extracting images from {selected_pdf}…"):
                            archive, image_count = extract_pdf_images(pdf_bytes)
                        st.session_state.tool_images_zip = archive
                        st.session_state.tool_images_file = selected_pdf
                        st.session_state.tool_images_count = image_count
                        st.session_state.tool_notice_file = selected_pdf
                        st.session_state.tool_notice = (
                            f"Extracted {image_count} image(s)." if image_count else "No embedded images were found in this PDF."
                        )
                    except Exception as exc:
                        st.session_state.tool_notice_file = selected_pdf
                        st.session_state.tool_notice = f"Could not extract images: {exc}"
                        st.session_state.tool_images_zip = None
                        st.session_state.tool_images_file = None

    summary_result = st.session_state.tool_summaries.get(selected_pdf)
    if summary_result:
        summary, summary_metadata = summary_result
        st.markdown('<div class="nx-rule"></div><div class="nx-section-title">File summary</div>', unsafe_allow_html=True)
        st.markdown(str(summary))
        if summary_metadata:
            with st.expander("Summary details", expanded=False):
                st.markdown(str(summary_metadata))
        if not str(summary).startswith("Error:"):
            stub = re.sub(r"[^a-zA-Z0-9_-]+", "-", Path(selected_pdf).stem).strip("-") or "document"
            st.download_button(
                "Download summary as PDF", data=build_text_pdf(f"NexRAG Summary: {selected_pdf}", summary),
                file_name=f"{stub}-summary.pdf", mime="application/pdf", key="download_tool_summary",
            )

    if st.session_state.tool_notice and st.session_state.tool_notice_file == selected_pdf:
        st.info(st.session_state.tool_notice)
    if st.session_state.tool_images_file == selected_pdf and st.session_state.tool_images_zip:
        stub = re.sub(r"[^a-zA-Z0-9_-]+", "-", Path(selected_pdf).stem).strip("-") or "document"
        st.download_button(
            "Download extracted images (.zip)", data=st.session_state.tool_images_zip,
            file_name=f"{stub}-images.zip", mime="application/zip", key="download_tool_images",
        )


def _pdf_literal(value):
    safe = str(value).encode("cp1252", "replace").decode("cp1252")
    return safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_chat_pdf(chat):
    """Build a compact, dependency-free PDF export for one saved conversation."""
    title = str(chat.get("title") or "NexRAG conversation")
    content_lines = [
        "NexRAG Conversation",
        f"Title: {title}",
        f"Created: {chat.get('created_at', 'Unknown')}",
        "",
    ]
    for index, message in enumerate(chat.get("messages", []), 1):
        content_lines.extend([
            f"Question {index}:",
            str(message.get("question", "")),
            "",
            "Answer:",
            str(message.get("answer", "")),
        ])
        citations = message.get("citations")
        if citations:
            source_text = unescape(re.sub(r"<[^>]+>", " ", str(citations)))
            source_text = re.sub(r"\s+", " ", source_text).strip()
            if source_text:
                content_lines.extend(["", f"Sources: {source_text}"])
        content_lines.append("")

    wrapped = []
    for line in content_lines:
        cleaned = re.sub(r"[*_`#]", "", line)
        if not cleaned:
            wrapped.append("")
        else:
            wrapped.extend(textwrap.wrap(cleaned, width=88, break_long_words=True, break_on_hyphens=False) or [""])

    pages = [wrapped[index:index + 50] for index in range(0, max(1, len(wrapped)), 50)]
    objects = [None, b"<< /Type /Catalog /Pages 2 0 R >>"]
    page_ids = [3 + index * 2 for index in range(len(pages))]
    regular_font_id = 3 + len(pages) * 2
    bold_font_id = regular_font_id + 1
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("ascii"))

    for page_index, page_lines in enumerate(pages):
        page_id = page_ids[page_index]
        stream_id = page_id + 1
        commands = [
            "BT /F2 17 Tf 54 790 Td (NexRAG Conversation) Tj ET",
            f"BT /F1 9 Tf 54 772 Td (Page {page_index + 1} of {len(pages)}) Tj ET",
        ]
        y = 746
        for line_index, line in enumerate(page_lines):
            font = "F2" if line.startswith(("Title:", "Created:", "Question ", "Answer:", "Sources:")) else "F1"
            size = 11 if font == "F2" else 10
            commands.append(f"BT /{font} {size} Tf 54 {y} Td ({_pdf_literal(line)}) Tj ET")
            y -= 13
        stream = "\n".join(commands).encode("cp1252", "replace")
        page_object = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {regular_font_id} 0 R /F2 {bold_font_id} 0 R >> >> "
            f"/Contents {stream_id} 0 R >>"
        ).encode("ascii")
        stream_object = f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream"
        objects.extend([page_object, stream_object])

    objects.extend([
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
    ])
    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id in range(1, len(objects)):
        offsets.append(len(pdf))
        pdf.extend(f"{object_id} 0 obj\n".encode("ascii"))
        pdf.extend(objects[object_id])
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii")
    )
    return bytes(pdf)


def render_history():
    apply_theme()
    render_header(
        "SESSION HISTORY",
        "Your documents and chats",
        "Browse uploaded PDFs and saved conversations from this session.",
        subtitle_align="left",
    )
    search_query = st.session_state.get("history_search", "").strip().lower()
    notice = st.session_state.get("history_notice")
    if notice:
        kind, message = notice
        if kind == "success":
            st.success(message)
        else:
            st.error(message)
        st.session_state.history_notice = None

    chats_tab, files_tab = st.tabs(["Chats", "Files"])
    engine = st.session_state.get("rag_system")
    metadata = getattr(engine, "pdf_metadata", {}) if engine else {}
    headers = getattr(engine, "doc_headers", {}) if engine else {}
    indexed_docs = getattr(engine, "documents", []) if engine else []

    with files_tab:
        st.markdown('<div class="nx-section-title">Files in this session</div>', unsafe_allow_html=True)
        document_entries = []
        for name, info in metadata.items():
            header = headers.get(name, {}) or {}
            all_chunks = [doc for doc in indexed_docs if doc.metadata.get("pdf_name") == name]
            excerpts = all_chunks[:3]
            searchable = " ".join([
                str(name), str((info or {}).get("added", "")), str(header.get("title", "")),
                " ".join(header.get("authors", [])),
                " ".join(doc.page_content for doc in all_chunks),
            ]).lower()
            if not search_query or search_query in searchable:
                document_entries.append((name, info, header, excerpts))

        if not metadata:
            st.markdown(
                '<div class="nx-empty"><div class="nx-empty-title">No files yet</div>'
                '<div class="nx-empty-copy">PDFs you add from the plus button will appear here.</div></div>',
                unsafe_allow_html=True,
            )
        elif not document_entries:
            st.markdown(
                '<div class="nx-empty"><div class="nx-empty-title">No matching files</div>'
                '<div class="nx-empty-copy">Try another filename, author, or phrase from the indexed text.</div></div>',
                unsafe_allow_html=True,
            )
        else:
            for name, info, header, excerpts in document_entries:
                safe_name = escape(str(name))
                info = info or {}
                title = escape(str(header.get("title", "")))
                authors = escape(", ".join(header.get("authors", [])[:3])) if header.get("authors") else ""
                st.markdown(
                    f'<div class="nx-card nx-history-doc"><div class="nx-card-label">PDF DOCUMENT</div>'
                    f'<div class="nx-card-title">{safe_name}</div><div class="nx-card-copy">'
                    f'{info.get("pages", "—")} pages · {info.get("chunks", "—")} indexed passages'
                    f'{f"<br>{title}" if title else ""}{f"<br>{authors}" if authors else ""}'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
                with st.expander(f"Preview indexed text · {name}"):
                    if not excerpts:
                        st.caption("No indexed passages are available for preview.")
                    for doc in excerpts:
                        page_number = int(doc.metadata.get("page", 0)) + 1
                        preview = str(doc.page_content).strip()[:700]
                        st.markdown(
                            f'<div class="nx-history-excerpt"><b>Page {page_number}</b><br>{escape(preview)}</div>',
                            unsafe_allow_html=True,
                        )
                file_key = hashlib.md5(str(name).encode("utf-8")).hexdigest()[:10]
                st.button(
                    "Remove file", type="secondary", key=f"remove_file_{file_key}",
                    on_click=remove_history_document, args=(name,),
                )

    with chats_tab:
        st.markdown('<div class="nx-section-title">Saved chats</div>', unsafe_allow_html=True)
        matching_chats = []
        for chat in reversed(st.session_state.chat_sessions):
            messages = chat.get("messages", [])
            title_text = str(chat.get("title", "Conversation"))
            matching_messages = [
                message for message in messages
                if search_query and search_query in (
                    str(message.get("question", "")) + " " + str(message.get("answer", ""))
                ).lower()
            ]
            title_matches = search_query and search_query in title_text.lower()
            if search_query and not title_matches and not matching_messages:
                continue
            preview = matching_messages[-1] if matching_messages else (messages[-1] if messages else {})
            matching_chats.append((chat, preview))

        if not matching_chats:
            title = "No matching chats" if search_query else "No saved chats yet"
            detail = "Try a different search phrase." if search_query else "Questions you ask in Home will be saved here automatically."
            st.markdown(
                f'<div class="nx-empty"><div class="nx-empty-title">{title}</div>'
                f'<div class="nx-empty-copy">{detail}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            for chat, latest in matching_chats:
                chat_id = chat["id"]
                messages = chat.get("messages", [])
                preview_question = escape(str(latest.get("question", ""))[:180])
                preview_answer = escape(str(latest.get("answer", ""))[:280])
                title = escape(str(chat.get("title", "Conversation")))
                created_at = escape(str(chat.get("created_at", "")))
                st.markdown(
                    f'<div class="nx-card nx-history-chat"><div class="nx-card-label">{created_at} · {len(messages)} question(s)</div>'
                    f'<div class="nx-card-title">{title}</div><div class="nx-card-copy"><b>Latest question:</b> {preview_question}'
                    f'<br><b>Answer preview:</b> {preview_answer}</div></div>',
                    unsafe_allow_html=True,
                )
                action_cols = st.columns([1, 1, 1, 3])
                with action_cols[0]:
                    st.button("Open chat", use_container_width=True, key=f"open_chat_{chat_id}", on_click=open_saved_chat, args=(chat_id,))
                with action_cols[1]:
                    filename = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(chat.get("title", "conversation"))).strip("-") or "conversation"
                    st.download_button(
                        "Save PDF", data=build_chat_pdf(chat), file_name=f"{filename}.pdf",
                        mime="application/pdf", use_container_width=True, key=f"export_chat_{chat_id}",
                    )
                with action_cols[2]:
                    st.button("Delete", use_container_width=True, key=f"delete_chat_{chat_id}", on_click=delete_saved_chat, args=(chat_id,))

def render_summary():
    apply_theme()
    render_header(
        "Document synthesis",
        "A unified view of your library",
        "Generate one comprehensive summary across all documents in your active library.",
    )
    st.write("")
    if not engine_is_ready():
        st.info("The system is initializing from your configured environment.")
    elif not has_loaded_documents():
        st.info("Add a PDF with the + button on Home before generating a summary.")
    if st.button(
        "✦  Generate library summary", disabled=not engine_is_ready() or not has_loaded_documents(),
        key="generate_summary",
    ):
        with st.spinner("Synthesizing your documents…"):
            summary, metadata = summarize_doc(st.session_state.rag_system)
        st.session_state.summary = summary
        st.session_state.summary_metadata = metadata
    if st.session_state.summary:
        st.markdown('<div class="nx-rule"></div><div class="nx-eyebrow">LIBRARY SUMMARY</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.summary)
        if st.session_state.summary_metadata:
            with st.expander("Summary details"):
                st.markdown(str(st.session_state.summary_metadata))




def main():
    initialize_state()

    # Initialize automatically once per Streamlit session when a secret is configured.
    if not engine_is_ready() and not st.session_state.init_attempted:
        st.session_state.init_attempted = True
        if get_setting("GROQ_API_KEY"):
            with st.spinner("Starting NexRAG and loading retrieval models…"):
                st.session_state.init_status = initialize_system()
        else:
            st.session_state.init_status = initialize_system()

    with st.container(key="app_shell"):
        with st.container(key="rail"):
            page = render_sidebar()
        with st.container(key="workspace"):
            render_topbar(page)
            if page == "Home":
                render_overview()
            elif page == "Overview":
                render_project_guide()
            elif page == "Chat":
                render_overview()
            elif page == "Tools":
                render_tools()
            elif page == "History":
                render_history()
            elif page == "Contact":
                render_contact()
            elif page == "Summarization":
                render_summary()


if __name__ == "__main__":
    main()
