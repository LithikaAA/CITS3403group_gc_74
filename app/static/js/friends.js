/**
 * friends.js - JavaScript for the VibeShare friend visualization
 */

document.addEventListener('DOMContentLoaded', () => {
  initializeBubbles();
  initializeFriendPanel();
  initializeTabSwitching();
});

/**
 * Initialize the center bubble and friend bubbles
 */
function initializeBubbles() {
  const center = document.getElementById('center-bubble');
  const svg = document.getElementById('link-lines');
  const bubbles = Array.from(document.querySelectorAll('.friend-bubble'));
  const lines = bubbles.map((_, i) => document.getElementById(`line-${i}`));
  const removeButtons = document.querySelectorAll('.remove-friend-btn');
  
  // Get user BPM from hidden input
  const userBpm = parseFloat(document.getElementById('user-bpm-data').value || 0);
  
  console.log("Found bubbles:", bubbles.length);

  // Handle remove friend button clicks
  removeButtons.forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation(); // Prevent event from bubbling
      const username = btn.dataset.username;
      if (confirm(`Are you sure you want to remove ${username} from your friends?`)) {
        removeFriend(username);
      }
    });
  });

  // Central user bubble click - go to dashboard
  center.addEventListener('click', () => window.location.href = '/dashboard');

  // Position and animate the friend bubbles
  positionBubbles(bubbles, userBpm);
  
  // Update connection lines between bubbles
  animateLines(center, bubbles, lines);
}

/**
 * Position the friend bubbles in an orbit based on BPM difference
 * @param {Array} bubbles - Array of friend bubble elements
 * @param {number} userBpm - User's BPM value
 */
function positionBubbles(bubbles, userBpm) {
  // Calculate BPM differences to determine bubble positions
  const diffs = bubbles.map(b => Math.abs(userBpm - (parseFloat(b.dataset.bpm) || 0)));
  const maxDiff = Math.max(...diffs, 1);

  bubbles.forEach((bubble, idx) => {
    const diff = diffs[idx];
    const t = diff / maxDiff;
    const minR = 150, maxR = 280;
    const radius = minR + t * (maxR - minR);
    const maxS = 100, minS = 60;
    const size = maxS - t * (maxS - minS);
    
    // Set bubble size
    bubble.style.width = `${size}px`;
    bubble.style.height = `${size}px`;

    // Calculate position on the orbit
    const angleRad = (idx * 2 * Math.PI / bubbles.length) - Math.PI/2;
    const tx = Math.cos(angleRad) * radius;
    const ty = Math.sin(angleRad) * radius;
    bubble.style.setProperty('--tx', `${tx}px`);
    bubble.style.setProperty('--ty', `${ty}px`);

    // Animate bubble into position without staggered delay
    setTimeout(() => {
      bubble.style.opacity = '1';
      bubble.style.transform = `translate(-50%, -50%) translate(${tx}px, ${ty}px)`;
      bubble.classList.add('idle');
    }, 50); // Fixed short delay for all bubbles

    // Add hover effects
    setupBubbleHoverEffects(bubble, tx, ty);
  });
}

/**
 * Set up hover effects for a bubble
 * @param {Element} bubble - The bubble element
 * @param {number} tx - X translation value
 * @param {number} ty - Y translation value
 */
function setupBubbleHoverEffects(bubble, tx, ty) {
  bubble.addEventListener('mouseenter', () => {
    // Don't change position, only scale up
    bubble.style.transform = `translate(-50%, -50%) translate(${tx}px, ${ty}px) scale(1.15)`;
    bubble.style.zIndex = '20';
    
    // Force show the remove button
    const removeBtn = bubble.querySelector('.remove-friend-btn');
    if (removeBtn) {
      removeBtn.style.opacity = '1';
    }
  });
  
  bubble.addEventListener('mouseleave', () => {
    // Return to original size without changing position
    bubble.style.transform = `translate(-50%, -50%) translate(${tx}px, ${ty}px)`;
    bubble.style.zIndex = '10';
    
    // Hide the remove button
    const removeBtn = bubble.querySelector('.remove-friend-btn');
    if (removeBtn) {
      removeBtn.style.opacity = '0';
    }
  });
}

