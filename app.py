import streamlit as st
from streamlit_local_storage import LocalStorage
import time

# ★★★ 七人の、英雄たちが、ここに、集結します ★★★
from tools import translator_tool, okozukai_recorder_tool, calendar_tool, gijiroku_tool, kensha_no_kioku_tool
from tools import ai_memory_partner

# --- アプリの基本設定 (変更なし) ---
st.set_page_config(page_title="Multi-Tool Portal", page_icon="🚀", layout="wide")

# --- サイドバー (最終形態) ---
with st.sidebar:
    st.title("🚀 Multi-Tool Portal")
    st.divider()

    # ★★★ 選択肢は、七つに ★★★
    tool_selection = st.radio(
        "利用するツールを選択してください:",
        ("❤️ 認知予防ツール", "🤝 翻訳ツール", "💰 お小遣い管理", "📅 カレンダーAI秘書", "📝 議事録作成", "🧠 賢者の記憶"),
        key="tool_selection"
    )
    st.divider()

    # ★★★ ここで、帝国の、唯一の、魔法使いが、生まれます ★★★
    localS = LocalStorage()

    # --- APIキー管理 (Gemini一本化の、思想は、揺るがない) ---
    saved_key = localS.getItem("gemini_api_key")
    gemini_default = saved_key if isinstance(saved_key, str) else ""
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = gemini_default
    with st.expander("⚙️ APIキーの設定", expanded=not st.session_state.gemini_api_key):
        with st.form("api_key_form", clear_on_submit=False):
            st.session_state.gemini_api_key = st.text_input("Gemini APIキー", type="password", value=st.session_state.gemini_api_key)
            col1, col2 = st.columns(2)
            with col1: save_button = st.form_submit_button("💾 保存", use_container_width=True)
            with col2: reset_button = st.form_submit_button("🔄 クリア", use_container_width=True)
    if save_button:
        # 聖典に倣い、setItemのkeyを削除し、信頼性を向上させます
        localS.setItem("gemini_api_key", st.session_state.gemini_api_key)
        st.success("キーをブラウザに保存しました！"); time.sleep(1); st.rerun()
    if reset_button:
        localS.setItem("gemini_api_key", None);
        st.session_state.gemini_api_key = ""
        st.success("キーをクリアしました。"); time.sleep(1); st.rerun()
    st.divider()
    st.markdown("""<div style="font-size: 0.9em;"><a href="https://aistudio.google.com/app/apikey" target="_blank">Gemini APIキーの取得はこちら</a></div>""", unsafe_allow_html=True)

# ★★★★★ 『偉大なる、仕分け人』の、最終契約書 ★★★★★
if st.session_state.tool_selection == "❤️ 認知予防ツール":
    # ★★★ 王が、英雄に、信頼する、魔法使いを、派遣します ★★★
    ai_memory_partner.show_tool(gemini_api_key=st.session_state.get('gemini_api_key', ''), localS_object=localS)
elif st.session_state.tool_selection == "🤝 翻訳ツール":
    translator_tool.show_tool(gemini_api_key=st.session_state.get('gemini_api_key', ''))
elif st.session_state.tool_selection == "💰 お小遣い管理":
    # お小遣い管理ツールにも、唯一の、魔法使いを、派遣します
    okozukai_recorder_tool.show_tool(gemini_api_key=st.session_state.get('gemini_api_key', ''), localS_object=localS)
elif st.session_state.tool_selection == "📅 カレンダーAI秘書":
    calendar_tool.show_tool(gemini_api_key=st.session_state.get('gemini_api_key', ''))
elif st.session_state.tool_selection == "📝 議事録作成":
    gijiroku_tool.show_tool(gemini_api_key=st.session_state.get('gemini_api_key', ''))
elif st.session_state.tool_selection == "🧠 賢者の記憶":
    kensha_no_kioku_tool.show_tool(gemini_api_key=st.session_state.get('gemini_api_key', ''))
