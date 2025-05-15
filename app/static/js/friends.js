window.addEventListener('DOMContentLoaded', () => {
  const center  = document.getElementById('center-bubble');
  const svg     = document.getElementById('link-lines');
  const bubbles = Array.from(document.querySelectorAll('.friend-bubble'));
  const lines   = bubbles.map((_, i) => document.getElementById(`line-${i}`));
  lines.forEach(line => {
    if (line) {
      if (window.innerWidth >= 1600) {
        line.setAttribute('stroke-width', '2.5');
      } else if (window.innerWidth >= 1024) {
        line.setAttribute('stroke-width', '1.5');
      } else {
        line.setAttribute('stroke-width', '1');
      }
    }
  });

  const menu           = document.getElementById('friend-menu');
  const menuUsername   = document.getElementById('friend-menu-username');
  const viewDataBtn    = document.getElementById('view-data-btn');
  const removeFriendBtn= document.getElementById('remove-friend-btn');
  console.log("Found bubbles:", bubbles.length);

  // When any bubble is clicked, show the menu
  bubbles.forEach(bubble => {
    bubble.addEventListener('click', e => {
      e.stopPropagation();

      const username = bubble.dataset.username;
      const rect = bubble.getBoundingClientRect();

      // Position relative to the bubble's parent container
      const containerRect = bubble.offsetParent.getBoundingClientRect();
      const x = rect.left - containerRect.left + rect.width + 10;
      const y = rect.top - containerRect.top;

      menu.style.left = `${x}px`;
      menu.style.top = `${y}px`;

      menuUsername.textContent = username;
      menu.classList.remove('hidden');

      // Attach button events
      viewDataBtn.onclick = () => {
        window.location.href = "/share/shared";
      };

      removeFriendBtn.onclick = () => {
        const username = menuUsername.textContent;
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        fetch(`/friends/remove/${username}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken, // Flask-WTF expects this
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify({}) // must include a body to avoid 400 Bad Request
        })
        .then(res => {
          if (res.ok) {
            window.location.reload();
          } else {
            alert("Failed to remove friend");
          }
        });
      };
    });
  });

  // Hide menu if you click anywhere else
  document.body.addEventListener('click', () => {
    menu.classList.add('hidden');
  });
  
  // But don't hide if you click inside the menu
  menu.addEventListener('click', e => e.stopPropagation());

  // Central user bubble click - go to dashboard
  center.addEventListener('click', () => window.location.href = '/dashboard');

  // BPM logic
  const userBpm = parseFloat(center.dataset.userBpm) || 0;
  const diffs   = bubbles.map(b => Math.abs(userBpm - (parseFloat(b.dataset.bpm)||0)));
  const maxDiff = Math.max(...diffs, 1);

  bubbles.forEach((bubble, idx) => {
    const radius = 180;  // Fixed radius for all bubbles
    const size   = 100;  // Fixed size for all bubbles

    bubble.style.width  = `${size}px`;
    bubble.style.height = `${size}px`;

    const angleRad = (idx * 2 * Math.PI / bubbles.length) - Math.PI / 2;
    const tx       = Math.cos(angleRad) * radius;
    const ty       = Math.sin(angleRad) * radius;

    bubble.style.setProperty('--tx', `${tx}px`);
    bubble.style.setProperty('--ty', `${ty}px`);

    // Animate out
    setTimeout(() => {
      bubble.style.opacity   = '1';
      bubble.style.transform = `translate(-50%, -50%) translate(${tx}px, ${ty}px)`;
      bubble.classList.add('idle');
    }, idx * 100);

    // Hover enlarge
    const hoverFactor = 1.3;
    bubble.addEventListener('mouseenter', () => {
      bubble.classList.remove('idle');
      bubble.style.transform = `translate(-50%, -50%) translate(${tx * hoverFactor}px, ${ty * hoverFactor}px) scale(1.15)`;
      bubble.style.zIndex = '20';
    });
    bubble.addEventListener('mouseleave', () => {
      bubble.classList.add('idle');
      bubble.style.transform = `translate(-50%, -50%) translate(${tx}px, ${ty}px)`;
      bubble.style.zIndex = '10';
    });
  });


  // update lines
  function updateLines() {
    const sRect = svg.getBoundingClientRect();
    const cRect = center.getBoundingClientRect();
    const cx    = cRect.left + cRect.width/2 - sRect.left;
    const cy    = cRect.top  + cRect.height/2 - sRect.top;
    bubbles.forEach((b,i) => {
      const br = b.getBoundingClientRect();
      const fx = br.left + br.width/2 - sRect.left;
      const fy = br.top  + br.height/2 - sRect.top;
      const line = lines[i];
      if(line) {
        line.setAttribute('x1', cx);
        line.setAttribute('y1', cy);
        line.setAttribute('x2', fx);
        line.setAttribute('y2', fy);
      }
    });
    requestAnimationFrame(updateLines);
  }
  requestAnimationFrame(updateLines);
});

// Toggle right-side overlay
const viewAllBtn = document.getElementById('view-all-friends-btn');
const overlay    = document.getElementById('all-friends-overlay');
const closeBtn   = document.getElementById('close-all-friends');

// Slide panel toggle
document.getElementById("view-all-friends-btn").addEventListener("click", () => {
  document.getElementById("friends-panel").classList.remove("translate-x-full");
});
document.getElementById("close-friends-panel").addEventListener("click", () => {
  document.getElementById("friends-panel").classList.add("translate-x-full");
});

// Tabs switching logic
const tabButtons = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const target = btn.getAttribute("data-tab");

    // Switch tab content
    tabContents.forEach(c => c.classList.add("hidden"));
    document.getElementById(`tab-${target}`).classList.remove("hidden");

    // Update button styles
    tabButtons.forEach(b => b.classList.remove("bg-indigo-100"));
    btn.classList.add("bg-indigo-100");
  });
});
