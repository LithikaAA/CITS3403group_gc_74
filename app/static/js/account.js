// Initialize Feather Icons
document.addEventListener('DOMContentLoaded', function() {
    feather.replace();
    
    // Setup modal functionality
    setupModal();
    
    // Setup gender selection
    setupGenderOptions();
    
    // Setup flash message auto-hide
    setupFlashMessages();
  });
  
  // Modal Controls
  function setupModal() {
    const openBtn = document.getElementById('openChangePassword');
    const closeBtn = document.getElementById('closeChangePassword');
    const overlay = document.getElementById('modalOverlay');
    const modal = document.getElementById('changePasswordModal');
  
    function openModal() {
      overlay.classList.add('active');
      modal.classList.add('active');
    }
  
    function closeModal() {
      modal.classList.remove('active');
      setTimeout(() => {
        overlay.classList.remove('active');
      }, 300); // Wait for the modal transition to finish
    }
  
    if (openBtn) openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (overlay) overlay.addEventListener('click', closeModal);
  }
  
  // Gender Options Enhancement
  function setupGenderOptions() {
    const genderOptions = document.querySelectorAll('.gender-option');
    
    genderOptions.forEach(option => {
      const radio = option.querySelector('input[type="radio"]');
      
      option.addEventListener('click', function() {
        radio.checked = true;
        
        // Remove selected class from all options
        genderOptions.forEach(opt => opt.classList.remove('selected'));
        
        // Add selected class to clicked option
        option.classList.add('selected');
      });
    });
  }
  
  // Flash Message Auto-hide
  function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    // Remove any duplicate flash messages
    const messageTexts = new Set();
    flashMessages.forEach(message => {
      const text = message.textContent.trim();
      
      if (messageTexts.has(text)) {
        // This is a duplicate, remove it
        message.remove();
      } else {
        messageTexts.add(text);
        
        // Add close button to flash message
        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.className = 'flash-close';
        closeBtn.addEventListener('click', () => {
          message.style.opacity = '0';
          message.style.transform = 'translateY(-10px)';
          
          setTimeout(() => {
            message.remove();
          }, 300);
        });
        
        message.appendChild(closeBtn);
      }
    });
    
    // Auto-hide flash messages after 5 seconds
    if (flashMessages.length > 0) {
      setTimeout(() => {
        document.querySelectorAll('.flash-message').forEach(message => {
          message.style.opacity = '0';
          message.style.transform = 'translateY(-10px)';
          
          setTimeout(() => {
            message.remove();
          }, 300);
        });
      }, 5000);
    }
  }