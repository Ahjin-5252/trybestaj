import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# --- [전략] 파일을 읽지 않고 데이터를 코드에 직접 저장합니다 ---
@st.cache_data
def get_data():
    raw_data = [
        ["환경", "초급", "What is soft-path river engineering? To visualize it, liken it to a trail in the woods. If a tree falls on the footpath, a soft-path way is just to move the trail around it. A more interventionist way is to remove the tree and restore the old path. A very strong interventionist way might be to pave the path to keep it permanently in the landscape. But the most extreme step is to create a superhighway that removes the landscape and bulldozes straight through all obstacles. Soft-path engineering is humble with respect to what we actually know about river movement. It accepts changes in the river as important parts of nature.", "visualize 시각화하다, trail 오솔길, liken 비유하다, interventionist 개입주의적인, restore 복구하다", "to create a superhighway: be동사의 주격 보어 역할을 하는 to부정사구", "1. Soft-path 방식에서 장애물(나무)을 만났을 때의 대처는?|2. 강을 자연의 일부로 받아들이는 방식은?|3. 가장 극단적인 개입 방식은 무엇인가요?|4. Soft-path 공학의 특징으로 알맞은 단어는?|5. 이 글의 주제로 가장 적절한 것은?", "(A) 경로 우회|(B) 고속도로 건설|(C) 나무 제거|(D) 영구 포장", "(A)"],
        ["진로", "초급", "The goal of class discussion is to help you be an active student. It encourages you to think critically and share your ideas with others. In a discussion, there are no wrong answers, only different perspectives. Learning to listen to your peers is as important as speaking your own mind. This process builds confidence and prepares you for future collaboration in the workplace.", "discussion 토론, active 능동적인, critically 비판적으로, perspective 관점, collaboration 협력", "to help you be: help 뒤에 목적어와 동사원형이 오는 구조", "1. 학급 토론의 주요 목적은?|2. 토론을 통해 기를 수 있는 능력은?|3. 토론에서 정답보다 중요한 것은?|4. 토론이 준비시켜주는 미래의 상황은?|5. 경청과 발언 중 무엇이 더 중요한가요?", "(A) 정답 암기|(B) 수동적 경청|(C) 비판적 사고|(D) 개인 경쟁", "(C)"],
        ["과학", "초급", "A good example of chaos is the magnetic pendulum. It has four magnets arranged in a square at the base and a pendulum that swings back and forth between them. At first, the motion looks predictable. But as the pendulum gains energy, its path becomes incredibly complex. Small changes in the starting position lead to completely different results. This sensitivity to initial conditions is a hallmark of chaotic systems.", "chaos 혼돈, magnetic pendulum 자기 진자, predictable 예측 가능한, incredibly 엄청나게, hallmark 특징", "arranged in a square: 과거분사구가 앞의 명사를 수식", "1. 혼돈(Chaos)의 예시로 든 도구는?|2. 자석은 총 몇 개가 사용되나요?|3. 혼돈 시스템의 주요 특징은?|4. 초기 조건의 작은 변화는 어떤 결과를 낳나요?|5. 처음에는 진자의 움직임이 어떻게 보이나요?", "(A) 자기 진자|(B) 단순 시계|(C) 회전 목마|(D) 자석판", "(A)"]
    ]
    df = pd.DataFrame(raw_data, columns=['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer'])
    return df

# 음성 재생 함수
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
        st.warning("음성 재생 실패")

# --- 앱 UI 시작 ---
st.set_page_config(page_title="고1 영어 학습", layout="wide")
st.title("📚 고등학교 1학년 영어 수준별 학습")

if 'quiz_start' not in st.session_state:
    st.session_state.quiz_start = False

df = get_data()

# 1. 사이드바 (정보 입력)
with st.sidebar:
    st.header("👤 학생 정보")
    name = st.text_input("이름")
    st.divider()
    st.header("⚙️ 학습 설정")
    topic = st.selectbox("주제 선택", ["환경", "진로", "과학"])
    level = st.selectbox("레벨 선택", ["초급", "중급", "고급"])

# 2. 지문 출력 영역
try:
    sel = df[df['Topic'] == topic].iloc[0]

    st.subheader(f"📖 {topic} 지문 학습")
    c1, c2 = st.columns([0.9, 0.1])
    with c1:
        st.info(sel['Passage'])
    with c2:
        if st.button("🔊"):
            speak(sel['Passage'])

    with st.expander("💡 학습 포인트 (어휘/구문)"):
        st.write("**[어휘]**", sel['Vocabulary'])
        st.write("**[구문]**", sel['Grammar'])

    st.divider()

    # 3. 문제 풀기 및 피드백
    if st.button("📝 학습하기 (문제 풀기)"):
        st.session_state.quiz_start = True

    if st.session_state.quiz_start:
        st.subheader("✍️ 확인 문제")
        qs = sel['Question'].split('|')
        ans = sel['Answer'].split('|')
        
        user_ans = []
        for i, q in enumerate(qs):
            st.write(f"**Q{i+1}. {q.strip()}**")
            u_choice = st.radio(f"답안 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q{i}", horizontal=True)
            user_ans.append(u_choice)

        if st.button("채점 완료"):
            score = sum([1 for u, a in zip(user_ans, ans) if u.strip() == a.strip()])
            st.subheader(f"📊 {name} 학생: 5문제 중 {score}문제를 맞혔습니다!")
            
            if score >= 4:
                st.balloons()
                st.success("🌟 열심히 공부한 것에 대해 선생님이 가득 칭찬합니다! 정말 대단해요!")
            elif score >= 2:
                st.warning("👏 노력하는 모습이 아주 멋져요! 조금만 더 열심히 하면 좋은 결과가 있을 거예요!")
            else:
                st.error("💪 어렵더라도 포기하지 말고 꾸준히 노력해보자! 선생님은 너를 응원해.")
except:
    st.warning("데이터를 불러올 수 없습니다.")
