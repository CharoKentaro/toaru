import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import time

# ===============================================================
# 補助関数 (『叡智Ⅲ:神の一閃』を適用した、AI統合バージョン)
# ===============================================================
def translate_with_gemini(content_to_process, api_key):
    """
    テキストまたは音声データをGeminiで翻訳する、新しい統合関数。
    content_to_process: 翻訳したいテキスト(str)または音声データ(bytes)。
    api_key: Gemini APIキー。
    戻り値: (元のテキスト, 翻訳されたテキスト) のタプル。
    """
    if not content_to_process or not api_key:
        return None, None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # プロンプトを定義
        system_prompt = "あなたは非常に優秀な翻訳アシスタントです。ユーザーから渡された日本語を、海外の親しい友人との会話で使われるような、自然でカジュアルでありながら礼儀正しい英語に翻訳してください。- 非常に硬い表現や、ビジネス文書のような翻訳は避けてください。- 翻訳後の英語テキストのみを回答し、他の言葉は一切含めないでください。"

        # コンテンツのタイプ（テキストか音声か）に応じてリクエストを作成
        if isinstance(content_to_process, str):
            # テキスト入力の場合
            original_text = content_to_process
            request_contents = [system_prompt, original_text]
        elif isinstance(content_to_process, bytes):
            # 音声入力の場合
            original_text = "(音声入力)" # 表示用に固定の文字列を用意
            audio_file = genai.upload_file(contents=content_to_process, mime_type='audio/webm')
            request_contents = [system_prompt, "この日本語の音声を翻訳してください:", audio_file]
        else:
            return None, None

        # AIにリクエストを送信
        response = model.generate_content(request_contents)

        # 翻訳済みテキストを返す
        return original_text, response.text.strip()

    except Exception as e:
        st.error(f"AI処理エラー: {e}")
        return None, None

# ===============================================================
# 専門家のメインの仕事 (『叡智の集大成』バージョン)
# ===============================================================
def show_tool(gemini_api_key): # ← speech_api_key は、もはや不要

    # ★★★【叡智の融合①】『帰還者の祝福』の儀式 (変更なし) ★★★
    if st.query_params.get("unlocked") == "true":
        st.session_state.translator_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！利用回数がリセットされました。")
        st.balloons()
        time.sleep(1)
        st.rerun()

    st.header("🤝 フレンドリー翻訳ツール", divider='rainbow')

    # --- 状態管理の初期化 (変更なし) ---
    if "translator_results" not in st.session_state: st.session_state.translator_results = []
    if "translator_last_mic_id" not in st.session_state: st.session_state.translator_last_mic_id = None
    if "text_to_process" not in st.session_state: st.session_state.text_to_process = None
    if "translator_last_input" not in st.session_state: st.session_state.translator_last_input = ""
    if "translator_usage_count" not in st.session_state: st.session_state.translator_usage_count = 0

    # --- 制限回数の設定 (本番運用時は「10」などに設定) ---
    usage_limit = 10
    is_limit_reached = st.session_state.translator_usage_count >= usage_limit

    # ★★★【叡智の融合②】「制限時」と「通常時」の世界の分離 (変更なし) ★★★
    if is_limit_reached:
        # --- 制限に達した場合の世界 ---
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info("このツールが、あなたの世界を広げる一助となれば幸いです。\n\n下のボタンから応援ページに移動することで、翻訳を続けることができます。")
        portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html"
        st.link_button("応援ページに移動して、翻訳を続ける", portal_url, type="primary")
    else:
        # --- 通常時の世界 ---
        st.info("マイクで日本語を話すか、テキストボックスに入力してください。自然な英語に翻訳します。")
        
        # ★★★【新機能】ユーザーに安心を届ける、無料枠の案内 ★★★
        st.caption(f"🚀 あと {usage_limit - st.session_state.translator_usage_count} 回、翻訳できます")
        with st.expander("💡 このツールのAIについて"):
            st.markdown("""
            このツールは、Googleの**Gemini 1.5 Flash**というAIモデルを使用しています。
            現在、このモデルには**1分あたり15回、1日あたり1,500回まで**の無料利用枠が設定されています。
            
            心ゆくまで、言語の壁を越える旅をお楽しみください！
            """, unsafe_allow_html=True)


        # ★★★【叡智Ⅵ】『on_change』による、検知と処理の分離 (安定性の心臓部) ★★★
        def handle_text_input():
            st.session_state.text_to_process = st.session_state.translator_text

        col1, col2 = st.columns([1, 2])
        with col1:
            # Geminiが扱いやすいように、音声フォーマットを 'webm' に指定
            audio_info = mic_recorder(start_prompt="🎤 話し始める", stop_prompt="⏹️ 翻訳する", key='translator_mic', format="webm")
        with col2:
            st.text_input("または、ここに日本語を入力してEnter...", key="translator_text", on_change=handle_text_input)

        # --- 検知フェーズ ---
        content_to_process = None
        # 音声入力をチェック
        if audio_info and audio_info['id'] != st.session_state.translator_last_mic_id:
            content_to_process = audio_info['bytes']
            st.session_state.translator_last_mic_id = audio_info['id']
        # テキスト入力をチェック
        elif st.session_state.text_to_process:
            content_to_process = st.session_state.text_to_process
            st.session_state.text_to_process = None # 重複実行を防ぐため、すぐにクリア

        # --- 処理フェーズ ---
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
                    st.warning("翻訳に失敗しました。もう一度お試しください。")

        # --- 結果表示エリア (変更なし) ---
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
