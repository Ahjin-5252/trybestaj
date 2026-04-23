
import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# 1. 선생님의 깃허브에 있는 실제 파일명입니다.
FILE_NAME = 'graded_reading_texts.xlsx - Sheet1.csv'

@st.cache_data
def load_data():
    try:
        # 데이터 로드 시 제목 행(header)을 무시하고 0번 행부터 데이터로 읽어옵니다.
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig', header=0)
        
        # [핵심 해결책] 제목 칸에 어떤 글자가 있든 무시하고 순서대로 강제 이름을 붙입니다.
        # 0:주제, 1:레벨, 2:지문, 3:어휘, 4:구문, 5:문제, 6:보기, 7:정답
        new_columns = ['Topic', 'Level', 'Passage', 'Vocabulary', 'Grammar', 'Question', 'Option', 'Answer']
        df.columns = new_columns[:len(df.columns)]
        
        # 데이터의 앞뒤 공백을 모두 제거하여 매칭 오류를 방지합니다.
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
        return None

# 앱 기본 설정
st.set_page_config(page_title="고1 영어 학습 앱", layout="wide")

if 'quiz_ready' not in st.session_state:
    st.session_state.quiz_ready = False

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
        st.warning("음성 재생이 지원되지 않는 환경입니다.")

st.title("📚 고등학교 1학년 수준별 영어 학습")

# 데이터 불러오기
df = load_data()

if df is not None:
    # 1. 사이드바 인터페이스
    with st.sidebar:
        st.header("👤 학생 정보")
        std_name = st.text_input("이름", placeholder="이름을 입력하세요")
        st.divider()
        
        st.header("⚙️ 학습 설정")
        # 데이터에서 중복 없는 주제와 레벨 추출
        topic_list = df['Topic'].unique()
        level_list = df['Level'].unique()
        
        sel_topic = st.selectbox("주제 선택", topic_list)
        sel_level = st.selectbox("레벨 선택", level_list)

    # 2. 본문 인터페이스
    try:
        # 선택한 주제와 레벨에 맞는 데이터 행 하나를 가져옵니다.
        row = df[(df['Topic'] == sel_topic) & (df['Level'] == sel_level)].iloc[0]

        st.subheader(f"📖 지문 읽기: {sel_topic} ({sel_level})")
        col_p, col_s = st.columns([0.85, 0.15])
        with col_p:
            st.info(row['Passage'])
        with col_s:
            if st.button("🔊 듣기"):
                speak(row['Passage'])

        with st.expander("💡 어휘 및 구문 설명 보기"):
            c1, c2 = st.columns(2)
            c1.write("**[핵심 어휘]**")
            c1.write(row['Vocabulary'])
            c2.write("**[구문 분석]**")
            c2.write(row['Grammar'])

        st.divider()

        # 3. 퀴즈 인터페이스
        if st.button("📝 문제 풀기 시작"):
            st.session_state.quiz_ready = True

        if st.session_state.quiz_ready:
            st.subheader("✍️ 학습 확인 문제")
            qs = str(row['Question']).split('|')
            opts = str(row['Option']).split('|')
            ans = str(row['Answer']).split('|')

            user_answers = []
            for i in range(len(qs)):
                st.write(f"**Q{i+1}. {qs[i].strip()}**")
                choice = st.radio(f"정답 선택 {i+1}", ["(A)", "(B)", "(C)", "(D)"], key=f"q_{i}", horizontal=True)
                user_answers.append(choice)

            if st.button("제출 및 채점하기"):
                correct_count = 0
                for u, a in zip(user_answers, ans):
                    if u.strip() == a.strip():
                        correct_count += 1
                
                st.subheader(f"📊 결과: 5문제 중 {correct_count}문제를 맞혔습니다!")
                
                # 점수별 피드백
                if correct_count >= 4:
                    st.balloons()
                    st.success(f"🌟 **{std_name} 학생, 정말 대단해요!** 지문의 핵심 내용을 완벽하게 파악했군요. 선생님이 가득 칭찬합니다!")
                elif correct_count >= 2:
                    st.warning(f"👏 **{std_name} 학생, 노력하는 모습이 멋져요!** 조금만 더 집중하면 다음엔 꼭 만점을 받을 거예요!")
                else:
                    st.error(f"💪 **{std_name} 학생, 포기하지 마세요!** 지금처럼 꾸준히 노력한다면 반드시 실력이 늘 거예요. 화이팅!")
    except:
        st.warning("데이터를 불러오는 중 문제가 발생했습니다. 선택한 주제/레벨이 파일에 있는지 확인해주세요.")
