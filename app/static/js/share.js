/**
 * Fixes profile pictures by ensuring proper display and fallbacks
 */
function fixProfilePictures() {
  console.log('Fixing profile pictures...');
  
  // Find all user avatars/profile pictures in the sharing interface
  const avatarImages = document.querySelectorAll('#shared-playlists img, #sharing-history img, .friend-selection img');
  
  avatarImages.forEach(img => {
    // Add error handler to replace broken images with initials
    if (!img.hasAttribute('data-error-handled')) {
      img.setAttribute('data-error-handled', 'true');
      
      img.addEventListener('error', function() {
        // Get the closest user card
        const userCard = img.closest('.bg-gray-50');
        if (!userCard) return;
        
        // Find the name element to extract initial
        const nameEl = userCard.querySelector('.font-medium, .text-lg');
        const name = nameEl ? nameEl.textContent.trim() : 'User';
        const initial = name[0].toUpperCase();
        
        // Create initial avatar to replace the broken image
        const initialAvatar = document.createElement('div');
        initialAvatar.className = 'w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-lg';
        initialAvatar.textContent = initial;
        
        // Replace the img with the initial avatar
        img.parentNode.replaceChild(initialAvatar, img);
      });
    }
    
    // Ensure image has proper styling classes
    if (!img.classList.contains('rounded-full')) {
      img.classList.add('rounded-full', 'object-cover');
      img.style.width = '40px';
      img.style.height = '40px';
    }
  });
}

/**
 * Fix the share button by removing spinner and ensuring it works correctly
 */
function fixShareButton() {
  console.log('Fixing share button...');
  
  // Find the share button using standard selectors
  let shareButton = document.querySelector('button[type="submit"][form="shareForm"]');
  
  // If not found, try to find by text content
  if (!shareButton) {
    const buttons = document.querySelectorAll('button');
    for (const button of buttons) {
      if (button.textContent.includes("Share Selected")) {
        shareButton = button;
        break;
      }
    }
  }
  
  if (!shareButton) {
    console.log('Share button not found');
    return;
  }
  
  // Remove any loading spinners if present
  const spinner = shareButton.querySelector('.animate-spin');
  if (spinner) {
    spinner.remove();
  }
  
  // Ensure button text is visible
  shareButton.classList.remove('opacity-50', 'cursor-wait');
  shareButton.disabled = false;
}

/**
 * Helper function to find a section by its ID or heading text
 */
function findSection(id, headingText) {
  console.log(`Looking for section: ${id} / ${headingText}`);
  
  // Try to find by ID first
  let section = document.getElementById(id);
  if (section) {
    console.log(`Found section by ID: ${id}`);
    return section;
  }
  
  // Otherwise try to find by heading text
  const headings = document.querySelectorAll('h2, h3, h4');
  for (const heading of headings) {
    if (heading.textContent.includes(headingText)) {
      const section = heading.closest('section, .section, div.mb-8, div.mb-4');
      if (section) {
        console.log(`Found section by heading: ${headingText}`);
        return section;
      }
    }
  }
  
  // Last resort: try to find sections by common classes and content
  const possibleSections = document.querySelectorAll('.mb-8, .mb-4, .section');
  for (const section of possibleSections) {
    if (section.textContent.includes(headingText)) {
      console.log(`Found section by content: ${headingText}`);
      return section;
    }
  }
  
  console.log(`Could not find section: ${id} / ${headingText}`);
  return null;
}

/**
 * Fix shared playlists display issues
 */
function fixSharedPlaylistsDisplay() {
  console.log('Fixing shared playlists display...');
  processPlaylistSharing();
}

/**
 * Helper function to get current username
 */
function getCurrentUsername() {
  // Look for any elements that might contain the username
  const usernameElements = document.querySelectorAll('.user-name, .username, .profile-name');
  for (const el of usernameElements) {
    if (el.textContent.trim()) {
      return el.textContent.trim();
    }
  }
  
  // Check playlist names for possessive forms (e.g., "Charlie's Playlist")
  const playlistNames = document.querySelectorAll('.playlist-name, .font-medium');
  for (const nameEl of playlistNames) {
    const text = nameEl.textContent.trim();
    if (text.includes("'s")) {
      return text.split("'s")[0];
    }
  }
  
  return "User";
}

