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
        margin: 0;
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
        font-weight: bold;
    }
    button:hover, select:hover { background-color: #e9ecef; }
    #btn-ranking { background-color: #ffca28; border-color: #ffb300; }
    #btn-ranking:hover { background-color: #ffb300; }

    .info-text { font-weight: bold; font-size: 18px; }
    #status { color: #d32f2f; min-width: 120px; text-align: center; }
    #timer { color: #1976d2; min-width: 100px; text-align: center; }

    #board {
        --cell-border: 3px; 
        display: grid;
        background-color: #9e9e9e; 
        border: 4px solid #808080;
        border-top-color: #ffffff;
        border-left-color: #ffffff;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    .cell {
        box-sizing: border-box;
        background-color: #c0c0c0; 
        border: var(--cell-border) outset #f4f4f4; 
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        cursor: pointer;
    }
    
    .cell.revealed {
        border: 1px solid #9e9e9e;
        background-color: #e8ecef; 
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.1); 
    }
    
    .num-1 { color: #0000ff; } .num-2 { color: #008000; } .num-3 { color: #ff0000; }
    .num-4 { color: #000080; } .num-5 { color: #800000; } .num-6 { color: #008080; }
    .num-7 { color: #000000; } .num-8 { color: #808080; }

    /* 모달 (팝업창) 디자인 */
    .modal-overlay {
        display: none; 
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        z-index: 1000;
        justify-content: center; align-items: center;
    }
    .modal-content {
        background-color: white; padding: 30px; border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        text-align: center; min-width: 400px; max-height: 80vh; overflow-y: auto;
    }
    .modal-content h2 { margin-top: 0; color: #333; }
    .modal-content input {
        width: 80%; padding: 10px; margin: 15px 0; font-size: 16px;
        border: 2px solid #ccc; border-radius: 5px; text-align: center;
    }
    .modal-btn { background-color: #1976d2; color: white; border: none; }
    .modal-btn:hover { background-color: #115293; }
    .close-btn { background-color: #d32f2f; color: white; border: none; margin-top: 20px; }
    .close-btn:hover { background-color: #9a0007; }

    /* 랭킹 탭 버튼 디자인 */
    .tab-container {
        display: flex; justify-content: center; gap: 10px; margin-bottom: 20px;
    }
    .tab-btn {
        padding: 8px 20px; border: none; border-radius: 5px; cursor: pointer;
        font-weight: bold; background-color: #e0e0e0; color: #333; transition: 0.2s;
    }
    .tab-btn:hover { background-color: #d5d5d5; }
    .tab-btn.active { background-color: #1976d2; color: white; } /* 선택된 탭 강조 */

    /* 랭킹 테이블 디자인 */
    table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
    th, td { border-bottom: 1px solid #ddd; padding: 10px 8px; text-align: center; }
    th { background-color: #f2f2f2; color: #333; font-size: 15px; }
    .rank-1 { font-weight: bold; color: #d4af37; background-color: #fffdf5; } 
    .rank-2 { font-weight: bold; color: #a0a0a0; background-color: #fafafa; } 
    .rank-3 { font-weight: bold; color: #cd7f32; background-color: #fffaf5; } 
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
    <button id="btn-ranking" onclick="showRanking()">🏆 랭킹 보기</button>
    <div id="status" class="info-text">🚩 남은 지뢰: 0</div>
    <div id="timer" class="info-text">⏱️ 0초</div>
</div>

<div id="board"></div>

<div id="name-modal" class="modal-overlay">
    <div class="modal-content">
        <h2>🎉 지뢰찾기 클리어! 🎉</h2>
        <p id="clear-record" class="info-text" style="color: #1976d2;"></p>
        <p>명예의 전당에 등록할 닉네임을 입력하세요!</p>
        <input type="text" id="player-name" placeholder="닉네임 (최대 10자)" maxlength="10">
        <br>
        <button class="modal-btn" onclick="saveScore()">랭킹 등록</button>
    </div>
</div>

<div id="ranking-modal" class="modal-overlay">
    <div class="modal-content">
        <h2>🏆 명예의 전당</h2>
        
        <div class="tab-container">
            <button id="tab-beginner" class="tab-btn" onclick="renderRankingTable('beginner')">초급</button>
            <button id="tab-intermediate" class="tab-btn" onclick="renderRankingTable('intermediate')">중급</button>
            <button id="tab-expert" class="tab-btn" onclick="renderRankingTable('expert')">고급</button>
        </div>

        <div id="ranking-boards"></div>
        <button class="close-btn" onclick="closeModal('ranking-modal')">닫기</button>
    </div>
</div>

<script>
    const levels = {
        beginner: { id: 'beginner', name: '초급', rows: 9, cols: 9, mines: 10, cellSize: 50 },       
        intermediate: { id: 'intermediate', name: '중급', rows: 16, cols: 16, mines: 40, cellSize: 35 }, 
        expert: { id: 'expert', name: '고급', rows: 16, cols: 30, mines: 99, cellSize: 35 } 
    };

    let board = [];
    let currentLevel;
    let isGameOver = false;
    let isFirstClick = true;
    let flagsPlaced = 0;
    let timerInterval = null;
    let seconds = 0;

    // --- 랭킹 시스템 로직 ---
    function getRanks() {
        let ranks = localStorage.getItem('minesweeper_ranks');
        if (ranks) return JSON.parse(ranks);
        return { beginner: [], intermediate: [], expert: [] };
    }

    function saveScore() {
        let name = document.getElementById('player-name').value.trim();
        if (!name) name = "이름없는고수";
        
        let ranks = getRanks();
        ranks[currentLevel.id].push({ name: name, time: seconds });
        ranks[currentLevel.id].sort((a, b) => a.time - b.time);
        ranks[currentLevel.id] = ranks[currentLevel.id].slice(0, 10);
        
        localStorage.setItem('minesweeper_ranks', JSON.stringify(ranks));
        
        closeModal('name-modal');
        showRanking(); 
    }

    // 랭킹 모달 열기 (기본값으로 현재 플레이 중인 난이도를 보여줌)
    function showRanking() {
        document.getElementById('ranking-modal').style.display = 'flex';
        renderRankingTable(currentLevel.id);
    }

    // 💡 선택한 난이도의 랭킹만 테이블로 그려주는 함수
    function renderRankingTable(diffId) {
        // 탭 버튼 활성화 디자인 처리
        ['beginner', 'intermediate', 'expert'].forEach(id => {
            document.getElementById(`tab-${id}`).classList.remove('active');
        });
        document.getElementById(`tab-${diffId}`).classList.add('active');

        let ranks = getRanks();
        let html = `<h3>[ ${levels[diffId].name} ]</h3>`;
        html += `<table><tr><th width="25%">순위</th><th width="45%">닉네임</th><th width="30%">기록</th></tr>`;
        
        let data = ranks[diffId];
        if (data.length === 0) {
            html += `<tr><td colspan="3" style="color:#777; padding: 20px;">아직 기록이 없습니다.<br>첫 번째 기록의 주인공이 되세요!</td></tr>`;
        } else {
            data.forEach((entry, idx) => {
                let rankClass = "";
                let medal = idx + 1;
                if (idx === 0) { rankClass = "rank-1"; medal = "🥇 1위"; }
                else if (idx === 1) { rankClass = "rank-2"; medal = "🥈 2위"; }
                else if (idx === 2) { rankClass = "rank-3"; medal = "🥉 3위"; }
                else { medal = `${idx + 1}위`; }
                
                html += `<tr class="${rankClass}">
                            <td>${medal}</td>
                            <td>${entry.name}</td>
                            <td>${entry.time}초</td>
                         </tr>`;
            });
        }
        html += `</table>`;
        
        document.getElementById('ranking-boards').innerHTML = html;
    }

    function closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }
    // ------------------------

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
            
            setTimeout(() => {
                document.getElementById('clear-record').innerText = `기록: ${seconds}초 (${currentLevel.name})`;
                document.getElementById('player-name').value = ''; 
                document.getElementById('name-modal').style.display = 'flex';
                document.getElementById('player-name').focus();
            }, 500);

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

components.html(minesweeper_html, height=1000, scrolling=True)
