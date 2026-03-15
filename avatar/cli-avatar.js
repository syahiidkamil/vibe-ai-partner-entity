#!/usr/bin/env node

const { stdin, stdout } = process;

// --- Avatar State ---
const state = {
  x: 20,
  y: 10,
  mood: 'neutral',
  action: 'idle',
  actionFrame: 0,
  message: '',
  messageTimer: null,
};

// --- Terminal Size ---
const cols = () => stdout.columns || 80;
const rows = () => stdout.rows || 24;

// --- Avatar Sprites (mood -> frames) ---
const sprites = {
  neutral: [
    [
      '  .-~~~-. ',
      ' /       \\',
      '|  o   o  |',
      '|    ~    |',
      ' \\  ___  /',
      '  \'-...-\' ',
      '   /|  |\\  ',
      '  / |  | \\ ',
      '    |  |   ',
      '   _|  |_  ',
    ],
  ],
  happy: [
    [
      '  .-~~~-. ',
      ' /       \\',
      '|  ^   ^  |',
      '|   \\~/   |',
      ' \\  \\_/  /',
      '  \'-...-\' ',
      '  \\|    |/ ',
      '   |    |  ',
      '   |    |  ',
      '   _|  |_  ',
    ],
  ],
  sad: [
    [
      '  .-~~~-. ',
      ' /       \\',
      '|  T   T  |',
      '|    ~    |',
      ' \\  ___  /',
      '  \'-...-\' ',
      '   /|  |\\  ',
      '  / |  | \\ ',
      '    |  |   ',
      '   _|  |_  ',
    ],
  ],
  angry: [
    [
      '  .-~~~-. ',
      ' /       \\',
      '| \\>   </ |',
      '|    ^    |',
      ' \\  ===  /',
      '  \'-...-\' ',
      '  \\| /|\\  ',
      '   |/ | \\ ',
      '    |  |   ',
      '   _|  |_  ',
    ],
  ],
  wink: [
    [
      '  .-~~~-. ',
      ' /       \\',
      '|  -   o  |',
      '|    ~    |',
      ' \\  \\_/  /',
      '  \'-...-\' ',
      '   /|  |\\  ',
      '  / |  | \\ ',
      '    |  |   ',
      '   _|  |_  ',
    ],
  ],
  thinking: [
    [
      '  .-~~~-. ',
      ' /       \\',
      '|  o   o  |',
      '|    ~    |',
      ' \\  ---  / . o O',
      '  \'-...-\'       ',
      '   /|  |\\  ',
      '  / |  | \\ ',
      '    |  |   ',
      '   _|  |_  ',
    ],
  ],
};

// --- Walking animation overlays ---
const walkFrames = {
  right: [
    ['   /|  |   ', '  / |  |   ', '   /    \\  ', '  /      \\ '],
    ['   /|  |\\  ', '  / |  | \\ ', '    |  |   ', '   _|  |_  '],
  ],
  left: [
    ['    |  |\\  ', '    |  | \\ ', '   /    \\  ', '  /      \\ '],
    ['   /|  |\\  ', '  / |  | \\ ', '    |  |   ', '   _|  |_  '],
  ],
};

// --- Render ---
function render() {
  const sprite = sprites[state.mood][0];
  const screenW = cols();
  const screenH = rows();

  // Clear screen
  stdout.write('\x1b[2J\x1b[H');

  // Build frame buffer
  const buffer = [];

  // Header
  const title = '=== CLI Avatar PoC ===';
  buffer.push('\x1b[36m' + title.padStart(Math.floor(screenW / 2 + title.length / 2)) + '\x1b[0m');
  buffer.push('');

  // Draw avatar at position
  for (let row = 0; row < screenH - 6; row++) {
    const spriteRow = row - state.y;
    if (spriteRow >= 0 && spriteRow < sprite.length) {
      const line = sprite[spriteRow];
      const padding = ' '.repeat(Math.max(0, state.x));
      buffer.push(padding + colorize(line));
    } else {
      buffer.push('');
    }
  }

  // Speech bubble
  if (state.message) {
    const bubbleX = Math.max(0, state.x - 2);
    const padding = ' '.repeat(bubbleX);
    const msgLine = `${padding}  💬 "${state.message}"`;
    buffer.splice(Math.max(0, state.y - 2), 1, '\x1b[33m' + msgLine + '\x1b[0m');
  }

  // Status bar
  const statusLine = ` Mood: \x1b[32m${state.mood}\x1b[0m | Pos: (${state.x}, ${state.y}) | Action: \x1b[35m${state.action}\x1b[0m`;
  const controlLine = ' \x1b[90m[Arrows] Move  [1-6] Mood  [S] Say  [W] Wave  [J] Jump  [D] Dance  [Q] Quit\x1b[0m';

  // Write output
  const output = buffer.slice(0, screenH - 4).join('\n');
  stdout.write(output + '\n');
  stdout.write('\x1b[0m' + '─'.repeat(screenW) + '\n');
  stdout.write(statusLine + '\n');
  stdout.write(controlLine + '\n');
}

function colorize(line) {
  // Head color
  return '\x1b[33m' + line + '\x1b[0m';
}

