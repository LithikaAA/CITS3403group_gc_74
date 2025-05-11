document.addEventListener("DOMContentLoaded", function () {
  // Helper function to get cookie by name
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  
  const queryInput = document.getElementById("search-query");
  const resultsBox = document.getElementById("searchResults");
  const resultsContainer = document.getElementById("resultsContainer");
  const songList = document.getElementById("song-list");
  const addedSongsSection = document.getElementById("added-songs");
  const playlistOutput = document.getElementById("playlist-output");
  const playlistContainer = document.getElementById("playlist-container");
  const playlistNameInput = document.getElementById("playlist-name");

  let selectedTracks = [];
  let debounceTimer;
  let selectedIndex = -1;

  queryInput.addEventListener("input", function () {
    const query = this.value.trim();
    clearTimeout(debounceTimer);
    selectedIndex = -1;

    if (query.length < 2) {
      resultsBox.style.display = "none";
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/api/search-tracks?query=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          resultsContainer.innerHTML = "";

          if (!data.length) {
            resultsContainer.innerHTML = '<li class="result-item text-center text-gray-500">No results found</li>';
            resultsBox.style.display = "block";
            return;
          }

          data.forEach((track) => {
            const li = document.createElement("li");
            li.className = "result-item";
            li.innerHTML = `
              <img src="${track.image || '/static/img/default-album.png'}" alt="${track.name}" onerror="this.src='/static/img/default-album.png'">
              <div class="track-info">
                <p class="track-name">${track.name}</p>
                <p class="track-artist">${track.artist}</p>
              </div>`;
            li.addEventListener("click", () => {
              queryInput.value = track.name;
              fillFormFields(track);
              resultsBox.style.display = "none";
            });
            resultsContainer.appendChild(li);
          });

          resultsBox.style.display = "block";
        })
        .catch(error => {
          console.error("Error searching tracks:", error);
          resultsContainer.innerHTML = '<li class="result-item text-center text-gray-500">Error searching tracks</li>';
          resultsBox.style.display = "block";
        });
    }, 300);
  });

  function fillFormFields(track) {
    document.getElementById("title").value = track.name || "";
    document.getElementById("artist").value = track.artist || "";
    document.getElementById("album").value = track.album || "";
    document.getElementById("genre").value = track.genre || "";
    document.getElementById("danceability").value = track.danceability ?? "";
    document.getElementById("energy").value = track.energy ?? "";
    document.getElementById("liveness").value = track.liveness ?? "";
    document.getElementById("acousticness").value = track.acousticness ?? "";
    document.getElementById("valence").value = track.valence ?? "";
    document.getElementById("mode").value = track.mode || "";
    document.getElementById("tempo").value = track.tempo ?? "";
    document.getElementById("duration_ms").value = track.duration_ms ?? "";
  }

  function displaySelectedSong(track) {
    if (document.getElementById(`song-${track.id}`)) return;

    const songItem = document.createElement("li");
    songItem.className = "bg-white shadow rounded p-4 flex items-center justify-between";
    songItem.id = `song-${track.id}`;

    const left = document.createElement("div");
    left.className = "flex items-center gap-4";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "form-checkbox h-5 w-5 text-blue-500";
    checkbox.checked = true; // Auto-check newly added songs
    checkbox.addEventListener("change", updatePlaylistButtonState);

    const details = document.createElement("div");
    details.innerHTML = `
      <p class="font-semibold">${track.name} <span class="text-gray-600">by</span> ${track.artist}</p>
      <p class="text-sm text-gray-500">Album: ${track.album || 'Unknown'}${track.genre ? ` | Genre: ${track.genre}` : ''}</p>
    `;

    left.appendChild(checkbox);
    left.appendChild(details);

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "Remove";
    removeBtn.className = "text-sm text-red-500 hover:underline";

    const right = document.createElement("div");
    right.appendChild(removeBtn);

    songItem.appendChild(left);
    songItem.appendChild(right);
    songList.appendChild(songItem);
    addedSongsSection.classList.remove("hidden");
    
    // Update the button state when a new song is added
    updatePlaylistButtonState();
  }

  songList.addEventListener("click", function (e) {
    if (e.target.tagName === "BUTTON" && e.target.textContent === "Remove") {
      const li = e.target.closest("li");
      if (li) {
        const trackId = li.id.replace("song-", "");
        li.remove();
        selectedTracks = selectedTracks.filter(t => t.id !== trackId);
        updatePlaylistButtonState();
        
        // Hide the added songs section if no songs are left
        if (selectedTracks.length === 0) {
          addedSongsSection.classList.add("hidden");
        }
      }
    }
  });

  document.getElementById("add-track-btn").addEventListener("click", function () {
    const title = document.getElementById("title").value.trim();
    const artist = document.getElementById("artist").value.trim();
    
    if (!title || !artist) {
      alert("Please add at least a title and artist for the track.");
      return;
    }
    
    const track = {
      id: `${title}-${artist}`.replace(/\s+/g, '-').toLowerCase(),
      name: title,
      artist: artist,
      album: document.getElementById("album").value.trim(),
      genre: document.getElementById("genre").value.trim(),
      danceability: document.getElementById("danceability").value.trim(),
      energy: document.getElementById("energy").value.trim(),
      liveness: document.getElementById("liveness").value.trim(),
      acousticness: document.getElementById("acousticness").value.trim(),
      valence: document.getElementById("valence").value.trim(),
      mode: document.getElementById("mode").value.trim(),
      tempo: document.getElementById("tempo").value.trim(),
      duration_ms: document.getElementById("duration_ms").value.trim() || "0"
    };

    if (selectedTracks.some(t => t.id === track.id)) {
      alert("This song has already been added to the playlist.");
      return;
    }

    selectedTracks.push(track);
    displaySelectedSong(track);
    
    // Clear the form fields after adding
    document.getElementById("title").value = "";
    document.getElementById("artist").value = "";
    document.getElementById("album").value = "";
    document.getElementById("genre").value = "";
    document.getElementById("danceability").value = "";
    document.getElementById("energy").value = "";
    document.getElementById("liveness").value = "";
    document.getElementById("acousticness").value = "";
    document.getElementById("valence").value = "";
    document.getElementById("mode").value = "";
    document.getElementById("tempo").value = "";
    document.getElementById("duration_ms").value = "";
    
    // Clear the search query input
    queryInput.value = "";
  });
  
  document.getElementById("create-playlist-btn").addEventListener("click", function () {
    const playlistName = document.getElementById("playlist-name").value.trim();
    if (!playlistName) {
      alert("Please enter a playlist name.");
      return;
    }

    const checkedBoxes = document.querySelectorAll("#song-list input[type='checkbox']:checked");
    if (checkedBoxes.length < 2) {
      alert("Please select at least 2 songs for your playlist.");
      return;
    }

    const checkedIds = Array.from(checkedBoxes).map(cb => cb.closest("li").id.replace("song-", ""));
    const tracksToSend = selectedTracks.filter(t => checkedIds.includes(t.id));
    
    // Validate tracks data before sending
    if (!tracksToSend.length) {
      alert("No valid tracks selected. Please try again.");
      return;
    }
    
    // Format the data according to what the server expects
    const formattedTracks = tracksToSend.map(track => {
      // Create a clean copy to avoid any unexpected properties
      return {
        title: track.name || "",
        artist: track.artist || "",
        album: track.album || "",
        genre: track.genre || "",
        // Convert strings to numbers with fallbacks
        danceability: parseFloat(track.danceability) || null,
        energy: parseFloat(track.energy) || null,
        liveness: parseFloat(track.liveness) || null,
        acousticness: parseFloat(track.acousticness) || null,
        valence: parseFloat(track.valence) || null,
        mode: track.mode || null,
        tempo: parseFloat(track.tempo) || null,
        duration_ms: parseInt(track.duration_ms) || 0
      };
    });

    // Show loading indicator
    const button = document.getElementById("create-playlist-btn");
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = "Creating...";
    
    // Show a processing message to the user
    const statusElement = document.createElement("div");
    statusElement.className = "mt-2 text-sm text-blue-600";
    statusElement.textContent = "Processing your request...";
    button.parentNode.appendChild(statusElement);

    // Get CSRF token from various possible sources
    const csrfToken = window.CSRF_TOKEN || 
                      document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                      document.querySelector('input[name="csrf_token"]')?.value || 
                      getCookie('csrf_token');
                      
    if (!csrfToken) {
      console.warn("CSRF token not found. This may cause form submissions to fail.");
    }
    
    // Debug info
    console.log("Sending request to create playlist");
    console.log("Playlist name:", playlistName);
    console.log("Number of tracks:", formattedTracks.length);
    
    // Send the request
    fetch("/upload/create-playlist", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        // Include the CSRF token in the request headers
        "X-CSRFToken": csrfToken || "",
        "X-XSRF-TOKEN": csrfToken || "",
        "CSRF-Token": csrfToken || ""
      },
      // Include credentials to ensure cookies are sent with the request
      credentials: "same-origin",
      body: JSON.stringify({ 
        playlist_name: playlistName, 
        tracks: formattedTracks 
      })
    })
    .then(res => {
      // Parse response as text first to get the raw response
      return res.text().then(text => {
        if (!res.ok) {
          // Parse the error if it's JSON
          try {
            const errorData = JSON.parse(text);
            throw new Error(`Server error (${res.status}): ${errorData.message || "Unknown error"}`);
          } catch (e) {
            // If it's not valid JSON, use the raw text
            if (e instanceof SyntaxError) {
              throw new Error(`Server error (${res.status}): ${text}`);
            }
            throw e;
          }
        }
        
        // Try to parse as JSON for valid responses
        try {
          return JSON.parse(text);
        } catch (e) {
          console.error("Invalid JSON response:", text);
          throw new Error("Server returned invalid JSON response");
        }
      });
    })
    .then(data => {
      if (data.status === "success") {
        // Update status message
        statusElement.textContent = "Playlist created successfully!";
        statusElement.className = "mt-2 text-sm text-green-600";
        
        // Show the playlist
        displaySimilarSongGroups(data.playlist);
        document.getElementById("playlist-name").value = "";
        
        // Optionally clear the selected tracks after successful creation
        // selectedTracks = [];
        // songList.innerHTML = "";
        // addedSongsSection.classList.add("hidden");
        
        // Scroll to the playlist section
        document.getElementById("playlist-output").scrollIntoView({ behavior: 'smooth' });
      } else {
        // Handle success=false response
        statusElement.textContent = `Failed to create playlist: ${data.message || "Unknown error"}`;
        statusElement.className = "mt-2 text-sm text-red-600";
        console.error("Server returned error:", data);
      }
    })
    .catch(err => {
      console.error("Error creating playlist:", err);
      
      // Update status with error message
      statusElement.textContent = `Error: ${err.message || "Failed to create playlist"}`;
      statusElement.className = "mt-2 text-sm text-red-600";
      
      // Show an alert for critical errors
      alert(`Error creating playlist: ${err.message || "Unknown error"}`);
    })
    .finally(() => {
      // Reset button state
      button.disabled = false;
      button.textContent = originalText;
      
      // Remove status message after 5 seconds for success messages
      if (statusElement.classList.contains("text-green-600")) {
        setTimeout(() => {
          statusElement.remove();
        }, 5000);
      }
    });
  });

  function displaySimilarSongGroups(playlist) {
    const container = document.getElementById("playlist-container");
    container.innerHTML = ""; // Clear previous

    const box = document.createElement("div");
    box.className = "border border-purple-300 rounded-lg p-4 bg-white shadow";

    const header = document.createElement("div");
    header.className = "font-semibold text-lg text-black cursor-pointer flex items-center";
    header.innerHTML = `<span class="mr-2">🎵</span> <span>Your Playlist: ${playlist.name}</span>`;
    
    const songList = document.createElement("ul");
    songList.className = "pl-4 mt-2 space-y-2";

    if (playlist.tracks && Array.isArray(playlist.tracks)) {
      playlist.tracks.forEach(track => {
        const li = document.createElement("li");
        li.className = "text-sm text-gray-700";
        li.textContent = `${track.title} by ${track.artist}${track.genre ? ` | Genre: ${track.genre}` : ''}`;
        songList.appendChild(li);
      });
    } else {
      const li = document.createElement("li");
      li.className = "text-sm text-gray-700";
      li.textContent = "No tracks found in playlist";
      songList.appendChild(li);
    }

    box.appendChild(header);
    box.appendChild(songList);
    container.appendChild(box);
    document.getElementById("playlist-output").classList.remove("hidden");
  }

  function updatePlaylistButtonState() {
    const checked = document.querySelectorAll("#song-list input[type='checkbox']:checked").length;
    const playlistBtn = document.getElementById("create-playlist-btn");
    const playlistNameField = document.getElementById("playlist-name");
    
    if (!playlistBtn) return;
    
    const isDisabled = checked < 2;
    playlistBtn.disabled = isDisabled;
    
    // Update button styling based on state
    if (isDisabled) {
      playlistBtn.classList.remove("bg-gradient-to-r", "from-purple-400", "to-pink-500", "text-white");
      playlistBtn.classList.add("bg-gray-300", "text-gray-500", "cursor-not-allowed");
    } else {
      playlistBtn.classList.remove("bg-gray-300", "text-gray-500", "cursor-not-allowed");
      playlistBtn.classList.add("bg-gradient-to-r", "from-purple-400", "to-pink-500", "text-white");
    }
    
    // Show/hide instructions based on number of tracks selected
    const instructionElem = document.getElementById("selection-instructions");
    if (instructionElem) {
      if (checked < 2) {
        instructionElem.textContent = `Select at least 2 songs (${checked} selected)`;
        instructionElem.classList.remove("hidden");
      } else {
        instructionElem.textContent = `${checked} songs selected`;
      }
    }
  }

  queryInput.addEventListener("keydown", function (e) {
    const items = resultsContainer.getElementsByClassName("result-item");

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
        updateSelection(items);
        break;
      case "ArrowUp":
        e.preventDefault();
        selectedIndex = Math.max(selectedIndex - 1, 0);
        updateSelection(items);
        break;
      case "Enter":
        e.preventDefault();
        if (selectedIndex >= 0 && items[selectedIndex]) {
          items[selectedIndex].click();
        }
        break;
      case "Escape":
        resultsBox.style.display = "none";
        break;
    }
  });

  function updateSelection(items) {
    Array.from(items).forEach((item, index) => {
      item.classList.toggle("selected", index === selectedIndex);
      if (index === selectedIndex) {
        item.scrollIntoView({ block: "nearest" });
      }
    });
  }

  document.addEventListener("click", (e) => {
    if (!resultsBox.contains(e.target) && e.target !== queryInput) {
      resultsBox.style.display = "none";
    }
  });
  
  // Call updatePlaylistButtonState initially to set the correct state
  updatePlaylistButtonState();
});