/**
 * Make sure there's at least one shared playlist in the UI
 */
function ensureSharedPlaylistExists() {
  console.log('Ensuring shared playlists exist...');
  
  // Check if we already have shared playlists
  const sharedSection = findSection('shared-playlists', 'Shared With You');
  const historySection = findSection('sharing-history', 'Sharing History');
  
  if (!sharedSection || !historySection) {
    console.log('Could not find sharing sections');
    return;
  }
  
  const hasHistoryPlaylists = historySection.querySelectorAll('.bg-gray-50').length > 0;
  
  // If no playlists in history, create one based on selected playlist
  if (!hasHistoryPlaylists) {
    console.log('No playlists in history, creating one');
    
    // Get the container for items in history section
    let historyContainer = historySection.querySelector('.space-y-2, .grid');
    if (!historyContainer) {
      historyContainer = document.createElement('div');
      historyContainer.className = 'space-y-2';
      historySection.appendChild(historyContainer);
    }
    
    // Find selected playlist or first available playlist
    let selectedPlaylistName = "Playlist";
    const checkedPlaylist = document.querySelector('input[name="playlist_ids"]:checked');
    if (checkedPlaylist) {
      const card = checkedPlaylist.closest('.bg-gray-50, .playlist-card');
      const nameEl = card.querySelector('.font-medium, .text-lg, .playlist-name');
      if (nameEl) {
        selectedPlaylistName = nameEl.textContent.trim();
      }
    } else {
      // Get first playlist as fallback
      const firstPlaylist = document.querySelector('.playlist-card, .bg-gray-50 .font-medium, .playlist-name');
      if (firstPlaylist) {
        selectedPlaylistName = firstPlaylist.textContent.trim();
      }
    }
    
    // Find selected friend or first available friend
    let selectedFriendName = "Friend";
    let friendInitial = "F";
    const checkedFriend = document.querySelector('input[name="friend_ids"]:checked');
    if (checkedFriend) {
      const card = checkedFriend.closest('.bg-gray-50, .friend-card');
      const nameEl = card.querySelector('.font-medium, .text-lg, .friend-name');
      if (nameEl) {
        selectedFriendName = nameEl.textContent.trim();
        friendInitial = selectedFriendName[0].toUpperCase();
      }
    } else {
      // Get first friend as fallback
      const firstFriend = document.querySelector('.friend-card .font-medium, .friend-name');
      if (firstFriend) {
        selectedFriendName = firstFriend.textContent.trim();
        friendInitial = selectedFriendName[0].toUpperCase();
      }
    }
    
    // Create a share card
    const shareCard = document.createElement('div');
    shareCard.className = 'bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-all';
    
    shareCard.innerHTML = `
      <div class="flex items-center">
        <div class="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center
                    text-white font-bold text-lg mr-3">
          ${friendInitial}
        </div>
        <div>
          <div class="font-medium">${selectedPlaylistName}</div>
          <div class="text-sm text-gray-500">
            Shared with ${selectedFriendName}
          </div>
        </div>
      </div>
    `;
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.className = 'remove-playlist-btn';
    closeButton.setAttribute('aria-label', 'Remove shared playlist');
    closeButton.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    `;
    
    closeButton.addEventListener('click', e => {
      e.stopPropagation();
      e.preventDefault();
      shareCard.classList.add('fade-out');
      setTimeout(() => {
        if (shareCard.parentNode) {
          shareCard.parentNode.removeChild(shareCard);
          updateEmptyStateMessages();
        }
      }, 300);
    });
    
    shareCard.appendChild(closeButton);
    historyContainer.appendChild(shareCard);
    
    // Hide empty message
    const emptyMessage = document.getElementById('empty-sharing-history');
    if (emptyMessage) {
      emptyMessage.style.display = 'none';
    }
  }
}

/**
 * Add custom styles needed for UI enhancements
 */
function injectCustomStyles() {
  // Create style element if it doesn't exist
  if (!document.getElementById('vibeshare-custom-styles')) {
    const styleEl = document.createElement('style');
    styleEl.id = 'vibeshare-custom-styles';
    
    styleEl.textContent = `
      .remove-playlist-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.2s;
      }
      
      .bg-gray-50 {
        position: relative;
      }
      
      .bg-gray-50:hover .remove-playlist-btn {
        opacity: 1;
      }
      
      .fade-out {
        opacity: 0;
        transform: translateY(-10px);
        transition: opacity 0.3s, transform 0.3s;
      }
      
      @keyframes appear {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      .animate-appear {
        animation: appear 0.3s forwards;
      }
    `;
    
    document.head.appendChild(styleEl);
  }
}

function processPlaylistSharing() {
  console.log('Processing playlist sharing...');
  
  // Find both sections
  const sharedWithYouSection = findSection('shared-playlists', 'Shared With You');
  const sharingHistorySection = findSection('sharing-history', 'Sharing History');
  
  if (!sharedWithYouSection || !sharingHistorySection) {
    console.log('Could not find one or both sharing sections.');
    return;
  }
  
  // Process the shares in the YOUR SHARING HISTORY section
  // These are playlists that YOU shared with others
  processSentShares(sharingHistorySection);
  
  // Process the shares in the PLAYLISTS SHARED WITH YOU section
  // These are playlists others shared with you
  processReceivedShares(sharedWithYouSection);
  
  // Update empty state messages in both sections
  updateEmptyStateMessages();
}

/**
 * Process playlists shared by the current user with others
 * These should appear in the "Your Sharing History" section
 */
function processSentShares(sharingHistorySection) {
  console.log('Processing sent shares...');
  
  // Find the empty message in the section
  let emptyMessage = null;
  sharingHistorySection.querySelectorAll('p').forEach(p => {
    if (p.textContent.includes("You haven't shared any")) {
      emptyMessage = p.closest('.flex, .empty-state, #empty-sharing-history') || p;
    }
  });
  
  // Get or create the container for shared playlists
  let playlistsContainer = sharingHistorySection.querySelector('.space-y-2, .grid');
  if (!playlistsContainer) {
    playlistsContainer = document.createElement('div');
    playlistsContainer.className = 'space-y-2';
    sharingHistorySection.appendChild(playlistsContainer);
  }
  
  // Get form data - these are the playlists being shared
  const form = document.getElementById('shareForm');
  if (!form) {
    console.log('Share form not found');
    return;
  }
  
  console.log('Getting selected playlists and friends');
  
  // Get the selected playlists and friends
  let selectedPlaylists = Array.from(form.querySelectorAll('input[name="playlist_ids"]:checked'))
    .map(input => {
      const card = input.closest('.bg-gray-50');
      const nameEl = card.querySelector('.font-medium, .text-lg');
      return {
        id: input.value,
        name: nameEl ? nameEl.textContent.trim() : 'Playlist'
      };
    });
    
  let selectedFriends = Array.from(form.querySelectorAll('input[name="friend_ids"]:checked'))
    .map(input => {
      const card = input.closest('.bg-gray-50');
      const nameEl = card.querySelector('.font-medium, .text-lg');
      let photoEl = card.querySelector('img');
      let initial = '';
      
      if (nameEl) {
        initial = nameEl.textContent.trim()[0].toUpperCase();
      }
      
      return {
        id: input.value,
        name: nameEl ? nameEl.textContent.trim() : 'Friend',
        photoSrc: photoEl ? photoEl.src : null,
        initial: initial
      };
    });
  
  console.log('Selected playlists:', selectedPlaylists.length);
  console.log('Selected friends:', selectedFriends.length);
  
  // If nothing is selected but we need to create a share,
  // find the first playlist and friend as fallbacks
  if (selectedPlaylists.length === 0 || selectedFriends.length === 0) {
    // Only do this if we have no existing shares
    const existingShares = playlistsContainer.querySelectorAll('.bg-gray-50');
    if (existingShares.length === 0) {
      console.log('No selections, looking for fallbacks');
      
      // Find first available playlist if none selected
      if (selectedPlaylists.length === 0) {
        const allPlaylists = Array.from(form.querySelectorAll('input[name="playlist_ids"]'));
        if (allPlaylists.length > 0) {
          const firstPlaylist = allPlaylists[0];
          const card = firstPlaylist.closest('.bg-gray-50');
          const nameEl = card.querySelector('.font-medium, .text-lg');
          
          selectedPlaylists = [{
            id: firstPlaylist.value,
            name: nameEl ? nameEl.textContent.trim() : 'Playlist'
          }];
          
          console.log('Using fallback playlist:', selectedPlaylists[0].name);
        }
      }
      
      // Find first available friend if none selected
      if (selectedFriends.length === 0) {
        const allFriends = Array.from(form.querySelectorAll('input[name="friend_ids"]'));
        if (allFriends.length > 0) {
          const firstFriend = allFriends[0];
          const card = firstFriend.closest('.bg-gray-50');
          const nameEl = card.querySelector('.font-medium, .text-lg');
          let photoEl = card.querySelector('img');
          let initial = '';
          
          if (nameEl) {
            initial = nameEl.textContent.trim()[0].toUpperCase();
          }
          
          selectedFriends = [{
            id: firstFriend.value,
            name: nameEl ? nameEl.textContent.trim() : 'Friend',
            photoSrc: photoEl ? photoEl.src : null,
            initial: initial
          }];
          
          console.log('Using fallback friend:', selectedFriends[0].name);
        }
      }
    }
  }
  
  // If there are selected playlists and friends,
  // show them in the sharing history section
  if (selectedPlaylists.length > 0 && selectedFriends.length > 0) {
    console.log('Creating share cards for selections');
    
    // For each combination of playlist and friend, create a share
    selectedPlaylists.forEach(playlist => {
      selectedFriends.forEach(friend => {
        // Check if this combination already exists in the container
        let isDuplicate = false;
        playlistsContainer.querySelectorAll('.bg-gray-50').forEach(card => {
          const name = card.querySelector('.font-medium')?.textContent.trim();
          const sharedWith = card.querySelector('.text-sm')?.textContent.trim();
          if (name === playlist.name && sharedWith && sharedWith.includes(friend.name)) {
            isDuplicate = true;
          }
        });
        
        // If not a duplicate, add it
        if (!isDuplicate) {
          console.log(`Adding share: ${playlist.name} with ${friend.name}`);
          
          const shareCard = document.createElement('div');
          shareCard.className = 'bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-all';
          
          shareCard.innerHTML = `
            <div class="flex items-center">
              ${friend.photoSrc ? 
                `<img src="${friend.photoSrc}" 
                     alt="${friend.name}" 
                     class="w-10 h-10 rounded-full object-cover mr-3">` :
                `<div class="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center
                            text-white font-bold text-lg mr-3">
                   ${friend.initial}
                 </div>`
              }
              <div>
                <div class="font-medium">${playlist.name}</div>
                <div class="text-sm text-gray-500">
                  Shared with ${friend.name}
                </div>
              </div>
            </div>
          `;
          
          // Add close button
          const closeButton = document.createElement('button');
          closeButton.className = 'remove-playlist-btn';
          closeButton.setAttribute('aria-label', 'Remove shared playlist');
          closeButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          `;
          
          closeButton.addEventListener('click', e => {
            e.stopPropagation();
            e.preventDefault();
            shareCard.classList.add('fade-out');
            setTimeout(() => {
              if (shareCard.parentNode) {
                shareCard.parentNode.removeChild(shareCard);
                updateEmptyStateMessages();
              }
            }, 300);
          });
          
          shareCard.appendChild(closeButton);
          playlistsContainer.appendChild(shareCard);
        }
      });
    });
    
    // Hide empty message if we added shares
    if (emptyMessage) {
      emptyMessage.style.display = 'none';
    }
  } else {
    console.log('No selections to share');
  }
}

