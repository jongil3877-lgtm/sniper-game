import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="블록 스나이퍼", page_icon="🎯", layout="centered")

st.title("🎯 블록 스나이퍼: 금발의 암살자")
st.markdown("**[리얼 스나이퍼 조작법]**\n* 화면을 **꾹 누르면** 금발 요원이 일어나 줌(Zoom)을 켭니다.\n* 손가락을 **떼는 순간** 사격(탕!)하고 다시 벽 뒤로 **숨습니다.**\n* ⚠️ 적이 붉은 레이저로 조준하면 **반드시 손을 떼서 엄폐하세요!**")
st.markdown("---")

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

  let score = 0; let hp = 3; let gameOver = false; let frameCount = 0;
  let recoilOffset = 0; let targets = []; let particles = []; let enemyBullets = [];
  let mouseX = canvas.width / 2; let mouseY = canvas.height / 2;
  
  let isHiding = true; 
  let currentWallY = canvas.height * 0.6; // 벽의 높이

  let highScores = JSON.parse(localStorage.getItem('7c_sniper_v2_ranking')) || [];
  let currentHighScore = highScores.length > 0 ? highScores[0].score : 0;
  document.getElementById("score").innerText = `👑최고: ${currentHighScore} | 🪙 0점`;

  function drawBlock(x, y, w, h, color) {
      ctx.fillStyle = color; ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = "rgba(0,0,0,0.6)"; ctx.lineWidth = 1.5; ctx.strokeRect(x, y, w, h);
  }

  // 👱‍♀️ 고화질 2D 금발 스나이퍼 그리기 (코드 수제작)
  function drawFemaleSniper() {
      ctx.save();
      ctx.shadowColor = "rgba(0,0,0,0.5)"; ctx.shadowBlur = 10;

      // 몸통 (전술 요원복)
      ctx.fillStyle = "#1e272e";
      ctx.beginPath(); ctx.moveTo(-10, canvas.height); ctx.lineTo(30, canvas.height - 180); 
      ctx.lineTo(130, canvas.height - 160); ctx.lineTo(160, canvas.height); ctx.fill();

      // 얼굴 (서양인 피부톤)
      ctx.fillStyle = "#ffeaa7"; 
      ctx.beginPath(); ctx.arc(100, canvas.height - 210, 35, 0, Math.PI*2); ctx.fill();

      // 코와 턱선 (측면 프로필)
      ctx.beginPath(); ctx.moveTo(120, canvas.height - 230); ctx.lineTo(145, canvas.height - 210); 
      ctx.lineTo(130, canvas.height - 195); ctx.lineTo(135, canvas.height - 185); 
      ctx.lineTo(100, canvas.height - 175); ctx.fill();

      // 파란 눈
      ctx.fillStyle = "#0984e3";
      ctx.beginPath(); ctx.ellipse(125, canvas.height - 220, 6, 3, Math.PI/8, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(126, canvas.height - 221, 1.5, 0, Math.PI*2); ctx.fill();

      // 빨간 입술
      ctx.fillStyle = "#d63031";
      ctx.beginPath(); ctx.ellipse(135, canvas.height - 195, 5, 2.5, Math.PI/6, 0, Math.PI*2); ctx.fill();

      // 금발 머리카락 (찰랑이는 포니테일)
      ctx.fillStyle = "#fdcb6e";
      ctx.beginPath(); ctx.moveTo(70, canvas.height - 180); ctx.quadraticCurveTo(50, canvas.height - 250, 110, canvas.height - 250);
      ctx.quadraticCurveTo(130, canvas.height - 245, 110, canvas.height - 230); ctx.quadraticCurveTo(80, canvas.height - 220, 80, canvas.height - 180); ctx.fill();
      ctx.beginPath(); ctx.moveTo(70, canvas.height - 230); ctx.quadraticCurveTo(20, canvas.height - 220, 30, canvas.height - 150);
      ctx.quadraticCurveTo(50, canvas.height - 180, 80, canvas.height - 200); ctx.fill();

      // 대물 저격총
      ctx.fillStyle = "#2d3436"; ctx.shadowBlur = 5;
      ctx.fillRect(120, canvas.height - 165, 150, 15); // 총열
      ctx.fillRect(160, canvas.height - 180, 50, 12); // 조준경
      
      // 총 잡은 손
      ctx.fillStyle = "#ffeaa7"; ctx.beginPath(); ctx.arc(140, canvas.height - 155, 12, 0, Math.PI*2); ctx.fill();

      ctx.restore();
  }

  // 👾 다양해진 마인크래프트 적군들
  function drawMinecraftEnemy(t) {
      if(t.subType === 'zombie') { // 일반 좀비
          drawBlock(t.x, t.y, t.size, t.size, "#2ecc71"); 
          drawBlock(t.x + t.size*0.1, t.y + t.size, t.size*0.8, t.size*1.2, "#3498db");
      } else if (t.subType === 'skeleton') { // 스켈레톤 (하얀색)
          drawBlock(t.x, t.y, t.size, t.size, "#ecf0f1"); 
          drawBlock(t.x + t.size*0.1, t.y + t.size, t.size*0.8, t.size*1.2, "#bdc3c7");
          drawBlock(t.x + t.size*0.2, t.y + t.size*0.3, t.size*0.6, t.size*0.2, "#111"); // 선글라스 모양 눈
      } else if (t.subType === 'spider') { // 거미 (납작하고 검은색)
          drawBlock(t.x - t.size*0.5, t.y + t.size*0.5, t.size*2, t.size*0.8, "#2c3e50"); 
          drawBlock(t.x + t.size*0.2, t.y + t.size*0.7, t.size*0.2, t.size*0.2, "#e74c3c"); // 빨간 눈
          drawBlock(t.x + t.size*0.6, t.y + t.size*0.7, t.size*0.2, t.size*0.2, "#e74c3c"); 
      } else if (t.subType === 'enderman') { // 엔더맨 (길쭉하고 보라색 눈)
          drawBlock(t.x, t.y - t.size*0.5, t.size*0.8, t.size*0.8, "#111"); 
          drawBlock(t.x + t.size*0.1, t.y + t.size*0.3, t.size*0.6, t.size*2.5, "#111"); // 긴 몸
          drawBlock(t.x + t.size*0.1, t.y - t.size*0.2, t.size*0.6, t.size*0.15, "#9b59b6"); // 보라색 눈
      }
  }

  function spawnTarget() {
      if(targets.length < 5) { 
          let types = ['zombie', 'skeleton', 'spider', 'enderman'];
          let sub = types[Math.floor(Math.random() * types.length)];
          let size = Math.random() * 15 + 20; 
          
          let yPos = (sub === 'spider') ? canvas.height*0.6 : (Math.random() * (canvas.height*0.2) + canvas.height*0.4);
          let speedX = (Math.random() * 1.5 + 0.5) * (Math.random() > 0.5 ? 1 : -1);
          if(sub === 'spider') speedX *= 1.8; // 거미는 빠름
          
          targets.push({
              subType: sub,
              x: speedX > 0 ? -60 : canvas.width + 60, 
              y: yPos, size: size, speedX: speedX,
              attackTimer: Math.random() * 80 + 100 // 공격까지 남은 시간
          });
      }
  }

  function shoot() {
      if(gameOver) return;
      recoilOffset = 25; 
      ctx.fillStyle = "rgba(255, 255, 0, 0.5)"; ctx.fillRect(0, 0, canvas.width, canvas.height); // 사격 섬광

      let hit = false;
      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i];
          let tHeight = t.size * 2.5; if(t.subType==='spider') tHeight = t.size; if(t.subType==='enderman') tHeight = t.size*3;
          
          if (mouseX > t.x - 20 && mouseX < t.x + t.size*2 + 20 && mouseY > t.y - 30 && mouseY < t.y + tHeight + 20) {
              
              if(mouseY < t.y + t.size + 10) { // 헤드샷 판정 후하게
                  score += 2; createParticles(mouseX, mouseY, "#e74c3c"); 
              } else {
                  score += 1; createParticles(mouseX, mouseY, "#3498db"); 
              }
              targets.splice(i, 1);
              updateUI(); hit = true; break;
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

      // 엄폐물 애니메이션
      let targetWallY = isHiding ? canvas.height * 0.55 : canvas.height;
      currentWallY += (targetWallY - currentWallY) * 0.25; 

      for (let i = targets.length - 1; i >= 0; i--) {
          let t = targets[i];
          t.x += t.speedX;
          
          // 엔더맨 순간이동 로직
          if(t.subType === 'enderman' && frameCount % 60 === 0 && Math.random() < 0.5) {
              t.x += (Math.random() > 0.5 ? 40 : -40); 
              createParticles(t.x, t.y, "#9b59b6");
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
          let b = enemyBullets[i];
          b.progress += 0.025; // 총알 날아오는 속도
          if(b.progress >= 1) { 
              if(!isHiding) {
                  hp--; updateUI(); ctx.fillStyle = "rgba(255,0,0,0.7)"; ctx.fillRect(0,0,canvas.width,canvas.height); 
                  createParticles(canvas.width/2, canvas.height/2, "#FF0000");
                  if(hp <= 0) handleGameOver();
              } else {
                  createParticles(canvas.width/2, canvas.height*0.7, "#f1c40f"); // 벽에 맞음
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
          
          // ★ 리얼한 공격 경고 (빨간 레이저 사이트)
          if(t.attackTimer > 0 && t.attackTimer < 60) {
              ctx.save();
              ctx.strokeStyle = `rgba(255, 0, 0, ${1 - t.attackTimer/60})`;
              ctx.lineWidth = 2 + (60 - t.attackTimer)*0.05;
              ctx.beginPath(); ctx.moveTo(t.x + t.size/2, t.y + t.size/2);
              
              // 숨어있으면 화면 가운데로, 조준중이면 조준경 쪽으로 레이저가 꽂힘!
              let targetX = isHiding ? canvas.width/2 : mouseX;
              let targetY = isHiding ? canvas.height/2 : mouseY;
              ctx.lineTo(targetX, targetY); ctx.stroke();
              
              ctx.fillStyle = "rgba(255, 0, 0, 0.9)"; ctx.font = "22px Arial"; ctx.textAlign = "center";
              ctx.fillText("⚠️ 적 조준 중!! 숨으세요!", canvas.width/2, 80);
              ctx.restore();
          }
      }
      
      for (let p of particles) { ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, p.size, p.size); }
      
      if(!isHiding) drawScope(); 
      
      for (let b of enemyBullets) {
          let currX = b.startX + (canvas.width/2 - b.startX) * b.progress;
          let currY = b.startY + (canvas.height/2 - b.startY) * b.progress;
          let currRadius = 5 + b.progress * 60; 
          ctx.fillStyle = "rgba(255, 69, 0, 0.9)"; ctx.beginPath(); ctx.arc(currX, currY, currRadius, 0, Math.PI*2); ctx.fill();
      }

      drawCoverWall(); 
      
      // ★ 숨어있을 때만 아리따운 금발 스나이퍼 등장!
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
      localStorage.setItem('7c_sniper_v2_ranking', JSON.stringify(highScores));
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
"""

components.html(game_html, height=600)
