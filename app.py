import streamlit as st
import google.generativeai as genai

# Streamlit Cloud에서는 .env 대신 secrets 사용
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# 페이지 설정
st.set_page_config(page_title="🧠 브레인스토밍 보드", layout="wide")
st.title("🧠 브레인스토밍 아이디어 보드")

# 세션 상태 초기화
if "topic" not in st.session_state:
    st.session_state.topic = ""
    st.session_state.ideas = []  # 각 idea: {text: str, removed: bool, memo: str, liked: bool}
    st.session_state.generated = []

# Gemini API 호출 함수
def generate_ideas(prompt):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ 아이디어 생성 중 오류 발생: {e}")
        return ""

# 프롬프트 생성 함수
def build_prompt(topic, kept_ideas, removed_ideas):
    prompt = f"""당신은 창의적인 브레인스토밍 보조 AI입니다.

다음은 사용자가 설정한 브레인스토밍 주제입니다:
- 주제: \"{topic}\"

💡 현재까지 사용자가 **유지한 아이디어**는 다음과 같습니다:
{chr(10).join([f"{i+1}. {idea['text']}" for i, idea in enumerate(kept_ideas)]) or '없음'}

❌ 그리고 사용자가 **제거한 아이디어**는 다음과 같습니다:
{chr(10).join([f"{i+1}. {idea['text']}" for i, idea in enumerate(removed_ideas)]) or '없음'}

✍️ 새로운 아이디어를 제안할 때 다음 지침을 따라주세요:
- 유지된 아이디어들과 **겹치지 않는 주제/기능**을 제안해주세요.
- 제거된 아이디어들과는 **아이디어 유형이나 용도 면에서 유사하지 않도록** 주의해주세요.
- 각 아이디어는 **서로 다른 유형** 또는 **다른 시각**을 반영해주세요 (예: 대상, 방식, 수익모델 등).
- 실현 가능성에 너무 얽매이지 말고, 창의적이고 실험적인 아이디어도 포함해주세요.
- 제안은 5개로, 각 아이디어는 **제목 + 간단한 설명** 형식으로 작성해주세요.
- 설명은 **1~2문장**, 약 **50~100자 내외**로 간결하게 작성해주세요.
"""
    return prompt

# 1. 주제 입력
if not st.session_state.topic:
    topic = st.text_input("아이디어를 생각하고 싶은 주제를 입력해주세요:")
    if st.button("주제 설정") and topic:
        st.session_state.topic = topic
        prompt = build_prompt(topic, [], [])
        with st.spinner("초기 아이디어를 생성 중입니다..."):
            output = generate_ideas(prompt)
            if output:
                for line in output.split("\n"):
                    if line.strip():
                        st.session_state.ideas.append({
                            "text": line.strip(),
                            "removed": False,
                            "memo": "",
                            "liked": False
                        })
        st.rerun()
else:
    st.subheader(f"🎯 주제: {st.session_state.topic}")

    # 2. 아이디어 출력 및 상호작용
    st.markdown("---")
    visible_ideas = [idea for idea in st.session_state.ideas if not idea.get("removed")]
    for i, idea in enumerate(visible_ideas):
        cols = st.columns([8, 1, 1])
        with cols[0]:
            st.markdown(f"**{i+1}.** {idea['text']}")
        with cols[1]:
            if st.button("🗑️", key=f"remove_{i}"):
                idx = st.session_state.ideas.index(idea)
                st.session_state.ideas[idx]["removed"] = True
                st.rerun()
        with cols[2]:
            if st.button("👍", key=f"like_{i}"):
                idx = st.session_state.ideas.index(idea)
                st.session_state.ideas[idx]["liked"] = True

    # 3. 아이디어 더 생성
    if st.button("아이디어 더 생성하기"):
        kept = [idea for idea in st.session_state.ideas if not idea.get("removed")]
        removed = [idea for idea in st.session_state.ideas if idea.get("removed")]
        prompt = build_prompt(st.session_state.topic, kept, removed)
        with st.spinner("새로운 아이디어를 생성 중입니다..."):
            output = generate_ideas(prompt)
            if output:
                for line in output.split("\n"):
                    if line.strip():
                        st.session_state.ideas.append({
                            "text": line.strip(),
                            "removed": False,
                            "memo": "",
                            "liked": False
                        })
                st.success("✅ 새로운 아이디어가 추가되었습니다!")

    # 4. 초기화 버튼
    if st.button("🔄 주제 초기화 및 새로 시작"):
        st.session_state.topic = ""
        st.session_state.ideas = []
        st.session_state.generated = []
        st.rerun()
