import streamlit as st
import google.generativeai as genai
from google.cloud import speech
from google.api_core.client_options import ClientOptions
from streamlit_mic_recorder import mic_recorder
import time

# (補助関数は変更なし)
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
# 専門家のメインの仕事 (『叡智の最終形態』バージョン)
# ===============================================================
def show_tool(gemini_api_key, speech_api_key):

    # ★★★【叡智の融合①】『帰還者の祝福』の儀式 ★★★
    if st.query_params.get("unlocked") == "true":
        st.session_state.translator_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！利用回数がリセットされました。")
        st.balloons()
        time.sleep(1)
        st.rerun()

    st.header("🤝 フレンドリー翻訳ツール", divider='rainbow')

    # --- 状態管理の初期化 ---
    if "translator_results" not in st.session_state: st.session_state.translator_results = []
    if "translator_last_mic_id" not in st.session_state: st.session_state.translator_last_mic_id = None
    if "translator_last_text" not in st.session_state: st.session_state.translator_last_text = ""
    if "translator_usage_count" not in st.session_state: st.session_state.translator_usage_count = 0
    # ★★★【修正案①】テキスト入力を処理するための、専用の状態を追加 ★★★
    if "text_to_process" not in st.session_state: st.session_state.text_to_process = None

    # --- 制限回数の設定 ---
    usage_limit = 2
    is_limit_reached = st.session_state.translator_usage_count >= usage_limit

    if is_limit_reached:
        # --- 制限に達した場合の世界 ---
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info(
            "このツールが、あなたの世界を広げる一助となれば幸いです。\n\n"
            "下のボタンから応援ページに移動することで、"
            f"**さらに{usage_limit}回**、翻訳を続けることができます。"
        )
        portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html"
        st.link_button("応援ページに移動して、翻訳を続ける", portal_url, type="primary")

    else:
        # --- 通常時の世界 ---
        st.info("マイクで日本語を話すか、テキストボックスに入力してください。自然な英語に翻訳します。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.translator_usage_count} 回、翻訳できます")

        # ★★★【修正案②】テキスト入力が変更された時に呼ばれる、コールバック関数を定義 ★★★
        def handle_text_input():
            # 入力されたテキストを「処理対象」としてセッション状態に保存する
            st.session_state.text_to_process = st.session_state.translator_text

        col1, col2 = st.columns([1, 2])
        with col1:
            audio_info = mic_recorder(start_prompt="🎤 話し始める", stop_prompt="⏹️ 翻訳する", key='translator_mic')
        with col2:
            # ★★★【修正案③】text_inputに on_change を設定 ★★★
            st.text_input(
                "または、ここに日本語を入力してEnterキーを押してください...",
                key="translator_text",
                on_change=handle_text_input
            )

        # ★★★【修正案④】検知と処理のロジックを、完全に再構築 ★★★
        japanese_text_to_process = None

        # --- 検知フェーズ ---
        # まず音声入力をチェック
        if audio_info and audio_info['id'] != st.session_state.translator_last_mic_id:
            with st.spinner("音声を日本語に変換中..."):
                text_from_mic = transcribe_audio(audio_info['bytes'], speech_api_key)
            if text_from_mic:
                japanese_text_to_process = text_from_mic
                st.session_state.translator_last_mic_id = audio_info['id']
        # 次に、コールバックによってセットされたテキスト入力をチェック
        elif st.session_state.text_to_process:
            japanese_text_to_process = st.session_state.text_to_process
            # 処理対象を取得したら、すぐにNoneに戻し、重複実行を防ぐ
            st.session_state.text_to_process = None

        # --- 処理フェーズ ---
        if japanese_text_to_process and japanese_text_to_process != st.session_state.translator_last_text:
            st.session_state.translator_last_text = japanese_text_to_process

            if not gemini_api_key:
                st.error("サイドバーでGemini APIキーを設定してください。")
            else:
                with st.spinner("AIが最適な英語を考えています..."):
                    translated_text = translate_text_with_gemini(japanese_text_to_process, gemini_api_key)
                if translated_text:
                    st.session_state.translator_usage_count += 1
                    st.session_state.translator_results.insert(0, {"original": japanese_text_to_process, "translated": translated_text})
                    st.rerun() # ★ 処理が成功し、結果を保存した直後に一度だけrerunし、画面を即座に更新する
                else:
                    st.warning("翻訳に失敗しました。もう一度お試しください。")

        # --- 結果表示エリア ---
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
                st.rerun()
