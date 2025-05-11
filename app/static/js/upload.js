document.addEventListener("DOMContentLoaded", function () {
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
              <img src="${track.image}" alt="${track.name}" onerror="this.src='/static/img/default-album.png'">
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
      <p class="text-sm text-gray-500">Album: ${track.album}${track.genre ? ` | Genre: ${track.genre}` : ''}</p>
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
    
    // Update button state after adding a song
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
        
        // Hide the added songs section if no songs remain
        if (selectedTracks.length === 0) {
          addedSongsSection.classList.add("hidden");
        }
      }
    }
  });

  document.getElementById("add-track-btn").addEventListener("click", function () {
    const track = {
      id: document.getElementById("title").value + "-" + document.getElementById("artist").value,
      name: document.getElementById("title").value,
      artist: document.getElementById("artist").value,
      album: document.getElementById("album").value,
      genre: document.getElementById("genre").value,
      danceability: parseFloat(document.getElementById("danceability").value) || 0,
      energy: parseFloat(document.getElementById("energy").value) || 0,
      liveness: parseFloat(document.getElementById("liveness").value) || 0,
      acousticness: parseFloat(document.getElementById("acousticness").value) || 0,
      valence: parseFloat(document.getElementById("valence").value) || 0,
      mode: document.getElementById("mode").value || "Major",
      tempo: parseFloat(document.getElementById("tempo").value) || 0,
      duration_ms: parseInt(document.getElementById("duration_ms").value) || 0
    };

    if (!track.name || !track.artist) return;
    if (selectedTracks.some(t => t.id === track.id)) return;

    selectedTracks.push(track);
    displaySelectedSong(track);
  });
  
  document.getElementById("create-playlist-btn").addEventListener("click", function () {
    const playlistName = document.getElementById("playlist-name").value.trim();
    if (!playlistName) {
      alert("Please enter a playlist name");
      return;
    }

    const checkedBoxes = document.querySelectorAll("#song-list input[type='checkbox']:checked");
    if (checkedBoxes.length < 2) {
      alert("Please select at least 2 songs");
      return;
    }

    const checkedIds = Array.from(checkedBoxes).map(cb => cb.closest("li").id.replace("song-", ""));
    const tracksToSend = selectedTracks.filter(t => checkedIds.includes(t.id));
    
    console.log("Sending playlist data:", {
      playlist_name: playlistName,
      tracks: tracksToSend
    });

    fetch("/upload/create-playlist", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
      },
      body: JSON.stringify({ 
        playlist_name: playlistName, 
        tracks: tracksToSend 
      })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(err => {
          throw new Error(err.message || `Server error: ${res.status}`);
        });
      }
      return res.json();
    })
    .then(data => {
      if (data.status === "success") {
        displaySimilarSongGroups(data.playlist);
        document.getElementById("playlist-name").value = "";
        
        // Clear selected tracks after successful creation
        selectedTracks = [];
        songList.innerHTML = "";
        addedSongsSection.classList.add("hidden");
      } else {
        alert(`Failed to create playlist: ${data.message}`);
      }
    })
    .catch(err => {
      console.error("Error creating playlist:", err);
      alert(`Error creating playlist: ${err.message}`);
    });
  });

  function displaySimilarSongGroups(playlist) {
    const container = document.getElementById("playlist-container");
    container.innerHTML = ""; // Clear previous

    const box = document.createElement("div");
    box.className = "border border-purple-300 rounded-lg p-4 bg-white shadow";

    const header = document.createElement("div");
    header.className = "font-semibold text-lg text-black cursor-pointer";
    header.textContent = `🎵 Your Playlist: ${playlist.name}`;
    
    const songList = document.createElement("ul");
    songList.className = "pl-4 mt-2 space-y-2";

    playlist.tracks.forEach(track => {
      const li = document.createElement("li");
      li.className = "text-sm text-gray-700";
      li.textContent = `${track.title} by ${track.artist} | Genre: ${track.genre || "N/A"}`;
      songList.appendChild(li);
    });

    box.appendChild(header);
    box.appendChild(songList);
    container.appendChild(box);
    document.getElementById("playlist-output").classList.remove("hidden");
  }

  function updatePlaylistButtonState() {
    const checked = document.querySelectorAll("#song-list input[type='checkbox']:checked").length;
    const playlistBtn = document.getElementById("create-playlist-btn");
    const playlistNameInput = document.getElementById("playlist-name");
    
    if (!playlistBtn) return;
    
    const hasPlaylistName = playlistNameInput && playlistNameInput.value.trim().length > 0;
    const isValid = checked >= 2 && hasPlaylistName;
    
    playlistBtn.disabled = !isValid;
    
    // Update button styling
    if (isValid) {
      playlistBtn.classList.add("bg-gradient-to-r", "from-purple-400", "to-pink-500", "text-white");
      playlistBtn.classList.remove("bg-gray-300", "cursor-not-allowed");
    } else {
      playlistBtn.classList.remove("bg-gradient-to-r", "from-purple-400", "to-pink-500", "text-white");
      playlistBtn.classList.add("bg-gray-300", "cursor-not-allowed");
    }
  }
  
  // Also update button state when playlist name changes
  if (playlistNameInput) {
    playlistNameInput.addEventListener("input", updatePlaylistButtonState);
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
});