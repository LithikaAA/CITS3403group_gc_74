document.addEventListener('DOMContentLoaded', function() {
    const navHTML = `
        <nav class="fixed top-0 left-0 right-0 bg-white shadow-md py-4 px-6 flex justify-between items-center z-50">
            <a href="/" class="text-xl font-bold text-indigo-600">VibeShare</a>
            <div class="space-x-4">
                <a href="/dashboard" class="text-gray-700 hover:text-indigo-600">Dashboard</a>
                <a href="/upload" class="text-gray-700 hover:text-indigo-600">Upload</a>
                <a href="/share" class="text-gray-700 hover:text-indigo-600">Share</a>
                <a href="/shared" class="text-gray-700 hover:text-indigo-600">Shared With You</a>
                <a href="/logout" class="text-gray-700 hover:text-red-500">Log out</a>
            </div>
        </nav>
        <div class="h-20"></div> <!-- Spacer to prevent content hiding under navbar -->
    `;
    
    const navbarContainer = document.getElementById('navbar-container');
    if (navbarContainer) {
        navbarContainer.innerHTML = navHTML;
    }
});