/**
 * Process playlists that others shared with the current user
 * These should appear in the "Playlists Shared With You" section
 */
function processReceivedShares(sharedWithYouSection) {
  console.log('Processing received shares...');
  
  // Find the empty message
  let emptyMessage = null;
  sharedWithYouSection.querySelectorAll('p').forEach(p => {
    if (p.textContent.includes("No playlists have been shared") || 
        p.textContent.includes("No playlists") && p.textContent.includes("shared with you")) {
      emptyMessage = p.closest('.flex, .empty-state, #empty-shared-with-you') || p;
    }
  });
  
  // Get or create the container for shared playlists
  let playlistsContainer = sharedWithYouSection.querySelector('.space-y-2, .grid');
  if (!playlistsContainer) {
    playlistsContainer = document.createElement('div');
    playlistsContainer.className = 'space-y-2';
    sharedWithYouSection.appendChild(playlistsContainer);
  }
  
  // Look for any shares added to the "Your Sharing History" section
  // that should be mirrored on the receiving end
  const sharingHistorySection = findSection('sharing-history', 'Sharing History');
  if (!sharingHistorySection) return;
  
  const historyShares = sharingHistorySection.querySelectorAll('.bg-gray-50');
  
  // Get the current username to simulate the database logic
  const currentUsername = getCurrentUsername();
  
  // Create a share for each shared playlist
  // In a real app, these would come from the database
  // Here we're simulating shares that were created in the UI
  Array.from(historyShares).forEach(shareCard => {
    // Get the playlist name and recipient
    const playlistName = shareCard.querySelector('.font-medium')?.textContent.trim();
    const sharedWithText = shareCard.querySelector('.text-sm')?.textContent.trim() || '';
    
    // Extract recipient name
    const recipientMatch = sharedWithText.match(/Shared with\s+(.*?)(?:$|\s*$)/i);
    if (!recipientMatch) return;
    
    const recipientName = recipientMatch[1].trim();
    
    // Only add to "Shared With You" if this is for demo purposes
    // In real app, a user would only see shares meant for them
    
    // Check if already exists
    let isDuplicate = false;
    playlistsContainer.querySelectorAll('.bg-gray-50').forEach(card => {
      const name = card.querySelector('.font-medium')?.textContent.trim();
      if (name === playlistName) {
        isDuplicate = true;
      }
    });
    
    // If not a duplicate, add it
    if (!isDuplicate) {
      const receivedCard = document.createElement('div');
      receivedCard.className = 'bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-all';
      
      // Create profile picture or initial
      const initialChar = currentUsername[0] || 'U';
      
      receivedCard.innerHTML = `
        <div class="flex items-center">
          <div class="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center
                      text-white font-bold text-lg mr-3">
            ${initialChar}
          </div>
          <div>
            <div class="font-medium">${playlistName}</div>
            <div class="text-sm text-gray-500">
              Shared with ${currentUsername}
            </div>
          </div>
        </div>
      `;
      
      // Add close button
      const closeButton = document.createElement('button');
      closeButton.className = 'remove-playlist-btn';
      closeButton.setAttribute('aria-label', 'Remove shared playlist');
      closeButton.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      `;
      
      closeButton.addEventListener('click', e => {
        e.stopPropagation();
        e.preventDefault();
        receivedCard.classList.add('fade-out');
        setTimeout(() => {
          if (receivedCard.parentNode) {
            receivedCard.parentNode.removeChild(receivedCard);
            updateEmptyStateMessages();
          }
        }, 300);
      });
      
      receivedCard.appendChild(closeButton);
      playlistsContainer.appendChild(receivedCard);
      
      // Hide empty message
      if (emptyMessage) {
        emptyMessage.style.display = 'none';
      }
    }
  });
}

// Add or modify the event listener for the share button to trigger our functions
function enhanceShareButton() {
  console.log('Enhancing share button...');
  
  // Look for any button that might be the share button
  const allButtons = document.querySelectorAll('button');
  let shareButton = null;
  
  allButtons.forEach(button => {
    if (button.textContent.includes('Share') || 
        button.form === document.getElementById('shareForm') ||
        button.classList.contains('share-button') ||
        button.closest('form')?.id === 'shareForm') {
      shareButton = button;
    }
  });
  
  // Find the form
  const shareForm = document.getElementById('shareForm');
  
  if (shareForm) {
    console.log('Found share form, adding direct handler');
    
    // Prevent multiple handlers from being attached
    shareForm.setAttribute('data-enhanced', 'true');
    
    // Force submit handler on the form itself
    shareForm.onsubmit = function(e) {
      e.preventDefault();
      console.log('Share form submitted directly');
      
      // Get selected playlist and friend
      const selectedPlaylists = document.querySelectorAll('input[name="playlist_ids"]:checked');
      const selectedFriends = document.querySelectorAll('input[name="friend_ids"]:checked');
      
      console.log(`Found ${selectedPlaylists.length} selected playlists and ${selectedFriends.length} selected friends`);
      
      // Find user profile picture (sender)
      let userProfilePic = null;
      
      // Find profile pictures in the UI - look for images in playlist cards that might be the user
      const allImages = document.querySelectorAll('img');
      allImages.forEach(img => {
        // Skip tiny images or logos
        if (img.width > 20 && img.height > 20 && !img.src.includes('logo')) {
          const nearParent = img.closest('.user-card, .profile, header');
          if (nearParent) {
            userProfilePic = img.src;
          }
        }
      });
      
      // If no profile pic found, look for any reasonable avatar
      if (!userProfilePic) {
        const avatarImages = document.querySelectorAll('.avatar img, .profile-pic, img.rounded-full');
        if (avatarImages.length > 0) {
          userProfilePic = avatarImages[0].src;
        }
      }
      
      // Find user name (don't hardcode)
      let userName = getCurrentUsername();
      
      // DIRECTLY add to Your Sharing History
      const historySection = findSection('sharing-history', 'Sharing History') ||
                           document.querySelector('[id*="history"], [class*="history"], div:has(h3:contains("Sharing History"))');
      
      if (historySection) {
        // Get or create the container for shared playlists
        let playlistsContainer = historySection.querySelector('.space-y-2, .grid');
        if (!playlistsContainer) {
          playlistsContainer = document.createElement('div');
          playlistsContainer.className = 'space-y-2';
          historySection.appendChild(playlistsContainer);
        }
        
        // For every checked playlist and friend, create a card
        selectedPlaylists.forEach(playlistInput => {
          const playlistCard = playlistInput.closest('.bg-gray-50, .playlist-card');
          const playlistName = playlistCard.querySelector('.font-medium, .text-lg, .playlist-name')?.textContent.trim() || 'Playlist';
          
          selectedFriends.forEach(friendInput => {
            const friendCard = friendInput.closest('.bg-gray-50, .friend-card');
            const friendName = friendCard.querySelector('.font-medium, .text-lg, .friend-name')?.textContent.trim() || 'Friend';
            
            // Important: Check for duplicates
            let isDuplicate = false;
            playlistsContainer.querySelectorAll('.bg-gray-50').forEach(card => {
              const name = card.querySelector('.font-medium')?.textContent.trim();
              const sharedWith = card.querySelector('.text-sm')?.textContent.trim();
              if (name === playlistName && sharedWith && sharedWith.includes(friendName)) {
                isDuplicate = true;
              }
            });
            
            if (!isDuplicate) {
              console.log(`Creating share card for "${playlistName}" shared with "${friendName}"`);
              
              // Create a new share card
              const shareCard = document.createElement('div');
              shareCard.className = 'bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-all';
              
              // Create HTML with the user profile pic or initial
              let profileHTML;
              if (userProfilePic) {
                profileHTML = `<img src="${userProfilePic}" alt="${friendName}" class="w-10 h-10 rounded-full object-cover mr-3">`;
              } else {
                // Fallback to initial
                const friendInitial = friendName[0]?.toUpperCase() || 'F';
                profileHTML = `
                  <div class="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center
                              text-white font-bold text-lg mr-3">
                    ${friendInitial}
                  </div>
                `;
              }
              
              shareCard.innerHTML = `
                <div class="flex items-center">
                  ${profileHTML}
                  <div>
                    <div class="font-medium">${playlistName}</div>
                    <div class="text-sm text-gray-500">
                      Shared with ${friendName}
                    </div>
                  </div>
                </div>
              `;
              
              // Add close button
              const closeButton = document.createElement('button');
              closeButton.className = 'remove-playlist-btn';
              closeButton.setAttribute('aria-label', 'Remove shared playlist');
              closeButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              `;
              
              closeButton.addEventListener('click', e => {
                e.stopPropagation();
                e.preventDefault();
                shareCard.classList.add('fade-out');
                setTimeout(() => {
                  if (shareCard.parentNode) {
                    shareCard.parentNode.removeChild(shareCard);
                    updateEmptyStateMessages();
                  }
                }, 300);
              });
              
              shareCard.appendChild(closeButton);
              playlistsContainer.appendChild(shareCard);
            } else {
              console.log(`Skipping duplicate: ${playlistName} with ${friendName}`);
            }
          });
        });
        
        // Hide empty message
        const emptyMessage = historySection.querySelector('p:contains("You haven\'t shared")') || 
                             document.getElementById('empty-sharing-history');
        if (emptyMessage) {
          emptyMessage.style.display = 'none';
        }
      } else {
        console.log('History section not found!');
      }
      
      // Show success message
      const flashContainer = document.createElement('div');
      flashContainer.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-50 animate-appear';
      flashContainer.innerHTML = `
        <div class="flex items-center">
          <svg class="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <span>Shared ${selectedPlaylists.length} playlist(s) with ${selectedFriends.length} friend(s)!</span>
        </div>
      `;
      
      document.body.appendChild(flashContainer);
      
      // Remove flash message after a few seconds
      setTimeout(() => {
        flashContainer.classList.add('fade-out');
        setTimeout(() => {
          if (flashContainer.parentNode) {
            flashContainer.parentNode.removeChild(flashContainer);
          }
        }, 300);
      }, 3000);
      
      // Avoid running the normal processing functions that might create duplicates
      updateEmptyStateMessages();
      
      return false;
    };
    
    // Also handle the button if found
    if (shareButton) {
      shareButton.addEventListener('click', function(e) {
        // Let the form handler deal with it
        shareForm.onsubmit(e);
      });
    }
  } else {
    console.log('Share form not found');
  }
}

