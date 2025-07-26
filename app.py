import streamlit as st
from streamlit_local_storage import LocalStorage
import time
# ★★★ ここで、我々は、二人の、偉大なる、専門家を、招聘します ★★★
from tools import translator_tool, okozukai_recorder_tool

# --- アプリの基本設定 (変更なし) ---
st.set_page_config(page_title="Multi-Tool Portal", page_icon="🚀", layout="wide")

# --- サイドバー (APIキーと、ツール選択の、司令塔へと、進化) ---
with st.sidebar:
    # ★★★ ポータルの、顔となる、タイトルです ★★★
    st.title("🚀 Multi-Tool Portal")
    st.divider()

    # ★★★ ここが、新たなる、叡智。ツール選択の、心臓部です ★★★
    tool_selection = st.radio(
        "利用するツールを選択してください:",
        ("🤝 翻訳ツール", "💰 お小遣いレコーダー"),
        key="tool_selection" # セッションステートに、選択を、記憶させます
    )
    st.divider()

    # --- APIキー管理部分は、全ての、ツールで、共通の、ため、変更なし ---
    localS = LocalStorage()
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
        localS.setItem("gemini_api_key", st.session_state.gemini_api_key)
        st.success("キーをブラウザに保存しました！"); time.sleep(1); st.rerun()
    if reset_button:
        localS.setItem("gemini_api_key", None); st.session_state.gemini_api_key = ""; st.success("キーをクリアしました。"); time.sleep(1); st.rerun()
    st.divider()
    st.markdown("""<div style="font-size: 0.9em;"><a href="https://aistudio.google.com/app/apikey" target="_blank">Gemini APIキーの取得はこちら</a></div>""", unsafe_allow_html=True)


# ★★★★★ ここが、ポータル・アーキテクチャの、真髄！『偉大なる、仕分け人』です ★★★★★
# ユーザーの選択に応じて、適切な専門家を呼び出します。
if st.session_state.tool_selection == "🤝 翻訳ツール":
    translator_tool.show_tool(
        gemini_api_key=st.session_state.get('gemini_api_key', '')
    )
elif st.session_state.tool_selection == "💰 お小遣いレコーダー":
    okozukai_recorder_tool.show_tool(
        gemini_api_key=st.session_state.get('gemini_api_key', '')
    )
