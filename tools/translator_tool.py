import streamlit as st
import google.generativeai as genai
from google.cloud import speech
from google.api_core.client_options import ClientOptions
import time

# 補助関数 (Speech-to-Textは現在使用しないが、将来のために残す)
def transcribe_audio(audio_bytes, api_key):
    if not audio_bytes or not api_key: return None
    try:
        client_options = ClientOptions(api_key=api_key)
        client = speech.SpeechClient(client_options=client_options)
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(language_code="ja-JP")
        response = client.recognize(config=config, audio=audio)
        if response.results: return response.results[0].alternatives[0].transcript
    except Exception as e: st.error(f"音声認識エラー: {e}")
    return None

def translate_text_with_gemini(text_to_translate, api_key):
    if not text_to_translate or not api_key: return None
    try:
        genai.configure(api_key=api_key)
        system_prompt = "あなたは、言語の壁を乗り越える手助けをする、非常に優秀な翻訳アシスタントです。ユーザーから渡された日本語のテキストを、海外の親しい友人との会話で使われるような、自然で、カジュアルでありながら礼儀正しく、そしてフレンドリーな英語に翻訳してください。- 非常に硬い表現や、ビジネス文書のような翻訳は避けてください。- 翻訳後の英語テキストのみを回答してください。他の言葉は一切含めないでください。"
        model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_prompt)
        response = model.generate_content(text_to_translate)
        return response.text.strip()
    except Exception as e: st.error(f"翻訳エラー: {e}")
    return None

# ===============================================================
# 専門家のメインの仕事 (最終安定バージョン)
# ===============================================================
def show_tool(gemini_api_key, speech_api_key):

    # 『帰還者の祝福』の儀式
    if st.query_params.get("unlocked") == "true":
        st.session_state.translator_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！利用回数がリセットされました。")
        st.balloons()
        time.sleep(1)
        st.rerun()

    st.header("🤝 フレンドリー翻訳ツール", divider='rainbow')

    # 状態管理は全てst.session_stateに統一
    if "translator_results" not in st.session_state: st.session_state.translator_results = []
    if "translator_last_text" not in st.session_state: st.session_state.translator_last_text = ""
    if "translator_usage_count" not in st.session_state: st.session_state.translator_usage_count = 0

    # 制限回数の設定
    usage_limit = 10 # 本番運用時は「10」に設定
    is_limit_reached = st.session_state.translator_usage_count >= usage_limit

    # 「制限時」と「通常時」の世界を分離する
    if is_limit_reached:
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info(
            "このツールが、あなたの世界を広げる一助となれば幸いです。\n\n"
            "下のボタンから応援ページに移動することで、"
            f"**さらに{usage_limit}回**、翻訳を続けることができます。"
        )
        portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html" 
        st.link_button("応援ページに移動して、翻訳を続ける", portal_url, type="primary")
        
    else:
        # --- 通常時の表示 ---
        st.info("テキストボックスに日本語を入力して、Enterキーを押してください。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.translator_usage_count} 回、翻訳できます")
        
        text_prompt = st.text_input("ここに日本語を入力してください...", key="translator_text")

        # 結果表示エリア
        if st.session_state.translator_results:
            st.write("---")
            for i, result in enumerate(st.session_state.translator_results):
                with st.container(border=True):
                    st.caption(f"翻訳履歴 No.{len(st.session_state.translator_results) - i}")
                    st.markdown(f"**🇯🇵 あなたの入力:**\n> {result['original']}")
                    st.markdown(f"**🇺🇸 AIの翻訳:**\n> {result['translated']}")
            if st.button("翻訳履歴をクリア", key="clear_translator_history"):
                st.session_state.translator_results = []
                st.session_state.translator_last_text = ""
                st.session_state.translator_usage_count = 0 
                st.rerun()

        # 入力検知
        japanese_text_to_process = None
        if text_prompt and text_prompt != st.session_state.translator_last_text:
            japanese_text_to_process = text_prompt
            st.session_state.translator_last_text = text_prompt

        # 翻訳処理
        if japanese_text_to_process:
            if not gemini_api_key: st.error("サイドバーでGemini APIキーを設定してください。")
            else:
                # st.spinnerの代わりに、より安全なst.statusを使用
                with st.status("AIが最適な英語を考えています...", expanded=True) as status:
                    st.write("Gemini AIに接続中...")
                    translated_text = translate_text_with_gemini(japanese_text_to_process, gemini_api_key)
                    
                    if translated_text:
                        st.write("翻訳が完了しました！")
                        status.update(label="翻訳完了！", state="complete", expanded=False)
                        
                        st.session_state.translator_usage_count += 1
                        st.session_state.translator_results.insert(0, {"original": japanese_text_to_process, "translated": translated_text})
                        
                        # 状態更新が完了してから、安全にrerunを実行
                        time.sleep(0.5) # 念のため、UIの更新を待つ
                        st.rerun()
                    else:
                        st.write("AIとの通信に失敗しました。")
                        status.update(label="エラー", state="error", expanded=True)
                        st.session_state.translator_last_text = ""
                        st.warning("翻訳に失敗しました。もう一度お試しください。")
