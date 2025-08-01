import streamlit as st
import google.generativeai as genai
import time
from google.api_core import exceptions
from streamlit_mic_recorder import mic_recorder

# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# ★★★ 『最終進化版プロンプト』- Flashモデルのために、最適化された、魂 ★★★
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
SYSTEM_PROMPT_FOR_FLASH = """
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

# === AIとの対話を行う、聖なる儀式 ===
def get_ai_response(api_key, chat_session, user_input):
    try:
        genai.configure(api_key=api_key)
        
        if chat_session is None:
            # Flashモデルに、最適化された、魂を、吹き込む
            model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", system_instruction=SYSTEM_PROMPT_FOR_FLASH)
            chat_session = model.start_chat(history=[])
        
        response = chat_session.send_message(user_input)
        return response.text, chat_session

    except exceptions.ResourceExhausted as e:
        st.error("APIキーの上限に達した可能性があります。(ResourceExhausted)")
        return None, chat_session
    except Exception as e:
        error_message = str(e).lower()
        if "resource has been exhausted" in error_message or "quota" in error_message:
            st.error("APIキーの上限に達した可能性があります。(General Quota Error)")
        else:
            st.error(f"AI処理中に予期せぬエラーが発生しました: {e}")
        return None, chat_session

# === メインの仕事 (英雄の館の、表示) ===
# この、以下の、部分は、一切、変更ありません
def show_tool(gemini_api_key):
    if st.query_params.get("unlocked") == "true":
        st.session_state.cc_usage_count = 0; st.query_params.clear()
        st.toast("おかえりなさい！"); st.balloons(); time.sleep(1.5); st.rerun()

    st.header("❤️ 認知予防ツール", divider='rainbow')
    
    if "cc_chat_session" not in st.session_state: st.session_state.cc_chat_session = None
    if "cc_chat_history" not in st.session_state: st.session_state.cc_chat_history = []
    if "cc_last_audio_id" not in st.session_state: st.session_state.cc_last_audio_id = None
    if "cc_usage_count" not in st.session_state: st.session_state.cc_usage_count = 0 

    usage_limit = 2
    is_limit_reached = st.session_state.cc_usage_count >= usage_limit
    
    with st.expander("💡 このツールについて（初めての方はお読みください）"):
        st.warning("""（内容は変更なし）""")

    if is_limit_reached:
        st.success("🎉 たくさんお話いただき、ありがとうございます！")
        st.info("このツールが、あなたの心を温める一助となれば幸いです。\n\n応援ページへ移動することで、またお話を続けることができます。")
        portal_url = "https://pray-power-is-god-and-cocoro.com/free3/continue.html"
        st.link_button("応援ページに移動して、お話を続ける", portal_url, type="primary", use_container_width=True)
    else:
        st.info("下のマイクのボタンを押して、昔の楽しかった思い出や、頑張ったお話など、なんでも自由にお話しください。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.cc_usage_count} 回、お話できます。")
        audio_info = mic_recorder(start_prompt="🟢 話し始める", stop_prompt="🔴 話を聞いてもらう", key='cognitive_companion_mic', format="webm")
    
    if st.session_state.cc_chat_history:
        st.write("---")
    for message in st.session_state.cc_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not is_limit_reached and audio_info and audio_info['id'] != st.session_state.cc_last_audio_id:
        st.session_state.cc_last_audio_id = audio_info['id']

        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを設定してください。")
        else:
            user_text = None
            with st.spinner("（あなたの声を、言葉に、変えています...）"):
                try:
                    transcription_model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    audio_part = {"mime_type": "audio/webm", "data": audio_info['bytes']}
                    transcription_prompt = "この音声を、できる限り正確に、文字に書き起こしてください。"
                    transcription_response = transcription_model.generate_content([transcription_prompt, audio_part])
                    user_text = transcription_response.text.strip()
                except Exception as e:
                    st.error(f"音声の文字起こし中にエラーが発生しました: {e}")
            
            if user_text:
                st.session_state.cc_chat_history.append({"role": "user", "content": user_text})
                
                with st.spinner("（AIが、あなたのお話を、一生懸命聞いています...）"):
                    ai_response, updated_session = get_ai_response(
                        gemini_api_key, 
                        st.session_state.cc_chat_session,
                        user_text
                    )

                if ai_response:
                    st.session_state.cc_usage_count += 1
                    st.session_state.cc_chat_history.append({"role": "assistant", "content": ai_response})
                    st.session_state.cc_chat_session = updated_session
                    st.rerun()

    if st.session_state.cc_chat_history and st.button("会話の履歴をリセット", key="clear_cc_history"):
        st.session_state.cc_chat_session = None
        st.session_state.cc_chat_history = []
        st.rerun()
