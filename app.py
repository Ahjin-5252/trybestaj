import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# 1. 앱 설정
st.set_page_config(page_title="고1 영어 수준별 학습", layout="wide")

# 2. 데이터 직접 내장 (파일 읽기 에러를 100% 방지합니다)
@st.cache_data
def get_data():
    data = [
        ["환경", "초급", "What is soft-path river engineering? To visualize it, liken it to a trail in the woods. If a tree falls on the footpath, a soft-path way is just to move the trail around it.", "visualize: 시각화하다, trail: 오솔길, liken: 비유하다", "to create a superhighway: 보어 역할을 하는 to부정사구", "1. Soft-path 방식의 특징은?|2. 본문에서 오솔길에 비유된 것은?|3. 나무가 쓰러졌을 때의 대처법은?|4. 강을 자연의 일부로 받아들이는 방식은?|5. 이 글의 주제로 적절한 것은?", "(A) 개입주의|(B) 자연 순응|(C) 파괴적|(D) 고속도로", "(B)"],
        ["진로", "초급", "The goal of class discussion is to help you be an active student. It encourages you to think critically and share your ideas with others.", "discussion: 토론, encourage: 격려하다, critically: 비판적으로", "to help you be: help+목적어+동사원형 구문", "1. 학급 토론의 목적은?|2. 어떤 학생이 되도록 돕나요?|3. 토론이 장려하는 사고방식은?|4. 아이디어를 어떻게 하나요?|5. 토론의 장점으로 알맞은 것은?", "(A) 수동적 태도|(B) 비판적 사고|(C) 단순 암기|(D) 개인주의", "(B)"],
        ["과학", "초급", "A good example of chaos is the magnetic pendulum. It has four magnets arranged in a square and a pendulum that swings back and forth.", "chaos: 혼돈, pendulum: 진자, magnetic: 자성의", "arranged in a square: 과거분사구의 수식", "1. 혼돈의 예시로 든 것은?|2. 자석은 몇 개인가요?|3. 자석은 어떤 모양으로 놓여있나요?|4. 진자는 어떻게 움직이나요?|5. 이 실험의 핵심 개념은?", "(A) 정지 상태|(B) 규칙적 진동|(C) 혼돈(Chaos)|(D) 중력", "(C)"]
    ]
    return pd.DataFrame(data, columns=['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer'])

# 3. 음성 재생 함수
def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()
        b64 = base64.b64encode(audio_bytes).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except:
        st.warning("음성 재생 기능을 사용할 수 없습니다.")

# --- 메인 화면 시작 ---
st.title("📚 고등학교 1학년 영어 수준별 학습")

df = get_data()

# 4. 사이드바 인터페이스
with st.sidebar:
    st.header("👤 학생 정보 입력")
    grade = st.text_input("학년", "1")
    s_class = st.text_input("반")
    number = st.text_input("번호")
    name = st.text_input("이름")
    st.divider()
    
    st.header("⚙️ 학습 설정")
    u_topic = st.selectbox("주제 선택", ["환경", "진로", "과학"])
    u_level = st.selectbox("레벨 선택", ["초급", "중급", "고급"])

# 5. 지문 출력 섹션
try:
    sel = df[(df['Topic'] == u_topic) & (df['Level'] == u_level)].iloc[0]
    
    st.subheader(f"📖 {u_topic} 지문 학습 ({u_level})")
    col_p, col_s = st.columns([0.9, 0.1])
    with col_p:
        st.info(sel['Passage'])
    with col_s:
        if st.button("🔊"):
            speak(sel['Passage'])

    with st.expander("💡 단어 및 문법 도움말"):
        st.write("**[핵심 단어]**", sel['Vocabulary'])
        st.write("**[문법 설명]**", sel['Grammar'])

    st.divider()

    # 6. 문제 풀기 (학습하기)
    if st.button("📝 학습하기 (문제 풀기)"):
        st.session_state.start = True

    if st.session_state.get('start'):
        st.subheader("✍️ 확인 문제")
        qs = sel['Question'].split('|')
        ans = sel['Answer'].split('|')
        
        user_ans = []
        for i, q in enumerate(qs):
            st.write(f"**{i+1}. {q.strip()}**")
            choice = st.radio(f"답안 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q{i}", horizontal=True)
            user_ans.append(choice)

        if st.button("결과 제출"):
            score = sum([1 for u, a in zip(user_ans, ans) if u.strip() == a.strip()])
            st.subheader(f"📊 {name} 학생: 5문제 중 {score}문제를 맞혔습니다!")
            
            if score >= 4:
                st.balloons()
                st.success("🌟 열심히 공부한 것에 대해 선생님이 가득 칭찬합니다!")
            elif score >= 2:
                st.warning("👏 노력에 대해 칭찬하며, 조금만 더 열심히 하면 좋은 결과가 있을 거예요!")
            else:
                st.error("💪 어렵더라도 포기하지 말고 꾸준히 노력해보자!")
except:
    st.warning("선택하신 주제와 레벨에 맞는 데이터를 준비 중입니다.")
