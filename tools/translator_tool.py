import streamlit as st
import google.generativeai as genai
from google.cloud import speech
from google.api_core.client_options import ClientOptions

# ===============================================================
# 補助関数
# ===============================================================
def translate_text_with_gemini(text_to_translate, api_key):
    if not text_to_translate or not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(
            f"以下の日本語を、海外の親しい友人との会話で使われるような、自然でフレンドリーな英語に翻訳してください。翻訳後の英語テキストのみを回答してください。\n\n日本語：{text_to_translate}"
        )
        return response.text.strip()
    except Exception:
        return "翻訳中にエラーが発生しました。"

# ===============================================================
# 専門家のメインの仕事 (原点回帰バージョン)
# ===============================================================
def show_tool(gemini_api_key, speech_api_key):

    st.header("🤝 フレンドリー翻訳ツール", divider='rainbow')

    # --- 状態管理の初期化 ---
    if "translator_results" not in st.session_state:
        st.session_state.translator_results = []
    if "translator_last_text" not in st.session_state:
        st.session_state.translator_last_text = ""

    # --- UIウィジェットの表示 ---
    st.info("テキストボックスに日本語を入力して、Enterキーを押してください。")
    text_prompt = st.text_input(
        "ここに日本語を入力してください...",
        key="translator_text"
    )

    # --- 結果表示エリア ---
    if st.session_state.translator_results:
        st.write("---")
        for result in st.session_state.translator_results:
            with st.container(border=True):
                st.markdown(f"**🇯🇵 あなたの入力:**\n> {result['original']}")
                st.markdown(f"**🇺🇸 AIの翻訳:**\n> {result['translated']}")
        
        if st.button("翻訳履歴をクリア", key="clear_translator_history"):
            st.session_state.translator_results = []
            st.session_state.translator_last_text = text_prompt
            st.rerun()

    # --- 入力検知と処理 ---
    japanese_text_to_process = None
    if text_prompt and text_prompt != st.session_state.translator_last_text:
        japanese_text_to_process = text_prompt
        st.session_state.translator_last_text = text_prompt

    if japanese_text_to_process:
        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを設定してください。")
        else:
            with st.spinner("AIが最適な英語を考えています..."):
                translated_text = translate_text_with_gemini(
                    japanese_text_to_process, gemini_api_key
                )
            
            if translated_text:
                st.session_state.translator_results.insert(
                    0,
                    {
                        "original": japanese_text_to_process,
                        "translated": translated_text
                    }
                )
                st.rerun()
            else:
                st.warning("翻訳に失敗しました。もう一度お試しください。")
