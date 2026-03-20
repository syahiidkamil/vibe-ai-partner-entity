const FEELINGS = ["happy","sad","frustrated","curious","proud","anxious","excited","calm","bored","guilty","angry","blushing","surprised","relieved"];
const ACTIONS = ["wave","nod","headTilt","laugh","sigh","celebrate","gasp","think","bow","headshake","giggle","sweat"];

export class ContextMenu {
  private el: HTMLElement;
  private ttsUrl: string;

  constructor(ttsUrl: string) {
    this.el = document.getElementById("context-menu")!;
    this.ttsUrl = ttsUrl;
  }

  init() {
    document.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      this.show(e.clientX, e.clientY);
    });
    document.addEventListener("click", () => this.hide());
  }

  private show(x: number, y: number) {
    this.el.innerHTML = this.buildMenu();
    this.el.style.left = `${Math.min(x, window.innerWidth - 200)}px`;
    this.el.style.top = `${Math.min(y, window.innerHeight - 300)}px`;
    this.el.classList.add("visible");
  }

  private hide() { this.el.classList.remove("visible"); }

  private buildMenu(): string {
    const feelingsItems = FEELINGS.map(f =>
      `<div class="item" onclick="fetch('${this.ttsUrl}/api/feeling',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:'${f}'})})">${f}</div>`
    ).join("");
    const actionsItems = ACTIONS.map(a =>
      `<div class="item" onclick="fetch('${this.ttsUrl}/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:'${a}'})})">${a}</div>`
    ).join("");
    return `
      <div class="submenu">
        <div class="item">Feelings &#9656;</div>
        <div class="submenu-content">${feelingsItems}</div>
      </div>
      <div class="separator"></div>
      <div class="submenu">
        <div class="item">Actions &#9656;</div>
        <div class="submenu-content">${actionsItems}</div>
      </div>
    `;
  }
}
