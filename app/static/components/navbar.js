document.addEventListener('DOMContentLoaded', function () {
  const navHTML = `
    <aside id="sidebar" class="fixed top-0 left-0 h-full w-72 bg-white shadow-md z-50 flex-col py-4 px-4 space-y-6 hidden md:flex animate-fade-in">
      <img src="/static/img/side_logo.png" alt="VibeShare Logo" class="mb-6" style="max-width: 100%; height: auto; width: 200px;" />
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
        <a href="/add-friend" class="nav-item" data-path="/add-friend">
          <i data-feather="user-plus"></i><span>Add Friend</span>
        </a>
      </nav>

      <!-- Account Section at bottom -->
      <div class="mt-auto border-t pt-4 border-gray-300">
        <a href="{{ url_for('auth.account_setup') }}" class="flex items-center space-x-3 px-4 py-3 hover:bg-gray-100 rounded-lg transition">
          <img src="{{ url_for('static', filename='uploads/' ~ (current_user.profile_pic or 'default_profile.jpg')) }}"
              alt="Profile Picture"
              class="w-10 h-10 rounded-full object-cover border" />
          <span class="text-gray-700 font-semibold">{{ current_user.username }}</span>
        </a>
      </div>

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
        "rounded-full", "transition", "duration-200", "text-lg"
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
