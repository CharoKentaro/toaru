import streamlit as st
import google.generativeai as genai
import traceback
import json
import time

# ===============================================================
# 補助関数 (変更なし)
# ===============================================================
# この専門家には、補助関数はありませんでした

# ===============================================================
# 専門家のメインの仕事 (最後の叡智を搭載)
# ===============================================================
def show_tool(gemini_api_key):
    st.header("🚃 乗り換え案内", divider='rainbow')

    # --- 【帰還者の祝福】 ---
    if st.query_params.get("unlocked") == "true":
        st.session_state["norikae_usage_count"] = 0
        st.query_params.clear()
        st.toast("おかえりなさい！検索回数がリセットされました。")
        st.balloons()
        time.sleep(1)
        st.rerun()

    # --- 【門番の存在保証】 ---
    if "norikae_usage_count" not in st.session_state:
        st.session_state.norikae_usage_count = 0

    # --- 【運命の分岐路】 ---
    usage_limit = 5
    is_limit_reached = st.session_state.get("norikae_usage_count", 0) >= usage_limit

    if is_limit_reached:
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info("このツールが、あなたの、移動を、少しでも、快適にできたなら、幸いです。\n\n下のボタンから応援ページに移動することで、検索を続けることができます。")
        portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html"
        st.link_button("応援ページに移動して、検索を続ける", portal_url, type="primary")

    else:
        # --- 通常モード ---
        st.info("出発地と目的地を入力すると、AIが標準的な所要時間や料金に基づいた最適なルートを3つ提案します。")
        st.warning("※これはリアルタイムの運行情報を反映したものではありません。あくまで目安としてご利用ください。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.get('norikae_usage_count', 0)} 回、検索できます。応援後、リセットされます。")

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
                        ユーザーから指定された「出発地」と「目的地」に基づき、標準的な所要時間、料金、乗り換え情報を基に、最適な移動ルートをシミュレートするのがあなたの役割です。
                        1. **3つのルート提案:** 必ず、「早さ・安さ・楽さ」のバランスが良い、優れたルートを「3つ」提案してください。
                        2. **厳格なJSONフォーマット:** 出力は、必ず、以下のJSON形式の配列のみで回答してください。他の言葉、説明、言い訳は、一切含めないでください。
                        3. **経路の詳細 (steps):** `transport_type`, `line_name`, `station_from`, `station_to`, `details` を記述してください。
                        4. **サマリー情報:** `total_time`, `total_fare`, `transfers` を数値のみで記述してください。
                        ```json
                        [
                          {
                            "route_name": "ルート1：最速",
                            "summary": { "total_time": 30, "total_fare": 450, "transfers": 1 },
                            "steps": [
                              { "transport_type": "電車", "line_name": "JR大阪環状線", "station_from": "大阪", "station_to": "鶴橋", "details": "内回り" },
                              { "transport_type": "徒歩", "details": "近鉄線へ乗り換え" },
                              { "transport_type": "電車", "line_name": "近鉄奈良線", "station_from": "鶴橋", "station_to": "河内小阪", "details": "普通・奈良行き" }
                            ]
                          },
                          { "route_name": "ルート2：乗り換え楽", "summary": { "total_time": 35, "total_fare": 480, "transfers": 0 }, "steps": [] },
                          { "route_name": "ルート3：最安", "summary": { "total_time": 40, "total_fare": 400, "transfers": 2 }, "steps": [] }
                        ]
                        ```
                        """
                        model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_prompt)
                        response = model.generate_content(f"出発地：{start_station}, 目的地：{end_station}")
                        
                        # ★★★★★ ここが、我々の、最後の、叡智！【存在確認】です！ ★★★★★
                        if not response.text:
                            st.error("AIからの応答が空でした。AIがルートを見つけられなかったか、一時的な問題が発生した可能性があります。条件を変えてもう一度お試しください。")
                        
                        else:
                            json_text = response.text.strip().lstrip("```json").rstrip("```")
                            routes = json.loads(json_text)
                            
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
                            
                            if st.session_state.get("norikae_usage_count", 0) >= usage_limit:
                                time.sleep(1)
                                st.rerun()

                    except json.JSONDecodeError as e:
                        st.error("AIからの応答を解析できませんでした。AIが予期せぬ形式で回答した可能性があります。")
                        st.info("AIからの生の応答は以下の通りです：")
                        st.code(response.text, language="text")
                    
                    except Exception as e:
                        st.error(f"シミュレーション中に予期せぬエラーが発生しました: {e}")
                        st.code(traceback.format_exc())
