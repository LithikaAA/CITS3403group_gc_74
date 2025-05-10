/**
 * Custom Dropdown for Playlist Selector
 * This script handles the custom dropdown functionality for the playlist selector
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get necessary DOM elements
    const customDropdown = document.querySelector('.custom-dropdown-container');
    const hiddenSelect = document.getElementById('playlist-selector');
    const dropdownButton = document.getElementById('playlist-display');
    const dropdownMenu = document.getElementById('playlist-dropdown');
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    const selectedText = document.getElementById('selected-playlist-text');
    const dropdownArrow = document.querySelector('.dropdown-arrow');
    
    // Only run if the custom dropdown exists
    if (customDropdown) {
      // Toggle dropdown visibility
      dropdownButton.addEventListener('click', function() {
        const isExpanded = dropdownButton.getAttribute('aria-expanded') === 'true';
        dropdownButton.setAttribute('aria-expanded', !isExpanded);
        dropdownMenu.classList.toggle('show');
        
        // Rotate arrow when dropdown is open
        if (!isExpanded) {
          dropdownArrow.style.transform = 'rotate(180deg)';
        } else {
          dropdownArrow.style.transform = 'rotate(0)';
        }
      });
      
      // Close dropdown when clicking outside
      document.addEventListener('click', function(event) {
        if (!dropdownButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
          dropdownButton.setAttribute('aria-expanded', 'false');
          dropdownMenu.classList.remove('show');
          dropdownArrow.style.transform = 'rotate(0)';
        }
      });
      
      // Handle item selection
      dropdownItems.forEach(item => {
        item.addEventListener('click', function() {
          const value = this.dataset.value;
          const text = this.querySelector('span').textContent;
          
          // Update the hidden select
          hiddenSelect.value = value;
          
          // Update button text
          selectedText.textContent = text;
          
          // Update selected state
          dropdownItems.forEach(el => {
            el.classList.remove('selected');
            el.setAttribute('aria-selected', 'false');
            // Remove existing check icons
            const existingIcon = el.querySelector('.check-icon');
            if (existingIcon) {
              el.removeChild(existingIcon);
            }
          });
          
          this.classList.add('selected');
          this.setAttribute('aria-selected', 'true');
          
          // Add check icon
          if (!this.querySelector('.check-icon')) {
            const checkIcon = document.createElement('div');
            checkIcon.innerHTML = `
              <svg class="check-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            `;
            this.prepend(checkIcon.firstElementChild);
          }
          
          // Close dropdown
          dropdownMenu.classList.remove('show');
          dropdownButton.setAttribute('aria-expanded', 'false');
          dropdownArrow.style.transform = 'rotate(0)';
          
          // Show loading state
          document.body.style.cursor = 'wait';
          
          // Create loading overlay
          const loadingOverlay = document.createElement('div');
          loadingOverlay.className = 'fixed inset-0 bg-gray-900 bg-opacity-30 flex items-center justify-center z-50';
          loadingOverlay.innerHTML = `
            <div class="bg-white p-6 rounded-xl shadow-xl flex flex-col items-center">
              <div class="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p class="text-gray-700 font-medium">Loading playlist data...</p>
            </div>
          `;
          document.body.appendChild(loadingOverlay);
          
          // Fetch new data for the selected playlist
          fetch(`/dashboard/playlist-data?playlist_id=${value}`)
            .then(response => {
              if (!response.ok) {
                throw new Error('Network response was not ok');
              }
              return response.json();
            })
            .then(data => {
              console.log("Received new playlist data:", data);
              updateCharts(data);
              document.body.style.cursor = 'default';
              loadingOverlay.remove();
            })
            .catch(error => {
              console.error('Error fetching playlist data:', error);
              document.body.style.cursor = 'default';
              loadingOverlay.remove();
              
              // Show error notification
              const errorNotification = document.createElement('div');
              errorNotification.className = 'fixed top-6 left-1/2 transform -translate-x-1/2 z-50 bg-red-500 text-white px-6 py-3 rounded-lg shadow-xl font-medium animate-fade-in';
              errorNotification.innerHTML = `
                <div class="flex items-center space-x-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                  <span>Failed to load playlist data. Please try again.</span>
                </div>
              `;
              document.body.appendChild(errorNotification);
              setTimeout(() => errorNotification.remove(), 3000);
            });
        });
      });
      
      // Handle keyboard navigation
      dropdownButton.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown' || e.key === 'ArrowUp') {
          e.preventDefault();
          
          if (e.key === 'Enter' || e.key === ' ') {
            dropdownButton.click();
          } else if (dropdownMenu.classList.contains('show')) {
            const currentIndex = Array.from(dropdownItems).findIndex(item => item.classList.contains('selected'));
            let nextIndex;
            
            if (e.key === 'ArrowDown') {
              nextIndex = (currentIndex + 1) % dropdownItems.length;
            } else if (e.key === 'ArrowUp') {
              nextIndex = (currentIndex - 1 + dropdownItems.length) % dropdownItems.length;
            }
            
            if (nextIndex !== undefined) {
              dropdownItems[nextIndex].click();
            }
          }
        }
      });
      
      // Add initial load behavior
      // Make sure the dropdown button reflects the currently selected playlist
      const initialSelected = document.querySelector('.dropdown-item.selected');
      if (initialSelected) {
        selectedText.textContent = initialSelected.querySelector('span').textContent;
      }
    } else {
      console.log("Custom dropdown not found, using native select element");
      
      // If using the native select element
      const playlistSelector = document.getElementById('playlist-selector');
      if (playlistSelector) {
        playlistSelector.addEventListener('change', function() {
          const playlistId = this.value;
          
          // Show loading state
          document.body.style.cursor = 'wait';
          
          // Create loading overlay
          const loadingOverlay = document.createElement('div');
          loadingOverlay.className = 'fixed inset-0 bg-gray-900 bg-opacity-30 flex items-center justify-center z-50';
          loadingOverlay.innerHTML = `
            <div class="bg-white p-6 rounded-xl shadow-xl flex flex-col items-center">
              <div class="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p class="text-gray-700 font-medium">Loading playlist data...</p>
            </div>
          `;
          document.body.appendChild(loadingOverlay);
          
          // Fetch new data for the selected playlist
          fetch(`/dashboard/playlist-data?playlist_id=${playlistId}`)
            .then(response => {
              if (!response.ok) {
                throw new Error('Network response was not ok');
              }
              return response.json();
            })
            .then(data => {
              console.log("Received new playlist data:", data);
              updateCharts(data);
              document.body.style.cursor = 'default';
              loadingOverlay.remove();
            })
            .catch(error => {
              console.error('Error fetching playlist data:', error);
              document.body.style.cursor = 'default';
              loadingOverlay.remove();
              
              // Show error notification
              const errorNotification = document.createElement('div');
              errorNotification.className = 'fixed top-6 left-1/2 transform -translate-x-1/2 z-50 bg-red-500 text-white px-6 py-3 rounded-lg shadow-xl font-medium animate-fade-in';
              errorNotification.innerHTML = `
                <div class="flex items-center space-x-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                  <span>Failed to load playlist data. Please try again.</span>
                </div>
              `;
              document.body.appendChild(errorNotification);
              setTimeout(() => errorNotification.remove(), 3000);
            });
        });
      } else {
        console.error('Playlist selector element not found');
      }
    }
  
    // Add hover effect to chart containers
    const chartContainers = document.querySelectorAll('.chart-container, .bg-white.rounded-2xl');
    chartContainers.forEach(container => {
      container.addEventListener('mouseenter', function() {
        this.classList.add('shadow-xl');
        this.style.transform = 'scale(1.01)';
      });
      
      container.addEventListener('mouseleave', function() {
        this.classList.remove('shadow-xl');
        this.style.transform = 'scale(1)';
      });
    });
  });