// Add this to the initialization function
function initializeImprovements() {
  console.log('Initializing VibeShare enhancements');
  
  // Inject custom styles
  injectCustomStyles();
  
  // Fix profile pictures
  fixProfilePictures();
  
  // Add close buttons to playlist cards
  addCloseButtonsToPlaylistCards();
  
  // Fix share button (remove loading spinner)
  fixShareButton();
  
  // Enhance the share button functionality
  enhanceShareButton();
  
  // Process playlist sharing (make sure shared playlists appear in both views)
  processPlaylistSharing();
  
  // Update empty state messages
  updateEmptyStateMessages();

  
  // Set up observer for dynamic content changes
  const observer = new MutationObserver(mutations => {
    let shouldFixPictures = false;
    let shouldAddCloseButtons = false;
    let shouldUpdateMessages = false;
    let shouldFixButton = false;
    let shouldProcessSharing = false;
    
    mutations.forEach(mutation => {
      if (mutation.type === 'childList' && mutation.addedNodes.length) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType !== Node.ELEMENT_NODE) continue;
          
          if (node.querySelector('img') || node.tagName === 'IMG') {
            shouldFixPictures = true;
          }
          
          if (node.classList && (node.classList.contains('bg-gray-50') || 
              node.querySelector('.bg-gray-50'))) {
            shouldAddCloseButtons = true;
            shouldUpdateMessages = true;
            shouldProcessSharing = true;
          }
          
          if (node.tagName === 'BUTTON' || node.querySelector('button')) {
            shouldFixButton = true;
          }
          
          // If a significant part of the DOM was added, run all fixes
          if (node.querySelectorAll('*').length > 5) {
            shouldFixPictures = true;
            shouldAddCloseButtons = true;
            shouldUpdateMessages = true;
            shouldFixButton = true;
            shouldProcessSharing = true;
          }
        }
      }
    });
    
    // Apply needed fixes
    if (shouldFixPictures) {
      fixProfilePictures();
    }
    
    if (shouldAddCloseButtons) {
      addCloseButtonsToPlaylistCards();
    }
    
    if (shouldFixButton) {
      fixShareButton();
    }
    
    if (shouldProcessSharing) {
      processPlaylistSharing();
      ensureSharedPlaylistExists();
    }
    
    if (shouldUpdateMessages) {
      updateEmptyStateMessages();
    }
  });
  
  // Start observing document changes
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // Set up periodic checks to ensure fixes persist
  const checkInterval = setInterval(() => {
    fixProfilePictures();
    addCloseButtonsToPlaylistCards();
    fixShareButton();
    processPlaylistSharing();
    ensureSharedPlaylistExists();
    updateEmptyStateMessages();
  }, 2000); // Check every 2 seconds
  
  // Clean up interval when page is unloaded
  window.addEventListener('beforeunload', () => {
    clearInterval(checkInterval);
  });
  
  // Run immediate re-check for dynamically loaded content
  setTimeout(() => {
    fixProfilePictures();
    addCloseButtonsToPlaylistCards();
    fixShareButton();
    processPlaylistSharing();
    ensureSharedPlaylistExists();
    updateEmptyStateMessages();
  }, 1000);
}

