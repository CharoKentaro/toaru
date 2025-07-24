import streamlit as st
from tools import translator_tool

# 1. アプリの基本設定
st.set_page_config(page_title="フレンドリー翻訳ツール", page_icon="🤝", layout="wide")

# 2. UI描画 + ツール起動ロジック
with st.sidebar:
    st.title("🤝 フレンドリー翻訳")
    st.divider()

    # --- APIキー管理を、Gemini APIキーのみにシンプル化 ---
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ""
    
    # Speech-to-Text APIキーに関する記述は、もはや不要なため完全に削除
    # if 'speech_api_key' not in st.session_state: st.session_state.speech_api_key = ""

    with st.expander("⚙️ APIキーの設定"):
        st.session_state.gemini_api_key = st.text_input(
            "Gemini APIキー",
            type="password",
            value=st.session_state.gemini_api_key
        )
        # Speech-to-Text APIキーの入力欄も、当然不要なため完全に削除
        # st.session_state.speech_api_key = st.text_input("Speech-to-Text APIキー", type="password", value=st.session_state.speech_api_key)

# --- メインコンテンツ ---
st.title("AIアシスタント・ポータル")

# --- 専門家の呼び出しを、新しい仕様に合わせる ---
# speech_api_keyの引数を削除し、gemini_api_keyのみを渡す
translator_tool.show_tool(
    gemini_api_key=st.session_state.get('gemini_api_key', '')
)
