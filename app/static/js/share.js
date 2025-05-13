/**
 * VibeShare share.js - Final Fix for All Issues
 * - Makes button clickable
 * - Preserves sharing history
 * - Prevents duplicates
 * - Ensures confirmation message stays
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('VibeShare share.js loaded, initializing page');
    
    // Initialize the UI components and ensure elements are clickable
    makeElementsClickable();
    
    // Set up checkboxes
    setupCheckboxes();
    
    // Fix the share button
    fixShareButton();
    
    // Fix empty state message issue 
    fixEmptyStateMessage();
    
    // Fix history retention
    preserveHistory();
  });
  
  /**
   * Make all interactive elements clickable
   */
  function makeElementsClickable() {
    console.log('Making elements clickable');
    
    // Fix checkboxes
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
      checkbox.style.pointerEvents = 'auto';
      checkbox.style.position = 'relative';
      checkbox.style.zIndex = '10';
      checkbox.style.cursor = 'pointer';
    });
    
    // Fix labels
    document.querySelectorAll('label').forEach(label => {
      label.style.cursor = 'pointer';
    });
    
    // Fix buttons
    document.querySelectorAll('button').forEach(button => {
      button.style.pointerEvents = 'auto';
      button.style.position = 'relative';
      button.style.zIndex = '10';
      button.style.cursor = 'pointer';
    });
  }
  
  /**
   * Set up checkbox behaviors
   */
  function setupCheckboxes() {
    // Add "Select All" functionality for playlists
    setupSelectAll('input[name="playlist_ids"]', 'Select All Playlists');
    
    // Add "Select All" functionality for friends
    setupSelectAll('input[name="friend_ids"]', 'Select All Friends');
  }
  
  /**
   * Set up "Select All" checkbox for a group of checkboxes
   */
  function setupSelectAll(selector, labelText) {
    const checkboxes = document.querySelectorAll(selector);
    if (checkboxes.length === 0) return;
    
    // Find the parent container
    const firstCheckbox = checkboxes[0];
    const container = firstCheckbox.closest('.space-y-5');
    if (!container) return;
    
    // Create select all checkbox
    const selectAllDiv = document.createElement('div');
    selectAllDiv.className = 'mb-3 flex items-center';
    selectAllDiv.innerHTML = `
      <label class="flex items-center cursor-pointer">
        <input type="checkbox" class="select-all-checkbox w-5 h-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2">
        <span class="text-indigo-700 font-medium">${labelText}</span>
      </label>
    `;
    
    container.prepend(selectAllDiv);
    
    // Add event listener
    const selectAllCheckbox = selectAllDiv.querySelector('.select-all-checkbox');
    
    selectAllCheckbox.addEventListener('change', function() {
      checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
      });
    });
    
    // Update select all when individual checkboxes change
    checkboxes.forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        const someChecked = Array.from(checkboxes).some(cb => cb.checked);
        
        selectAllCheckbox.checked = allChecked;
        selectAllCheckbox.indeterminate = someChecked && !allChecked;
      });
    });
  }
  
  /**
   * Fix the share button
   */
  function fixShareButton() {
    console.log('Applying share button fix');
    
    // Find the share button using multiple selectors
    const shareButton = document.querySelector('button[type="submit"]') || 
                        document.querySelector('button[form="shareForm"]') ||
                        document.querySelector('.bg-gradient-to-r');
    
    if (!shareButton) {
      console.error('Share button not found!');
      return;
    }
    
    console.log('Share button found:', shareButton);
    
    // Store original button HTML
    const originalButtonHTML = shareButton.innerHTML;
    
    // Make button clickable
    shareButton.style.pointerEvents = 'auto';
    shareButton.style.cursor = 'pointer';
    shareButton.style.position = 'relative';
    shareButton.style.zIndex = '9999';
    shareButton.disabled = false;
    
    // If button is stuck in loading state, fix it
    if (shareButton.textContent.includes('Sharing...')) {
      console.log('Button is in loading state, restoring...');
      shareButton.innerHTML = originalButtonHTML;
      shareButton.disabled = false;
    }
    
    // Get the form
    const shareForm = document.getElementById('shareForm');
    if (!shareForm) {
      console.error('Share form not found!');
      return;
    }
    
    // Add the direct onclick handler to the button
    shareButton.onclick = function(e) {
      console.log('Share button clicked (direct onclick handler)');
      
      // Get selected playlists and friends
      const playlistCheckboxes = document.querySelectorAll('input[name="playlist_ids"]:checked');
      const friendCheckboxes = document.querySelectorAll('input[name="friend_ids"]:checked');
      
      // Basic validation
      if (playlistCheckboxes.length === 0) {
        alert('Please select at least one playlist');
        e.preventDefault();
        return false;
      }
      
      if (friendCheckboxes.length === 0) {
        alert('Please select at least one friend');
        e.preventDefault();
        return false;
      }
      
      // Save the current state of sharing history to localStorage
      saveHistoryToStorage();
      
      // Add new entries
      try {
        addToSharingHistory(playlistCheckboxes, friendCheckboxes);
      } catch (err) {
        console.error('Error adding to sharing history:', err);
      }
      
      // Show loading state
      shareButton.innerHTML = '<span class="animate-spin mr-2">↻</span> Sharing...';
      shareButton.disabled = true;
      
      // Allow form submission to continue
      return true;
    };
    
    console.log('Share button handler attached');
  }
  
  /**
   * Save the current sharing history to localStorage
   */
  function saveHistoryToStorage() {
    try {
      const historyContainer = document.querySelector('.your-sharing-history-container');
      if (!historyContainer) return;
      
      const historyContent = historyContainer.innerHTML;
      localStorage.setItem('vibeshare_history', historyContent);
      console.log('Saved sharing history to localStorage');
    } catch (err) {
      console.error('Error saving history to localStorage:', err);
    }
  }
  
  /**
   * Restore sharing history from localStorage
   */
  function restoreHistoryFromStorage() {
    try {
      const savedHistory = localStorage.getItem('vibeshare_history');
      if (!savedHistory) return false;
      
      const historyContainer = document.querySelector('.your-sharing-history-container');
      if (!historyContainer) return false;
      
      // Only restore if the current page doesn't already have entries
      const currentEntries = historyContainer.querySelectorAll('.bg-gray-50');
      if (currentEntries.length > 0) {
        console.log('Page already has entries, not restoring from localStorage');
        return false;
      }
      
      // Check if the saved history has actual entries
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = savedHistory;
      const savedEntries = tempDiv.querySelectorAll('.bg-gray-50');
      
      if (savedEntries.length === 0) {
        console.log('Saved history has no entries, not restoring');
        return false;
      }
      
      historyContainer.innerHTML = savedHistory;
      console.log('Restored sharing history from localStorage');
      return true;
    } catch (err) {
      console.error('Error restoring history from localStorage:', err);
      return false;
    }
  }
  
  /**
   * Fix empty state message issue
   */
  function fixEmptyStateMessage() {
    console.log('Setting up empty state message fix');
    
    // Check on page load
    checkAndFixEmptyStateMessage();
    
    // Set up a MutationObserver to watch for changes
    const observer = new MutationObserver(function() {
      checkAndFixEmptyStateMessage();
    });
    
    // Start observing the document
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Check again after delays
    setTimeout(checkAndFixEmptyStateMessage, 1000);
    setTimeout(checkAndFixEmptyStateMessage, 2000);
  }
  
  /**
   * Check for and fix empty state messages
   */
  function checkAndFixEmptyStateMessage() {
    // Find history containers
    const containers = [];
    
    // By class
    const classContainer = document.querySelector('.your-sharing-history-container');
    if (classContainer) containers.push(classContainer);
    
    // By heading
    document.querySelectorAll('h2').forEach(function(heading) {
      if (heading.textContent.includes('Your Sharing History')) {
        const container = heading.closest('.bg-white');
        if (container && !containers.includes(container)) {
          containers.push(container);
        }
      }
    });
    
    // Process each container
    containers.forEach(container => {
      const entries = container.querySelectorAll('.bg-gray-50');
      const emptyMessage = container.querySelector('.flex.items-center.justify-center');
      
      if (entries.length > 0 && emptyMessage) {
        console.log('Found entries and empty message, removing empty message');
        emptyMessage.remove();
      }
    });
  }
  
  /**
   * Preserve history across page loads
   */
  function preserveHistory() {
    console.log('Setting up history preservation');
    
    // Try to restore history from localStorage
    const restored = restoreHistoryFromStorage();
    
    // If not restored, set up localStorage for future saves
    if (!restored) {
      // Set up storage event to save on page unload
      window.addEventListener('beforeunload', function() {
        saveHistoryToStorage();
      });
    }
    
    // Check for entries after a delay
    setTimeout(function() {
      const historyContainer = document.querySelector('.your-sharing-history-container');
      if (!historyContainer) return;
      
      const entries = historyContainer.querySelectorAll('.bg-gray-50');
      if (entries.length === 0) {
        // No entries, try to restore again
        restoreHistoryFromStorage();
      }
    }, 1500);
  }
  
  /**
   * Add new entries to the sharing history
   */
  function addToSharingHistory(playlistCheckboxes, friendCheckboxes) {
    // Get the history container
    const historyContainer = document.querySelector('.your-sharing-history-container');
    if (!historyContainer) {
      console.error('History container not found');
      return;
    }
    
    // Remove empty state if present
    const emptyMessage = historyContainer.querySelector('.flex.items-center.justify-center');
    if (emptyMessage) {
      emptyMessage.remove();
    }
    
    // Get or create entries container
    let entriesContainer = historyContainer.querySelector('.space-y-2');
    if (!entriesContainer) {
      entriesContainer = document.createElement('div');
      entriesContainer.className = 'space-y-2';
      
      // Find where to insert
      const header = historyContainer.querySelector('h2');
      if (header) {
        const headerContainer = header.closest('.flex');
        if (headerContainer) {
          headerContainer.parentNode.insertBefore(entriesContainer, headerContainer.nextSibling);
        } else {
          historyContainer.appendChild(entriesContainer);
        }
      } else {
        historyContainer.appendChild(entriesContainer);
      }
    }
    
    // Track existing entries to avoid duplicates
    const existingEntries = new Set();
    entriesContainer.querySelectorAll('.bg-gray-50').forEach(entry => {
      const friendElem = entry.querySelector('.text-sm.text-gray-500');
      const playlistElem = entry.querySelector('.font-medium');
      
      if (friendElem && playlistElem) {
        const key = `${playlistElem.textContent.trim()}|${friendElem.textContent.trim()}`;
        existingEntries.add(key);
      }
    });
    
    // Add entries for each friend
    friendCheckboxes.forEach(friendCheckbox => {
      const label = friendCheckbox.closest('label');
      if (!label) return;
      
      // Get friend info
      const nameElement = label.querySelector('.font-medium.text-gray-800');
      const friendName = nameElement ? nameElement.textContent.trim() : 'Friend';
      const initial = friendName[0].toUpperCase();
      
      // Get profile photo
      let photoHTML = '';
      const photoElement = label.querySelector('img.rounded-full');
      if (photoElement) {
        photoHTML = `<img src="${photoElement.src}" alt="${friendName}" class="w-10 h-10 rounded-full object-cover mr-3">`;
      } else {
        photoHTML = `
          <div class="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-lg mr-3">
            ${initial}
          </div>
        `;
      }
      
      // Get playlists
      const playlistNames = [];
      playlistCheckboxes.forEach(playlistCheckbox => {
        const playlistLabel = playlistCheckbox.closest('label');
        if (playlistLabel) {
          const nameEl = playlistLabel.querySelector('.font-medium.text-gray-800');
          if (nameEl) {
            playlistNames.push(nameEl.textContent.trim());
          }
        }
      });
      
      // Format playlist names
      const playlistDisplay = playlistNames.length === 1 
        ? playlistNames[0] 
        : playlistNames.length === 2 
          ? `${playlistNames[0]} and ${playlistNames[1]}`
          : `${playlistNames[0]} and ${playlistNames.length - 1} more`;
      
      // Check for duplicates
      const entryKey = `${playlistDisplay}|Shared with ${friendName}`;
      if (existingEntries.has(entryKey)) {
        console.log('Skipping duplicate entry:', entryKey);
        return;
      }
      
      // Create entry
      const entry = document.createElement('div');
      entry.className = 'bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-all animate-appear';
      entry.innerHTML = `
        <div class="flex items-center">
          ${photoHTML}
          <div>
            <div class="font-medium">${playlistDisplay}</div>
            <div class="text-sm text-gray-500">Shared with ${friendName}</div>
          </div>
        </div>
      `;
      
      // Add to container
      entriesContainer.prepend(entry);
      
      // Save to localStorage immediately
      saveHistoryToStorage();
    });
  }