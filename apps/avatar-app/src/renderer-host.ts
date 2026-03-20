export class RendererHost {
  private model: any = null;  // pixi-live2d-display model instance
  private app: any = null;    // PIXI.Application

  async mount(container: HTMLElement, modelPath: string) {
    // Dynamic import to avoid bundling pixi at compile time
    const PIXI = await import("pixi.js");
    const { Live2DModel } = await import("pixi-live2d-display");

    // Register Live2D interaction with PIXI
    Live2DModel.registerTicker(PIXI.Ticker);

    this.app = new PIXI.Application({
      view: document.createElement("canvas"),
      transparent: true,
      resizeTo: container,
      autoStart: true,
    });
    container.appendChild(this.app.view as HTMLCanvasElement);

    this.model = await Live2DModel.from(modelPath);
    this.model.scale.set(0.3);
    this.model.anchor.set(0.5, 0.5);
    this.model.x = this.app.renderer.width / 2;
    this.model.y = this.app.renderer.height / 2;
    this.app.stage.addChild(this.model);
  }

  update(deltaTime: number) {
    // PIXI ticker handles updates automatically
  }

  setFeeling(feeling: string, intensity: number) {
    if (!this.model) return;
    this.model.expression(feeling);
  }

  async playSelfExpression(name: string) {
    if (!this.model) return;
    this.model.motion(name);
  }

  setLipSyncAmplitude(amplitude: number) {
    if (!this.model) return;
    const coreModel = this.model.internalModel?.coreModel;
    if (coreModel) {
      const idx = coreModel.getParameterIndex("ParamMouthOpenY");
      if (idx >= 0) coreModel.setParameterValueByIndex(idx, amplitude);
    }
  }

  unmount() {
    if (this.app) {
      this.app.destroy(true);
      this.app = null;
      this.model = null;
    }
  }
}
