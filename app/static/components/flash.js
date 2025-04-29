export function enableFlashDismiss() {
  document.querySelectorAll('.flash-message').forEach(msg => {
    msg.addEventListener('click', () => msg.remove());
  });
}
