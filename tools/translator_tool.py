import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import time
import io # ioライブラリをインポート

# ===============================================================
# 補助関数 (最新のライブラリ仕様に対応した、最終バージョン)
# ===============================================================
def translate_with_gemini(content_to_process, api_key):
    if not content_to_process or not api_key:
        return None, None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        system_prompt = "あなたは非常に優秀な翻訳アシスタントです。ユーザーから渡された日本語を、海外の親しい友人との会話で使われるような、自然でカジュアルでありながら礼儀正しく、そしてフレンドリーな英語に翻訳してください。- 非常に硬い表現や、ビジネス文書のような翻訳は避けてください。- 翻訳後の英語テキストのみを回答し、他の言葉は一切含めないでください。"

        if isinstance(content_to_process, str):
            original_text = content_to_process
            request_contents = [system_prompt, original_text]
        elif isinstance(content_to_process, bytes):
            original_text = "(音声入力)"
            
            # ★★★ ここが、今回の、絶対的な、修正点です ★★★
            # 古い 'contents' 引数から、最新の 'file' 引数に修正する
            # また、バイトデータをファイルのように扱うためにio.BytesIOを使用する
            audio_file = genai.upload_file(file=io.BytesIO(content_to_process), mime_type='audio/webm')
            
            request_contents = [system_prompt, "この日本語の音声を翻訳してください:", audio_file]
        else:
            return None, None

        response = model.generate_content(request_contents)
        return original_text, response.text.strip()

    except Exception as e:
        # エラーメッセージをより具体的に表示
        st.error(f"AI処理エラーが発生しました: {e}")
        return None, None

# ===============================================================
# 専門家のメインの仕事 (変更なし、私たちの叡智の集大成)
# ===============================================================
def show_tool(gemini_api_key):
    if st.query_params.get("unlocked") == "true":
        st.session_state.translator_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！利用回数がリセットされました。")
        st.balloons()
        time.sleep(1)
        st.rerun()

    st.header("🤝 フレンドリー翻訳ツール", divider='rainbow')

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
        st.info("マイクで日本語を話すか、テキストボックスに入力してください。自然な英語に翻訳します。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.translator_usage_count} 回、翻訳できます")
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
                with st.spinner("AIが音声を認識し、最適な英語を考えています..."):
                    original, translated = translate_with_gemini(content_to_process, gemini_api_key)
                if translated:
                    st.session_state.translator_usage_count += 1
                    st.session_state.translator_results.insert(0, {"original": original, "translated": translated})
                    st.rerun()
                else:
                    st.session_state.translator_last_input = ""
                    # 警告メッセージは補助関数内で表示されるため、ここでは不要
                    # st.warning("翻訳に失敗しました。もう一度お試しください。")

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
