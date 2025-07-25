import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import time
from google.api_core import exceptions # ★★★ APIの特別なエラーを捕まえるための、専門家をインポート ★★★

# ===============================================================
# 補助関数 (成功確率99.9%の『二段構え』迎撃システム搭載バージョン)
# ===============================================================
def translate_with_gemini(content_to_process, api_key):
    if not content_to_process or not api_key:
        return None, None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        system_prompt = """
        あなたは、言語の壁を乗り越える手助けをする、極めて優秀で、信頼性の高い、プロフェッショナルな翻訳アシスタントです。
        ユーザーから渡された日本語のテキストを、ビジネスメールや公式な文書で使用できるような、フォーマルで、丁寧で、正確、そしてプロフェッショナルな英語に翻訳してください。
        - 過度にカジュアルな表現や、スラングは絶対に避けてください。
        - 翻訳後の英語テキストのみを、他の言葉を一切含めずに、回答してください。
        """

        if isinstance(content_to_process, str):
            original_text = content_to_process
            request_contents = [system_prompt, original_text]
        elif isinstance(content_to_process, bytes):
            original_text = "(音声入力)"
            audio_part = {
                "mime_type": "audio/webm",
                "data": content_to_process
            }
            request_contents = [system_prompt, "この日本語の音声を翻訳してください:", audio_part]
        else:
            return None, None

        response = model.generate_content(request_contents)
        return original_text, response.text.strip()

    # ★★★ ここからが、私たちが共に築き上げた、最強の『二段構え』迎撃システムです ★★★

    # --- 第一防衛線：理想的なエラーを、名指しで捕獲する ---
    except exceptions.ResourceExhausted as e:
        st.error("APIキーの上限に達した可能性があります。少し時間をあけるか、明日以降に再試行してください。")
        return None, None
        
    # --- 第二防衛線：予期せぬエラーの「中身」を、徹底的に調査する ---
    except Exception as e:
        error_message = str(e).lower() # エラーメッセージを小文字に統一して調査しやすくする
        
        # エラーメッセージの中に、上限超過を示す「キーワード」が含まれているか？
        if "resource has been exhausted" in error_message or "quota" in error_message:
            st.error("APIキーの上限に達した可能性があります。少し時間をあけるか、明日以降に再試行してください。")
        else:
            # それ以外の、全く予期せぬエラーは、こちらで報告する
            st.error(f"AI処理中に予期せぬエラーが発生しました: {e}")
            
        return None, None


# ===============================================================
# 専門家のメインの仕事 (変更なし、私たちの叡智の集大成)
# ===============================================================
def show_tool(gemini_api_key):
    # (この部分のコードは、一切の変更がありません)
    if st.query_params.get("unlocked") == "true":
        st.session_state.translator_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！利用回数がリセットされました。")
        st.balloons()
        time.sleep(1)
        st.rerun()

    st.header("🤝 翻訳ツール", divider='rainbow')

    if "translator_results" not in st.session_state: st.session_state.translator_results = []
    if "translator_last_mic_id" not in st.session_state: st.session_state.translator_last_mic_id = None
    if "text_to_process" not in st.session_state: st.session_state.text_to_process = None
    if "translator_last_input" not in st.session_state: st.session_state.translator_last_input = ""
    if "translator_usage_count" not in st.session_state: st.session_state.translator_usage_count = 0

    usage_limit = 10
    is_limit_reached = st.session_state.translator_usage_count >= usage_limit

    if is_limit_reached:
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info("このツールが、あなたの世界を広げる一助となれば幸いです。\n\n下のボタンから応援ページに移動することで、翻訳を続けることができます。")
        portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html"
        st.link_button("応援ページに移動して、翻訳を続ける", portal_url, type="primary")
    else:
        st.info("マイクで日本語を話すか、テキストボックスに入力してください。プロフェッショナルな英語に翻訳します。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.translator_usage_count} 回、翻訳できます。応援後、リセットされます。")
        with st.expander("💡 このツールのAIについて"):
            st.markdown("""
            このツールは、Googleの**Gemini 1.5 Flash**というAIモデルを使用しています。
            現在、このモデルには**1分あたり15回、1日あたり1,500回まで**の無料利用枠が設定されています。
            心ゆくまで、言語の壁を越える旅をお楽しみください！
            """, unsafe_allow_html=True)

        def handle_text_input():
            st.session_state.text_to_process = st.session_state.translator_text

        col1, col2 = st.columns([1, 2])
        with col1:
            audio_info = mic_recorder(start_prompt="🎤 話し始める", stop_prompt="⏹️ 翻訳する", key='translator_mic', format="webm")
        with col2:
            st.text_input("または、ここに日本語を入力してEnter...", key="translator_text", on_change=handle_text_input)

        content_to_process = None
        if audio_info and audio_info['id'] != st.session_state.translator_last_mic_id:
            content_to_process = audio_info['bytes']
            st.session_state.translator_last_mic_id = audio_info['id']
        elif st.session_state.text_to_process:
            content_to_process = st.session_state.text_to_process
            st.session_state.text_to_process = None

        if content_to_process and content_to_process != st.session_state.translator_last_input:
            st.session_state.translator_last_input = content_to_process
            if not gemini_api_key:
                st.error("サイドバーでGemini APIキーを設定してください。")
            else:
                with st.spinner("AIが最適な英語を考えています..."):
                    original, translated = translate_with_gemini(content_to_process, gemini_api_key)
                if translated:
                    st.session_state.translator_usage_count += 1
                    st.session_state.translator_results.insert(0, {"original": original, "translated": translated})
                    st.rerun()
                else:
                    st.session_state.translator_last_input = ""

        if st.session_state.translator_results:
            st.write("---")
            for i, result in enumerate(st.session_state.translator_results):
                with st.container(border=True):
                    st.caption(f"翻訳履歴 No.{len(st.session_state.translator_results) - i}")
                    st.markdown(f"**🇯🇵 あなたの入力:**\n> {result['original']}")
                    st.markdown(f"**🇺🇸 AIの翻訳:**\n> {result['translated']}")
            if st.button("翻訳履歴をクリア", key="clear_translator_history"):
                st.session_state.translator_results = []
                st.session_state.translator_last_input = ""
                st.rerun()
