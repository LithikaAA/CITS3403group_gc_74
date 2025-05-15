// Initialize with CSRF token 
document.addEventListener('DOMContentLoaded', function() {
    // Make sure the CSRF token is available for JavaScript
    window.CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                        document.querySelector('input[name="csrf_token"]')?.value;

    if (!window.CSRF_TOKEN) {
        console.warn('CSRF token not found. This may cause form submissions to fail.');
    }

    // Global variables for playlist modal
    let currentPlaylistId = null;
    let currentPlaylistTracks = [];
    let isEditingPlaylist = false;
    
    // Export for upload.js to check
    window.playlistEditor = {
      isEditingPlaylist: function() {
        return isEditingPlaylist;
      },
      loadPlaylist: function(playlistId) {
        openPlaylistModal(playlistId);
      }
    };

    // DOM Elements
    const viewPlaylistsBtn = document.getElementById('view-playlists-btn');
    const closePlaylistsBtn = document.getElementById('close-playlists-btn');
    const playlistsSidebar = document.getElementById('playlists-sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const playlistModal = document.getElementById('playlist-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const modalPlaylistName = document.getElementById('modal-playlist-name');
    const modalSongList = document.getElementById('modal-song-list');
    const addToPlaylistBtn = document.getElementById('add-to-playlist-btn');
    const savePlaylistChangesBtn = document.getElementById('save-playlist-changes-btn');

    // Add createPlaylistCallback for immediate sidebar updates
    window.createPlaylistCallback = function(playlist) {
        // After a playlist is created, add it to the sidebar without reloading
        const playlistsSidebar = document.getElementById('your-playlists-sidebar');
        
        // If there's a "no playlists" message, clear it
        if (playlistsSidebar.querySelector('.empty-playlists')) {
            playlistsSidebar.innerHTML = '';
        }
        
        // Create the new playlist item
        const playlistItem = document.createElement('div');
        playlistItem.className = 'playlist-item';
        playlistItem.dataset.id = playlist.id;
        
        // Create the inner HTML for the playlist item
        playlistItem.innerHTML = `
            <div class="playlist-name">${playlist.name} <span class="song-count">${playlist.tracks.length} songs</span></div>
            <div class="playlist-actions">
                <button class="edit-playlist-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Edit
                </button>
                <button class="delete-playlist-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>
        `;
        
        // Add to the sidebar
        playlistsSidebar.appendChild(playlistItem);
        
        // Add event listeners to the new element
        const editBtn = playlistItem.querySelector('.edit-playlist-btn');
        const deleteBtn = playlistItem.querySelector('.delete-playlist-btn');
        
        // Item click listener to open the modal
        playlistItem.addEventListener('click', function(e) {
            if (e.target.closest('.edit-playlist-btn') || e.target.closest('.delete-playlist-btn')) {
                return;
            }
            
            const playlistId = this.dataset.id;
            const playlistName = this.querySelector('.playlist-name').textContent.split(' ')[0];
            
            closeSidebar();
            openPlaylistModal(playlistId, playlistName);
        });
        
        // Edit button listener
        editBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const playlistItem = this.closest('.playlist-item');
            const playlistId = playlistItem.dataset.id;
            const playlistName = playlistItem.querySelector('.playlist-name').textContent.split(' ')[0];
            
            closeSidebar();
            openPlaylistModal(playlistId, playlistName);
        });
        
        // Delete button listener
        deleteBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const playlistItem = this.closest('.playlist-item');
            const playlistId = playlistItem.dataset.id;
            
            if (confirm('Are you sure you want to delete this playlist?')) {
                // Delete playlist via API
                fetch(`/api/playlist/${playlistId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': window.CSRF_TOKEN
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to delete playlist');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        // Remove from UI with animation
                        playlistItem.style.opacity = '0';
                        playlistItem.style.transform = 'translateX(100px)';
                        
                        setTimeout(() => {
                            playlistItem.remove();
                            
                            // Show empty state if no playlists left
                            if (document.querySelectorAll('.playlist-item').length === 0) {
                                document.getElementById('your-playlists-sidebar').innerHTML = `
                                    <div class="empty-playlists">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                                        </svg>
                                        <h4>No playlists yet</h4>
                                        <p>Create your first playlist by selecting songs and clicking "Create Playlist"</p>
                                    </div>
                                `;
                            }
                        }, 300);
                    } else {
                        alert('Failed to delete playlist.');
                    }
                })
                .catch(error => {
                    console.error('Error deleting playlist:', error);
                    alert('An error occurred while deleting the playlist.');
                });
            }
        });
        
        // Show a notification that the playlist was created
        showToast(`Playlist "${playlist.name}" created with ${playlist.tracks.length} songs!`, 'success');
    };

    // Sidebar toggle functionality
    if (viewPlaylistsBtn) {
        viewPlaylistsBtn.addEventListener('click', function() {
        playlistsSidebar.classList.add('open');
        sidebarOverlay.classList.remove('hidden');
        });
    }

    // Close sidebar
    function closeSidebar() {
        playlistsSidebar.classList.remove('open');
        sidebarOverlay.classList.add('hidden');
    }

    if (closePlaylistsBtn) {
        closePlaylistsBtn.addEventListener('click', closeSidebar);
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // Modal functionality
    function openPlaylistModal(playlistId, playlistName) {
        currentPlaylistId = playlistId;
        isEditingPlaylist = true;
        
        if (!playlistName) {
            const playlistElement = document.querySelector(`.playlist-item[data-id="${playlistId}"] .playlist-name`);
            if (playlistElement) {
                playlistName = playlistElement.textContent.split(' ')[0];
            } else {
                playlistName = "Playlist";
            }
        }
        
        modalPlaylistName.textContent = playlistName;
        loadPlaylistTracks(playlistId);
        playlistModal.classList.add('open');
        
        // Enable modal search functionality
        setupModalSearch();
    }

    function closePlaylistModal() {
        playlistModal.classList.remove('open');
        currentPlaylistId = null;
        currentPlaylistTracks = [];
        isEditingPlaylist = false;
        modalSongList.innerHTML = '';
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closePlaylistModal);
    }

    // Load playlist tracks
    function loadPlaylistTracks(playlistId) {
        // Clear previous tracks
        modalSongList.innerHTML = '';
        
        // Show loading state
        modalSongList.innerHTML = '<div class="py-6 text-center text-gray-500">Loading songs...</div>';
        
        // Fetch playlist tracks from server
        fetch(`/api/playlist/${playlistId}`)
        .then(response => {
            if (!response.ok) {
            throw new Error('Failed to load playlist');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success' && data.playlist && data.playlist.tracks) {
            currentPlaylistTracks = data.playlist.tracks;
            
            // Clear loading state
            modalSongList.innerHTML = '';
            
            if (currentPlaylistTracks.length === 0) {
                modalSongList.innerHTML = '<div class="py-6 text-center text-gray-500">No songs in this playlist yet.</div>';
                return;
            }
            
            // Render tracks
            currentPlaylistTracks.forEach(track => {
                const li = document.createElement('li');
                li.className = 'modal-song-item';
                li.dataset.id = track.id;
                
                // Format duration
                const duration = track.duration_ms ? formatDuration(track.duration_ms) : '0:00';
                
                li.innerHTML = `
                <div class="song-info">
                    <h4 class="song-title">${track.title || 'Unknown Title'}</h4>
                    <p class="song-artist">${track.artist || 'Unknown Artist'}</p>
                    <div class="song-meta">
                    ${track.genre ? `
                        <span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2z" />
                        </svg>
                        ${track.genre}
                        </span>
                    ` : ''}
                    <span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        ${duration}
                    </span>
                    </div>
                </div>
                <button class="song-remove-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
                `;
                
                const removeBtn = li.querySelector('.song-remove-btn');
                removeBtn.addEventListener('click', () => {
                removeSongFromPlaylist(track.id);
                });
                
                modalSongList.appendChild(li);
            });
            
            // Update the sidebar count after loading tracks
            updatePlaylistCount(currentPlaylistId, currentPlaylistTracks.length);
            } else {
            modalSongList.innerHTML = '<div class="py-6 text-center text-red-500">Failed to load playlist tracks.</div>';
            }
        })
        .catch(error => {
            console.error('Error loading playlist tracks:', error);
            modalSongList.innerHTML = '<div class="py-6 text-center text-red-500">An error occurred while loading tracks.</div>';
        });
    }

    // Format duration from milliseconds to MM:SS
    function formatDuration(ms) {
        if (!ms) return '0:00';
        
        const totalSeconds = Math.floor(ms / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    // Remove song from playlist
    function removeSongFromPlaylist(trackId) {
        if (!currentPlaylistId || !trackId) return;
        
        fetch(`/api/playlist/${currentPlaylistId}/remove-track/${trackId}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': window.CSRF_TOKEN,
            'Content-Type': 'application/json'
        }
        })
        .then(response => {
            if (!response.ok) {
            throw new Error('Failed to remove track');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
            // Remove from UI
            const trackElement = modalSongList.querySelector(`li[data-id="${trackId}"]`);
            if (trackElement) {
                trackElement.classList.add('opacity-0');
                setTimeout(() => {
                trackElement.remove();
                
                // Update tracks array
                currentPlaylistTracks = currentPlaylistTracks.filter(track => track.id !== trackId);
                
                // Show empty message if no tracks left
                if (currentPlaylistTracks.length === 0) {
                    modalSongList.innerHTML = '<div class="py-6 text-center text-gray-500">No songs in this playlist yet.</div>';
                }
                
                // Update sidebar count
                updateSidebarPlaylistCount(currentPlaylistId, currentPlaylistTracks.length);
                updatePlaylistCount(currentPlaylistId, currentPlaylistTracks.length);
                }, 300);
            }
            } else {
            alert('Failed to remove track from playlist.');
            }
        })
        .catch(error => {
            console.error('Error removing track:', error);
            alert('An error occurred while removing the track.');
        });
    }

    // Update playlist song count in sidebar
    function updateSidebarPlaylistCount(playlistId, count) {
        const playlistItem = document.querySelector(`.playlist-item[data-id="${playlistId}"]`);
        if (playlistItem) {
        const countBadge = playlistItem.querySelector('.song-count');
        if (countBadge) {
            countBadge.textContent = `${count} songs`;
        }
        }
    }

    // Update playlist count function
    function updatePlaylistCount(playlistId, count) {
        const playlistItem = document.querySelector(`.playlist-item[data-id="${playlistId}"]`);
        if (playlistItem) {
            const countBadge = playlistItem.querySelector('.song-count');
            if (countBadge) {
                countBadge.textContent = `${count} songs`;
            }
        }
    }

    // Show toast notification function
    function showToast(message, type = 'info') {
      // Remove any existing toasts
      const existingToasts = document.querySelectorAll('.toast-notification');
      existingToasts.forEach(toast => toast.remove());
      
      // Create new toast
      const toast = document.createElement('div');
      toast.className = `toast-notification fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' : 
        type === 'error' ? 'bg-red-500 text-white' : 
        'bg-blue-500 text-white'
      }`;
      toast.style.transition = 'opacity 0.5s ease';
      toast.textContent = message;
      document.body.appendChild(toast);
      
      // Fade out and remove
      setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
      }, 3000);
    }

    // Setup modal search functionality
    function setupModalSearch() {
        const modalSearchQuery = document.getElementById('modal-search-query');
        const modalSearchResults = document.getElementById('modal-search-results');
        const modalResultsContainer = document.getElementById('modal-results-container');
        const modalTitle = document.getElementById('modal-title');
        const modalArtist = document.getElementById('modal-artist');
        
        let debounceTimer;
        
        // Search query input handler
        modalSearchQuery.addEventListener('input', function() {
        const query = this.value.trim();
        clearTimeout(debounceTimer);
        
        if (query.length < 2) {
            modalSearchResults.style.display = 'none';
            return;
        }
        
        debounceTimer = setTimeout(() => {
            // Use the same search API as the main search
            fetch(`/api/search-tracks?query=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                modalResultsContainer.innerHTML = '';
                
                if (!data.length) {
                modalResultsContainer.innerHTML = '<li class="p-3 text-center text-gray-500">No results found</li>';
                modalSearchResults.style.display = 'block';
                return;
                }
                
                data.forEach((track) => {
                const li = document.createElement('li');
                li.className = 'result-item';
                li.innerHTML = `
                    <img src="${track.image || '/static/img/default-album.png'}" alt="${track.name}" onerror="this.src='/static/img/default-album.png'">
                    <div class="track-info">
                    <p class="track-name">${track.name}</p>
                    <p class="track-artist">${track.artist}</p>
                    </div>`;
                
                li.addEventListener('click', () => {
                    // Fill the hidden fields
                    modalTitle.value = track.name || '';
                    modalArtist.value = track.artist || '';
                    
                    // Update the search input
                    modalSearchQuery.value = track.name;
                    
                    // Store track data for adding
                    modalSearchQuery.dataset.trackData = JSON.stringify(track);
                    
                    // Enable add button
                    addToPlaylistBtn.disabled = false;
                    
                    // Hide results
                    modalSearchResults.style.display = 'none';
                });
                
                modalResultsContainer.appendChild(li);
                });
                
                modalSearchResults.style.display = 'block';
            })
            .catch(error => {
                console.error('Error searching tracks:', error);
                modalResultsContainer.innerHTML = '<li class="p-3 text-center text-gray-500">Error searching tracks</li>';
                modalSearchResults.style.display = 'block';
            });
        }, 300);
        });
        
        // Add to playlist button handler
        addToPlaylistBtn.addEventListener('click', function() {
        const trackDataString = modalSearchQuery.dataset.trackData;
        
        if (!trackDataString || !currentPlaylistId) {
            console.error('Missing track data or playlist ID');
            return;
        }
        
        try {
            const trackData = JSON.parse(trackDataString);
            
            // Format track data for API
            const trackToAdd = {
            title: trackData.name || modalTitle.value,
            artist: trackData.artist || modalArtist.value,
            album: trackData.album || '',
            genre: trackData.genre || '',
            danceability: trackData.danceability || null,
            energy: trackData.energy || null,
            liveness: trackData.liveness || null,
            acousticness: trackData.acousticness || null,
            valence: trackData.valence || null,
            mode: trackData.mode || null,
            tempo: trackData.tempo || null,
            duration_ms: trackData.duration_ms || 0
            };
            
            // Add to playlist via API
            fetch(`/api/playlist/${currentPlaylistId}/add-track`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.CSRF_TOKEN,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(trackToAdd)
            })
            .then(response => {
                if (!response.ok) {
                throw new Error('Failed to add track');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                // Update the playlist count in the sidebar
                updatePlaylistCount(currentPlaylistId, currentPlaylistTracks.length + 1);
                
                // Reload tracks to show the newly added one
                loadPlaylistTracks(currentPlaylistId);
                
                // Clear search
                modalSearchQuery.value = '';
                modalTitle.value = '';
                modalArtist.value = '';
                modalSearchQuery.dataset.trackData = '';
                
                // Disable add button
                addToPlaylistBtn.disabled = true;
                } else {
                alert('Failed to add track to playlist.');
                }
            })
            .catch(error => {
                console.error('Error adding track:', error);
                alert('An error occurred while adding the track.');
            });
            
        } catch (error) {
            console.error('Error parsing track data:', error);
        }
        });
        
        // Close results when clicking outside
        document.addEventListener('click', function(e) {
        if (!modalSearchResults.contains(e.target) && e.target !== modalSearchQuery) {
            modalSearchResults.style.display = 'none';
        }
        });
    }

    // Save playlist changes button handler
    if (savePlaylistChangesBtn) {
        savePlaylistChangesBtn.addEventListener('click', function() {
        // Simply close the modal since changes are saved in real-time
        closePlaylistModal();
        });
    }

    // Click handler for playlist items
    document.querySelectorAll('.playlist-item').forEach(item => {
        item.addEventListener('click', function(e) {
        // Ignore clicks on buttons
        if (e.target.closest('.edit-playlist-btn') || e.target.closest('.delete-playlist-btn')) {
            return;
        }
        
        const playlistId = this.dataset.id;
        const playlistName = this.querySelector('.playlist-name').textContent.split(' ')[0]; // Get just the name without song count
        
        // Close sidebar
        closeSidebar();
        
        // Open modal
        openPlaylistModal(playlistId, playlistName);
        });
    });

    // Edit button click handler
    document.querySelectorAll('.edit-playlist-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
        e.stopPropagation(); // Prevent playlist item click
        
        const playlistItem = this.closest('.playlist-item');
        const playlistId = playlistItem.dataset.id;
        const playlistName = playlistItem.querySelector('.playlist-name').textContent.split(' ')[0];
        
        // Close sidebar
        closeSidebar();
        
        // Open modal
        openPlaylistModal(playlistId, playlistName);
        });
    });

    // Delete button click handler
    document.querySelectorAll('.delete-playlist-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
        e.stopPropagation(); // Prevent playlist item click
        
        const playlistItem = this.closest('.playlist-item');
        const playlistId = playlistItem.dataset.id;
        
        if (confirm('Are you sure you want to delete this playlist?')) {
            // Delete playlist via API
            fetch(`/api/playlist/${playlistId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': window.CSRF_TOKEN
            }
            })
            .then(response => {
                if (!response.ok) {
                throw new Error('Failed to delete playlist');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                // Remove from UI with animation
                playlistItem.style.opacity = '0';
                playlistItem.style.transform = 'translateX(100px)';
                
                setTimeout(() => {
                    playlistItem.remove();
                    
                    // Show empty state if no playlists left
                    if (document.querySelectorAll('.playlist-item').length === 0) {
                    document.getElementById('your-playlists-sidebar').innerHTML = `
                        <div class="empty-playlists">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                        </svg>
                        <h4>No playlists yet</h4>
                        <p>Create your first playlist by selecting songs and clicking "Create Playlist"</p>
                        </div>
                    `;
                    }
                }, 300);
                } else {
                alert('Failed to delete playlist.');
                }
            })
            .catch(error => {
                console.error('Error deleting playlist:', error);
                alert('An error occurred while deleting the playlist.');
            });
        }
        });
    });
});