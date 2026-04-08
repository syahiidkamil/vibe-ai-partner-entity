export class SpeechBubble {
  private el: HTMLElement;
  constructor() { this.el = document.getElementById("speech-bubble")!; }
  show(text?: string) {
    if (text) this.el.textContent = text;
    this.el.classList.add("visible");
  }
  hide() { this.el.classList.remove("visible"); this.el.textContent = ""; }
}