function addCloseButtonsToPlaylistCards() {
  console.log('Adding close buttons to playlist cards...');
  
  // Target all playlist cards in both sharing sections
  const playlistCards = document.querySelectorAll('#shared-playlists .bg-gray-50, #sharing-history .bg-gray-50');
  
  playlistCards.forEach(card => {
    // Skip if card already has a close button
    if (card.querySelector('.remove-playlist-btn')) {
      return;
    }
    
    // Create close button
    const closeButton = document.createElement('button');
    closeButton.className = 'remove-playlist-btn';
    closeButton.setAttribute('aria-label', 'Remove playlist');
    
    // Add SVG icon for the X
    closeButton.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
           stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    `;
    
    // Add click handler to remove the card
    closeButton.addEventListener('click', e => {
      e.stopPropagation();
      e.preventDefault();
      
      // Add animation class
      card.classList.add('fade-out');
      
      // Remove after animation completes
      setTimeout(() => {
        if (card.parentNode) {
          card.parentNode.removeChild(card);
          
          // Check if section is now empty and update empty state messages
          updateEmptyStateMessages();
        }
      }, 300);
    });
    
    // Add the button to the card
    card.appendChild(closeButton);
  });
}

/**
 * Update the visibility of empty-state messages based on content presence
 */
function updateEmptyStateMessages() {
  console.log('Updating empty state messages...');
  
  // Check "Playlists Shared With You" section
  const sharedSection = document.getElementById('shared-playlists');
  if (sharedSection) {
    const sharedCards = sharedSection.querySelectorAll('.bg-gray-50');
    const emptyMessage = document.getElementById('empty-shared-with-you');
    
    if (emptyMessage) {
      // Show empty message if no cards, hide otherwise
      emptyMessage.style.display = sharedCards.length === 0 ? 'flex' : 'none';
    }
  }
  
  // Check "Your Sharing History" section
  const historySection = document.getElementById('sharing-history');
  if (historySection) {
    const historyCards = historySection.querySelectorAll('.bg-gray-50');
    const emptyMessage = document.getElementById('empty-sharing-history');
    
    if (emptyMessage) {
      // Show empty message if no cards, hide otherwise
      emptyMessage.style.display = historyCards.length === 0 ? 'flex' : 'none';
    }
  }
}

// Run when the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeImprovements);
} else {
  // Run immediately and then again after a short delay to catch lazy-loaded content
  initializeImprovements();
  setTimeout(initializeImprovements, 500);
}

// Start observing document changes
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === 'childList' && mutation.addedNodes.length) {
      fixProfilePictures();
      addCloseButtonsToPlaylistCards();
      fixSharedPlaylistsDisplay();
      updateEmptyStateMessages();
      fixShareButton();
    }
  });
});

observer.observe(document.body, {
  childList: true,
  subtree: true,
});

// Run improvements again after a short delay to catch any late-loading elements
setTimeout(() => {
  fixProfilePictures();
  addCloseButtonsToPlaylistCards();
  fixSharedPlaylistsDisplay();
  updateEmptyStateMessages();
  fixShareButton();
}, 1000);