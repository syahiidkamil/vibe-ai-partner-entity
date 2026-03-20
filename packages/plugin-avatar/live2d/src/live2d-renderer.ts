import type { IPluginManifest, IAvatarRenderer } from "@vibe-ai-partner/core";
import type { Live2DRendererConfig, Live2DCapabilities } from "./types.js";
import { createPixiApp, type PixiAppHandle } from "./pixi-setup.js";
import { ExpressionManager } from "./expression-manager.js";
import { MotionPlayer } from "./motion-player.js";
import { LipSyncDriver } from "./lip-sync-driver.js";

export class Live2DRenderer implements IAvatarRenderer {
  // ─── IPlugin ─────────────────────────────────────────────────
  readonly manifest: IPluginManifest = {
    id: "live2d",
    name: "Live2D Cubism Renderer",
    version: "0.1.0",
    type: "avatar-renderer",
    capabilities: ["expressions", "motions", "lipsync", "physics"],
  };

  // ─── Private state ──────────────────────────────────────────
  private config: Live2DRendererConfig | null = null;
  private capabilities: Live2DCapabilities | null = null;
  private pixiHandle: PixiAppHandle | null = null;
  private model: any = null; // pixi-live2d-display Live2DModel instance
  private expressionManager: ExpressionManager | null = null;
  private motionPlayer: MotionPlayer | null = null;
  private lipSyncDriver: LipSyncDriver | null = null;
  private mounted = false;

  // ─── IPlugin lifecycle ──────────────────────────────────────

  async initialize(config: Record<string, unknown>): Promise<void> {
    this.config = config as unknown as Live2DRendererConfig;

    // Load capabilities.json from model directory
    const capabilitiesUrl = `${this.config.modelPath}/capabilities.json`;
    const response = await fetch(capabilitiesUrl);
    if (!response.ok) {
      throw new Error(
        `Failed to load capabilities.json from ${capabilitiesUrl}`,
      );
    }
    this.capabilities = await response.json();

    if (this.capabilities!.renderer !== "live2d") {
      throw new Error(
        `capabilities.json renderer is "${this.capabilities!.renderer}", expected "live2d"`,
      );
    }

    // Initialize sub-modules with capabilities data
    this.expressionManager = new ExpressionManager(
      this.capabilities!.feelings,
    );
    this.motionPlayer = new MotionPlayer(
      this.capabilities!.selfExpressions,
    );
    this.lipSyncDriver = new LipSyncDriver(this.capabilities!.lipSync);
  }

  async dispose(): Promise<void> {
    if (this.mounted) {
      this.unmount();
    }
    this.model = null;
    this.expressionManager = null;
    this.motionPlayer = null;
    this.lipSyncDriver = null;
    this.capabilities = null;
    this.config = null;
  }

  // ─── IAvatarRenderer ────────────────────────────────────────

  async mount(container: HTMLElement): Promise<void> {
    if (!this.config || !this.capabilities) {
      throw new Error("Plugin not initialized. Call initialize() first.");
    }

    const width = this.config.width ?? container.clientWidth;
    const height = this.config.height ?? container.clientHeight;

    // Create PixiJS application with transparent background
    this.pixiHandle = createPixiApp(container, width, height);

    // Load model via pixi-live2d-display
    // Ported from submodule: index.html init() function
    const { Live2DModel, MotionPreloadStrategy } = await import(
      "pixi-live2d-display"
    );
    const modelPath = `${this.config.modelPath}/${this.capabilities.model}.model3.json`;

    this.model = await Live2DModel.from(modelPath, {
      motionPreload: MotionPreloadStrategy.ALL,
    });

    // Scale and center the model to fill the container
    // Ported from submodule: scale calculation in init()
    const scale =
      Math.min(width / this.model.width, height / this.model.height) * 0.95;
    this.model.scale.set(scale);
    this.model.anchor.set(0.5, 0.5);
    this.model.x = width / 2;
    this.model.y = height / 2 - 20;

    // Disable auto eye blink to prevent conflict with motion blink curves
    // Ported from submodule: model.internalModel.eyeBlink = null
    this.model.internalModel.eyeBlink = null;

    this.pixiHandle.app.stage.addChild(this.model);

    // Bind sub-modules to the loaded model
    this.expressionManager!.bind(this.model);
    this.motionPlayer!.bind(this.model);
    this.lipSyncDriver!.bind(this.model);

    // Start idle motion
    // Ported from submodule: model.motion('Idle', 0)
    this.model.motion("Idle", 0);

    this.mounted = true;
  }

  update(_deltaTime: number): void {
    // PixiJS handles its own render loop via requestAnimationFrame.
    // This method exists for the host to call if it needs explicit frame control.
    // The Live2D model's Cubism physics and idle animations update automatically
    // through pixi-live2d-display's internal ticker.
    //
    // If we need manual control later (e.g., pausing physics), we can
    // intercept the ticker here.
  }

  setFeeling(feeling: string, intensity: number): void {
    if (!this.expressionManager || !this.mounted) return;
    this.expressionManager.apply(feeling, intensity);
  }

  async playSelfExpression(name: string): Promise<void> {
    if (!this.motionPlayer || !this.mounted) return;
    await this.motionPlayer.play(name);
  }

  setLipSyncAmplitude(amplitude: number): void {
    if (!this.lipSyncDriver || !this.mounted) return;
    this.lipSyncDriver.setAmplitude(amplitude);
  }

  resize(width: number, height: number): void {
    if (!this.pixiHandle || !this.model) return;

    this.pixiHandle.app.renderer.resize(width, height);

    // Recalculate model scale and position
    const scale =
      Math.min(width / this.model.width, height / this.model.height) * 0.95;
    this.model.scale.set(scale);
    this.model.x = width / 2;
    this.model.y = height / 2 - 20;
  }

  getAvailableFeelings(): string[] {
    if (!this.capabilities) return [];
    return Object.entries(this.capabilities.feelings)
      .filter(([_, mapping]) => mapping !== null)
      .map(([name]) => name);
  }

  getAvailableSelfExpressions(): string[] {
    if (!this.capabilities) return [];
    return Object.keys(this.capabilities.selfExpressions);
  }

  unmount(): void {
    if (this.pixiHandle) {
      this.pixiHandle.destroy();
      this.pixiHandle = null;
    }
    this.model = null;
    this.mounted = false;
  }
}
