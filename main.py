import streamlit as st
import streamlit.components.v1 as components

# --- 페이지 설정 ---
st.set_page_config(page_title="클래식 지뢰찾기", page_icon="💣", layout="wide")

st.title("💣 리얼 클래식 지뢰찾기")
st.markdown("**좌클릭:** 탐색 | **우클릭:** 깃발 꽂기 | **좌+우 동시클릭(양클릭):** 주변 8칸 한 번에 열기")

# --- HTML/JS/CSS 지뢰찾기 구현 ---
minesweeper_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f0f2f6; 
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        user-select: none;
    }
    
    #controls {
        background-color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        display: flex;
        gap: 20px;
        align-items: center;
    }
    select, button {
        padding: 8px 15px;
        font-size: 16px;
        border: 1px solid #ccc;
        border-radius: 5px;
        cursor: pointer;
        background-color: #ffffff;
        transition: 0.2s;
    }
    button:hover, select:hover {
        background-color: #e9ecef;
    }
    .info-text {
        font-weight: bold;
        font-size: 18px;
    }
    #status { color: #d32f2f; min-width: 120px; text-align: center; }
    #timer { color: #1976d2; min-width: 100px; text-align: center; }

    #board {
        /* JS에서 테두리 두께를 조절할 CSS 변수 세팅 */
        --cell-border: 3px; 
        
        display: grid;
        background-color: #9e9e9e; 
        border: 4px solid #808080;
        border-top-color: #ffffff;
        border-left-color: #ffffff;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    /* 🧱 안 열린 블럭: 동적 테두리 두께 적용 */
    .cell {
        box-sizing: border-box;
        background-color: #c0c0c0; 
        border: var(--cell-border) outset #f4f4f4; /* 👈 난이도마다 자동으로 테두리가 굵어짐! */
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        cursor: pointer;
    }
    
    /* 🕳️ 열린 바닥: 파인 느낌 */
    .cell.revealed {
        border: 1px solid #9e9e9e;
        background-color: #e8ecef; 
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.1); 
    }
    
    /* 숫자별 색상 */
    .num-1 { color: #0000ff; }
    .num-2 { color: #008000; }
    .num-3 { color: #ff0000; }
    .num-4 { color: #000080; }
    .num-5 { color: #800000; }
    .num-6 { color: #008080; }
    .num-7 { color: #000000; }
    .num-8 { color: #808080; }
</style>
</head>
<body>

<div id="controls">
    <select id="difficulty" onchange="initGame()">
        <option value="beginner">초급 (9x9)</option>
        <option value="intermediate">중급 (16x16)</option>
        <option value="expert">고급 (30x16)</option>
    </select>
    <button onclick="initGame()">🔄 재시작</button>
    <div id="status" class="info-text">🚩 남은 지뢰: 0</div>
    <div id="timer" class="info-text">⏱️ 0초</div>
</div>

<div id="board"></div>

<script>
    const levels = {
        beginner: { rows: 9, cols: 9, mines: 10, cellSize: 50 },       
        intermediate: { rows: 16, cols: 16, mines: 40, cellSize: 35 }, 
        expert: { rows: 16, cols: 30, mines: 99, cellSize: 25 }        
    };

    let board = [];
    let currentLevel;
    let isGameOver = false;
    let isFirstClick = true;
    let flagsPlaced = 0;
    
    let timerInterval = null;
    let seconds = 0;

    function initGame() {
        const diff = document.getElementById('difficulty').value;
        currentLevel = levels[diff];
        board = [];
        isGameOver = false;
        isFirstClick = true;
        flagsPlaced = 0;
        
        stopTimer();
        seconds = 0;
        document.getElementById('timer').innerText = `⏱️ 0초`;
        
        document.getElementById('status').innerText = `🚩 남은 지뢰: ${currentLevel.mines}`;
        document.getElementById('status').style.color = "#d32f2f";
        
        const boardEl = document.getElementById('board');
        boardEl.style.gridTemplateColumns = `repeat(${currentLevel.cols}, ${currentLevel.cellSize}px)`;
        
        // 💡 핵심: 블럭 크기의 약 12% 비율로 테두리 두께를 동적으로 설정!
        const borderSize = Math.max(2, Math.floor(currentLevel.cellSize * 0.12));
        boardEl.style.setProperty('--cell-border', `${borderSize}px`);
        
        boardEl.innerHTML = '';

        for (let r = 0; r < currentLevel.rows; r++) {
            let row = [];
            for (let c = 0; c < currentLevel.cols; c++) {
                let cell = { r: r, c: c, isMine: false, isRevealed: false, isFlagged: false, neighborMines: 0 };
                row.push(cell);

                let cellEl = document.createElement('div');
                cellEl.className = 'cell';
                cellEl.id = `cell-${r}-${c}`;
                
                cellEl.style.width = `${currentLevel.cellSize}px`;
                cellEl.style.height = `${currentLevel.cellSize}px`;
                cellEl.style.fontSize = `${currentLevel.cellSize * 0.55}px`; 
                
                cellEl.addEventListener('mousedown', (e) => handleMouseDown(e, r, c));
                cellEl.addEventListener('contextmenu', (e) => { e.preventDefault(); });

                boardEl.appendChild(cellEl);
            }
            board.push(row);
        }
    }

    function startTimer() {
        if (timerInterval !== null) return;
        timerInterval = setInterval(() => {
            seconds++;
            document.getElementById('timer').innerText = `⏱️ ${seconds}초`;
        }, 1000);
    }

    function stopTimer() {
        if (timerInterval !== null) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    function handleMouseDown(e, r, c) {
        if (isGameOver) return;
        
        if (e.buttons === 3) {
            handleChording(r, c);
            return;
        }

        if (e.button === 2) {
            toggleFlag(r, c);
        } else if (e.button === 0) {
            revealCell(r, c);
        }
    }

    function placeMinesSafe(firstR, firstC) {
        let placed = 0;
        while (placed < currentLevel.mines) {
            let r = Math.floor(Math.random() * currentLevel.rows);
            let c = Math.floor(Math.random() * currentLevel.cols);
            
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
            startTimer();
            isFirstClick = false;
        }

        cell.isRevealed = true;
        let cellEl = document.getElementById(`cell-${r}-${c}`);
        cellEl.classList.add('revealed');

        if (cell.isMine) {
            cellEl.innerText = '💣';
            cellEl.style.backgroundColor = '#ff4d4d';
            gameOver(false);
            return;
        }

        if (cell.neighborMines > 0) {
            cellEl.innerText = cell.neighborMines;
            cellEl.classList.add(`num-${cell.neighborMines}`);
        } else {
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
        document.getElementById('status').innerText = `🚩 남은 지뢰: ${currentLevel.mines - flagsPlaced}`;
    }

    function handleChording(r, c) {
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
        stopTimer();
        
        if (win) {
            document.getElementById('status').innerText = "🎉 승리! 🎉";
            document.getElementById('status').style.color = "#1976d2";
        } else {
            document.getElementById('status').innerText = "💥 게임 오버! 💥";
            document.getElementById('status').style.color = "red";
            
            for (let r = 0; r < currentLevel.rows; r++) {
                for (let c = 0; c < currentLevel.cols; c++) {
                    if (board[r][c].isMine && !board[r][c].isFlagged) {
                        let el = document.getElementById(`cell-${r}-${c}`);
                        el.classList.add('revealed');
                        el.innerText = '💣';
                    } else if (!board[r][c].isMine && board[r][c].isFlagged) {
                        let el = document.getElementById(`cell-${r}-${c}`);
                        el.innerText = '❌';
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

    window.onload = initGame;
</script>
</body>
</html>
"""

components.html(minesweeper_html, height=850, scrolling=True)
