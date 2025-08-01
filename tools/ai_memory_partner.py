import streamlit as st
import google.generativeai as genai
import time
from google.api_core import exceptions
from streamlit_mic_recorder import mic_recorder

# ===============================================================
# 【実験用】補助関数 - 『魂なき、木霊』
# ===============================================================
def echo_by_gemini(content_to_process, api_key):
    # この関数は、成功している翻訳ツールの構造を、完全に、模倣しています
    if not content_to_process or not api_key:
        return None, None

    try:
        genai.configure(api_key=api_key)
        # 翻訳ツールと同じ、最も、シンプルな、モデルを使用します
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # --- 第一段階：文字起こし（翻訳ツールと、全く、同じ） ---
        if isinstance(content_to_process, bytes):
            with st.spinner("（あなたの声を、言葉に、変えています...）"):
                audio_part = {"mime_type": "audio/webm", "data": content_to_process}
                transcription_prompt = "この日本語の音声を、できる限り正確に、文字に書き起こしてください。書き起こした日本語テキストのみを回答してください。"
                transcription_response = model.generate_content([transcription_prompt, audio_part])
                processed_text = transcription_response.text.strip()
            if not processed_text:
                st.error("あなたの声を、言葉に、変えることができませんでした。もう一度お試しください。")
                return None, None
            original_input_display = f"{processed_text} (🎙️音声より)"
        else:
            return None, None # この実験では、音声入力のみを、想定します

        # --- 第二段階：オウム返し（AIの、仕事を、究極に、単純化） ---
        with st.spinner("（AIが、あなたの、言葉を、聞いています...）"):
            # ここでは、複雑なプロンプトは、一切、与えません
            # AIは、ただ、受け取った言葉を、そのまま、返すだけです
            ai_response_text = processed_text
        
        # 成功の、聖典に、倣い、二つの、値を、返します
        return original_input_display, ai_response_text

    # --- エラー処理も、翻訳ツールと、全く、同じです ---
    except exceptions.ResourceExhausted as e:
        st.error("【実験中のエラー】APIキーの上限に達した可能性があります。(ResourceExhausted)")
        return None, None
    except Exception as e:
        error_message = str(e).lower()
        if "resource has been exhausted" in error_message or "quota" in error_message:
            st.error("【実験中のエラー】APIキーの上限に達した可能性があります。(General Quota Error)")
        else:
            st.error(f"【実験中のエラー】AI処理中に予期せぬエラーが発生しました: {e}")
        return None, None

# ===============================================================
# 【実験用】メインの仕事
# ===============================================================
def show_tool(gemini_api_key):
    # この部分は、翻訳ツールの、表示ロジックを、忠実に、再現します
    st.header("❤️【実験】木霊（こだま）の部屋", divider='rainbow')

    if "echo_results" not in st.session_state: st.session_state.echo_results = []
    if "echo_last_mic_id" not in st.session_state: st.session_state.echo_last_mic_id = None
    if "echo_last_input" not in st.session_state: st.session_state.echo_last_input = None

    st.info("マイクで話しかけてください。AIが、あなたの、言葉を、そのまま、返します。")

    audio_info = mic_recorder(start_prompt="🎤 話し始める", stop_prompt="⏹️ 聞いてもらう", key='echo_mic', format="webm")

    content_to_process = None
    if audio_info and audio_info['id'] != st.session_state.echo_last_mic_id:
        content_to_process = audio_info['bytes']
        st.session_state.echo_last_mic_id = audio_info['id']

    if content_to_process and content_to_process != st.session_state.echo_last_input:
        st.session_state.echo_last_input = content_to_process
        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを設定してください。")
        else:
            # 実験用の、関数を、呼び出します
            original, echo_text = echo_by_gemini(content_to_process, gemini_api_key)
            
            if original and echo_text:
                st.session_state.echo_results.insert(0, {"original": original, "echo": echo_text})
                st.rerun()
            else:
                # 失敗した場合、入力をクリアして、再試行を、可能にする
                st.session_state.echo_last_input = None
    
    if st.session_state.echo_results:
        st.write("---")
        for result in st.session_state.echo_results:
            st.markdown(f"**あなたが、話した言葉：** {result['original']}")
            st.success(f"**AIが、返した言葉：** {result['echo']}")
            st.write("---")

        if st.button("履歴をクリア"):
            st.session_state.echo_results = []
            st.session_state.echo_last_input = None
            st.rerun()
