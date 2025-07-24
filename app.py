import streamlit as st
from streamlit_local_storage import LocalStorage
import time
from tools import translator_tool

# 1. アプリの基本設定
st.set_page_config(page_title="🤝 フレンドリー翻訳ツール", page_icon="🤝", layout="wide")

# 2. サイドバー (APIキー管理の司令塔)
with st.sidebar:
    st.title("🤝 フレンドリー翻訳")
    st.divider()

    # --- LocalStorageの準備 (成功コードからの叡智) ---
    localS = LocalStorage()

    # --- ローカルストレージからAPIキーを読み込む ---
    saved_key = localS.getItem("gemini_api_key")
    gemini_default = saved_key if isinstance(saved_key, str) else ""

    # --- セッションステートの初期化 ---
    # アプリ起動時に一度だけ、ローカルストレージの値で初期化する
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = gemini_default

    # --- APIキー設定フォーム (成功コードのUIを継承) ---
    with st.expander("⚙️ APIキーの設定", expanded=not st.session_state.gemini_api_key):
        with st.form("api_key_form", clear_on_submit=False):
            st.session_state.gemini_api_key = st.text_input(
                "Gemini APIキー",
                type="password",
                value=st.session_state.gemini_api_key
            )
            # Speech-to-Text APIキーの入力欄は、私たちの進化により不要となった

            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("💾 保存", use_container_width=True)
            with col2:
                reset_button = st.form_submit_button("🔄 クリア", use_container_width=True)

    # --- フォームボタンの処理 (成功コードのロジックを継承) ---
    if save_button:
        localS.setItem("gemini_api_key", st.session_state.gemini_api_key)
        st.success("キーをブラウザに保存しました！")
        time.sleep(1)
        st.rerun()

    if reset_button:
        localS.setItem("gemini_api_key", None)
        st.session_state.gemini_api_key = ""
        st.success("キーをクリアしました。")
        time.sleep(1)
        st.rerun()

    st.divider()
    st.markdown("""<div style="font-size: 0.9em;"><a href="https://aistudio.google.com/app/apikey" target="_blank">Gemini APIキーの取得はこちら</a></div>""", unsafe_allow_html=True)


# 3. メインコンテンツ (専門家の呼び出し)
# --- 司令塔が管理するAPIキーを、専門家に渡す ---
translator_tool.show_tool(
    gemini_api_key=st.session_state.get('gemini_api_key', '')
)