/**
 * Animate the connection lines between the center and friend bubbles
 * @param {Element} center - Center bubble element
 * @param {Array} bubbles - Array of friend bubble elements
 * @param {Array} lines - Array of SVG line elements
 */
function animateLines(center, bubbles, lines) {
  function updateLines() {
    const sRect = document.getElementById('link-lines').getBoundingClientRect();
    const cRect = center.getBoundingClientRect();
    const cx = cRect.left + cRect.width/2 - sRect.left;
    const cy = cRect.top + cRect.height/2 - sRect.top;
    
    bubbles.forEach((b, i) => {
      const br = b.getBoundingClientRect();
      const fx = br.left + br.width/2 - sRect.left;
      const fy = br.top + br.height/2 - sRect.top;
      const line = lines[i];
      if (line) {
        line.setAttribute('x1', cx);
        line.setAttribute('y1', cy);
        line.setAttribute('x2', fx);
        line.setAttribute('y2', fy);
      }
    });
    
    requestAnimationFrame(updateLines);
  }
  
  requestAnimationFrame(updateLines);
}

/**
 * Initialize the sliding friends panel
 */
function initializeFriendPanel() {
  const viewAllBtn = document.getElementById('view-all-friends-btn');
  const friendsPanel = document.getElementById('friends-panel');
  const closeBtn = document.getElementById('close-friends-panel');

  viewAllBtn.addEventListener('click', () => {
    friendsPanel.classList.remove('translate-x-full');
  });
  
  closeBtn.addEventListener('click', () => {
    friendsPanel.classList.add('translate-x-full');
  });
}

/**
 * Initialize tab switching in the friends panel
 */
function initializeTabSwitching() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-tab');

      // Switch tab content
      tabContents.forEach(c => c.classList.add('hidden'));
      document.getElementById(`tab-${target}`).classList.remove('hidden');

      // Update button styles to match the screenshot
      tabButtons.forEach(b => {
        b.classList.remove('bg-white', 'text-purple-600', 'shadow-sm', 'active');
        b.classList.add('text-gray-500');
      });
      btn.classList.remove('text-gray-500');
      btn.classList.add('bg-white', 'text-purple-600', 'shadow-sm', 'active');
    });
  });
}

/**
 * Remove a friend
 * @param {string} username - Username of the friend to remove
 */
function removeFriend(username) {
  fetch(`/friends/remove/${username}`, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
  .then(res => {
    if (res.ok) {
      window.location.reload();
    } else {
      alert("Failed to remove friend");
    }
  })
  .catch(err => {
    console.error("Error removing friend:", err);
    alert("An error occurred while trying to remove friend");
  });
}

/**
 * Display a flash message
 * @param {string} message - Message text
 * @param {string} category - Message category (success or error)
 */
function showFlashMessage(message, category = 'success') {
  const container = document.createElement('div');
  container.className = 'absolute top-4 right-4 space-y-2 z-50';
  
  const messageEl = document.createElement('div');
  messageEl.className = `px-4 py-2 rounded-xl shadow-lg text-white flash-message ${
    category === 'success' ? 'bg-green-500' : 'bg-red-500'
  }`;
  messageEl.textContent = message;
  
  container.appendChild(messageEl);
  document.body.appendChild(container);
  
  // Remove after 3 seconds
  setTimeout(() => {
    container.remove();
  }, 3000);
}

/**
 * Add subtle animation to the BPM matches text (optional)
 */
function enhanceBPMMatchesText() {
  const bpmText = document.querySelector('.absolute.bottom-8 .text-purple-600');
  if (bpmText) {
    // This is now handled in CSS, but could be extended further with JS if needed
  }
}