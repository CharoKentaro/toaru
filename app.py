import streamlit as st
from tools import translator_tool

# 1. アプリの基本設定
st.set_page_config(page_title="フレンドリー翻訳ツール", page_icon="🤝", layout="wide")

# 2. UI描画 + ツール起動ロジック
with st.sidebar:
    st.title("🤝 フレンドリー翻訳")
    st.divider()
    if 'gemini_api_key' not in st.session_state: st.session_state.gemini_api_key = ""
    if 'speech_api_key' not in st.session_state: st.session_state.speech_api_key = ""
    with st.expander("⚙️ APIキーの設定"):
        st.session_state.gemini_api_key = st.text_input("Gemini APIキー", type="password", value=st.session_state.gemini_api_key)
        st.session_state.speech_api_key = st.text_input("Speech-to-Text APIキー", type="password", value=st.session_state.speech_api_key)

# --- メインコンテンツ ---
st.title("AIアシスタント・ポータル")
translator_tool.show_tool(
    gemini_api_key=st.session_state.get('gemini_api_key', ''),
    speech_api_key=st.session_state.get('speech_api_key', '')
)
