# ポータルのメインファイル Ver. Ω (オメガ)
import streamlit as st
from tools import translator_tool

# 1. アプリの基本設定
st.set_page_config(page_title="フレンドリー翻訳ツール", page_icon="🤝", layout="wide")

# 2. UI描画 + ツール起動ロジック
with st.sidebar:
    st.title("🤝 フレンドリー翻訳")
    st.info("このツールは、あなたの言葉を、海外の親しい友人との会話で使われるような、自然でフレンドリーな英語に翻訳します。")
    st.divider()
    if 'gemini_api_key' not in st.session_state: st.session_state.gemini_api_key = ""
    if 'speech_api_key' not in st.session_state: st.session_state.speech_api_key = ""
    with st.expander("⚙️ APIキーの設定", expanded=not(st.session_state.gemini_api_key)):
        st.session_state.gemini_api_key = st.text_input("Gemini APIキー", type="password", value=st.session_state.gemini_api_key, help="翻訳機能に必要です。")
        st.session_state.speech_api_key = st.text_input("Speech-to-Text APIキー", type="password", value=st.session_state.speech_api_key, help="音声入力機能には現在対応していません。")
    st.markdown("""<div style="font-size: 0.9em; text-align: center;"><a href="https://aistudio.google.com/app/apikey" target="_blank">Gemini APIキーの取得はこちら</a><br><a href="https://console.cloud.google.com/apis/credentials" target="_blank">Speech-to-Text APIキーの取得はこちら</a></div>""", unsafe_allow_html=True)

# --- メインコンテンツ ---
st.title("AIアシスタント・ポータル")
translator_tool.show_tool(
    gemini_api_key=st.session_state.get('gemini_api_key', ''),
    speech_api_key=st.session_state.get('speech_api_key', '')
)
