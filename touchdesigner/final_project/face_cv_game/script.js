const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const video = document.getElementById('video');
const faceCanvas = document.getElementById('faceCanvas');
const faceCtx = faceCanvas.getContext('2d');
const scoreElement = document.getElementById('score');
const resetBtn = document.getElementById('resetBtn');

let score = 0;
let gameRunning = true;
let player = { x: 400, y: 300, radius: 20, speed: 0.1 };
let stars = [];
let facePosition = { x: 0, y: 0 };
let hasCamera = false;

// Set canvas size to match video
faceCanvas.width = 320;
faceCanvas.height = 240;

// MediaPipe Face Mesh
const faceMesh = new FaceMesh({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`});
faceMesh.setOptions({
  maxNumFaces: 1,
  refineLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});
faceMesh.onResults(onResults);

const camera = new Camera(video, {
  onFrame: async () => {
    await faceMesh.send({image: video});
  },
  width: 640,
  height: 480
});

async function initCamera() {
  try {
    await camera.start();
    hasCamera = true;
  } catch (err) {
    console.error('Camera error:', err);
    fallbackToMouse();
  }
}

function onResults(results) {
  // Draw the video frame on the canvas
  faceCtx.save();
  faceCtx.drawImage(video, 0, 0, faceCanvas.width, faceCanvas.height);
  faceCtx.restore();

  if (results.multiFaceLandmarks) {
    for (const landmarks of results.multiFaceLandmarks) {
      drawConnectors(faceCtx, landmarks, FACEMESH_TESSELATION, {color: '#C0C0C070', lineWidth: 1});
      drawConnectors(faceCtx, landmarks, FACEMESH_RIGHT_EYE, {color: '#FF3030', lineWidth: 1});
      drawConnectors(faceCtx, landmarks, FACEMESH_RIGHT_IRIS, {color: '#FF3030', lineWidth: 1});
      drawConnectors(faceCtx, landmarks, FACEMESH_LEFT_EYE, {color: '#30FF30', lineWidth: 1});
      drawConnectors(faceCtx, landmarks, FACEMESH_LEFT_IRIS, {color: '#30FF30', lineWidth: 1});
      drawConnectors(faceCtx, landmarks, FACEMESH_FACE_OVAL, {color: '#E0E0E0', lineWidth: 1});
      drawLandmarks(faceCtx, landmarks, {color: '#FF0000', lineWidth: 1, radius: 1});
    }

    const landmarks = results.multiFaceLandmarks[0];
    const noseTip = landmarks[1]; // Nose tip landmark
    facePosition.x = noseTip.x * canvas.width;
    facePosition.y = noseTip.y * canvas.height;
  }
}

function fallbackToMouse() {
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    facePosition.x = e.clientX - rect.left;
    facePosition.y = e.clientY - rect.top;
  });
}

// Game objects
function createStar() {
  return {
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    radius: 10,
    collected: false
  };
}

for (let i = 0; i < 5; i++) {
  stars.push(createStar());
}

// Update player position based on face
function updatePlayer() {
  if (hasCamera) {
    player.x += (facePosition.x - player.x) * player.speed;
    player.y += (facePosition.y - player.y) * player.speed;
  }
  // Boundaries
  player.x = Math.max(player.radius, Math.min(canvas.width - player.radius, player.x));
  player.y = Math.max(player.radius, Math.min(canvas.height - player.radius, player.y));
}

// Check collisions
function checkCollisions() {
  stars.forEach(star => {
    if (!star.collected) {
      const dx = player.x - star.x;
      const dy = player.y - star.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      if (distance < player.radius + star.radius) {
        star.collected = true;
        score++;
        scoreElement.textContent = `Score: ${score}`;
        // Respawn star
        star.x = Math.random() * canvas.width;
        star.y = Math.random() * canvas.height;
        star.collected = false;
      }
    }
  });
}

// Render
function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Draw player (blue ball)
  ctx.beginPath();
  ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
  ctx.fillStyle = '#4CAF50';
  ctx.fill();
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();
  
  // Draw stars (yellow)
  stars.forEach(star => {
    if (!star.collected) {
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
      ctx.fillStyle = '#FFEB3B';
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  });
}

// Game loop
function gameLoop() {
  if (gameRunning) {
    updatePlayer();
    checkCollisions();
    render();
    requestAnimationFrame(gameLoop);
  }
}

// Reset
resetBtn.addEventListener('click', () => {
  score = 0;
  scoreElement.textContent = `Score: ${score}`;
  stars.forEach(star => {
    star.x = Math.random() * canvas.width;
    star.y = Math.random() * canvas.height;
    star.collected = false;
  });
  player.x = 400;
  player.y = 300;
});

// Start
initCamera();
gameLoop();