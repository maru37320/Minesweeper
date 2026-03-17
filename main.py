import streamlit as st
import streamlit.components.v1 as components

# --- 페이지 설정 ---
st.set_page_config(page_title="클래식 지뢰찾기", page_icon="💣", layout="wide")

st.title("💣 리얼 클래식 지뢰찾기")
st.markdown("**좌클릭:** 탐색 | **우클릭:** 깃발 꽂기 | **숫자 더블클릭:** 주변 8칸 한 번에 열기 (깃발 개수가 맞을 때)")

# --- HTML/JS/CSS를 이용한 완벽한 지뢰찾기 구현 ---
# 스트림릿의 한계(우클릭 불가, 렌더링 지연)를 극복하기 위해 클라이언트 사이드 로직 사용
minesweeper_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    body {
        font-family: sans-serif;
        background-color: #bdbdbd;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        user-select: none;
    }
    #controls {
        margin-bottom: 20px;
        display: flex;
        gap: 15px;
        align-items: center;
    }
    select, button {
        padding: 5px 10px;
        font-size: 16px;
        cursor: pointer;
    }
    #board {
        display: grid;
        background-color: #7b7b7b;
        border: 3px solid #808080;
        border-top-color: #ffffff;
        border-left-color: #ffffff;
    }
    .cell {
        width: 25px;
        height: 25px;
        box-sizing: border-box;
        background-color: #bdbdbd;
        border: 3px outset #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
    }
    .cell.revealed {
        border: 1px solid #7b7b7b;
        background-color: #bdbdbd;
    }
    /* 숫자별 색상 (공식 지뢰찾기 기준) */
    .num-1 { color: blue; }
    .num-2 { color: green; }
    .num-3 { color: red; }
    .num-4 { color: darkblue; }
    .num-5 { color: darkred; }
    .num-6 { color: teal; }
    .num-7 { color: black; }
    .num-8 { color: gray; }
</style>
</head>
<body>

<div id="controls">
    <select id="difficulty" onchange="initGame()">
        <option value="beginner">초급 (9x9, 지뢰 10개)</option>
        <option value="intermediate">중급 (16x16, 지뢰 40개)</option>
        <option value="expert">고급 (30x16, 지뢰 99개)</option>
    </select>
    <button onclick="initGame()">🔄 재시작</button>
    <div id="status" style="font-weight: bold; font-size: 18px; color: red;"></div>
</div>

<div id="board"></div>

