/// <reference types="vite/client" />

// pixi.js and pixi-live2d-display are dynamically imported at runtime
// and not bundled as direct dependencies. Declare minimal types to satisfy TS.
declare module "pixi.js" {
  export const Ticker: any;
  export class Application {
    constructor(options?: any);
    view: HTMLCanvasElement;
    renderer: { width: number; height: number };
    stage: { addChild(child: any): void };
    destroy(removeView?: boolean): void;
  }
}

declare module "pixi-live2d-display" {
  export class Live2DModel {
    static registerTicker(ticker: any): void;
    static from(source: string, options?: any): Promise<Live2DModel>;
    scale: { set(x: number, y?: number): void };
    anchor: { set(x: number, y?: number): void };
    x: number;
    y: number;
    internalModel?: {
      coreModel?: {
        getParameterIndex(id: string): number;
        setParameterValueByIndex(index: number, value: number): void;
      };
    };
    expression(name: string): void;
    motion(group: string, index?: number): void;
  }
}
