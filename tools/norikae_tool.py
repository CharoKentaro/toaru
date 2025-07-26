# tools/norikae_tool.py

import streamlit as st
import google.generativeai as genai
import traceback
import json
import time # sleepのために追加

# ===============================================================
# 専門家のメインの仕事
# ===============================================================
def show_tool(gemini_api_key):
    st.header("🚃 乗り換え案内", divider='rainbow')

    # --- ★★★【帰還者の祝福】★★★ ---
    if st.query_params.get("unlocked") == "true":
        st.session_state["norikae_usage_count"] = 0
        st.query_params.clear()
        st.toast("おかえりなさい！検索回数がリセットされました。")
        st.balloons()
        time.sleep(1)
        st.rerun()

    # --- ★★★【門番の存在保証】★★★ ---
    if "norikae_usage_count" not in st.session_state:
        st.session_state.norikae_usage_count = 0

    # --- ★★★【運命の分岐路】★★★ ---
    usage_limit = 2 # ご指定の通り、5回に設定
    is_limit_reached = st.session_state.get("norikae_usage_count", 0) >= usage_limit

    if is_limit_reached:
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info("このツールが、あなたの、移動を、少しでも、快適にできたなら、幸いです。\n\n下のボタンから応援ページに移動することで、検索を続けることができます。")
        portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html"
        st.link_button("応援ページに移動して、検索を続ける", portal_url, type="primary")

    else:
        # --- 通常モード (上限に達していない場合) ---
        st.info("出発地と目的地を入力すると、AIが標準的な所要時間や料金に基づいた最適なルートを3つ提案します。")
        st.warning("※これはリアルタイムの運行情報を反映したものではありません。あくまで目安としてご利用ください。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.get('norikae_usage_count', 0)} 回、検索できます。応援後に残り回数がリセットされます。")

        col1, col2 = st.columns(2)
        with col1:
            start_station = st.text_input("🚩 出発地を入力してください", "大阪")
        with col2:
            end_station = st.text_input("🎯 目的地を入力してください", "東京")

        if st.button(f"「{start_station}」から「{end_station}」へのルートを検索"):
            if not gemini_api_key:
                st.error("サイドバーでGemini APIキーを設定してください。")
            else:
                with st.spinner(f"AIが「{start_station}」から「{end_station}」への最適なルートをシミュレーションしています..."):
                    try:
                        genai.configure(api_key=gemini_api_key)
                        
                        system_prompt = """
                        あなたは、日本の公共交通機関の膨大なデータベースを内蔵した、世界最高の「乗り換え案内エンジン」です。
                        (中身は変更ありません)
                        """
                        model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_prompt)
                        response = model.generate_content(f"出発地：{start_station}, 目的地：{end_station}")
                        
                        json_text = response.text.strip().lstrip("```json").rstrip("```")
                        routes = json.loads(json_text)
                        
                        # ★★★【通行料の徴収】★★★
                        st.session_state.norikae_usage_count += 1
                        
                        st.success(f"AIによるルートシミュレーションが完了しました！")
                        
                        for i, route in enumerate(routes):
                            with st.expander(f"**{route.get('route_name', 'ルート')}** - 約{route.get('summary', {}).get('total_time', '?')}分 / {route.get('summary', {}).get('total_fare', '?')}円 / 乗り換え{route.get('summary', {}).get('transfers', '?')}回", expanded=(i==0)):
                                if route.get('steps'):
                                    for step in route['steps']:
                                        if step.get('transport_type') == "電車":
                                            st.markdown(f"**<font color='blue'>{step.get('station_from', '?')}</font>**", unsafe_allow_html=True)
                                            st.markdown(f"｜ 🚃 {step.get('line_name', '不明な路線')} ({step.get('details', '')})")
                                        elif step.get('transport_type') == "徒歩":
                                            st.markdown(f"**<font color='green'>👟 {step.get('details', '徒歩')}</font>**", unsafe_allow_html=True)
                                        elif step.get('transport_type') == "バス":
                                            st.markdown(f"**<font color='purple'>{step.get('station_from', '?')}</font>**", unsafe_allow_html=True)
                                            st.markdown(f"｜ 🚌 {step.get('line_name', '不明なバス')} ({step.get('details', '')})")
                                
                                last_station = end_station
                                if route.get('steps'):
                                    train_steps = [s for s in route['steps'] if s.get('transport_type') == '電車' and s.get('station_to')]
                                    if train_steps:
                                        last_station = train_steps[-1].get('station_to')

                                st.markdown(f"**<font color='red'>{last_station}</font>**", unsafe_allow_html=True)
                        
                        # 最後の検索でrerunを呼ぶと、結果表示後に即座に利用制限画面に切り替わる
                        if st.session_state.get("norikae_usage_count", 0) >= usage_limit:
                            time.sleep(1) # ユーザーが結果を見るための、一瞬の間
                            st.rerun()

                    except Exception as e:
                        st.error(f"シミュレーション中にエラーが発生しました: {e}")
                        st.code(traceback.format_exc())
