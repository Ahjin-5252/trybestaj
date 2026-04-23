import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# 1. 파일명 설정 (깃허브에 올린 이름과 똑같이 맞춤)
FILE_NAME = 'graded_reading_texts.xlsx - Sheet1.csv'

@st.cache_data
def load_data():
    # 파일 읽기
    df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
    
   
    df.columns = df.columns.str.strip().str.capitalize()
    
   
    return df

def speak(text):
    tts = gTTS(text=text, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_bytes = fp.read()
    b64 = base64.b64encode(audio_bytes).decode()
    md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
    st.markdown(md, unsafe_allow_html=True)

# 인터페이스 구성 시작
st.set_page_config(page_title="고1 수준별 영어 학습", layout="wide")
st.title("📚 고등학교 1학년 수준별 영어 학습 앱")

# 1. 학생 정보 입력
with st.sidebar:
    st.header("👤 학생 정보 입력")
    grade = st.text_input("학년", "1")
    s_class = st.text_input("반")
    number = st.text_input("번호")
    name = st.text_input("이름")
    
    st.divider()
    
    # 2. 주제 및 레벨 선택
    df = load_data()
    topic = st.selectbox("주제 선택", df['Topic'].unique())
    level = st.selectbox("레벨 선택", df['Level'].unique())

# 데이터 추출
selected = df[(df['Topic'] == topic) & (df['Level'] == level)].iloc[0]

# 3. 지문 출력
st.subheader(f"📖 지문 읽기: {topic} ({level})")
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.info(selected['Passage'])
with col2:
    if st.button("🔊 듣기"):
        speak(selected['Passage'])

# 4. 학습 도움말
with st.expander("💡 어휘 및 구문 설명 보기"):
    st.write("**어휘:**", selected['Vocabulary'])
    st.write("**구문:**", selected['Grammar'])

st.divider()

# 5. 문제 풀기 및 피드백
if st.button("📝 문제 풀기"):
    st.session_state.quiz = True

if st.session_state.get('quiz'):
    st.subheader("✍️ 확인 문제")
    qs = selected['Question'].split('|')
    opts = selected['Option'].split('|')
    ans = selected['Answer'].split('|')
    
    user_choices = []
    for i in range(len(qs)):
        st.write(f"**Q{i+1}. {qs[i]}**")
        choice = st.radio(f"정답 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q{i}", horizontal=True)
        user_choices.append(choice)
    
    if st.button("채점하기"):
        score = sum([1 for u, a in zip(user_choices, ans) if u.strip() == a.strip()])
        st.success(f"결과: 5문제 중 {score}문제를 맞혔습니다!")
        
        # 성취도별 피드백
        if score >= 4:
            st.balloons()
            st.write(f"🌟 **{name} 학생, 정말 훌륭해요!** 지문을 완벽히 이해했군요! 선생님은 당신의 실력을 믿습니다.")
        elif score >= 2:
            st.write(f"👏 **{name} 학생, 잘했습니다!** 조금만 더 꼼꼼히 읽어보면 다음엔 만점을 받을 수 있을 거예요.")
        else:
            st.write(f"💪 **{name} 학생, 포기하지 마세요!** 어려운 내용이었지만 도전한 것만으로도 멋집니다. 다시 천천히 읽어봐요!")
