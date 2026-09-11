import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="블록 스나이퍼", page_icon="🎯", layout="centered")

st.title("🎯 블록 스나이퍼: 좀비 소탕 작전")
st.markdown("마인크래프트 감성의 저격 게임입니다! \n* **PC:** 마우스로 조준하고 **클릭**하여 사격! \n* **모바일:** 목표물을 화면에서 직접 **터치(탭)**하여 사격!")
st.markdown("---")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; background-color: #2c3e50; color: white; margin: 0; padding: 10px; touch-action: none; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
  
  /* 마인크래프트 느낌의 화면 테두리 */
  #game-container { position: relative; border: 8px solid #555; border-radius: 5px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); background-color: #87CEEB; }
  canvas { display: block; cursor: crosshair; }
  
  .ui-bar { width: 100%; display: flex; justify-content: space-between; position: absolute; top: 10px; padding: 0 20px; box-sizing: border-box; font-size: 20px; text-shadow: 2px 2px 0 #000; pointer-events: none; z-index: 10;}
  
  #game-over-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 20;}
  #game-over-text { color: #e74c3c; font-size: 40px; text-shadow: 3px 3px 0 #000; margin-bottom: 20px;}
  #final-score { font-size: 24px; color: #f1c40f; margin-bottom: 30px; text-shadow: 2px 2px 0 #000;}
  
  #btn-restart { padding: 15px 30px; font-size: 22px; font-weight: bold; background: #2ecc71; color: white; border: 4px solid #27ae60; border-radius: 0; cursor: pointer; text-transform: uppercase; font-family: 'Courier New', Courier, monospace;}
  #btn-restart:active { background: #27ae60; transform: scale(0.95); }
</style>
</head>
<body>

  <div id="game-container">
      <div class="ui-bar">
          <span id="score" style="color: #f1c40f;">🪙 점수: 0</span>
          <span id="timer" style="color: #ecf0f1;">⏱️ 60초</span>
      </div>
      <canvas id="gameCanvas" width="400" height="500"></canvas>
      
      <div id="game-over-screen">
          <div id="game-over-text">작전 종료!</div>
          <div id="final-score">총 처치: 0 마리</div>
          <button id="btn-restart" onclick="resetGame()">다시 플레이</button>
      </div>
  </div>

<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");

  let score = 0; let timeLeft = 60; let gameOver = false; 
  let lastTime = 0; let timerInterval;
  
  let targetX = canvas.width / 2; let targetY = canvas.height / 2;
  let recoilOffset = 0; // 사격 시 화면 흔들림(반동)

  let targets = [];
  let particles = [];

  // 마우스(조준점) 위치
  let mouseX = canvas.width / 2; let mouseY = canvas.height / 2;

  // 블록(복셀) 스타일 그리기 함수
  function drawBlock(x, y, w, h, color) {
      ctx.fillStyle = color;
      ctx.fillRect(x, y, w, h);
      // 블록 테두리 (마인크래프트 느낌)
      ctx.strokeStyle = "rgba(0,0,0,0.3)";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, w, h);
  }

  // 🟩 좀비(크리퍼 느낌) 그리기
  function drawZombie(t) {
      // 머리
      drawBlock(t.x, t.y, t.size, t.size, "#2ecc71");
      // 눈
      drawBlock(t.x + t.size*0.15, t.y + t.size*0.25, t.size*0.2, t.size*0.2, "#111");
      drawBlock(t.x + t.size*0.65, t.y + t.size*0.25, t.size*0.2, t.size*0.2, "#111");
      // 입 (일자)
      drawBlock(t.x + t.size*0.3, t.y + t.size*0.6, t.size*0.4, t.size*0.15, "#111");
      
      // 몸통
      drawBlock(t.x + t.size*0.1, t.y + t.size, t.size*0.8, t.size*1.2, "#3498db");
  }

  function spawnTarget() {
      if(targets.length < 4) { // 화면에 최대 4마리만
          let size = Math.random() * 20 + 30; // 30~50 크기 (원근감)
          targets.push({
              x: Math.random() * (canvas.width - size*2) + size,
              y: Math.random() * (canvas.height*0.5) + canvas.height*0.3, // 땅 부근에 소환
              size: size,
              life: Math.random() * 60 + 60, // 1~2초 뒤에 도망감
              speedX: (Math.random() - 0.5) * 3 // 좌우로 슬금슬금 이동
          });
      }
  }

  function shoot() {
      if(gameOver) return;
      
      recoilOffset = 15; // 총기 반동 이펙트
      
      // 총소리 및 타격 효과음 (화면 번쩍임)
      ctx.fillStyle = "rgba(255, 255, 0, 0.3)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      let hit = false;
      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i];
          // 타격 판정 (머리 또는 몸통 박스 안을 쐈는지)
          if (mouseX > t.x && mouseX < t.x + t.size &&
              mouseY > t.y && mouseY < t.y + t.size * 2.2) {
              
              // 헤드샷 판정 (머리 부분)
              if(mouseY < t.y + t.size) score += 2; // 헤드샷 2점!
              else score += 1; // 몸샷 1점

              createParticles(mouseX, mouseY, "#c0392b"); // 피 파편(빨간 블록)
              targets.splice(i, 1);
              document.getElementById("score").innerText = "🪙 점수: " + score;
              hit = true;
              break;
          }
      }
      
      if(!hit) {
          // 빗나갔을 때 벽 파편
          createParticles(mouseX, mouseY, "#7f8c8d");
      }
  }

  function createParticles(x, y, color) {
      for(let i=0; i<8; i++) {
          particles.push({
              x: x, y: y,
              vx: (Math.random() - 0.5) * 10,
              vy: (Math.random() - 0.5) * 10,
              size: Math.random() * 6 + 4,
              color: color,
              life: 15
          });
      }
  }

  // 배경(마인크래프트 초원) 그리기
  function drawBackground() {
      // 하늘
      ctx.fillStyle = "#87CEEB";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // 땅 (블록 느낌)
      ctx.fillStyle = "#27ae60"; // 잔디
      ctx.fillRect(0, canvas.height * 0.6, canvas.width, canvas.height * 0.4);
      ctx.fillStyle = "#8e44ad"; // 멀리 있는 산
      ctx.fillRect(50, canvas.height * 0.5, 100, canvas.height * 0.1);
      ctx.fillRect(200, canvas.height * 0.45, 150, canvas.height * 0.15);
  }

  // 🎯 스나이퍼 스코프 (조준경) 그리기
  function drawScope() {
      ctx.save();
      
      // 반동 적용
      let currentY = mouseY - recoilOffset;
      if(recoilOffset > 0) recoilOffset -= 1.5;

      // 화면 전체를 까맣게 덮기
      ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // 조준경 구멍 뚫기 (투명하게)
      ctx.globalCompositeOperation = "destination-out";
      ctx.beginPath();
      ctx.arc(mouseX, currentY, 120, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalCompositeOperation = "source-over";

      // 십자선 (크로스헤어)
      ctx.strokeStyle = "rgba(0, 255, 0, 0.7)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(mouseX - 120, currentY); ctx.lineTo(mouseX + 120, currentY);
      ctx.moveTo(mouseX, currentY - 120); ctx.lineTo(mouseX, currentY + 120);
      ctx.stroke();

      // 스코프 렌즈 눈금자 디테일
      ctx.strokeStyle = "rgba(255, 0, 0, 0.8)";
      ctx.beginPath();
      ctx.arc(mouseX, currentY, 2, 0, Math.PI*2); ctx.fill(); // 정중앙 레드닷
      for(let i=20; i<=100; i+=20) {
          ctx.moveTo(mouseX - 10, currentY + i); ctx.lineTo(mouseX + 10, currentY + i);
      }
      ctx.stroke();

      ctx.restore();
  }

  function update() {
      if(gameOver) return;

      // 타겟 업데이트
      if(Math.random() < 0.05) spawnTarget();

      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i];
          t.x += t.speedX;
          t.life--;
          
          // 화면 밖으로 나가거나 수명이 다하면 도망감 (사라짐)
          if(t.life <= 0 || t.x < 0 || t.x > canvas.width) {
              targets.splice(i, 1);
          }
      }

      // 파티클 업데이트
      for (let i = particles.length - 1; i >= 0; i--) {
          let p = particles[i];
          p.x += p.vx; p.y += p.vy;
          p.life--;
          if (p.life <= 0) particles.splice(i, 1);
      }
  }

  function gameLoop(timestamp) {
      if (gameOver) return;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      drawBackground();
      
      // 타겟(좀비) 그리기
      for (let t of targets) drawZombie(t);
      
      // 파티클(파편) 그리기
      for (let p of particles) {
          ctx.fillStyle = p.color;
          ctx.fillRect(p.x, p.y, p.size, p.size); // 네모난 파편
      }
      
      // 가장 위에 스코프 덮기
      drawScope();

      requestAnimationFrame(gameLoop);
  }

  // 입력 처리 (마우스 & 터치)
  canvas.addEventListener("mousemove", (e) => {
      let rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
  });

  canvas.addEventListener("mousedown", (e) => { shoot(); });

  // 모바일 터치 처리 (터치하는 순간 거기로 조준경이 이동하고 사격됨!)
  canvas.addEventListener("touchstart", (e) => {
      e.preventDefault();
      let rect = canvas.getBoundingClientRect();
      mouseX = e.touches[0].clientX - rect.left;
      mouseY = e.touches[0].clientY - rect.top;
      shoot();
  }, { passive: false });
  
  canvas.addEventListener("touchmove", (e) => {
      e.preventDefault();
      let rect = canvas.getBoundingClientRect();
      mouseX = e.touches[0].clientX - rect.left;
      mouseY = e.touches[0].clientY - rect.top;
  }, { passive: false });

  // 타이머 로직
  function startTimer() {
      timerInterval = setInterval(() => {
          timeLeft--;
          document.getElementById("timer").innerText = "⏱️ " + timeLeft + "초";
          if(timeLeft <= 0) {
              clearInterval(timerInterval);
              endGame();
          }
      }, 1000);
  }

  function endGame() {
      gameOver = true;
      document.getElementById("game-over-screen").style.display = "flex";
      document.getElementById("final-score").innerText = "총 점수: " + score + " 점";
  }

  function resetGame() {
      score = 0; timeLeft = 60; gameOver = false; targets = []; particles = [];
      document.getElementById("score").innerText = "🪙 점수: 0";
      document.getElementById("timer").innerText = "⏱️ 60초";
      document.getElementById("game-over-screen").style.display = "none";
      clearInterval(timerInterval);
      startTimer();
      gameLoop();
  }

  resetGame();
</script>
</body>
</html>
"""

components.html(game_html, height=600)
