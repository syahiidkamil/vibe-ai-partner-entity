// Typed event emitter
type EventHandler<T> = (data: T) => void;

export class EventBus<TEventMap extends { [K in keyof TEventMap]: unknown }> {
  private listeners = new Map<keyof TEventMap, Set<EventHandler<any>>>();

  on<K extends keyof TEventMap>(event: K, handler: EventHandler<TEventMap[K]>): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(handler);
  }

  off<K extends keyof TEventMap>(event: K, handler: EventHandler<TEventMap[K]>): void {
    this.listeners.get(event)?.delete(handler);
  }

  once<K extends keyof TEventMap>(event: K, handler: EventHandler<TEventMap[K]>): void {
    const wrapped = (data: TEventMap[K]) => {
      handler(data);
      this.off(event, wrapped);
    };
    this.on(event, wrapped);
  }

  emit<K extends keyof TEventMap>(event: K, data: TEventMap[K]): void {
    this.listeners.get(event)?.forEach(handler => handler(data));
  }

  removeAllListeners(event?: keyof TEventMap): void {
    if (event) {
      this.listeners.delete(event);
    } else {
      this.listeners.clear();
    }
  }
}
