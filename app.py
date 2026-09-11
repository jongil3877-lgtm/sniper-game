import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="블록 스나이퍼", page_icon="🎯", layout="centered")

st.title("🎯 블록 스나이퍼: 픽셀 좀비 소탕")
st.markdown("**[조작법]**\n* 📱 **스마트폰:** 화면을 **꾹 눌러서 조준**하고, **손가락을 떼면 발사**합니다!\n* 💻 **PC:** 마우스로 조준하고 **클릭**하여 사격합니다!\n* **꿀팁:** 머리(헤드샷)를 맞추면 2점입니다!")
st.markdown("---")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; background-color: #2c3e50; color: white; margin: 0; padding: 10px; touch-action: none; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
  
  #game-container { position: relative; border: 8px solid #555; border-radius: 5px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); background-color: #87CEEB; overflow: hidden; width: 350px; height: 500px;}
  canvas { display: block; cursor: crosshair; }
  
  .ui-bar { width: 100%; display: flex; justify-content: space-between; position: absolute; top: 10px; padding: 0 15px; box-sizing: border-box; font-size: 18px; text-shadow: 2px 2px 0 #000; pointer-events: none; z-index: 10;}
  
  #game-over-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 20;}
  #game-over-text { color: #e74c3c; font-size: 36px; text-shadow: 3px 3px 0 #000; margin-bottom: 15px;}
  #final-score { font-size: 22px; color: #f1c40f; margin-bottom: 25px; text-shadow: 2px 2px 0 #000;}
  
  #btn-restart { padding: 12px 24px; font-size: 20px; font-weight: bold; background: #2ecc71; color: white; border: 4px solid #27ae60; border-radius: 0; cursor: pointer; font-family: 'Courier New', Courier, monospace;}
  #btn-restart:active { transform: scale(0.95); }
</style>
</head>
<body>

  <div id="game-container">
      <div class="ui-bar">
          <span id="score" style="color: #f1c40f;">🪙 점수: 0</span>
          <span id="timer" style="color: #ecf0f1;">⏱️ 60초</span>
      </div>
      <canvas id="gameCanvas" width="350" height="500"></canvas>
      
      <div id="game-over-screen">
          <div id="game-over-text">MISSION END</div>
          <div id="final-score">총 획득: 0 점</div>
          <button id="btn-restart" onclick="resetGame()">다시 작전 투입</button>
      </div>
  </div>

<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");

  let score = 0; let timeLeft = 60; let gameOver = false; 
  let timerInterval; let frameCount = 0;
  
  let recoilOffset = 0; 
  let targets = []; let particles = [];

  let mouseX = canvas.width / 2; let mouseY = canvas.height / 2;
  let isAimingMobile = false; // 모바일 조준 상태

  function drawBlock(x, y, w, h, color) {
      ctx.fillStyle = color; ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = "rgba(0,0,0,0.4)"; ctx.lineWidth = 1.5; ctx.strokeRect(x, y, w, h);
  }

  // 🧟 좀비 그리기 (걷는 애니메이션 추가)
  function drawZombie(t) {
      // 머리
      drawBlock(t.x, t.y, t.size, t.size, "#2ecc71");
      drawBlock(t.x + t.size*0.15, t.y + t.size*0.25, t.size*0.2, t.size*0.2, "#111"); // 눈
      drawBlock(t.x + t.size*0.65, t.y + t.size*0.25, t.size*0.2, t.size*0.2, "#111"); // 눈
      drawBlock(t.x + t.size*0.3, t.y + t.size*0.6, t.size*0.4, t.size*0.15, "#111"); // 입
      
      // 몸통
      drawBlock(t.x + t.size*0.1, t.y + t.size, t.size*0.8, t.size*1.2, "#3498db");

      // 다리 걷기 애니메이션 (sin 그래프 활용)
      let legOffset = Math.sin(frameCount * 0.3) * (t.size*0.2);
      drawBlock(t.x + t.size*0.1, t.y + t.size*2.2 + legOffset, t.size*0.35, t.size*0.7, "#2c3e50");
      drawBlock(t.x + t.size*0.55, t.y + t.size*2.2 - legOffset, t.size*0.35, t.size*0.7, "#2c3e50");
  }

  // 🦅 날아다니는 돌연변이 새 그리기
  function drawBird(t) {
      // 몸통
      drawBlock(t.x, t.y, t.size, t.size*0.6, "#e67e22");
      drawBlock(t.x + (t.speedX > 0 ? t.size : -t.size*0.2), t.y + t.size*0.1, t.size*0.2, t.size*0.2, "#000"); // 부리

      // 날개 펄럭임 애니메이션
      let flap = (frameCount % 10 < 5) ? -t.size*0.4 : t.size*0.4;
      drawBlock(t.x + t.size*0.3, t.y + flap, t.size*0.4, t.size*0.2, "#d35400");
  }

  // 적 소환
  function spawnTarget() {
      if(targets.length < 5) { 
          let isBird = Math.random() < 0.4; // 40% 확률로 새
          let size = Math.random() * 15 + 20; 
          
          let yPos = isBird ? (Math.random() * (canvas.height*0.3) + 30) : (Math.random() * (canvas.height*0.2) + canvas.height*0.5);
          let speedX = (Math.random() * 2 + 1) * (Math.random() > 0.5 ? 1 : -1);
          
          targets.push({
              type: isBird ? 'bird' : 'zombie',
              x: speedX > 0 ? -40 : canvas.width + 40, // 화면 밖에서 등장
              y: yPos,
              baseY: yPos, // 새의 물결 비행을 위한 기준점
              size: size,
              speedX: isBird ? speedX * 1.5 : speedX, // 새는 더 빠름
              offset: Math.random() * 100 // 애니메이션 오프셋
          });
      }
  }

  // 💥 사격 판정 로직
  function shoot() {
      if(gameOver) return;
      recoilOffset = 20; 
      
      // 화면 번쩍!
      ctx.fillStyle = "rgba(255, 255, 0, 0.4)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      let hit = false;
      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i];
          let tHeight = t.type === 'zombie' ? t.size * 2.8 : t.size;
          
          // 조준점이 몬스터 사각형 안에 들어왔는지 확인 (스마트폰 편의를 위해 판정 범위를 10px 넓힘)
          if (mouseX > t.x - 10 && mouseX < t.x + t.size + 10 &&
              mouseY > t.y - 10 && mouseY < t.y + tHeight + 10) {
              
              if(t.type === 'zombie' && mouseY < t.y + t.size + 5) {
                  score += 2; // 헤드샷!
                  createParticles(mouseX, mouseY, "#FF0000"); // 빨간 피
              } else {
                  score += 1; // 몸샷 (새는 무조건 1점)
                  createParticles(mouseX, mouseY, t.type === 'zombie' ? "#3498db" : "#e67e22"); 
              }

              targets.splice(i, 1);
              document.getElementById("score").innerText = "🪙 점수: " + score;
              hit = true; break;
          }
      }
      if(!hit) createParticles(mouseX, mouseY, "#7f8c8d"); // 빗맞으면 흙먼지
  }

  function createParticles(x, y, color) {
      for(let i=0; i<12; i++) {
          particles.push({
              x: x, y: y,
              vx: (Math.random() - 0.5) * 12, vy: (Math.random() - 0.5) * 12,
              size: Math.random() * 5 + 3, color: color, life: 20
          });
      }
  }

  function drawBackground() {
      ctx.fillStyle = "#87CEEB"; ctx.fillRect(0, 0, canvas.width, canvas.height); // 하늘
      ctx.fillStyle = "#27ae60"; ctx.fillRect(0, canvas.height * 0.5, canvas.width, canvas.height * 0.5); // 잔디밭
      
      // 산맥
      ctx.fillStyle = "#2c3e50";
      ctx.beginPath(); ctx.moveTo(0, canvas.height*0.5); ctx.lineTo(80, canvas.height*0.35); ctx.lineTo(160, canvas.height*0.5); ctx.fill();
      ctx.fillStyle = "#34495e";
      ctx.beginPath(); ctx.moveTo(120, canvas.height*0.5); ctx.lineTo(240, canvas.height*0.3); ctx.lineTo(360, canvas.height*0.5); ctx.fill();
  }

  function drawScope() {
      ctx.save();
      let currentY = mouseY - recoilOffset;
      if(recoilOffset > 0) recoilOffset -= 2; // 반동 회복

      // 어두운 렌즈 밖 화면
      ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // 구멍 뚫기
      ctx.globalCompositeOperation = "destination-out";
      ctx.beginPath(); ctx.arc(mouseX, currentY, 100, 0, Math.PI * 2); ctx.fill();
      ctx.globalCompositeOperation = "source-over";

      // 십자선 (빨간색)
      ctx.strokeStyle = "rgba(255, 0, 0, 0.8)"; ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(mouseX - 100, currentY); ctx.lineTo(mouseX + 100, currentY);
      ctx.moveTo(mouseX, currentY - 100); ctx.lineTo(mouseX, currentY + 100);
      ctx.stroke();

      // 스코프 눈금
      ctx.beginPath(); ctx.arc(mouseX, currentY, 3, 0, Math.PI*2); ctx.fill();
      for(let i=20; i<=80; i+=20) { ctx.moveTo(mouseX - 8, currentY + i); ctx.lineTo(mouseX + 8, currentY + i); }
      ctx.stroke();

      ctx.restore();
  }

  // ★ 아까 빼먹었던 그 핵심 스위치입니다!
  function update() {
      frameCount++;
      if(Math.random() < 0.03) spawnTarget(); // 적 생성

      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i];
          t.x += t.speedX;
          if(t.type === 'bird') t.y = t.baseY + Math.sin(frameCount * 0.1 + t.offset) * 30; // 새는 물결 비행
          
          if(t.x < -60 || t.x > canvas.width + 60) targets.splice(i, 1); // 화면 밖으로 나가면 삭제
      }

      for (let i = particles.length - 1; i >= 0; i--) {
          let p = particles[i];
          p.x += p.vx; p.y += p.vy; p.life--;
          if (p.life <= 0) particles.splice(i, 1);
      }
  }

  function gameLoop() {
      if (gameOver) return;
      
      update(); // 데이터 업데이트
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawBackground();
      
      for (let t of targets) {
          if(t.type === 'zombie') drawZombie(t);
          else drawBird(t);
      }
      
      for (let p of particles) {
          ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, p.size, p.size);
      }
      
      drawScope(); // 제일 위에 조준경 그리기

      requestAnimationFrame(gameLoop);
  }

  // --- PC 마우스 조작 ---
  canvas.addEventListener("mousemove", (e) => {
      let rect = canvas.getBoundingClientRect(); mouseX = e.clientX - rect.left; mouseY = e.clientY - rect.top;
  });
  canvas.addEventListener("mousedown", () => shoot());

  // --- 모바일 터치 조작 (꾹 눌러서 이동, 떼면 발사) ---
  canvas.addEventListener("touchstart", (e) => {
      e.preventDefault(); isAimingMobile = true;
      let rect = canvas.getBoundingClientRect(); mouseX = e.touches[0].clientX - rect.left; mouseY = e.touches[0].clientY - rect.top;
  }, { passive: false });
  
  canvas.addEventListener("touchmove", (e) => {
      e.preventDefault();
      let rect = canvas.getBoundingClientRect(); mouseX = e.touches[0].clientX - rect.left; mouseY = e.touches[0].clientY - rect.top;
  }, { passive: false });

  canvas.addEventListener("touchend", (e) => {
      e.preventDefault();
      if(isAimingMobile) { shoot(); isAimingMobile = false; }
  }, { passive: false });

  // 타이머 로직
  function startTimer() {
      timerInterval = setInterval(() => {
          timeLeft--; document.getElementById("timer").innerText = "⏱️ " + timeLeft + "초";
          if(timeLeft <= 0) { clearInterval(timerInterval); endGame(); }
      }, 1000);
  }

  function endGame() {
      gameOver = true;
      document.getElementById("game-over-screen").style.display = "flex";
      document.getElementById("final-score").innerText = "최종 점수: " + score + " 점";
  }

  function resetGame() {
      score = 0; timeLeft = 60; gameOver = false; targets = []; particles = []; frameCount = 0;
      document.getElementById("score").innerText = "🪙 점수: 0";
      document.getElementById("timer").innerText = "⏱️ 60초";
      document.getElementById("game-over-screen").style.display = "none";
      clearInterval(timerInterval); startTimer(); gameLoop();
  }

  resetGame();
</script>
</body>
</html>
"""

components.html(game_html, height=600)
