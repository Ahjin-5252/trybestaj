import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# 1. 선생님의 실제 파일명으로 정확히 수정했습니다.
FILE_NAME = 'graded_reading_texts.xlsx - Sheet1.csv'

@st.cache_data
def load_data():
    try:
        # 파일 로드
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        
        # 제목 행의 앞뒤 공백을 제거하고 첫 글자만 대문자로 통일 (KeyError 방지)
        df.columns = df.columns.str.strip().str.capitalize()
        
        # 데이터 내용의 앞뒤 공백도 제거
        df['Topic'] = df['Topic'].astype(str).str.strip()
        df['Level'] = df['Level'].astype(str).str.strip()
        
        return df
    except Exception as e:
        st.error(f"파일을 찾을 수 없거나 읽기 오류가 발생했습니다: {e}")
        return None

# 앱 설정 및 인터페이스
st.set_page_config(page_title="고1 영어 수준별 학습", layout="wide")

if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False

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

st.title("📚 고등학교 1학년 수준별 영어 학습")

df = load_data()

if df is not None:
    with st.sidebar:
        st.header("👤 학생 정보")
        name = st.text_input("이름", placeholder="이름 입력")
        st.divider()
        
        # 실제 데이터에서 주제와 레벨 추출
        topic_options = df['Topic'].unique()
        level_options = df['Level'].unique()
        
        selected_topic = st.selectbox("주제 선택", topic_options)
        selected_level = st.selectbox("레벨 선택", level_options)

    try:
        # 선택한 조건에 맞는 데이터 필터링
        data = df[(df['Topic'] == selected_topic) & (df['Level'] == selected_level)].iloc[0]

        st.subheader(f"📖 지문: {selected_topic} ({selected_level})")
        c1, c2 = st.columns([0.85, 0.15])
        with c1:
            st.info(data['Passage'])
        with c2:
            if st.button("🔊 듣기"):
                speak(data['Passage'])

        with st.expander("💡 어휘 및 구문 보기"):
            st.write("**[어휘]**", data['Vocabulary'])
            st.write("**[구문]**", data['Grammar'])

        st.divider()

        if st.button("📝 문제 풀기 시작"):
            st.session_state.quiz_active = True

        if st.session_state.quiz_active:
            st.subheader("✍️ 확인 문제")
            questions = str(data['Question']).split('|')
            options = str(data['Option']).split('|')
            answers = str(data['Answer']).split('|')

            user_choices = []
            for i in range(len(questions)):
                st.write(f"**Q{i+1}. {questions[i].strip()}**")
                choice = st.radio(f"정답 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"ans_{i}", horizontal=True)
                user_choices.append(choice)

            if st.button("채점 및 피드백 확인"):
                score = 0
                for u, a in zip(user_choices, answers):
                    if u.strip() == a.strip(): score += 1
                
                st.subheader(f"📊 점수: {score} / 5")
                
                # 선생님이 요청하신 피드백 멘트
                if score >= 4:
                    st.balloons()
                    st.success(f"🌟 **{name} 학생, 정말 대단해요!** 열심히 공부한 보람이 있네요. 선생님이 가득 칭찬합니다!")
                elif score >= 2:
                    st.warning(f"👏 **{name} 학생, 노력하는 모습이 아주 멋져요!** 조금만 더 집중하면 다음엔 꼭 만점을 받을 거예요!")
                else:
                    st.error(f"💪 **{name} 학생, 포기하지 마세요!** 지금처럼 꾸준히 노력한다면 반드시 실력이 늘 거예요. 화이팅!")
    except:
        st.warning("선택한 주제와 레벨에 해당하는 데이터를 찾을 수 없습니다.")
