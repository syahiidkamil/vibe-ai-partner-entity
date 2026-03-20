import { RendererHost } from "./renderer-host.js";
import { WSClient } from "./ws-client.js";
import { EventLoop } from "./event-loop.js";
import { SpeechBubble } from "./ui/speech-bubble.js";
import { ContextMenu } from "./ui/context-menu.js";

export interface AppConfig {
  ttsServerUrl: string;
  wsStatusUrl: string;
  renderer: string;
  modelPath: string;
}

export class App {
  private config: AppConfig;
  private rendererHost: RendererHost;
  private wsClient: WSClient;
  private eventLoop: EventLoop;
  private speechBubble: SpeechBubble;
  private contextMenu: ContextMenu;

  constructor(config: AppConfig) {
    this.config = config;
    this.rendererHost = new RendererHost();
    this.wsClient = new WSClient(config.wsStatusUrl);
    this.eventLoop = new EventLoop();
    this.speechBubble = new SpeechBubble();
    this.contextMenu = new ContextMenu(config.ttsServerUrl);
  }

  async start() {
    // Mount renderer
    const container = document.getElementById("avatar-container")!;
    await this.rendererHost.mount(container, this.config.modelPath);

    // Wire WebSocket events to renderer
    this.wsClient.onMessage((msg) => {
      if (msg.type === "amplitude") {
        this.rendererHost.setLipSyncAmplitude(msg.value);
      } else if (msg.type === "feeling") {
        this.rendererHost.setFeeling(msg.name, 80);
      } else if (msg.type === "action") {
        this.rendererHost.playSelfExpression(msg.name);
      } else if (msg.type === "state") {
        if (msg.mode === "speaking") this.speechBubble.show();
        else this.speechBubble.hide();
      }
    });

    // Start event loop
    this.eventLoop.start((deltaTime) => {
      this.rendererHost.update(deltaTime);
    });

    // Connect WebSocket
    this.wsClient.connect();

    // Init context menu
    this.contextMenu.init();
  }
}
