export class Toast {
  constructor() {
    this.container = document.createElement('div');
    this.container.className = 'toast-container fixed top-4 right-4 z-50';
    document.body.appendChild(this.container);
  }
  show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast bg-${type === 'error' ? 'red' : 'green'}-500 text-white px-4 py-2 rounded mb-2 shadow`;
    toast.textContent = message;
    this.container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
  }
}
