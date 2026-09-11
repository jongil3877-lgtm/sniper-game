import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(page_title="블록 스나이퍼", page_icon="🎯", layout="centered")

st.title("🎯 블록 스나이퍼: 특수 요원 SJI")
st.markdown("**[리얼 스나이퍼 조작법]**\n* 화면을 **꾹 누르면** 요원이 줌(Zoom)을 켭니다.\n* 손가락을 **떼는 순간** 사격(탕!)하고 다시 벽 뒤로 **숨습니다.**\n* ⚠️ 적이 붉은 레이저로 조준하면 **반드시 손을 떼서 엄폐하세요!**")
st.markdown("---")

# 부장님이 올리신 이미지를 파이썬이 읽어서 웹용으로 변환하는 마법의 코드
image_path = "sniper.jpg"
img_base64 = ""

if os.path.exists(image_path):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
        img_base64 = f"data:image/jpeg;base64,{encoded_string}"

# 게임 엔진 코드 (HTML/JS)
game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; background-color: #1a1a2e; color: white; margin: 0; padding: 10px; touch-action: none; font-family: 'Courier New', Courier, monospace; font-weight: bold;}
  
  #game-container { position: relative; border: 8px solid #222; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); background-color: #87CEEB; overflow: hidden; width: 350px; height: 500px;}
  canvas { display: block; cursor: crosshair; }
  
  .ui-bar { width: 100%; display: flex; justify-content: space-between; position: absolute; top: 10px; padding: 0 15px; box-sizing: border-box; font-size: 16px; text-shadow: 2px 2px 0 #000; pointer-events: none; z-index: 10;}
  
  #game-over-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 20; padding: 15px; box-sizing: border-box;}
  #game-over-text { color: #e74c3c; font-size: 32px; text-shadow: 3px 3px 0 #000; margin-bottom: 10px;}
  
  #new-record-input { display: none; text-align: center; margin-bottom: 15px;}
  #new-record-input input { width: 80px; font-size: 24px; text-align: center; text-transform: uppercase; font-weight: bold; margin: 10px; border-radius: 5px; border: 2px solid #FFD700; background: #222; color: white;}
  #new-record-input button { padding: 8px 15px; font-size: 18px; font-weight: bold; background: #FFD700; color: black; border: none; border-radius: 5px; cursor: pointer;}
  
  #leaderboard { display: none; margin-bottom: 20px; width: 100%;}
  #leaderboard h3 { margin: 0 0 10px 0; text-align: center; color: #00FFFF; }
  .rank-row { display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 5px; border-bottom: 1px solid #444; padding-bottom: 3px;}
  
  #btn-restart { padding: 12px 20px; font-size: 18px; font-weight: bold; background: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; width: 100%;}
</style>
</head>
<body>

  <div id="game-container">
      <div class="ui-bar">
          <span id="score" style="color: #f1c40f;">👑최고: 0 | 🪙 0점</span>
          <span id="hp" style="color: #ff4d4d;">💖💖💖</span>
      </div>
      <canvas id="gameCanvas" width="350" height="500"></canvas>
      
      <div id="game-over-screen">
          <div id="game-over-text">KIA (작전 실패)</div>
          <div id="new-record-input">
              <p style="color:#FFD700; margin:0; font-size:20px;">🎉 랭킹 달성! 🎉</p>
              <input type="text" id="initials" maxlength="3" placeholder="AAA">
              <button onclick="saveScore()">등록</button>
          </div>
          <div id="leaderboard">
              <h3>🏆 명예의 전당 🏆</h3>
              <div id="leaderboard-list"></div>
          </div>
          <button id="btn-restart" onclick="resetGame()">다시 작전 투입</button>
      </div>
  </div>

<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");

  // ★ 부장님의 스나이퍼 이미지 로딩
  const sniperImg = new Image();
  sniperImg.src = "SNIPER_IMG_SRC";

  let score = 0; let hp = 3; let gameOver = false; let frameCount = 0;
  let recoilOffset = 0; let targets = []; let particles = []; let enemyBullets = [];
  let mouseX = canvas.width / 2; let mouseY = canvas.height / 2;
  
  let isHiding = true; 
  let currentWallY = canvas.height * 0.6; 

  let highScores = JSON.parse(localStorage.getItem('7c_sniper_v3_ranking')) || [];
  let currentHighScore = highScores.length > 0 ? highScores[0].score : 0;
  document.getElementById("score").innerText = `👑최고: ${currentHighScore} | 🪙 0점`;

  function drawBlock(x, y, w, h, color) {
      ctx.fillStyle = color; ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = "rgba(0,0,0,0.6)"; ctx.lineWidth = 1.5; ctx.strokeRect(x, y, w, h);
  }

  // ★ 요원 프로필 그리기 (커스텀 이미지 적용)
  function drawFemaleSniper() {
      // 이미지가 정상적으로 불러와졌다면 (부장님의 이미지 출력)
      if (sniperImg.complete && sniperImg.src && sniperImg.src.length > 50) {
          let frameW = 160;
          let frameH = 220;
          let frameX = canvas.width - frameW - 15;
          let frameY = canvas.height - frameH - 15;

          ctx.save();
          // 이미지 박스 금장 테두리 및 그림자 효과 (블랙 배경을 살림)
          ctx.shadowColor = "rgba(0,0,0,0.8)";
          ctx.shadowBlur = 15;
          ctx.strokeStyle = "#FFD700";
          ctx.lineWidth = 3;
          ctx.strokeRect(frameX, frameY, frameW, frameH);
          ctx.shadowBlur = 0;

          // 진짜 이미지 그리기
          ctx.drawImage(sniperImg, frameX, frameY, frameW, frameH);

          // 하단 이름표 바 (AGENT SJI)
          ctx.fillStyle = "rgba(0,0,0,0.7)";
          ctx.fillRect(frameX, frameY + frameH - 30, frameW, 30);
          ctx.fillStyle = "#FFF";
          ctx.font = "16px Arial";
          ctx.textAlign = "center";
          ctx.fillText("AGENT SJI", frameX + frameW/2, frameY + frameH - 10);
          ctx.restore();
      } else {
          // 혹시 이미지를 못 찾았을 때를 대비한 찰흙 비상용 스나이퍼
          ctx.save();
          ctx.fillStyle = "#1e272e";
          ctx.beginPath(); ctx.moveTo(-10, canvas.height); ctx.lineTo(30, canvas.height - 180); 
          ctx.lineTo(130, canvas.height - 160); ctx.lineTo(160, canvas.height); ctx.fill();
          ctx.fillStyle = "#ffeaa7"; ctx.beginPath(); ctx.arc(100, canvas.height - 210, 35, 0, Math.PI*2); ctx.fill();
          ctx.restore();
      }
  }

  function drawMinecraftEnemy(t) {
      if(t.subType === 'zombie') { 
          drawBlock(t.x, t.y, t.size, t.size, "#2ecc71"); 
          drawBlock(t.x + t.size*0.1, t.y + t.size, t.size*0.8, t.size*1.2, "#3498db");
      } else if (t.subType === 'skeleton') { 
          drawBlock(t.x, t.y, t.size, t.size, "#ecf0f1"); 
          drawBlock(t.x + t.size*0.1, t.y + t.size, t.size*0.8, t.size*1.2, "#bdc3c7");
          drawBlock(t.x + t.size*0.2, t.y + t.size*0.3, t.size*0.6, t.size*0.2, "#111"); 
      } else if (t.subType === 'spider') { 
          drawBlock(t.x - t.size*0.5, t.y + t.size*0.5, t.size*2, t.size*0.8, "#2c3e50"); 
          drawBlock(t.x + t.size*0.2, t.y + t.size*0.7, t.size*0.2, t.size*0.2, "#e74c3c"); 
          drawBlock(t.x + t.size*0.6, t.y + t.size*0.7, t.size*0.2, t.size*0.2, "#e74c3c"); 
      } else if (t.subType === 'enderman') { 
          drawBlock(t.x, t.y - t.size*0.5, t.size*0.8, t.size*0.8, "#111"); 
          drawBlock(t.x + t.size*0.1, t.y + t.size*0.3, t.size*0.6, t.size*2.5, "#111"); 
          drawBlock(t.x + t.size*0.1, t.y - t.size*0.2, t.size*0.6, t.size*0.15, "#9b59b6"); 
      }
  }

  function spawnTarget() {
      if(targets.length < 5) { 
          let types = ['zombie', 'skeleton', 'spider', 'enderman'];
          let sub = types[Math.floor(Math.random() * types.length)];
          let size = Math.random() * 15 + 20; 
          
          let yPos = (sub === 'spider') ? canvas.height*0.6 : (Math.random() * (canvas.height*0.2) + canvas.height*0.4);
          let speedX = (Math.random() * 1.5 + 0.5) * (Math.random() > 0.5 ? 1 : -1);
          if(sub === 'spider') speedX *= 1.8; 
          
          targets.push({
              subType: sub, x: speedX > 0 ? -60 : canvas.width + 60, 
              y: yPos, size: size, speedX: speedX,
              attackTimer: Math.random() * 80 + 100 
          });
      }
  }

  function shoot() {
      if(gameOver) return;
      recoilOffset = 25; 
      ctx.fillStyle = "rgba(255, 255, 0, 0.5)"; ctx.fillRect(0, 0, canvas.width, canvas.height); 

      let hit = false;
      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i];
          let tHeight = t.size * 2.5; if(t.subType==='spider') tHeight = t.size; if(t.subType==='enderman') tHeight = t.size*3;
          
          if (mouseX > t.x - 20 && mouseX < t.x + t.size*2 + 20 && mouseY > t.y - 30 && mouseY < t.y + tHeight + 20) {
              if(mouseY < t.y + t.size + 10) { 
                  score += 2; createParticles(mouseX, mouseY, "#e74c3c"); 
              } else {
                  score += 1; createParticles(mouseX, mouseY, "#3498db"); 
              }
              targets.splice(i, 1); updateUI(); hit = true; break;
          }
      }
      if(!hit) createParticles(mouseX, mouseY, "#95a5a6"); 
  }

  function createParticles(x, y, color) {
      for(let i=0; i<15; i++) {
          particles.push({ x: x, y: y, vx: (Math.random() - 0.5)*15, vy: (Math.random() - 0.5)*15, size: Math.random()*6+4, color: color, life: 20 });
      }
  }

  function drawBackground() {
      ctx.fillStyle = "#87CEEB"; ctx.fillRect(0, 0, canvas.width, canvas.height); 
      ctx.fillStyle = "#27ae60"; ctx.fillRect(0, canvas.height * 0.55, canvas.width, canvas.height * 0.45); 
      ctx.fillStyle = "#2c3e50"; ctx.beginPath(); ctx.moveTo(0, canvas.height*0.55); ctx.lineTo(120, canvas.height*0.3); ctx.lineTo(240, canvas.height*0.55); ctx.fill();
      ctx.fillStyle = "#34495e"; ctx.beginPath(); ctx.moveTo(180, canvas.height*0.55); ctx.lineTo(300, canvas.height*0.35); ctx.lineTo(420, canvas.height*0.55); ctx.fill();
  }

  function drawScope() {
      ctx.save();
      let currentY = mouseY - recoilOffset;
      if(recoilOffset > 0) recoilOffset -= 3; 
      let scopeRadius = 140; 

      ctx.fillStyle = "rgba(0, 0, 0, 0.9)";
      ctx.beginPath(); ctx.rect(0, 0, canvas.width, canvas.height); ctx.arc(mouseX, currentY, scopeRadius, 0, Math.PI * 2, true); ctx.fill();

      ctx.strokeStyle = "rgba(255, 0, 0, 0.8)"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(mouseX - scopeRadius, currentY); ctx.lineTo(mouseX + scopeRadius, currentY);
      ctx.moveTo(mouseX, currentY - scopeRadius); ctx.lineTo(mouseX, currentY + scopeRadius); ctx.stroke();
      
      ctx.strokeStyle = "#111"; ctx.lineWidth = 10; ctx.beginPath(); ctx.arc(mouseX, currentY, scopeRadius, 0, Math.PI*2); ctx.stroke();
      ctx.beginPath(); ctx.arc(mouseX, currentY, 3, 0, Math.PI*2); ctx.fill();
      ctx.restore();
  }

  function drawCoverWall() {
      ctx.fillStyle = "#7f8c8d"; ctx.fillRect(0, currentWallY, canvas.width, canvas.height);
      ctx.strokeStyle = "#2c3e50"; ctx.lineWidth = 3;
      for(let y = currentWallY; y < canvas.height; y += 40) {
          ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
          let offset = (y % 80 === 0) ? 0 : 40;
          for(let x = offset; x < canvas.width; x += 80) { ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + 40); ctx.stroke(); }
      }
  }

  function update() {
      frameCount++;
      if(Math.random() < 0.05) spawnTarget(); 

      let targetWallY = isHiding ? canvas.height * 0.55 : canvas.height;
      currentWallY += (targetWallY - currentWallY) * 0.25; 

      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i]; t.x += t.speedX;
          
          if(t.subType === 'enderman' && frameCount % 60 === 0 && Math.random() < 0.5) {
              t.x += (Math.random() > 0.5 ? 40 : -40); createParticles(t.x, t.y, "#9b59b6");
          }
          
          if(t.x < -80 || t.x > canvas.width + 80) targets.splice(i, 1); 
          else {
              t.attackTimer--;
              if(t.attackTimer <= 0) {
                  enemyBullets.push({ startX: t.x + t.size/2, startY: t.y, progress: 0 });
                  t.attackTimer = Math.random() * 100 + 100; 
              }
          }
      }

      for (let i = enemyBullets.length - 1; i >= 0; i--) {
          let b = enemyBullets[i]; b.progress += 0.025; 
          if(b.progress >= 1) { 
              if(!isHiding) {
                  hp--; updateUI(); ctx.fillStyle = "rgba(255,0,0,0.7)"; ctx.fillRect(0,0,canvas.width,canvas.height); 
                  createParticles(canvas.width/2, canvas.height/2, "#FF0000");
                  if(hp <= 0) handleGameOver();
              } else {
                  createParticles(canvas.width/2, canvas.height*0.7, "#f1c40f"); 
              }
              enemyBullets.splice(i, 1);
          }
      }

      for (let i = particles.length - 1; i >= 0; i--) {
          let p = particles[i]; p.x += p.vx; p.y += p.vy; p.life--;
          if (p.life <= 0) particles.splice(i, 1);
      }
  }

  function gameLoop() {
      if (gameOver) return;
      update(); 
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawBackground();
      
      for (let t of targets) {
          drawMinecraftEnemy(t);
          
          if(t.attackTimer > 0 && t.attackTimer < 60) {
              ctx.save(); ctx.strokeStyle = `rgba(255, 0, 0, ${1 - t.attackTimer/60})`; ctx.lineWidth = 2 + (60 - t.attackTimer)*0.05;
              ctx.beginPath(); ctx.moveTo(t.x + t.size/2, t.y + t.size/2);
              let targetX = isHiding ? canvas.width/2 : mouseX; let targetY = isHiding ? canvas.height/2 : mouseY;
              ctx.lineTo(targetX, targetY); ctx.stroke();
              ctx.fillStyle = "rgba(255, 0, 0, 0.9)"; ctx.font = "22px Arial"; ctx.textAlign = "center";
              ctx.fillText("⚠️ 적 조준 중!! 숨으세요!", canvas.width/2, 80);
              ctx.restore();
          }
      }
      
      for (let p of particles) { ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, p.size, p.size); }
      
      if(!isHiding) drawScope(); 
      
      for (let b of enemyBullets) {
          let currX = b.startX + (canvas.width/2 - b.startX) * b.progress; let currY = b.startY + (canvas.height/2 - b.startY) * b.progress;
          let currRadius = 5 + b.progress * 60; 
          ctx.fillStyle = "rgba(255, 69, 0, 0.9)"; ctx.beginPath(); ctx.arc(currX, currY, currRadius, 0, Math.PI*2); ctx.fill();
      }

      drawCoverWall(); 
      
      // ★ 숨어있을 때만 부장님의 커스텀 요원 이미지가 짠! 하고 나타납니다.
      if(isHiding) drawFemaleSniper();

      requestAnimationFrame(gameLoop);
  }

  function startAim(x, y) { if(gameOver) return; isHiding = false; mouseX = x; mouseY = y; }
  function endAim() { if(gameOver) return; if(!isHiding) shoot(); isHiding = true; }

  canvas.addEventListener("mousedown", (e) => { let rect = canvas.getBoundingClientRect(); startAim(e.clientX - rect.left, e.clientY - rect.top); });
  canvas.addEventListener("mousemove", (e) => { if(!isHiding) { let rect = canvas.getBoundingClientRect(); mouseX = e.clientX - rect.left; mouseY = e.clientY - rect.top; } });
  canvas.addEventListener("mouseup", endAim);
  canvas.addEventListener("mouseleave", () => { if(!isHiding) endAim(); });

  canvas.addEventListener("touchstart", (e) => { e.preventDefault(); let rect = canvas.getBoundingClientRect(); startAim(e.touches[0].clientX - rect.left, e.touches[0].clientY - rect.top); }, { passive: false });
  canvas.addEventListener("touchmove", (e) => { e.preventDefault(); if(!isHiding) { let rect = canvas.getBoundingClientRect(); mouseX = e.touches[0].clientX - rect.left; mouseY = e.touches[0].clientY - rect.top; } }, { passive: false });
  canvas.addEventListener("touchend", (e) => { e.preventDefault(); endAim(); }, { passive: false });

  function updateUI() {
      if (score > currentHighScore) currentHighScore = score;
      document.getElementById("score").innerText = `👑최고: ${currentHighScore} | 🪙 ${score}점`;
      let hpText = ""; for(let i=0; i<hp; i++) hpText += "💖"; document.getElementById("hp").innerText = hpText;
  }

  function handleGameOver() {
      gameOver = true; document.getElementById("game-over-screen").style.display = "flex";
      let isTop5 = false;
      if (score > 0 && (highScores.length < 5 || score > highScores[highScores.length - 1].score)) isTop5 = true;

      if (isTop5) {
          document.getElementById("new-record-input").style.display = "block"; document.getElementById("leaderboard").style.display = "none"; document.getElementById("initials").value = ""; 
      } else {
          document.getElementById("new-record-input").style.display = "none"; showLeaderboard();
      }
  }

  function saveScore() {
      let initials = document.getElementById("initials").value.toUpperCase() || "UNK";
      highScores.push({name: initials.substring(0,3), score: score});
      highScores.sort((a,b) => b.score - a.score); highScores = highScores.slice(0,5); 
      localStorage.setItem('7c_sniper_v3_ranking', JSON.stringify(highScores));
      currentHighScore = highScores[0].score; document.getElementById("new-record-input").style.display = "none"; showLeaderboard();
  }

  function showLeaderboard() {
      let html = ""; let colors = ["#FFD700", "#C0C0C0", "#CD7F32", "white", "gray"]; 
      if (highScores.length === 0) html = "<p style='text-align:center; color:gray;'>기록이 없습니다.</p>";
      else { highScores.forEach((s, idx) => { html += `<div class="rank-row" style="color:${colors[idx]};"><span>${idx+1}위. ${s.name}</span><span>${s.score} 점</span></div>`; }); }
      document.getElementById("leaderboard-list").innerHTML = html; document.getElementById("leaderboard").style.display = "block";
  }

  function resetGame() {
      score = 0; hp = 3; gameOver = false; targets = []; particles = []; enemyBullets = []; frameCount = 0; isHiding = true; currentWallY = canvas.height * 0.6;
      updateUI(); document.getElementById("game-over-screen").style.display = "none"; gameLoop();
  }

  resetGame();
</script>
</body>
</html>
""".replace("SNIPER_IMG_SRC", img_base64)

components.html(game_html, height=600)
