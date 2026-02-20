const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const transcriptEl = document.getElementById('transcript');
const statusEl = document.getElementById('status');
const statsEl = document.getElementById('stats');

let audioContext;
let mediaStream;
let source;
let processor;
let ws;

function setStatus(text) {
  statusEl.textContent = `Status: ${text}`;
}

function int16FromFloat32(float32Array) {
  const out = new Int16Array(float32Array.length);
  for (let i = 0; i < float32Array.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, float32Array[i]));
    out[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
  }
  return out;
}

async function startStreaming() {
  const wsProto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${wsProto}://${location.host}/ws/transcribe`);

  ws.onopen = () => setStatus('websocket connected');

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'status') {
      const details = data.sample_rate ? ` @ ${data.sample_rate} Hz` : '';
      setStatus(`${data.message}${details}`);
      return;
    }

    if (data.type === 'audio_stats') {
      const buffered = data.buffered_ms ? ` | buffered: ${data.buffered_ms}ms` : '';
      statsEl.textContent = `RMS: ${data.rms} | speech: ${data.speech}${buffered}`;
      return;
    }

    if (data.type === 'transcript') {
      transcriptEl.textContent += `${data.text || '[no speech detected]'}\n`;
    }
  };

  ws.onerror = () => setStatus('websocket error');
  ws.onclose = () => setStatus('websocket closed');

  mediaStream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: 1,
      sampleRate: 16000,
      echoCancellation: true,
      noiseSuppression: true,
    },
  });

  audioContext = new AudioContext({ sampleRate: 16000 });
  source = audioContext.createMediaStreamSource(mediaStream);
  processor = audioContext.createScriptProcessor(4096, 1, 1);

  processor.onaudioprocess = (event) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const channelData = event.inputBuffer.getChannelData(0);
    ws.send(int16FromFloat32(channelData).buffer);
  };

  source.connect(processor);
  processor.connect(audioContext.destination);

  startBtn.disabled = true;
  stopBtn.disabled = false;
}

function stopStreaming() {
  if (processor) processor.disconnect();
  if (source) source.disconnect();
  if (audioContext) audioContext.close();
  if (mediaStream) mediaStream.getTracks().forEach((track) => track.stop());
  if (ws) ws.close();

  processor = null;
  source = null;
  audioContext = null;
  mediaStream = null;
  ws = null;

  startBtn.disabled = false;
  stopBtn.disabled = true;
  setStatus('idle');
}

startBtn.addEventListener('click', async () => {
  try {
    await startStreaming();
  } catch (error) {
    setStatus(`failed: ${error.message}`);
  }
});

stopBtn.addEventListener('click', stopStreaming);
