type MessageHandler = (msg: any) => void;

export class WSClient {
  private url: string;
  private ws: WebSocket | null = null;
  private handlers: MessageHandler[] = [];
  private reconnectMs = 1000;
  private maxReconnectMs = 30000;
  private intentionalClose = false;

  constructor(url: string) { this.url = url; }

  onMessage(handler: MessageHandler) { this.handlers.push(handler); }

  connect() {
    this.intentionalClose = false;
    this.tryConnect();
  }

  private tryConnect() {
    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => { this.reconnectMs = 1000; console.log("WS connected"); };
    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        this.handlers.forEach(h => h(msg));
      } catch { /* ignore parse errors */ }
    };
    this.ws.onclose = () => {
      if (this.intentionalClose) return;
      const delay = this.reconnectMs + Math.random() * 500;
      this.reconnectMs = Math.min(this.reconnectMs * 2, this.maxReconnectMs);
      setTimeout(() => this.tryConnect(), delay);
    };
    this.ws.onerror = () => { this.ws?.close(); };
  }

  disconnect() { this.intentionalClose = true; this.ws?.close(); }
}
