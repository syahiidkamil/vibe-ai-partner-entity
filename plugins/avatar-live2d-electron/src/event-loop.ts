export class EventLoop {
  private running = false;
  private lastTime = 0;
  private callback: ((dt: number) => void) | null = null;
  private frameId = 0;

  start(callback: (deltaTime: number) => void) {
    this.callback = callback;
    this.running = true;
    this.lastTime = performance.now();
    this.tick();
  }

  private tick = () => {
    if (!this.running) return;
    const now = performance.now();
    const dt = Math.min((now - this.lastTime) / 1000, 1/15); // clamp for physics stability
    this.lastTime = now;
    this.callback?.(dt);
    this.frameId = requestAnimationFrame(this.tick);
  };

  stop() { this.running = false; cancelAnimationFrame(this.frameId); }
}
