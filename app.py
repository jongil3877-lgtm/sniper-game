import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="블록 스나이퍼", page_icon="🎯", layout="centered")

st.title("🎯 블록 스나이퍼: 픽셀 좀비 소탕")
st.markdown("**[조작법]**\n* 📱 **스마트폰:** 화면을 **꾹 눌러서 조준**하고, **손가락을 떼면 발사!**\n* 💻 **PC:** 마우스로 조준하고 **클릭**하여 사격!\n* **꿀팁:** 초록색 머리(헤드샷)를 쏘면 2점입니다!")
st.markdown("---")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; background-color: #2c3e50; color: white; margin: 0; padding: 10px; touch-action: none; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
  
  #game-container { position: relative; border: 8px solid #333; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); background-color: #87CEEB; overflow: hidden; width: 350px; height: 500px;}
  canvas { display: block; cursor: crosshair; }
  
  .ui-bar { width: 100%; display: flex; justify-content: space-between; position: absolute; top: 10px; padding: 0 15px; box-sizing: border-box; font-size: 20px; text-shadow: 2px 2px 0 #000; pointer-events: none; z-index: 10;}
  
  #game-over-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 20;}
  #game-over-text { color: #e74c3c; font-size: 36px; text-shadow: 3px 3px 0 #000; margin-bottom: 15px;}
  #final-score { font-size: 24px; color: #f1c40f; margin-bottom: 25px; text-shadow: 2px 2px 0 #000;}
  
  #btn-restart { padding: 12px 24px; font-size: 22px; font-weight: bold; background: #2ecc71; color: white; border: 4px solid #27ae60; border-radius: 5px; cursor: pointer; font-family: 'Courier New', Courier, monospace;}
  #btn-restart:active { transform: scale(0.95); }
</style>
</head>
<body>

  <div id="game-container">
      <div class="ui-bar">
          <span id="score" style="color: #f1c40f;">🪙 0점</span>
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
  let isAimingMobile = false; 

  function drawBlock(x, y, w, h, color) {
      ctx.fillStyle = color; ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = "rgba(0,0,0,0.5)"; ctx.lineWidth = 1.5; ctx.strokeRect(x, y, w, h);
  }

  // 🧟 좀비 그리기 (크기 키움)
  function drawZombie(t) {
      // 머리
      drawBlock(t.x, t.y, t.size, t.size, "#2ecc71");
      drawBlock(t.x + t.size*0.15, t.y + t.size*0.25, t.size*0.2, t.size*0.2, "#111"); 
      drawBlock(t.x + t.size*0.65, t.y + t.size*0.25, t.size*0.2, t.size*0.2, "#111"); 
      drawBlock(t.x + t.size*0.3, t.y + t.size*0.6, t.size*0.4, t.size*0.15, "#111"); 
      
      // 몸통
      drawBlock(t.x + t.size*0.1, t.y + t.size, t.size*0.8, t.size*1.2, "#3498db");

      // 걷기 애니메이션
      let legOffset = Math.sin(frameCount * 0.3) * (t.size*0.2);
      drawBlock(t.x + t.size*0.1, t.y + t.size*2.2 + legOffset, t.size*0.35, t.size*0.7, "#2c3e50");
      drawBlock(t.x + t.size*0.55, t.y + t.size*2.2 - legOffset, t.size*0.35, t.size*0.7, "#2c3e50");
  }

  // 🦅 돌연변이 새 그리기
  function drawBird(t) {
      drawBlock(t.x, t.y, t.size, t.size*0.6, "#e67e22"); // 몸통
      drawBlock(t.x + (t.speedX > 0 ? t.size : -t.size*0.2), t.y + t.size*0.1, t.size*0.2, t.size*0.2, "#111"); // 부리

      let flap = (frameCount % 10 < 5) ? -t.size*0.4 : t.size*0.4;
      drawBlock(t.x + t.size*0.3, t.y + flap, t.size*0.4, t.size*0.2, "#d35400"); // 날개
  }

  function spawnTarget() {
      if(targets.length < 5) { 
          let isBird = Math.random() < 0.4; 
          let size = Math.random() * 20 + 25; // ★ 타겟 크기 대폭 확장! (25~45px)
          
          let yPos = isBird ? (Math.random() * (canvas.height*0.3) + 30) : (Math.random() * (canvas.height*0.15) + canvas.height*0.55);
          let speedX = (Math.random() * 2 + 1) * (Math.random() > 0.5 ? 1 : -1);
          
          targets.push({
              type: isBird ? 'bird' : 'zombie',
              x: speedX > 0 ? -60 : canvas.width + 60, 
              y: yPos, baseY: yPos,
              size: size,
              speedX: isBird ? speedX * 1.5 : speedX,
              offset: Math.random() * 100
          });
      }
  }

  function shoot() {
      if(gameOver) return;
      recoilOffset = 25; // 반동 세게!
      
      // 화면 번쩍!
      ctx.fillStyle = "rgba(255, 255, 0, 0.4)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      let hit = false;
      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i];
          let tHeight = t.type === 'zombie' ? t.size * 2.8 : t.size;
          
          if (mouseX > t.x - 15 && mouseX < t.x + t.size + 15 &&
              mouseY > t.y - 15 && mouseY < t.y + tHeight + 15) {
              
              if(t.type === 'zombie' && mouseY < t.y + t.size + 5) {
                  score += 2; 
                  createParticles(mouseX, mouseY, "#FF0000"); 
              } else {
                  score += 1; 
                  createParticles(mouseX, mouseY, t.type === 'zombie' ? "#3498db" : "#e67e22"); 
              }

              targets.splice(i, 1);
              document.getElementById("score").innerText = "🪙 " + score + "점";
              hit = true; break;
          }
      }
      if(!hit) createParticles(mouseX, mouseY, "#7f8c8d"); 
  }

  function createParticles(x, y, color) {
      for(let i=0; i<12; i++) {
          particles.push({
              x: x, y: y,
              vx: (Math.random() - 0.5) * 12, vy: (Math.random() - 0.5) * 12,
              size: Math.random() * 6 + 4, color: color, life: 20
          });
      }
  }

  function drawBackground() {
      ctx.fillStyle = "#87CEEB"; ctx.fillRect(0, 0, canvas.width, canvas.height); 
      ctx.fillStyle = "#27ae60"; ctx.fillRect(0, canvas.height * 0.55, canvas.width, canvas.height * 0.45); 
      
      ctx.fillStyle = "#2c3e50";
      ctx.beginPath(); ctx.moveTo(0, canvas.height*0.55); ctx.lineTo(90, canvas.height*0.35); ctx.lineTo(180, canvas.height*0.55); ctx.fill();
      ctx.fillStyle = "#34495e";
      ctx.beginPath(); ctx.moveTo(130, canvas.height*0.55); ctx.lineTo(260, canvas.height*0.3); ctx.lineTo(380, canvas.height*0.55); ctx.fill();
  }

  function drawScope() {
      ctx.save();
      let currentY = mouseY - recoilOffset;
      if(recoilOffset > 0) recoilOffset -= 2.5; 

      // ★ 투명 지우개 버그 완벽 해결 구간! (마스크 씌우기)
      let scopeRadius = 130; // 조준경 크기도 더 키움!

      ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
      ctx.beginPath();
      // 전체 화면 덮는 사각형 그리기
      ctx.rect(0, 0, canvas.width, canvas.height);
      // 조준경 구멍 부분만 반대 방향(true)으로 원을 그려서 구멍 뻥 뚫기!
      ctx.arc(mouseX, currentY, scopeRadius, 0, Math.PI * 2, true);
      ctx.fill();

      // 십자선 (빨간색)
      ctx.strokeStyle = "rgba(255, 0, 0, 0.8)"; ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(mouseX - scopeRadius, currentY); ctx.lineTo(mouseX + scopeRadius, currentY);
      ctx.moveTo(mouseX, currentY - scopeRadius); ctx.lineTo(mouseX, currentY + scopeRadius);
      ctx.stroke();

      // 조준경 테두리 (리얼리티 추가)
      ctx.strokeStyle = "#111"; ctx.lineWidth = 8;
      ctx.beginPath(); ctx.arc(mouseX, currentY, scopeRadius, 0, Math.PI*2); ctx.stroke();
      ctx.strokeStyle = "#555"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(mouseX, currentY, scopeRadius - 4, 0, Math.PI*2); ctx.stroke();

      // 스코프 눈금
      ctx.beginPath(); ctx.arc(mouseX, currentY, 3, 0, Math.PI*2); ctx.fill();
      for(let i=25; i<=100; i+=25) { 
          ctx.moveTo(mouseX - 10, currentY + i); ctx.lineTo(mouseX + 10, currentY + i); 
      }
      ctx.stroke();

      ctx.restore();
  }

  function update() {
      frameCount++;
      if(Math.random() < 0.04) spawnTarget(); 

      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i];
          t.x += t.speedX;
          if(t.type === 'bird') t.y = t.baseY + Math.sin(frameCount * 0.1 + t.offset) * 30; 
          
          if(t.x < -80 || t.x > canvas.width + 80) targets.splice(i, 1); 
      }

      for (let i = particles.length - 1; i >= 0; i--) {
          let p = particles[i];
          p.x += p.vx; p.y += p.vy; p.life--;
          if (p.life <= 0) particles.splice(i, 1);
      }
  }

  function gameLoop() {
      if (gameOver) return;
      
      update(); 
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawBackground();
      
      // ★ 몬스터들이 지워지지 않고 완벽하게 그려집니다!
      for (let t of targets) {
          if(t.type === 'zombie') drawZombie(t);
          else drawBird(t);
      }
      
      for (let p of particles) {
          ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, p.size, p.size);
      }
      
      drawScope(); 

      requestAnimationFrame(gameLoop);
  }

  canvas.addEventListener("mousemove", (e) => {
      let rect = canvas.getBoundingClientRect(); mouseX = e.clientX - rect.left; mouseY = e.clientY - rect.top;
  });
  canvas.addEventListener("mousedown", () => shoot());

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
      document.getElementById("score").innerText = "🪙 0점";
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
