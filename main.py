function handleInteraction(e, r, c) {
        if (isGameOver) return;
        
        // 🚨 핵심 포인트: 팝업 메뉴나 버튼 자체를 터치/클릭한 거라면 이벤트가 셀로 전달되는 걸 막음
        if (e.target.closest('.mobile-menu')) {
            e.stopPropagation();
            return; 
        }

        // PC 모드일 때
        if (!isMobileMode) {
            if (e.buttons === 3) { handleChording(r, c); return; } 
            if (e.button === 2) { toggleFlag(r, c); } 
            else if (e.button === 0) { revealCell(r, c); }
            return;
        }

        // 📱 모바일 모드일 때 (좌클릭/터치만 반응)
        if (e.button === 0 || e.type === 'touchstart') {
            let cell = board[r][c];
            if (cell.isRevealed) return;

            // 이미 열려있는 메뉴 닫기
            let existingMenu = document.getElementById('mobile-menu-popup');
            if (existingMenu) {
                let isSameCell = activeMenuCell && activeMenuCell.r === r && activeMenuCell.c === c;
                existingMenu.remove(); activeMenuCell = null;
                if (isSameCell) return; // 같은 칸을 누르면 메뉴 닫기만 함
            }

            // 팝업 메뉴 생성
            let menu = document.createElement('div');
            menu.id = 'mobile-menu-popup'; menu.className = 'mobile-menu';
            
            // 메뉴 창의 빈 공간을 눌러도 메뉴가 닫히지 않게 이벤트 전파 차단
            menu.onmousedown = (ev) => ev.stopPropagation();
            menu.ontouchstart = (ev) => ev.stopPropagation();
            
            let btnDig = document.createElement('button');
            btnDig.className = 'mobile-btn'; btnDig.innerText = '⛏️';
            // onclick 대신 onpointerdown을 써서 터치/클릭 즉시 반응하도록 수정!
            btnDig.onpointerdown = (ev) => { 
                ev.stopPropagation(); ev.preventDefault(); 
                closeMobileMenu(); revealCell(r, c); 
            };
            
            let btnFlag = document.createElement('button');
            btnFlag.className = 'mobile-btn'; btnFlag.innerText = '🚩';
            btnFlag.onpointerdown = (ev) => { 
                ev.stopPropagation(); ev.preventDefault(); 
                closeMobileMenu(); toggleFlag(r, c); 
            };

            menu.appendChild(btnDig); menu.appendChild(btnFlag);
            
            let cellEl = document.getElementById(`cell-${r}-${c}`);
            cellEl.appendChild(menu);
            activeMenuCell = {r, c};
        }
    }
