import { Live2DRenderer } from "@vibe-ai-partner/plugin-avatar-live2d";

export class RendererHost {
  private renderer: Live2DRenderer;
  private resizeObserver: ResizeObserver | null = null;

  constructor() {
    this.renderer = new Live2DRenderer();
  }

  async mount(container: HTMLElement, modelPath: string) {
    await this.renderer.initialize({ modelPath });
    await this.renderer.mount(container);

    this.resizeObserver = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      this.renderer.resize(width, height);
    });
    this.resizeObserver.observe(container);
  }

  update(deltaTime: number) {
    this.renderer.update(deltaTime);
  }

  setFeeling(feeling: string, intensity: number) {
    this.renderer.setFeeling(feeling, intensity);
  }

  async playSelfExpression(name: string) {
    await this.renderer.playSelfExpression(name);
  }

  setLipSyncAmplitude(amplitude: number) {
    this.renderer.setLipSyncAmplitude(amplitude);
  }

  unmount() {
    this.resizeObserver?.disconnect();
    this.resizeObserver = null;
    this.renderer.unmount();
  }
}
