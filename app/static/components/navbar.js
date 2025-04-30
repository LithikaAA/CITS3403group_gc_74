document.addEventListener('DOMContentLoaded', function () {
    const navHTML = `
      <aside id="sidebar" class="fixed top-0 left-0 h-full w-52 bg-white shadow-md z-50 flex-col py-8 px-4 space-y-6 hidden md:flex animate-fade-in">
        <a href="/" class="text-2xl font-bold text-indigo-600 mb-6">VibeShare</a>
        <nav class="flex flex-col gap-4 text-sm">
          <a href="/dashboard" class="nav-item" data-path="/dashboard">
            <i data-feather="home"></i><span>Dashboard</span>
          </a>
          <a href="/upload" class="nav-item" data-path="/upload">
            <i data-feather="plus-square"></i><span>Add Data</span>
          </a>
          <a href="/share/shared" class="nav-item" data-path="/share/shared">
            <i data-feather="eye"></i><span>View Data</span>
          </a>
          <a href="/share" class="nav-item" data-path="/share">
            <i data-feather="share-2"></i><span>Share</span>
          </a>
  
        <!-- Account Section -->
        <div class="mt-10 border-t pt-4 border-gray-300">
            <p class="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Account</p>
            <a href="/auth/account-setup" class="nav-item" data-path="/auth/account-setup">
                <i data-feather="user"></i><span>Account Settings</span>
            </a>
        </div>
        </nav>
      </aside>
      <div class="pt-20 md:ml-52"></div>
    `;
  
    const navbarContainer = document.getElementById('navbar-container');
    if (navbarContainer) {
      navbarContainer.innerHTML = navHTML;
      feather.replace();
  
      // Apply base classes to all nav items
      navbarContainer.querySelectorAll('.nav-item').forEach(link => {
        link.classList.add(
          "flex", "items-center", "space-x-3", "text-gray-700",
          "hover:text-indigo-600", "hover:bg-gradient-to-r",
          "hover:from-indigo-400", "hover:to-pink-400",
          "hover:text-white", "px-4", "py-2",
          "rounded-full", "transition", "duration-200"
        );
      });
  
      // Highlight current path: longest-prefix match wins
      const path = window.location.pathname;
      const items = Array.from(navbarContainer.querySelectorAll('.nav-item'));
      items.sort((a, b) => b.getAttribute('data-path').length - a.getAttribute('data-path').length);
      for (const link of items) {
        if (path.startsWith(link.getAttribute('data-path'))) {
          link.classList.add('nav-active');
          break;
        }
      }
    }
  });
