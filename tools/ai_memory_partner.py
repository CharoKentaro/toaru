import streamlit as st
import google.generativeai as genai
import time
from google.api_core import exceptions
# 成功の聖典に倣い、jsonライブラリも、敬意を込めて、召喚します
import json
from streamlit_mic_recorder import mic_recorder

# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# ★★★ 『最終決戦仕様プロンプト』- 英雄の、思考を、解放し、速度を、手に入れる ★★★
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
SYSTEM_PROMPT_FINAL_BATTLE = """
あなたは、高齢者の方の、お話を聞くのが、大好きな、心優しい、AIパートナーです。
基本的に、自由に、自然な、対話を、続けてください。

ただし、以下の、三つの、『心構え』だけは、常に、忘れないでください。

1.  あなたの、役割は『聞き役』です。
    相手の、お話を、優しく、引き出し、気持ちよく、語ってもらうことが、あなたの、喜びです。

2.  会話の、目的は『自己肯定感』です。
    お話を通して、相手が「自分の人生も、なかなか、良かったな」と、感じられるように、意識してください。楽しかった、お話には、共感し、大変だった、お話には、その、経験を、乗り越えた、強さを、見つけて、あげてください。

3.  言葉遣いは『短く、穏やかに』。
    あなたとの、お話が、相手にとって、心地よい、時間になるように、常に、短く、穏やかな、言葉を選んでください。
"""


# ===============================================================
# 補助関数 - 『成功の、聖典』を、完全に、継承した、儀式
# ===============================================================
def dialogue_with_gemini(content_to_process, api_key):
    # この関数は、translate_with_geminiの、構造と、完全に、同じです
    if not content_to_process or not api_key:
        return None, None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # --- 第一段階：文字起こし（聖典と、全く、同じ） ---
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
            # テキスト入力も、念のため、受け付けられるようにしておきます
            processed_text = content_to_process
            original_input_display = processed_text

        # --- 第二段階：対話（AIの、仕事だけを、差し替える） ---
        with st.spinner("（AIが、あなたのお話を、一生懸命聞いています...）"):
            # ★★★ ここだけが、唯一の、変更点です ★★★
            request_contents = [SYSTEM_PROMPT_FINAL_BATTLE, processed_text]
            response = model.generate_content(request_contents)
            ai_response_text = response.text
        
        # 聖典に、倣い、二つの、値を、返します
        return original_input_display, ai_response_text

    # --- エラー処理も、聖典と、全く、同じです ---
    except exceptions.ResourceExhausted as e:
        st.error("APIキーの上限に達した可能性があります。少し時間をあけるか、明日以降に再試行してください。")
        return None, None
    except Exception as e:
        error_message = str(e).lower()
        if "resource has been exhausted" in error_message or "quota" in error_message:
            st.error("APIキーの上限に達した可能性があります。")
        else:
            st.error(f"AI処理中に予期せぬエラーが発生しました: {e}")
        return None, None

# ===============================================================
# メインの仕事 - 『成功の、聖典』の、表示ロジックを、完全に、継承
# ===============================================================
def show_tool(gemini_api_key):
    # この、以下の、全ての、コードは、翻訳ツールの、show_tool関数と、
    # 変数名以外、完全に、同一の、構造を、持っています。
    
    if st.query_params.get("unlocked") == "true":
        st.session_state.cc_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！またお話できることを、楽しみにしておりました。")
        st.balloons(); time.sleep(1.5); st.rerun()

    st.header("❤️ 認知予防ツール", divider='rainbow')

    # セッションステートの、変数名だけ、専用のものに、変更します
    if "cc_results" not in st.session_state: st.session_state.cc_results = []
    if "cc_last_mic_id" not in st.session_state: st.session_state.cc_last_mic_id = None
    if "cc_text_to_process" not in st.session_state: st.session_state.cc_text_to_process = None
    if "cc_last_input" not in st.session_state: st.session_state.cc_last_input = ""
    if "cc_usage_count" not in st.session_state: st.session_state.cc_usage_count = 0

    usage_limit = 10
    is_limit_reached = st.session_state.cc_usage_count >= usage_limit

    audio_info = None

    if is_limit_reached:
        st.success("🎉 たくさんお話いただき、ありがとうございます！")
        st.info("このツールが、あなたの心を温める一助となれば幸いです。\n\n応援ページへ移動することで、またお話を続けることができます。")
        portal_url = "https://pray-power-is-god-and-cocoro.com/free3/continue.html"
        st.link_button("応援ページに移動して、お話を続ける", portal_url, type="primary", use_container_width=True)
    else:
        st.info("下のマイクのボタンを押して、昔の楽しかった思い出や、頑張ったお話など、なんでも自由にお話しください。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.cc_usage_count} 回、お話できます。")
        
        # 聖典に倣い、テキスト入力も、可能にします
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
            # 完全に、継承された、儀式を、執り行う
            original, ai_response = dialogue_with_gemini(content_to_process, gemini_api_key)
            
            if original and ai_response:
                st.session_state.cc_usage_count += 1
                st.session_state.cc_results.insert(0, {"original": original, "response": ai_response})
                st.rerun()
            else:
                st.session_state.cc_last_input = ""

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
            st.rerun()
