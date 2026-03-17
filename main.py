import streamlit as st
import random

# --- 페이지 설정 (가장 먼저 와야 함) ---
st.set_page_config(page_title="화려한 지뢰찾기", page_icon="💣", layout="centered")

# --- CSS 스타일링 (화려하고 깔끔한 버튼 UI 만들기) ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 10px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        border-color: #ff4b4b;
        color: #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

# --- 게임 설정 ---
ROWS, COLS = 8, 8
MINES = 10

# --- 게임 초기화 함수 ---
def init_game():
    st.session_state.board = [[0] * COLS for _ in range(ROWS)]
    st.session_state.revealed = [[False] * COLS for _ in range(ROWS)]
    st.session_state.flags = [[False] * COLS for _ in range(ROWS)]
    st.session_state.game_over = False
    st.session_state.game_won = False
    
    # 지뢰 배치 (-1은 지뢰)
    mines_placed = 0
    while mines_placed < MINES:
        r, c = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
        if st.session_state.board[r][c] != -1:
            st.session_state.board[r][c] = -1
            mines_placed += 1
            
    # 주변 지뢰 개수 계산
    for r in range(ROWS):
        for c in range(COLS):
            if st.session_state.board[r][c] == -1:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and st.session_state.board[nr][nc] == -1:
                        count += 1
            st.session_state.board[r][c] = count

# --- 빈 칸 자동 열기 (Flood Fill) ---
def reveal_empty(r, c):
    if r < 0 or r >= ROWS or c < 0 or c >= COLS: return
    if st.session_state.revealed[r][c] or st.session_state.flags[r][c]: return
    
    st.session_state.revealed[r][c] = True
    
    # 빈 칸(0)이면 주변 8칸도 재귀적으로 엶
    if st.session_state.board[r][c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                reveal_empty(r + dr, c + dc)

# --- 승리 조건 체크 ---
def check_win():
    for r in range(ROWS):
        for c in range(COLS):
            # 지뢰가 아닌데 안 열린 칸이 있다면 아직 승리가 아님
            if st.session_state.board[r][c] != -1 and not st.session_state.revealed[r][c]:
                return False
    return True

# --- 세션 상태 초기화 ---
if 'board' not in st.session_state:
    init_game()

# --- 화면 UI 구성 ---
st.title("💥 심장이 쫄깃한 지뢰찾기!")
st.write(f"총 지뢰 개수: **{MINES}개** | 깃발과 탐색 모드를 번갈아가며 사용하세요!")

# 컨트롤 패널
col1, col2 = st.columns([1, 1])
with col1:
    mode = st.radio("모드 선택", ["🔍 탐색", "🚩 깃발 꽂기"], horizontal=True)
with col2:
    if st.button("🔄 게임 재시작", use_container_width=True):
        init_game()
        st.rerun()

st.divider()

# --- 게임 보드 그리기 ---
if st.session_state.game_over:
    st.error("💣 지뢰를 밟았습니다! 게임 오버! 💣")
elif st.session_state.game_won:
    st.success("🎉 축하합니다! 모든 지뢰를 피했습니다! 🎉")
    st.balloons() # 화려한 승리 효과!

for r in range(ROWS):
    cols = st.columns(COLS)
    for c in range(COLS):
        with cols[c]:
            # 이미 열린 칸
            if st.session_state.revealed[r][c]:
                val = st.session_state.board[r][c]
                if val == -1:
                    st.button("💥", key=f"btn_{r}_{c}", disabled=True)
                elif val == 0:
                    st.button("⬜", key=f"btn_{r}_{c}", disabled=True)
                else:
                    # 숫자 이모지 매핑을 위한 리스트
                    number_emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
                    st.button(number_emojis[val], key=f"btn_{r}_{c}", disabled=True)
            
            # 아직 안 열린 칸
            else:
                # 깃발이 꽂힌 칸
                if st.session_state.flags[r][c]:
                    btn_label = "🚩"
                else:
                    btn_label = "🔲"
                
                # 버튼 클릭 이벤트
                if st.button(btn_label, key=f"btn_{r}_{c}", disabled=st.session_state.game_over or st.session_state.game_won):
                    if mode == "🚩 깃발 꽂기":
                        st.session_state.flags[r][c] = not st.session_state.flags[r][c]
                        st.rerun()
                    else: # 탐색 모드
                        if not st.session_state.flags[r][c]: # 깃발 꽂힌 곳은 탐색 불가
                            if st.session_state.board[r][c] == -1:
                                st.session_state.game_over = True
                                st.session_state.revealed[r][c] = True
                            else:
                                reveal_empty(r, c)
                                if check_win():
                                    st.session_state.game_won = True
                            st.rerun()