<script>
    const levels = {
        beginner: { rows: 9, cols: 9, mines: 10 },
        intermediate: { rows: 16, cols: 16, mines: 40 },
        expert: { rows: 16, cols: 30, mines: 99 } // 폭 30, 높이 16
    };

    let board = [];
    let currentLevel;
    let isGameOver = false;
    let isFirstClick = true;
    let flagsPlaced = 0;

    function initGame() {
        const diff = document.getElementById('difficulty').value;
        currentLevel = levels[diff];
        board = [];
        isGameOver = false;
        isFirstClick = true;
        flagsPlaced = 0;
        document.getElementById('status').innerText = `남은 지뢰: ${currentLevel.mines}`;
        
        const boardEl = document.getElementById('board');
        boardEl.style.gridTemplateColumns = `repeat(${currentLevel.cols}, 25px)`;
        boardEl.innerHTML = '';

        for (let r = 0; r < currentLevel.rows; r++) {
            let row = [];
            for (let c = 0; c < currentLevel.cols; c++) {
                let cell = {
                    r: r, c: c, isMine: false, isRevealed: false, isFlagged: false, neighborMines: 0
                };
                row.push(cell);

                let cellEl = document.createElement('div');
                cellEl.className = 'cell';
                cellEl.id = `cell-${r}-${c}`;
                
                // 마우스 이벤트 등록
                cellEl.addEventListener('mousedown', (e) => handleMouseDown(e, r, c));
                cellEl.addEventListener('contextmenu', (e) => { e.preventDefault(); }); // 기본 우클릭 메뉴 방지
                cellEl.addEventListener('dblclick', (e) => handleDoubleClick(r, c)); // 더블클릭으로 주변 열기(Chording)

                boardEl.appendChild(cellEl);
            }
            board.push(row);
        }
    }

    // 마우스 좌/우 클릭 처리
    function handleMouseDown(e, r, c) {
        if (isGameOver) return;
        // 우클릭 (버튼 2)
        if (e.button === 2) {
            toggleFlag(r, c);
        } 
        // 좌클릭 (버튼 0)
        else if (e.button === 0) {
            revealCell(r, c);
        }
    }

    // 구글 스타일: 첫 클릭 시 주변 8칸도 지뢰가 없도록 배치
    function placeMinesSafe(firstR, firstC) {
        let placed = 0;
        while (placed < currentLevel.mines) {
            let r = Math.floor(Math.random() * currentLevel.rows);
            let c = Math.floor(Math.random() * currentLevel.cols);
            
            // 첫 클릭 위치와 그 주변 8칸에는 지뢰 생성 안 함
            let isSafeZone = Math.abs(r - firstR) <= 1 && Math.abs(c - firstC) <= 1;
            
            if (!board[r][c].isMine && !isSafeZone) {
                board[r][c].isMine = true;
                placed++;
            }
        }
        calculateNumbers();
    }

    function calculateNumbers() {
        for (let r = 0; r < currentLevel.rows; r++) {
            for (let c = 0; c < currentLevel.cols; c++) {
                if (board[r][c].isMine) continue;
                let count = 0;
                for (let i = -1; i <= 1; i++) {
                    for (let j = -1; j <= 1; j++) {
                        let nr = r + i, nc = c + j;
                        if (nr >= 0 && nr < currentLevel.rows && nc >= 0 && nc < currentLevel.cols) {
                            if (board[nr][nc].isMine) count++;
                        }
                    }
                }
                board[r][c].neighborMines = count;
            }
        }
    }

    function revealCell(r, c) {
        if (r < 0 || r >= currentLevel.rows || c < 0 || c >= currentLevel.cols) return;
        let cell = board[r][c];
        if (cell.isRevealed || cell.isFlagged || isGameOver) return;

        if (isFirstClick) {
            placeMinesSafe(r, c);
            isFirstClick = false;
        }

        cell.isRevealed = true;
        let cellEl = document.getElementById(`cell-${r}-${c}`);
        cellEl.classList.add('revealed');

        if (cell.isMine) {
            cellEl.innerText = '💣';
            cellEl.style.backgroundColor = 'red';
            gameOver(false);
            return;
        }

        if (cell.neighborMines > 0) {
            cellEl.innerText = cell.neighborMines;
            cellEl.classList.add(`num-${cell.neighborMines}`);
        } else {
            // 빈 칸이면 주변 8칸 연쇄 오픈 (Flood Fill)
            for (let i = -1; i <= 1; i++) {
                for (let j = -1; j <= 1; j++) {
                    revealCell(r + i, c + j);
                }
            }
        }
        checkWin();
    }

    function toggleFlag(r, c) {
        let cell = board[r][c];
        if (cell.isRevealed || isGameOver) return;

        let cellEl = document.getElementById(`cell-${r}-${c}`);
        if (cell.isFlagged) {
            cell.isFlagged = false;
            cellEl.innerText = '';
            flagsPlaced--;
        } else {
            cell.isFlagged = true;
            cellEl.innerText = '🚩';
            flagsPlaced++;
        }
        document.getElementById('status').innerText = `남은 지뢰: ${currentLevel.mines - flagsPlaced}`;
    }

    // 더블클릭: 주변 지뢰 수와 깃발 수가 같으면 남은 칸 한 번에 오픈 (Chording)
    function handleDoubleClick(r, c) {
        if (isGameOver) return;
        let cell = board[r][c];
        if (!cell.isRevealed || cell.neighborMines === 0) return;

        let flagCount = 0;
        for (let i = -1; i <= 1; i++) {
            for (let j = -1; j <= 1; j++) {
                let nr = r + i, nc = c + j;
                if (nr >= 0 && nr < currentLevel.rows && nc >= 0 && nc < currentLevel.cols) {
                    if (board[nr][nc].isFlagged) flagCount++;
                }
            }
        }

        if (flagCount === cell.neighborMines) {
            for (let i = -1; i <= 1; i++) {
                for (let j = -1; j <= 1; j++) {
                    let nr = r + i, nc = c + j;
                    if (nr >= 0 && nr < currentLevel.rows && nc >= 0 && nc < currentLevel.cols) {
                        if (!board[nr][nc].isFlagged && !board[nr][nc].isRevealed) {
                            revealCell(nr, nc);
                        }
                    }
                }
            }
        }
    }

    function gameOver(win) {
        isGameOver = true;
        if (win) {
            document.getElementById('status').innerText = "🎉 승리했습니다! 🎉";
            document.getElementById('status').style.color = "blue";
        } else {
            document.getElementById('status').innerText = "💥 게임 오버! 💥";
            // 모든 지뢰 공개
            for (let r = 0; r < currentLevel.rows; r++) {
                for (let c = 0; c < currentLevel.cols; c++) {
                    if (board[r][c].isMine && !board[r][c].isFlagged) {
                        let el = document.getElementById(`cell-${r}-${c}`);
                        el.classList.add('revealed');
                        el.innerText = '💣';
                    }
                }
            }
        }
    }

    function checkWin() {
        let revealedCount = 0;
        for (let r = 0; r < currentLevel.rows; r++) {
            for (let c = 0; c < currentLevel.cols; c++) {
                if (board[r][c].isRevealed) revealedCount++;
            }
        }
        if (revealedCount === (currentLevel.rows * currentLevel.cols) - currentLevel.mines) {
            gameOver(true);
        }
    }

    // 초기 실행
    window.onload = initGame;
</script>
</body>
</html>
"""

# HTML을 스트림릿 화면에 꽉 차게 렌더링 (높이를 충분히 주어 짤림 방지)
components.html(minesweeper_html, height=800, scrolling=True)
