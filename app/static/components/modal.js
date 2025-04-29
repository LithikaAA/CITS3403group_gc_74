export class Modal {
  constructor(selector) {
    this.modal = document.querySelector(selector);
    this.closeBtn = this.modal.querySelector('.modal-close');
    this.init();
  }

  init() {
    this.closeBtn.addEventListener('click', () => this.hide());
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.hide();
    });
  }

  show() {
    this.modal.classList.remove('hidden');
  }

  hide() {
    this.modal.classList.add('hidden');
  }
}
