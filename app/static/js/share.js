/**
 * Process shared playlists between users
 * This function ensures shared playlists appear in the correct sections:
 * - "Your Sharing History" for the sender 
 * - "Playlists Shared With You" for the recipient
 */
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
  if (!form) return;
  
  // Get the selected playlists and friends
  const selectedPlaylists = Array.from(form.querySelectorAll('input[name="playlist_ids"]:checked'))
    .map(input => {
      const card = input.closest('.bg-gray-50');
      const nameEl = card.querySelector('.font-medium, .text-lg');
      return {
        id: input.value,
        name: nameEl ? nameEl.textContent.trim() : 'Playlist'
      };
    });
    
  const selectedFriends = Array.from(form.querySelectorAll('input[name="friend_ids"]:checked'))
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
  
  // If there are selected playlists and friends,
  // show them in the sharing history section
  if (selectedPlaylists.length > 0 && selectedFriends.length > 0) {
    // For each combination of playlist and friend, create a share
    selectedPlaylists.forEach(playlist => {
      selectedFriends.forEach(friend => {
        // Check if this combination already exists in the container
        let isDuplicate = false;
        playlistsContainer.querySelectorAll('.bg-gray-50').forEach(card => {
          const name = card.querySelector('.font-medium')?.textContent.trim();
          const sharedWith = card.querySelector('.text-sm')?.textContent.trim();
          if (name === playlist.name && sharedWith.includes(friend.name)) {
            isDuplicate = true;
          }
        });
        
        // If not a duplicate, add it
        if (!isDuplicate) {
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
              Shared by ${currentUsername}
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
  const shareForm = document.getElementById('shareForm');
  const shareButton = document.querySelector('button[type="submit"][form="shareForm"]');
  
  if (shareForm && shareButton) {
    shareForm.addEventListener('submit', function(e) {
      e.preventDefault(); // Prevent actual form submission for demo
      
      // Process sharing logic
      processPlaylistSharing();
      
      // Show success message
      const selectedPlaylists = shareForm.querySelectorAll('input[name="playlist_ids"]:checked').length;
      const selectedFriends = shareForm.querySelectorAll('input[name="friend_ids"]:checked').length;
      
      if (selectedPlaylists > 0 && selectedFriends > 0) {
        // Create flash message
        const flashContainer = document.createElement('div');
        flashContainer.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-50 animate-appear';
        flashContainer.innerHTML = `
          <div class="flex items-center">
            <svg class="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span>Shared ${selectedPlaylists} playlist(s) with ${selectedFriends} friend(s)!</span>
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
      }
    });
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

/**
 * Initialize all enhancements
 */
function initializeImprovements() {
  console.log('Initializing VibeShare enhancements');
  
  // Add close buttons to playlist cards
  addCloseButtonsToPlaylistCards();
  
  // Update empty state messages based on content
  updateEmptyStateMessages();
  
  // Set up observer for dynamic content changes
  const observer = new MutationObserver(mutations => {
    let shouldAddCloseButtons = false;
    let shouldUpdateMessages = false;
    
    mutations.forEach(mutation => {
      if (mutation.type === 'childList' && mutation.addedNodes.length) {
        // Check if new nodes contain playlist cards
        for (const node of mutation.addedNodes) {
          if (node.nodeType !== Node.ELEMENT_NODE) continue;
          
          if (node.classList && (node.classList.contains('bg-gray-50') || 
              node.querySelector('.bg-gray-50'))) {
            shouldAddCloseButtons = true;
            shouldUpdateMessages = true;
          }
        }
      }
    });
    
    // Apply needed fixes
    if (shouldAddCloseButtons) {
      addCloseButtonsToPlaylistCards();
    }
    
    if (shouldUpdateMessages) {
      updateEmptyStateMessages();
    }
  });
  
  // Start observing the entire document for changes
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // Handle form submission
  const shareForm = document.getElementById('shareForm');
  if (shareForm) {
    shareForm.addEventListener('submit', function(e) {
      // We don't prevent default here to allow the actual form submission
      
      // After a short delay (to allow for page refresh),
      // make sure close buttons are added to any new cards
      setTimeout(() => {
        addCloseButtonsToPlaylistCards();
        updateEmptyStateMessages();
      }, 500);
    });
  }
}

// Run when the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeImprovements);
} else {
  initializeImprovements();
}