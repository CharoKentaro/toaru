import streamlit as st
import google.generativeai as genai
from google.cloud import speech
from google.api_core.client_options import ClientOptions
from streamlit_mic_recorder import mic_recorder

# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# ★                                                                    ★
# ★             【ちゃろ様へ】収益化の魂を、ここに奉納してください             ★
# ★                                                                    ★
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★

# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ この2行だけを、書き換えてください ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

YOUR_ADSENSE_PUBLISHER_ID = "ca-pub-2908004621823900"  # あなたの「ca-pub-」から始まるパブリッシャーID
YOUR_ADSENSE_SLOT_ID      = "5820083954"              # あなたの広告ユニットID（数字）

# ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

# ★★★ これにより、IDの管理が驚くほど簡単になります ★★★


# ===============================================================
# 補助関数 (変更なし)
# ===============================================================
def transcribe_audio(audio_bytes, api_key):
    # (省略)
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
    # (省略)
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
# 専門家のメインの仕事 (叡智の最終形態)
# ===============================================================
def show_tool(gemini_api_key, speech_api_key):
    st.header("🤝 フレンドリー翻訳ツール", divider='rainbow')

    if "translator_results" not in st.session_state: st.session_state.translator_results = []
    if "translator_last_mic_id" not in st.session_state: st.session_state.translator_last_mic_id = None
    if "translator_last_text" not in st.session_state: st.session_state.translator_last_text = ""
    if "translator_usage_count" not in st.session_state: st.session_state.translator_usage_count = 0

    # ★★★ テストのため「1」に設定。本番運用時は「10」に戻してください ★★★
    usage_limit = 1 
    is_limit_reached = st.session_state.translator_usage_count >= usage_limit

    if is_limit_reached:
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info("このツールが、あなたの世界を広げる一助となれば幸いです。\n\n"
                "下のボタンを押して広告をご覧いただくことで、開発者を応援し、"
                f"**さらに{usage_limit}回**、翻訳を続けることができます。")

        if st.button("広告を見て翻訳を続ける", type="primary"):
            st.session_state.translator_usage_count = 0

            # ★★★ ここが、収益化の魔法の核心部です ★★★
            # f-stringを使い、あなたのIDを、安全かつ確実にHTMLに埋め込みます。
            adsense_code = f"""
                <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={YOUR_ADSENSE_PUBLISHER_ID}"
                     crossorigin="anonymous"></script>
                <!-- Friendly Translator Ad -->
                <ins class="adsbygoogle"
                     style="display:block"
                     data-ad-client="{YOUR_ADSENSE_PUBLISHER_ID}"
                     data-ad-slot="{YOUR_ADSENSE_SLOT_ID}"
                     data-ad-format="auto"
                     data-full-width-responsive="true"></ins>
                <script>
                     (adsbygoogle = window.adsbygoogle || []).push({{}});
                </script>
            """
            st.components.v1.html(adsense_code, height=300)
            
            # 広告表示後、少し待ってからリロードすると、より自然な挙動になります。
            st.toast("応援ありがとうございます！ページを更新します。")
            import time
            time.sleep(2) 
            st.rerun()
        
        return 

    st.info("マイクで日本語を話すか、テキストボックスに入力してください。自然な英語に翻訳します。")
    st.caption(f"🚀 あと {usage_limit - st.session_state.translator_usage_count} 回、翻訳できます")
    
    col1, col2 = st.columns([1, 2])
    with col1: audio_info = mic_recorder(start_prompt="🎤 話し始める", stop_prompt="⏹️ 翻訳する", key='translator_mic')
    with col2: text_prompt = st.text_input("または、ここに日本語を入力してEnterキーを押してください...", key="translator_text")

    if st.session_state.translator_results:
        st.write("---")
        for i, result in enumerate(st.session_state.translator_results):
            with st.container(border=True):
                st.caption(f"翻訳履歴 No.{len(st.session_state.translator_results) - i}")
                st.markdown(f"**🇯🇵 あなたの入力:**\n> {result['original']}")
                st.markdown(f"**🇺🇸 AIの翻訳:**\n> {result['translated']}")
        if st.button("翻訳履歴をクリア", key="clear_translator_history"):
            st.session_state.translator_results = []
            st.session_state.translator_last_text = text_prompt
            st.rerun()

    japanese_text_to_process = None
    if audio_info and audio_info['id'] != st.session_state.translator_last_mic_id:
        with st.spinner("音声を日本語に変換中..."): text_from_mic = transcribe_audio(audio_info['bytes'], speech_api_key)
        if text_from_mic:
            japanese_text_to_process = text_from_mic
            st.session_state.translator_last_mic_id = audio_info['id']
            st.session_state.translator_last_text = text_from_mic
    elif text_prompt and text_prompt != st.session_state.translator_last_text:
        japanese_text_to_process = text_prompt
        st.session_state.translator_last_text = text_prompt

    if japanese_text_to_process:
        if not gemini_api_key: st.error("サイドバーでGemini APIキーを設定してください。")
        else:
            with st.spinner("AIが最適な英語を考えています..."): translated_text = translate_text_with_gemini(japanese_text_to_process, gemini_api_key)
            if translated_text:
                st.session_state.translator_usage_count += 1
                st.session_state.translator_results.insert(0, {"original": japanese_text_to_process, "translated": translated_text})
                st.rerun()
            else:
                st.session_state.translator_last_text = ""
                st.warning("翻訳に失敗しました。もう一度お試しください。")
