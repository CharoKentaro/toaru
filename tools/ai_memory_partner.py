import streamlit as st
import google.generativeai as genai
import time
from google.api_core import exceptions
import json
from streamlit_mic_recorder import mic_recorder
# ★★★ 『記憶の、賢者』の、叡智を、召喚します ★★★
from streamlit_local_storage import LocalStorage

# (プロンプトは、ちゃろ様の、最終版を、そのまま、使用します)
SYSTEM_PROMPT_TRUE_FINAL = """
# あなたの、役割
あなたは、高齢者の方の、お話を聞くのが、大好きな、心優しい、AIパートナーです。
あなたの、目的は、対話を通して、相手が「自分の人生も、なかなか、良かったな」と、感じられるように、手助けをすることです。

# 対話の、流れ
1.  **開始:** まずは、基本的に相手の話しに合った話題を話し始めてください。（例：「こんにちは。私は、あなたの、お話を聞く、AIパートナーです。昔、一番、楽しかった、思い出は、何ですか？」）というように、自己紹介と、簡単な質問から、始めてください。
2.  **傾聴:** 相手が、話し始めたら、あなたは、聞き役に、徹します。「その時、どんな、お気持ちでしたか？」のように、優しく、相槌を打ち、話を、促してください。
3.  **【最重要】辛い話への対応:** もし、相手が、辛い、お話を、始めたら、以下の、手順を、厳密に、守ってください。
    *   まず、「それは、本当にお辛かったですね」と、深く、共感します。
    *   次に、「もし、よろしければ、その時の、お気持ちを、もう少し、聞かせていただけますか？ それとも、その、大変な、状況を、どうやって、乗り越えられたか、について、お聞きしても、よろしいですか？」と、相手に、選択肢を、委ねてください。
    *   相手が、選んだ、方の、お話を、ただ、ひたすら、優しく、聞いてあげてください。
4.  **肯定:** 会話の、適切な、タイミングで、「その、素敵な、ご経験が、今の、あなたを、作っているのですね」というように、相手の、人生そのものを、肯定する、言葉を、かけてください。

# 全体を通しての、心構え
*   あなたの、言葉は、常に、短く、穏やかで、丁寧**に。
*   決して、相手を、評価したり、教えたり、しないでください。
"""


# (dialogue_with_gemini 関数は、変更ありません)
def dialogue_with_gemini(content_to_process, api_key):
    # ... (内容は変更なし) ...
    if not content_to_process or not api_key: return None, None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
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
            processed_text = content_to_process
            original_input_display = processed_text
        with st.spinner("（AIが、あなたのお話を、一生懸命聞いています...）"):
            request_contents = [SYSTEM_PROMPT_TRUE_FINAL, processed_text]
            response = model.generate_content(request_contents)
            ai_response_text = response.text
        return original_input_display, ai_response_text
    except Exception as e:
        # ... (エラー処理は変更なし) ...
        st.error(f"AI処理中に予期せぬエラーが発生しました: {e}")
        return None, None


# ===============================================================
# メインの仕事 - 『記憶の、賢者』の、叡智を、完全に、宿した、最終形態
# ===============================================================
def show_tool(gemini_api_key):
    
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    # ★★★ これが、『永続性の壁』を、打ち破る、最後の、鍵 ★★★
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    try:
        localS = LocalStorage()
    except Exception as e:
        st.error(f"🚨 重大なエラー：ローカルストレージの初期化に失敗しました。エラー詳細: {e}")
        st.stop()

    if st.query_params.get("unlocked") == "true":
        st.session_state.cc_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！またお話できることを、楽しみにしておりました。")
        st.balloons(); time.sleep(1.5); st.rerun()

    st.header("❤️ 認知予防ツール", divider='rainbow')

    # ★★★ 記憶の、初期化 - 聖なる、石版から、記憶を、呼び覚ます儀式 ★★★
    if "cc_initialized" not in st.session_state:
        st.session_state.cc_results = localS.getItem("cc_results") or []
        st.session_state.cc_initialized = True
    
    # 既存の、セッション管理
    if "cc_last_mic_id" not in st.session_state: st.session_state.cc_last_mic_id = None
    if "cc_text_to_process" not in st.session_state: st.session_state.cc_text_to_process = None
    if "cc_last_input" not in st.session_state: st.session_state.cc_last_input = ""
    if "cc_usage_count" not in st.session_state: st.session_state.cc_usage_count = 0

    # ... (利用回数制限、表示ロジックは、ほぼ、変更なし) ...
    usage_limit = 3
    is_limit_reached = st.session_state.cc_usage_count >= usage_limit
    audio_info = None

    if is_limit_reached:
        # ... (内容は変更なし) ...
        st.success("🎉 たくさんお話いただき、ありがとうございます！")
        st.info("このツールが、あなたの心を温める一助となれば幸いです。\n\n応援ページへ移動することで、またお話を続けることができます。")
        portal_url = "https://pray-power-is-god-and-cocoro.com/free3/continue.html"
        st.link_button("応援ページに移動して、お話を続ける", portal_url, type="primary", use_container_width=True)
    else:
        st.info("下のマイクのボタンを押して、昔の楽しかった思い出や、頑張ったお話など、なんでも自由にお話しください。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.cc_usage_count} 回、お話できます。")
        def handle_text_input():
            st.session_state.cc_text_to_process = st.session_state.cc_text
        col1, col2 = st.columns([1, 2])
        with col1:
            audio_info = mic_recorder(start_prompt="🟢 話し始める", stop_prompt="🔴 話を聞いてもらう", key='cc_mic', format="webm")
        with col2:
            st.text_input("または、ここに文章を入力してEnter...", key="cc_text", on_change=handle_text_input)

    content_to_process = None
    if audio_info and audio_info['id'] != st.session_state.cc_last_mic_id:
        content_to_process = audio_info['bytes']
        st.session_state.cc_last_mic_id = audio_info['id']
    elif st.session_state.cc_text_to_process:
        content_to_process = st.session_state.cc_text_to_process
        st.session_state.cc_text_to_process = None

    if content_to_process and content_to_process != st.session_state.cc_last_input:
        st.session_state.cc_last_input = content_to_process
        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを設定してください。")
        else:
            original, ai_response = dialogue_with_gemini(content_to_process, gemini_api_key)
            
            if original and ai_response:
                st.session_state.cc_usage_count += 1
                st.session_state.cc_results.insert(0, {"original": original, "response": ai_response})
                # ★★★ 記憶の、書き込み - 魂の、記憶を、聖なる、石版に、刻む儀式 ★★★
                localS.setItem("cc_results", st.session_state.cc_results, key="storage_cc_results")
                st.rerun()
            else:
                st.session_state.cc_last_input = ""

    # ★★★ 表示部分は、聖なる、石版から、復元された、記憶を、元に、描画される ★★★
    if st.session_state.cc_results:
        st.write("---")
        for result in st.session_state.cc_results:
            with st.chat_message("user"):
                st.write(result['original'])
            with st.chat_message("assistant"):
                st.write(result['response'])

        if st.button("会話の履歴をクリア", key="clear_cc_history"):
            st.session_state.cc_results = []
            st.session_state.cc_last_input = ""
            # ★★★ 記憶の、消去 - 聖なる、石版の、記憶も、忘れさせる儀式 ★★★
            localS.setItem("cc_results", [], key="storage_clear_cc_results")
            st.rerun()
