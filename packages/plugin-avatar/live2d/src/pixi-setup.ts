import * as PIXI from "pixi.js";

export interface PixiAppHandle {
  app: PIXI.Application;
  destroy(): void;
}

/**
 * Create a transparent PixiJS application inside a container element.
 *
 * Ported from submodule index.html:
 *   new PIXI.Application({ view: canvas, transparent: true, width: 280, height: 400, ... })
 *
 * Changes from submodule:
 *   - Creates its own canvas (no pre-existing <canvas> element required)
 *   - Container-based sizing instead of fixed 280x400
 *   - Returns a handle for clean destruction
 */
export function createPixiApp(
  container: HTMLElement,
  width: number,
  height: number,
): PixiAppHandle {
  const app = new PIXI.Application({
    width,
    height,
    backgroundAlpha: 0, // transparent background
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
  });

  // PixiJS 7 creates its own canvas. Append it to the container.
  container.appendChild(app.view as HTMLCanvasElement);

  return {
    app,
    destroy() {
      app.destroy(true, { children: true, texture: true, baseTexture: true });
    },
  };
}