// --- Actions ---
function wave() {
  state.action = 'waving';
  const original = sprites[state.mood][0][6];
  const waveFrames = [
    '  \\|    |/ ',
    '  -|    |/ ',
    '  /|    |/ ',
    '  -|    |/ ',
  ];

  let frame = 0;
  const interval = setInterval(() => {
    sprites[state.mood][0][6] = waveFrames[frame % waveFrames.length];
    render();
    frame++;
    if (frame >= 8) {
      clearInterval(interval);
      sprites[state.mood][0][6] = original;
      state.action = 'idle';
      render();
    }
  }, 150);
}

function jump() {
  state.action = 'jumping';
  const origY = state.y;
  const jumpSeq = [-1, -2, -3, -2, -1, 0];

  let frame = 0;
  const interval = setInterval(() => {
    state.y = origY + jumpSeq[frame];
    render();
    frame++;
    if (frame >= jumpSeq.length) {
      clearInterval(interval);
      state.y = origY;
      state.action = 'idle';
      render();
    }
  }, 100);
}

function dance() {
  state.action = 'dancing';
  const moods = ['happy', 'wink', 'happy', 'neutral', 'wink', 'happy'];
  const origMood = state.mood;
  const origX = state.x;

  let frame = 0;
  const interval = setInterval(() => {
    state.mood = moods[frame % moods.length];
    state.x = origX + (frame % 2 === 0 ? 2 : -2);
    render();
    frame++;
    if (frame >= 12) {
      clearInterval(interval);
      state.mood = origMood;
      state.x = origX;
      state.action = 'idle';
      render();
    }
  }, 200);
}

function say(msg) {
  state.message = msg;
  if (state.messageTimer) clearTimeout(state.messageTimer);
  state.messageTimer = setTimeout(() => {
    state.message = '';
    render();
  }, 3000);
  render();
}

// --- Input Handling ---
let inputMode = null;
let inputBuffer = '';

function handleInput(key) {
  // Say mode - collecting text
  if (inputMode === 'say') {
    if (key === '\r' || key === '\n') {
      say(inputBuffer);
      inputMode = null;
      inputBuffer = '';
      return;
    }
    if (key === '\x1b') {
      inputMode = null;
      inputBuffer = '';
      render();
      return;
    }
    if (key === '\x7f') {
      inputBuffer = inputBuffer.slice(0, -1);
      // Show typing indicator
      stdout.write('\x1b[' + (rows()) + ';1H\x1b[K Type: ' + inputBuffer + '█');
      return;
    }
    inputBuffer += key;
    stdout.write('\x1b[' + (rows()) + ';1H\x1b[K Type: ' + inputBuffer + '█');
    return;
  }

  const step = 2;
  const maxX = cols() - 15;
  const maxY = rows() - 16;

  switch (key) {
    // Arrow keys
    case '\x1b[A': // Up
      state.y = Math.max(0, state.y - step);
      state.action = 'walking';
      break;
    case '\x1b[B': // Down
      state.y = Math.min(maxY, state.y + step);
      state.action = 'walking';
      break;
    case '\x1b[C': // Right
      state.x = Math.min(maxX, state.x + step);
      state.action = 'walking';
      break;
    case '\x1b[D': // Left
      state.x = Math.max(0, state.x - step);
      state.action = 'walking';
      break;

    // Moods
    case '1': state.mood = 'neutral'; break;
    case '2': state.mood = 'happy'; break;
    case '3': state.mood = 'sad'; break;
    case '4': state.mood = 'angry'; break;
    case '5': state.mood = 'wink'; break;
    case '6': state.mood = 'thinking'; break;

    // Actions
    case 'w': case 'W': wave(); return;
    case 'j': case 'J': jump(); return;
    case 'd': case 'D': dance(); return;
    case 's': case 'S':
      inputMode = 'say';
      inputBuffer = '';
      stdout.write('\x1b[' + (rows()) + ';1H\x1b[K Type: █');
      return;

    // Quit
    case 'q': case 'Q': case '\x03':
      stdout.write('\x1b[2J\x1b[H');
      stdout.write('\x1b[36mAvatar says goodbye! 👋\x1b[0m\n\n');
      process.exit(0);
  }

  // Reset walking action after a brief moment
  if (state.action === 'walking') {
    setTimeout(() => {
      if (state.action === 'walking') {
        state.action = 'idle';
        render();
      }
    }, 300);
  }

  render();
}

// --- Main ---
function main() {
  // Setup raw mode for keypress detection
  if (!stdin.isTTY) {
    console.log('Error: This script requires an interactive terminal.');
    process.exit(1);
  }

  stdin.setRawMode(true);
  stdin.resume();
  stdin.setEncoding('utf8');

  // Center avatar initially
  state.x = Math.floor(cols() / 2) - 6;
  state.y = Math.floor((rows() - 14) / 2);

  // Hide cursor
  stdout.write('\x1b[?25l');

  // Initial render
  render();

  // Listen for input
  stdin.on('data', (data) => {
    handleInput(data);
  });

  // Show cursor on exit
  process.on('exit', () => {
    stdout.write('\x1b[?25h');
  });
  process.on('SIGINT', () => {
    stdout.write('\x1b[?25h');
    process.exit(0);
  });

  // Re-render on terminal resize
  stdout.on('resize', () => {
    render();
  });
}

main();
