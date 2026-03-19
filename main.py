import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="글로벌 랭킹 지뢰찾기", page_icon="🌍", layout="wide")

st.title("🌍 궁극의 지뢰찾기 (글로벌 랭킹 버전)")
st.markdown("**좌클릭:** 탐색 | **우클릭:** 깃발 | **좌+우 동시클릭:** 주변 열기 | **힌트 사용 시 기록 +15초 페널티!**")

minesweeper_html = """
<!DOCTYPE html>
<html>
<head>
<style>
    /* 🎨 테마 설정 (CSS 변수 활용) */
    :root {
        --bg-color: #f0f2f6; --panel-bg: white; --text-color: #333;
        --board-bg: #9e9e9e; --cell-bg: #c0c0c0; --cell-border-light: #ffffff;
        --cell-border-dark: #808080; --cell-revealed-bg: #e8ecef;
        --cell-revealed-border: #9e9e9e; --btn-bg: #ffffff; --btn-hover: #e9ecef;
    }
    body.theme-dark {
        --bg-color: #121212; --panel-bg: #2d2d2d; --text-color: #e0e0e0;
        --board-bg: #222; --cell-bg: #444; --cell-border-light: #666;
        --cell-border-dark: #111; --cell-revealed-bg: #333;
        --cell-revealed-border: #222; --btn-bg: #444; --btn-hover: #555;
    }
    body.theme-retro {
        --bg-color: #008080; --panel-bg: #c0c0c0; --text-color: #000000;
        --board-bg: #c0c0c0; --cell-bg: #c0c0c0; --cell-border-light: #ffffff;
        --cell-border-dark: #808080; --cell-revealed-bg: #c0c0c0;
        --cell-revealed-border: #808080; --btn-bg: #c0c0c0; --btn-hover: #d4d4d4;
        font-family: 'MS Sans Serif', Tahoma, sans-serif !important;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: var(--bg-color); color: var(--text-color);
        display: flex; flex-direction: column; align-items: center;
        padding: 20px; margin: 0; user-select: none;
        transition: background-color 0.3s, color 0.3s;
    }
    
    .toolbar {
        background-color: var(--panel-bg); padding: 15px 25px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 15px; 
        display: flex; gap: 15px; align-items: center; flex-wrap: wrap; justify-content: center;
    }
    select, button {
        padding: 8px 15px; font-size: 16px; font-weight: bold;
        border: 2px solid var(--cell-border-dark); border-radius: 5px;
        cursor: pointer; background-color: var(--btn-bg); color: var(--text-color);
        transition: 0.2s;
    }
    button:hover, select:hover { background-color: var(--btn-hover); }
    
    #btn-ranking { background-color: #ffca28; color: #333; border-color: #ffb300; }
    #btn-ranking:hover { background-color: #ffb300; }
    #btn-hint { background-color: #4caf50; color: white; border-color: #388e3c; }
    #btn-hint:hover { background-color: #43a047; }

    .info-text { font-weight: bold; font-size: 18px; }
    #status { color: #d32f2f; min-width: 120px; text-align: center; }
    #timer { color: #1976d2; min-width: 100px; text-align: center; }
    body.theme-dark #status { color: #ff6b6b; }
    body.theme-dark #timer { color: #64b5f6; }

    #board {
        --cell-border: 3px; display: grid; background-color: var(--board-bg); 
        border: 4px solid var(--cell-border-dark); border-top-color: var(--cell-border-light);
        border-left-color: var(--cell-border-light); box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    
    .cell {
        box-sizing: border-box; background-color: var(--cell-bg); 
        border-style: solid; border-width: var(--cell-border);
        border-color: var(--cell-border-light) var(--cell-border-dark) var(--cell-border-dark) var(--cell-border-light);
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; cursor: pointer; transition: background-color 0.1s;
    }
    .cell.revealed {
        border: 1px solid var(--cell-revealed-border);
        background-color: var(--cell-revealed-bg); box-shadow: inset 1px 1px 3px rgba(0,0,0,0.2); 
    }
    
    .num-1 { color: #0000ff; } .num-2 { color: #008000; } .num-3 { color: #ff0000; }
    .num-4 { color: #000080; } .num-5 { color: #800000; } .num-6 { color: #008080; }
    body.theme-dark .num-1 { color: #64b5f6; } body.theme-dark .num-2 { color: #81c784; } 
    body.theme-dark .num-3 { color: #e57373; } body.theme-dark .num-4 { color: #9575cd; }

    /* 모달 디자인 */
    .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); z-index: 1000; justify-content: center; align-items: center; }
    .modal-content { background-color: var(--panel-bg); color: var(--text-color); padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; min-width: 450px; }
    .modal-content input { width: 80%; padding: 10px; margin: 15px 0; font-size: 16px; border: 2px solid #ccc; border-radius: 5px; text-align: center; }
    .modal-btn { background-color: #1976d2; color: white; border: none; }
    .modal-btn:disabled { background-color: #999; cursor: not-allowed; }
    .close-btn { background-color: #d32f2f; color: white; border: none; margin-top: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border-bottom: 1px solid #777; padding: 10px; text-align: center; }
    
    .tab-container { display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; }
    .tab-btn { padding: 8px 16px; border: none; background-color: #888; color: white; }
    .tab-btn.active { background-color: #1976d2; }
    .reset-btn { background-color: #ffccbc; color: #d84315; margin-left: auto; }

    .confetti { position: fixed; z-index: 9999; pointer-events: none; }
</style>
</head>
<body class="theme-light">

<div class="toolbar">
    <select id="difficulty" onchange="initGame()">
        <option value="beginner">초급 (9x9)</option>
        <option value="intermediate">중급 (16x16)</option>
        <option value="expert">고급 (30x16)</option>
    </select>
    <button onclick="initGame()">🔄 재시작</button>
    <button id="btn-ranking" onclick="showRanking()">🌍 글로벌 랭킹</button>
    <div id="status" class="info-text">🚩 남은 지뢰: 0</div>
    <div id="timer" class="info-text">⏱️ 0초</div>
</div>

<div class="toolbar" style="padding: 10px 25px;">
    <select id="theme-selector" onchange="changeTheme()">
        <option value="theme-light">☀️ 라이트 모드</option>
        <option value="theme-dark">🌙 다크 모드</option>
        <option value="theme-retro">💻 레트로(Win98)</option>
    </select>
    <button id="btn-sound" onclick="toggleSound()">🔊 소리 켜짐</button>
    <button id="btn-hint" onclick="useHint()">💡 힌트 (+15초)</button>
</div>

<div id="board"></div>

<div id="name-modal" class="modal-overlay">
    <div class="modal-content">
        <h2>🎉 지뢰찾기 클리어! 🎉</h2>
        <p id="clear-record" class="info-text" style="color: #4caf50;"></p>
        <p>전 세계 명예의 전당에 등록할 닉네임을 입력하세요!</p>
        <input type="text" id="player-name" placeholder="닉네임 (최대 10자)" maxlength="10">
        <br>
        <button id="save-btn" class="modal-btn" onclick="saveScore()">랭킹 등록</button>
    </div>
</div>

<div id="ranking-modal" class="modal-overlay">
    <div class="modal-content">
        <h2>🌍 글로벌 명예의 전당</h2>
        <div class="tab-container">
            <button id="tab-beginner" class="tab-btn" onclick="renderRankingTable('beginner')">초급</button>
            <button id="tab-intermediate" class="tab-btn" onclick="renderRankingTable('intermediate')">중급</button>
            <button id="tab-expert" class="tab-btn" onclick="renderRankingTable('expert')">고급</button>
            <button class="tab-btn reset-btn" onclick="resetNickname()">👤 내 닉네임 초기화</button>
        </div>
        <div id="ranking-boards"></div>
        <button class="close-btn" onclick="closeModal('ranking-modal')">닫기</button>
    </div>
</div>

<script>
    // 💡 네가 발급받은 구글 앱스 스크립트 주소!
    const SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIhXW_fY1O0jZbPCj0-DFV9tO740ScI4fnHU4fs5wZez91UI64e_gUCEBxbAt9oFoL/exec";

    const levels = {
        beginner: { id: 'beginner', name: '초급', rows: 9, cols: 9, mines: 10, cellSize: 45 },       
        intermediate: { id: 'intermediate', name: '중급', rows: 16, cols: 16, mines: 40, cellSize: 35 }, 
        expert: { id: 'expert', name: '고급', rows: 16, cols: 30, mines: 99, cellSize: 35 } 
    };

    let board = []; let currentLevel; let isGameOver = false; let isFirstClick = true; 
    let flagsPlaced = 0; let timerInterval = null; let seconds = 0;
    let currentNickname = localStorage.getItem('minesweeper_nickname') || null;
    let audioCtx = null; let soundEnabled = true;
    let globalRanksCache = null;

    // --- 🌍 구글 스프레드시트 글로벌 랭킹 시스템 ---
    async function saveScore(autoName = null) {
        let name = autoName || document.getElementById('player-name').value.trim() || "이름없는고수";
        if (!autoName) {
            currentNickname = name;
            localStorage.setItem('minesweeper_nickname', name); // 닉네임만 브라우저에 저장
        }
        
        let saveBtn = document.getElementById('save-btn');
        saveBtn.innerText = "서버에 저장 중... 📡";
        saveBtn.disabled = true;

        try {
            // 구글 서버로 데이터 전송 (fetch)
            let url = `${SCRIPT_URL}?action=write&level=${currentLevel.id}&name=${encodeURIComponent(name)}&time=${seconds}`;
            await fetch(url);
        } catch (error) {
            console.error(error);
            alert("서버 연결에 실패했습니다. 구글 시트를 확인해주세요.");
        }
        
        saveBtn.innerText = "랭킹 등록";
        saveBtn.disabled = false;
        closeModal('name-modal'); 
        showRanking(); 
    }

    async function showRanking() { 
        document.getElementById('ranking-modal').style.display = 'flex'; 
        document.getElementById('ranking-boards').innerHTML = '<h3 style="margin:40px 0; color:#1976d2;">📡 전 세계 랭킹을 불러오는 중...</h3>';
        
        try {
            let response = await fetch(SCRIPT_URL);
            globalRanksCache = await response.json();
        } catch (error) {
            console.error(error);
            document.getElementById('ranking-boards').innerHTML = '<p style="color:red;">랭킹 데이터를 불러오지 못했습니다.</p>';
            return;
        }
        renderRankingTable(currentLevel.id);
    }

    function renderRankingTable(diffId) {
        ['beginner', 'intermediate', 'expert'].forEach(id => document.getElementById(`tab-${id}`).classList.remove('active'));
        document.getElementById(`tab-${diffId}`).classList.add('active');

        if (!globalRanksCache) return;
        let ranks = globalRanksCache[diffId] || [];
        
        let html = `<h3>[ ${levels[diffId].name} ]</h3><table><tr><th>순위</th><th>닉네임</th><th>기록</th></tr>`;
        
        if (ranks.length === 0) {
            html += `<tr><td colspan="3">아직 기록이 없습니다. 첫 1위의 주인공이 되어보세요!</td></tr>`;
        } else {
            ranks.forEach((entry, idx) => {
                let medal = idx === 0 ? "🥇 1위" : idx === 1 ? "🥈 2위" : idx === 2 ? "🥉 3위" : `${idx + 1}위`;
                let style = idx === 0 ? "font-weight:bold; color:#d4af37;" : "";
                let isMe = entry.name === currentNickname ? " (나)" : "";
                html += `<tr style="${style}"><td>${medal}</td><td>${entry.name}${isMe}</td><td>${entry.time}초</td></tr>`;
            });
        }
        document.getElementById('ranking-boards').innerHTML = html + `</table>`;
    }

    function resetNickname() { 
        currentNickname = null; 
        localStorage.removeItem('minesweeper_nickname');
        alert("내 닉네임이 초기화되었습니다. 다음 클리어 시 새로 입력할 수 있습니다."); 
    }

    // --- 기존 사운드 및 게임 기능 ---
    function toggleSound() {
        soundEnabled = !soundEnabled;
        document.getElementById('btn-sound').innerText = soundEnabled ? '🔊 소리 켜짐' : '🔇 소리 꺼짐';
        if (soundEnabled && !audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }

    function playSound(type) {
        if (!soundEnabled) return;
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
        osc.connect(gain); gain.connect(audioCtx.destination);
        let now = audioCtx.currentTime;

        if (type === 'reveal') {
            osc.type = 'sine'; osc.frequency.setValueAtTime(800, now);
            gain.gain.setValueAtTime(0.05, now); gain.exponentialRampToValueAtTime(0.001, now + 0.1);
            osc.start(now); osc.stop(now + 0.1);
        } else if (type === 'flag') {
            osc.type = 'square'; osc.frequency.setValueAtTime(400, now);
            gain.gain.setValueAtTime(0.05, now); gain.exponentialRampToValueAtTime(0.001, now + 0.1);
            osc.start(now); osc.stop(now + 0.1);
        } else if (type === 'bomb') {
            osc.type = 'sawtooth'; osc.frequency.setValueAtTime(150, now);
            osc.frequency.exponentialRampToValueAtTime(10, now + 0.5);
            gain.gain.setValueAtTime(0.2, now); gain.exponentialRampToValueAtTime(0.001, now + 0.5);
            osc.start(now); osc.stop(now + 0.5);
        } else if (type === 'win') {
            [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
                let o = audioCtx.createOscillator(); let g = audioCtx.createGain();
                o.type = 'sine'; o.frequency.value = freq;
                o.connect(g); g.connect(audioCtx.destination);
                g.gain.setValueAtTime(0.1, now + i*0.1); g.gain.exponentialRampToValueAtTime(0.001, now + i*0.1 + 0.3);
                o.start(now + i*0.1); o.stop(now + i*0.1 + 0.3);
            });
        }
    }

    function changeTheme() { document.body.className = document.getElementById('theme-selector').value; }

    function fireConfetti() {
        const emojis = ['🎉', '✨', '🏆', '🎊', '💣'];
        for (let i = 0; i < 60; i++) {
            let conf = document.createElement('div'); conf.className = 'confetti';
            conf.innerText = emojis[Math.floor(Math.random() * emojis.length)];
            conf.style.left = Math.random() * 100 + 'vw'; conf.style.top = '-50px';
            conf.style.fontSize = (Math.random() * 20 + 15) + 'px';
            conf.style.transition = 'transform 2.5s ease-in, top 2.5s ease-in, opacity 2.5s ease-in';
            document.body.appendChild(conf);
            setTimeout(() => { conf.style.top = '100vh'; conf.style.transform = `rotate(${Math.random() * 720}deg)`; conf.style.opacity = '0'; }, 50);
            setTimeout(() => conf.remove(), 2500);
        }
    }

    function useHint() {
        if (isGameOver || isFirstClick) { alert("게임을 시작한 후(첫 클릭 이후)에 힌트를 사용할 수 있습니다!"); return; }
        let safeCells = [];
        for (let r = 0; r < currentLevel.rows; r++) for (let c = 0; c < currentLevel.cols; c++) {
            if (!board[r][c].isMine && !board[r][c].isRevealed && !board[r][c].isFlagged) safeCells.push({r, c});
        }
        if (safeCells.length > 0) {
            let pick = safeCells[Math.floor(Math.random() * safeCells.length)];
            seconds += 15; document.getElementById('timer').innerText = `⏱️ ${seconds}초 (힌트 페널티!)`;
            let cellEl = document.getElementById(`cell-${pick.r}-${pick.c}`);
            cellEl.style.backgroundColor = '#ffeb3b'; playSound('reveal');
            setTimeout(() => { revealCell(pick.r, pick.c); }, 400);
        }
    }

    function closeModal(id) { document.getElementById(id).style.display = 'none'; }

    function initGame() {
        const diff = document.getElementById('difficulty').value;
        currentLevel = levels[diff]; board = []; isGameOver = false; isFirstClick = true; flagsPlaced = 0;
        stopTimer(); seconds = 0; document.getElementById('timer').innerText = `⏱️ 0초`;
        document.getElementById('status').innerText = `🚩 남은 지뢰: ${currentLevel.mines}`;
        
        const boardEl = document.getElementById('board');
        boardEl.style.gridTemplateColumns = `repeat(${currentLevel.cols}, ${currentLevel.cellSize}px)`;
        boardEl.style.setProperty('--cell-border', `${Math.max(2, Math.floor(currentLevel.cellSize * 0.12))}px`);
        boardEl.innerHTML = '';

        for (let r = 0; r < currentLevel.rows; r++) {
            let row = [];
            for (let c = 0; c < currentLevel.cols; c++) {
                let cell = { r, c, isMine: false, isRevealed: false, isFlagged: false, neighborMines: 0 }; row.push(cell);
                let cellEl = document.createElement('div'); cellEl.className = 'cell'; cellEl.id = `cell-${r}-${c}`;
                cellEl.style.width = cellEl.style.height = `${currentLevel.cellSize}px`;
                cellEl.style.fontSize = `${currentLevel.cellSize * 0.55}px`; 
                cellEl.addEventListener('mousedown', (e) => handleMouseDown(e, r, c));
                cellEl.addEventListener('contextmenu', (e) => e.preventDefault());
                boardEl.appendChild(cellEl);
            }
            board.push(row);
        }
    }

    function startTimer() {
        if (timerInterval !== null) return;
        if (soundEnabled && !audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        timerInterval = setInterval(() => { seconds++; document.getElementById('timer').innerText = `⏱️ ${seconds}초`; }, 1000);
    }
    function stopTimer() { if (timerInterval) clearInterval(timerInterval); timerInterval = null; }

    function handleMouseDown(e, r, c) {
        if (isGameOver) return;
        if (e.buttons === 3) { handleChording(r, c); return; }
        if (e.button === 2) { toggleFlag(r, c); } else if (e.button === 0) { revealCell(r, c); }
    }

    function placeMinesSafe(firstR, firstC) {
        let placed = 0;
        while (placed < currentLevel.mines) {
            let r = Math.floor(Math.random() * currentLevel.rows), c = Math.floor(Math.random() * currentLevel.cols);
            if (!board[r][c].isMine && (Math.abs(r - firstR) > 1 || Math.abs(c - firstC) > 1)) { board[r][c].isMine = true; placed++; }
        }
        for (let r = 0; r < currentLevel.rows; r++) for (let c = 0; c < currentLevel.cols; c++) {
            if (board[r][c].isMine) continue;
            let count = 0;
            for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) {
                let nr = r + i, nc = c + j;
                if (nr >= 0 && nr < currentLevel.rows && nc >= 0 && nc < currentLevel.cols && board[nr][nc].isMine) count++;
            }
            board[r][c].neighborMines = count;
        }
    }

    function revealCell(r, c) {
        if (r < 0 || r >= currentLevel.rows || c < 0 || c >= currentLevel.cols) return;
        let cell = board[r][c]; if (cell.isRevealed || cell.isFlagged || isGameOver) return;
        if (isFirstClick) { placeMinesSafe(r, c); startTimer(); isFirstClick = false; }
        
        cell.isRevealed = true; let cellEl = document.getElementById(`cell-${r}-${c}`);
        cellEl.classList.add('revealed'); cellEl.style.backgroundColor = ''; 

        if (cell.isMine) {
            playSound('bomb'); cellEl.innerText = '💣'; cellEl.style.backgroundColor = '#ff4d4d';
            gameOver(false); return;
        }

        playSound('reveal');
        if (cell.neighborMines > 0) {
            cellEl.innerText = cell.neighborMines; cellEl.classList.add(`num-${cell.neighborMines}`);
        } else {
            for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) revealCell(r + i, c + j);
        }
        checkWin();
    }

    function toggleFlag(r, c) {
        let cell = board[r][c]; if (cell.isRevealed || isGameOver) return;
        let cellEl = document.getElementById(`cell-${r}-${c}`);
        if (cell.isFlagged) { cell.isFlagged = false; cellEl.innerText = ''; flagsPlaced--; playSound('reveal'); } 
        else { cell.isFlagged = true; cellEl.innerText = '🚩'; flagsPlaced++; playSound('flag'); }
        document.getElementById('status').innerText = `🚩 남은 지뢰: ${currentLevel.mines - flagsPlaced}`;
    }

    function handleChording(r, c) {
        let cell = board[r][c]; if (isGameOver || !cell.isRevealed || cell.neighborMines === 0) return;
        let flagCount = 0;
        for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) {
            let nr = r + i, nc = c + j;
            if (nr >= 0 && nr < currentLevel.rows && nc >= 0 && nc < currentLevel.cols && board[nr][nc].isFlagged) flagCount++;
        }
        if (flagCount === cell.neighborMines) {
            for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) {
                let nr = r + i, nc = c + j;
                if (nr >= 0 && nr < currentLevel.rows && nc >= 0 && nc < currentLevel.cols && !board[nr][nc].isFlagged && !board[nr][nc].isRevealed) revealCell(nr, nc);
            }
        }
    }

    function gameOver(win) {
        isGameOver = true; stopTimer();
        if (win) {
            playSound('win'); fireConfetti();
            document.getElementById('status').innerText = "🎉 승리! 🎉";
            setTimeout(() => {
                if (currentNickname) saveScore(currentNickname); 
                else {
                    document.getElementById('clear-record').innerText = `기록: ${seconds}초`;
                    document.getElementById('player-name').value = ''; 
                    document.getElementById('name-modal').style.display = 'flex';
                }
            }, 1000);
        } else {
            for (let r = 0; r < currentLevel.rows; r++) for (let c = 0; c < currentLevel.cols; c++) {
                if (board[r][c].isMine && !board[r][c].isFlagged) {
                    let el = document.getElementById(`cell-${r}-${c}`); el.classList.add('revealed'); el.innerText = '💣';
                } else if (!board[r][c].isMine && board[r][c].isFlagged) document.getElementById(`cell-${r}-${c}`).innerText = '❌';
            }
        }
    }

    function checkWin() {
        let revealedCount = 0;
        for (let r = 0; r < currentLevel.rows; r++) for (let c = 0; c < currentLevel.cols; c++) if (board[r][c].isRevealed) revealedCount++;
        if (revealedCount === (currentLevel.rows * currentLevel.cols) - currentLevel.mines) gameOver(true);
    }

    window.onload = initGame;
</script>
</body>
</html>
"""

components.html(minesweeper_html, height=1050, scrolling=True)
