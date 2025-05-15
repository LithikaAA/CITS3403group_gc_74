/**
 * Shared Playlist Dropdown JS
 * Handles functionality for the Friend Comparison Dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Initializing shared playlist dropdown JS...');
  
  // Get references to the dropdown elements
  const yourPlaylistSelect = document.getElementById('yourPlaylistSelect');
  const friendPlaylistSelect = document.getElementById('friendPlaylistSelect');
  const errorMessage = document.getElementById('errorMessage');
  const closeError = document.getElementById('closeError');
  const selectedPlaylists = document.getElementById('selectedPlaylists');
  
  // Debug logs to check if elements are found
  console.log('Your playlist dropdown found:', !!yourPlaylistSelect);
  console.log('Friend playlist dropdown found:', !!friendPlaylistSelect);
  
  // Fix Z-index and pointer events to ensure dropdowns work
  if (yourPlaylistSelect) {
      yourPlaylistSelect.style.zIndex = "50";
      yourPlaylistSelect.style.pointerEvents = "auto";
      
      // Add styling for the selected option to show it as gradient
      yourPlaylistSelect.addEventListener('change', function() {
          console.log('Your playlist changed:', yourPlaylistSelect.value);
          updateGradientStyles();
          checkSelections();
      });
  }
  
  if (friendPlaylistSelect) {
      friendPlaylistSelect.style.zIndex = "50";
      friendPlaylistSelect.style.pointerEvents = "auto";
      
      // Add styling for the selected option to show it as gradient
      friendPlaylistSelect.addEventListener('change', function() {
          console.log('Friend playlist changed:', friendPlaylistSelect.value);
          updateGradientStyles();
          checkSelections();
      });
  }
  
  // Event listener for error message close button
  if (closeError) {
      closeError.addEventListener('click', function() {
          errorMessage.classList.add('hidden');
      });
  }
  
  // Apply gradient styling to selected options
  function updateGradientStyles() {
      // Your playlist select styling
      if (yourPlaylistSelect && yourPlaylistSelect.value) {
          const selectedText = yourPlaylistSelect.options[yourPlaylistSelect.selectedIndex].text;
          const parentWrapper = yourPlaylistSelect.closest('.select-wrapper');
          
          if (parentWrapper) {
              // Create or update the visual element
              let visualElement = parentWrapper.querySelector('.visual-selected');
              if (!visualElement) {
                  visualElement = document.createElement('div');
                  visualElement.className = 'visual-selected absolute top-0 left-0 right-0 bottom-0 pointer-events-none z-0';
                  parentWrapper.appendChild(visualElement);
              }
              
              // Style the visual element with gradient
              visualElement.innerHTML = `
                  <div class="gradient-button w-full h-full flex items-center justify-between px-4">
                      <span>${selectedText}</span>
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                  </div>
              `;
              
              // Make the actual select transparent
              yourPlaylistSelect.style.opacity = "0";
          }
      }
      
      // Friend playlist select styling
      if (friendPlaylistSelect && friendPlaylistSelect.value) {
          const selectedText = friendPlaylistSelect.options[friendPlaylistSelect.selectedIndex].text;
          const parentWrapper = friendPlaylistSelect.closest('.select-wrapper');
          
          if (parentWrapper) {
              // Create or update the visual element
              let visualElement = parentWrapper.querySelector('.visual-selected');
              if (!visualElement) {
                  visualElement = document.createElement('div');
                  visualElement.className = 'visual-selected absolute top-0 left-0 right-0 bottom-0 pointer-events-none z-0';
                  parentWrapper.appendChild(visualElement);
              }
              
              // Style the visual element with gradient
              visualElement.innerHTML = `
                  <div class="gradient-button w-full h-full flex items-center justify-between px-4">
                      <span>${selectedText}</span>
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                  </div>
              `;
              
              // Make the actual select transparent
              friendPlaylistSelect.style.opacity = "0";
          }
      }
  }
  
  // Function to check if both dropdowns have selections
  function checkSelections() {
      console.log('Checking selections...');
      
      if (yourPlaylistSelect.value && friendPlaylistSelect.value) {
          console.log('Both playlists selected, updating display and loading data');
          
          // Update selected playlists display
          updateSelectedPlaylists();
          
          // Load comparison data
          loadComparisonData(yourPlaylistSelect.value, friendPlaylistSelect.value);
      }
  }
  
  // Update selected playlists display
  function updateSelectedPlaylists() {
      if (!selectedPlaylists) return;
      
      const yourPlaylistName = yourPlaylistSelect.options[yourPlaylistSelect.selectedIndex].text;
      const friendOption = friendPlaylistSelect.options[friendPlaylistSelect.selectedIndex];
      const friendPlaylistName = friendOption.text;
      
      // Set playlist names
      const yourPlaylistNameEl = document.getElementById('yourPlaylistName');
      const friendPlaylistNameEl = document.getElementById('friendPlaylistName');
      
      if (yourPlaylistNameEl) yourPlaylistNameEl.textContent = yourPlaylistName;
      if (friendPlaylistNameEl) friendPlaylistNameEl.textContent = friendPlaylistName;
      
      // Show the selected playlists info
      selectedPlaylists.classList.remove('hidden');
      
      // Save selections to localStorage
      localStorage.setItem('yourPlaylistId', yourPlaylistSelect.value);
      localStorage.setItem('friendPlaylistId', friendPlaylistSelect.value);
  }
  
  // Function to load comparison data
  function loadComparisonData(yourId, friendId) {
      console.log(`Loading comparison data: your_id=${yourId}, friend_id=${friendId}`);
      
      // Show loading state on charts
      document.querySelectorAll('canvas').forEach(canvas => {
          if (canvas.parentNode) {
              canvas.parentNode.classList.add('opacity-50');
          }
      });
      
      // Hide any previous error
      if (errorMessage) {
          errorMessage.classList.add('hidden');
      }
      
      // Fetch comparison data
      fetch(`/share/compare-playlists?your_id=${yourId}&friend_id=${friendId}`)
          .then(response => {
              if (!response.ok) {
                  throw new Error(`Server response error: ${response.status}`);
              }
              return response.json();
          })
          .then(data => {
              console.log('Received comparison data successfully');
              
              // Update charts with new data
              updateCharts(data);
              
              // Remove loading state
              document.querySelectorAll('canvas').forEach(canvas => {
                  if (canvas.parentNode) {
                      canvas.parentNode.classList.remove('opacity-50');
                  }
              });
          })
          .catch(error => {
              console.error('Error fetching comparison data:', error);
              
              // Remove loading state
              document.querySelectorAll('canvas').forEach(canvas => {
                  if (canvas.parentNode) {
                      canvas.parentNode.classList.remove('opacity-50');
                  }
              });
              
              // Show error message
              if (errorMessage) {
                  errorMessage.classList.remove('hidden');
              }
          });
  }
  
  // Update all charts with new data
  function updateCharts(data) {
      if (!data) {
          console.error('No data received for charts update');
          return;
      }
      
      // Update valence vs acousticness chart
      if (data.valence_acousticness) {
          updateValenceAcousticnessChart(data.valence_acousticness);
      }
      
      // Update danceability vs energy chart
      if (data.comparison_bubble) {
          updateDanceabilityEnergyChart(data.comparison_bubble);
      }
      
      // Update mood profile chart
      if (data.comparison_mood) {
          updateMoodProfileChart(data.comparison_mood);
      }
      
      // Update mode chart
      if (data.comparison_mode) {
          updateModeChart(data.comparison_mode);
      }
      
      // Update summary
      if (data.shared_summary) {
          updateSummary(data.shared_summary);
      }
      
      // Update top songs
      if (data.top_popular_songs) {
          updatePopularSongs(data.top_popular_songs);
      }
  }
  
  // Update valence vs acousticness chart
  function updateValenceAcousticnessChart(data) {
      const canvas = document.getElementById('valenceAcousticness');
      if (!canvas) {
          console.error('Valence chart not found');
          return;
      }
      
      // Destroy old chart if it exists
      if (valenceChart) {
          safeDestroyChart(valenceChart);
          valenceChart = null;
      }
      
      // Create new chart
      const ctx = canvas.getContext('2d');
      valenceChart = new Chart(ctx, {
          type: 'scatter',
          data: {
              datasets: [
                  {
                      label: 'Your Songs',
                      data: data.you || [],
                      backgroundColor: 'rgba(99, 102, 241, 0.7)',
                      pointRadius: 8,
                      pointHoverRadius: 10,
                      borderColor: '#6366F1',
                      borderWidth: 1
                  },
                  {
                      label: "Friend's Songs",
                      data: data.friend || [],
                      backgroundColor: 'rgba(236, 72, 153, 0.7)',
                      pointRadius: 8,
                      pointHoverRadius: 10,
                      borderColor: '#EC4899',
                      borderWidth: 1
                  }
              ]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      position: 'top',
                      labels: {
                          usePointStyle: true,
                          boxWidth: 8,
                          font: { size: 11 }
                      }
                  },
                  tooltip: {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      titleColor: '#1F2937',
                      bodyColor: '#4B5563',
                      borderColor: '#E5E7EB',
                      borderWidth: 1,
                      padding: 10,
                      cornerRadius: 6,
                      callbacks: {
                          label: function(context) {
                              const point = context.raw;
                              if (!point) return ['Unknown'];
                              return [
                                  `${point.title || 'Unknown'} - ${point.artist || 'Unknown'}`,
                                  `Valence: ${point.y?.toFixed(2) || 'N/A'}`,
                                  `Acousticness: ${point.x?.toFixed(2) || 'N/A'}`
                              ];
                          }
                      }
                  }
              },
              scales: {
                  x: {
                      title: { 
                          display: true, 
                          text: 'Acousticness',
                          color: '#9CA3AF',
                          font: { size: 10 }
                      },
                      min: 0,
                      max: 1,
                      grid: {
                          color: 'rgba(243, 244, 246, 0.6)',
                          borderColor: 'rgba(243, 244, 246, 0.9)'
                      },
                      ticks: {
                          color: '#9CA3AF',
                          font: { size: 9 }
                      }
                  },
                  y: {
                      title: { 
                          display: true, 
                          text: 'Valence',
                          color: '#9CA3AF',
                          font: { size: 10 }
                      },
                      min: 0,
                      max: 1,
                      grid: {
                          color: 'rgba(243, 244, 246, 0.6)',
                          borderColor: 'rgba(243, 244, 246, 0.9)'
                      },
                      ticks: {
                          color: '#9CA3AF',
                          font: { size: 9 }
                      }
                  }
              }
          }
      });
      
      // Add divider lines via the chart's draw function
      const originalDraw = valenceChart.draw;
      valenceChart.draw = function() {
          originalDraw.apply(this, arguments);
          
          const chartArea = this.chartArea;
          const xAxis = this.scales.x;
          const yAxis = this.scales.y;
          
          if (!xAxis || !yAxis) return;
          
          // Draw divider lines
          const ctx = this.ctx;
          ctx.save();
          ctx.strokeStyle = 'rgba(203, 213, 225, 0.5)';
          ctx.lineWidth = 1;
          ctx.setLineDash([5, 5]);
          
          // Vertical line at x=0.5
          const xMid = xAxis.getPixelForValue(0.5);
          ctx.beginPath();
          ctx.moveTo(xMid, chartArea.top);
          ctx.lineTo(xMid, chartArea.bottom);
          ctx.stroke();
          
          // Horizontal line at y=0.5
          const yMid = yAxis.getPixelForValue(0.5);
          ctx.beginPath();
          ctx.moveTo(chartArea.left, yMid);
          ctx.lineTo(chartArea.right, yMid);
          ctx.stroke();
          
          ctx.restore();
      };
  }
  
  // Update danceability vs energy chart
  function updateDanceabilityEnergyChart(data) {
      const canvas = document.getElementById('danceabilityEnergy');
      if (!canvas) {
          console.error('Danceability chart not found');
          return;
      }
      
      // Get the existing chart
      const existingChart = Chart.getChart(canvas);
      if (existingChart) {
          // Destroy the existing chart first
          existingChart.destroy();
      }
      
      // Create new chart
      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
          type: 'bubble',
          data: {
              datasets: [
                  {
                      label: 'Your Songs',
                      data: data.you || [],
                      backgroundColor: 'rgba(129, 140, 248, 0.7)',
                      borderColor: '#6366F1',
                      borderWidth: 1
                  },
                  {
                      label: "Friend's Songs",
                      data: data.friend || [],
                      backgroundColor: 'rgba(244, 114, 182, 0.7)',
                      borderColor: '#EC4899',
                      borderWidth: 1
                  }
              ]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      position: 'top',
                      labels: {
                          usePointStyle: true,
                          boxWidth: 8,
                          font: { size: 11 }
                      }
                  },
                  tooltip: {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      titleColor: '#1F2937',
                      bodyColor: '#4B5563',
                      borderColor: '#E5E7EB',
                      borderWidth: 1,
                      padding: 10,
                      cornerRadius: 6,
                      callbacks: {
                          label: function(context) {
                              const point = context.raw;
                              if (!point) return ['Unknown'];
                              return [
                                  `${point.title || 'Unknown'} - ${point.artist || 'Unknown'}`,
                                  `Danceability: ${point.x?.toFixed(2) || 'N/A'}`,
                                  `Energy: ${point.y?.toFixed(2) || 'N/A'}`,
                                  `Minutes: ${(point.r/5)?.toFixed(1) || 'N/A'}`
                              ];
                          }
                      }
                  }
              },
              scales: {
                  x: {
                      title: { 
                          display: true, 
                          text: 'Danceability',
                          color: '#9CA3AF',
                          font: { size: 10 }
                      },
                      min: 0.5,
                      max: 0.9,
                      grid: {
                          color: 'rgba(243, 244, 246, 0.6)',
                          borderColor: 'rgba(243, 244, 246, 0.9)'
                      },
                      ticks: {
                          color: '#9CA3AF',
                          font: { size: 9 }
                      }
                  },
                  y: {
                      title: { 
                          display: true, 
                          text: 'Energy',
                          color: '#9CA3AF',
                          font: { size: 10 }
                      },
                      min: 0.5,
                      max: 0.9,
                      grid: {
                          color: 'rgba(243, 244, 246, 0.6)',
                          borderColor: 'rgba(243, 244, 246, 0.9)'
                      },
                      ticks: {
                          color: '#9CA3AF',
                          font: { size: 9 }
                      }
                  }
              }
          }
      });
  }
  
  // Update mood profile chart
  function updateMoodProfileChart(data) {
      const canvas = document.getElementById('moodProfile');
      if (!canvas) {
          console.error('Mood profile chart not found');
          return;
      }
      
      // Get the existing chart
      const existingChart = Chart.getChart(canvas);
      if (existingChart) {
          // Destroy the existing chart first
          existingChart.destroy();
      }
      
      // Create new chart
      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
          type: 'radar',
          data: {
              labels: ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Liveness'],
              datasets: [
                  {
                      label: 'Your Profile',
                      data: data.you || [0, 0, 0, 0, 0],
                      backgroundColor: 'rgba(99, 102, 241, 0.2)',
                      borderColor: '#6366F1',
                      pointBackgroundColor: '#6366F1',
                      pointBorderColor: '#FFFFFF',
                      borderWidth: 2,
                      pointRadius: 3
                  },
                  {
                      label: "Friend's Profile",
                      data: data.friend || [0, 0, 0, 0, 0],
                      backgroundColor: 'rgba(236, 72, 153, 0.2)',
                      borderColor: '#EC4899',
                      pointBackgroundColor: '#EC4899',
                      pointBorderColor: '#FFFFFF',
                      borderWidth: 2,
                      pointRadius: 3
                  }
              ]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      position: 'top',
                      labels: {
                          usePointStyle: true,
                          boxWidth: 8,
                          font: { size: 11 }
                      }
                  },
                  tooltip: {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      titleColor: '#1F2937',
                      bodyColor: '#4B5563',
                      borderColor: '#E5E7EB',
                      borderWidth: 1,
                      padding: 10,
                      cornerRadius: 6
                  }
              },
              scales: {
                  r: {
                      angleLines: {
                          color: 'rgba(203, 213, 225, 0.3)'
                      },
                      grid: {
                          color: 'rgba(203, 213, 225, 0.3)'
                      },
                      pointLabels: {
                          color: '#6B7280',
                          font: { size: 9 }
                      },
                      beginAtZero: true,
                      max: 1,
                      ticks: {
                          display: false,
                          stepSize: 0.2
                      }
                  }
              }
          }
      });
  }
  
  // Update mode chart
  function updateModeChart(data) {
      const canvas = document.getElementById('modeChart');
      if (!canvas) {
          console.error('Mode chart not found');
          return;
      }
      
      // Get the existing chart
      const existingChart = Chart.getChart(canvas);
      if (existingChart) {
          // Destroy the existing chart first
          existingChart.destroy();
      }
      
      // Create new chart
      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
          type: 'bar',
          data: {
              labels: ['Major', 'Minor'],
              datasets: [
                  {
                      label: 'Your Songs',
                      data: data.you || [0, 0],
                      backgroundColor: '#6366F1',
                      borderRadius: 6,
                      maxBarThickness: 35
                  },
                  {
                      label: "Friend's Songs",
                      data: data.friend || [0, 0],
                      backgroundColor: '#EC4899',
                      borderRadius: 6,
                      maxBarThickness: 35
                  }
              ]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      position: 'top',
                      labels: {
                          usePointStyle: true,
                          boxWidth: 8,
                          font: { size: 11 }
                      }
                  },
                  tooltip: {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      titleColor: '#1F2937',
                      bodyColor: '#4B5563',
                      borderColor: '#E5E7EB',
                      borderWidth: 1,
                      padding: 10,
                      cornerRadius: 6,
                      callbacks: {
                          label: function(context) {
                              return context.dataset.label + ': ' + context.parsed.y + ' songs';
                          }
                      }
                  }
              },
              scales: {
                  y: {
                      beginAtZero: true,
                      grid: {
                          color: 'rgba(243, 244, 246, 0.6)',
                          borderColor: 'rgba(243, 244, 246, 0.9)'
                      },
                      ticks: {
                          color: '#9CA3AF',
                          font: { size: 9 },
                          precision: 0,
                          stepSize: 1
                      }
                  },
                  x: {
                      grid: {
                          display: false
                      },
                      ticks: {
                          color: '#6B7280',
                          font: { size: 10 }
                      }
                  }
              }
          }
      });
  }
  
  // Update summary data
  function updateSummary(data) {
      if (!data) return;
      
      // Update all summary items
      const elements = {
          'your-avg-tempo': data.your_avg_tempo ? `${data.your_avg_tempo} BPM` : 'N/A',
          'friend-avg-tempo': data.friend_avg_tempo ? `${data.friend_avg_tempo} BPM` : 'N/A',
          'your-mood': data.your_mood || 'N/A',
          'friend-mood': data.friend_mood || 'N/A'
      };
      
      // Update by data-summary attribute
      for (const [key, value] of Object.entries(elements)) {
          const element = document.querySelector(`[data-summary="${key}"]`);
          if (element) {
              element.textContent = value;
          }
      }
  }
  
  // Update popular songs
  function updatePopularSongs(data) {
      if (!data) return;
      
      // Update your songs
      updateSongsList('.your-top-songs', data.you || []);
      
      // Update friend songs
      updateSongsList('.friend-top-songs', data.friend || []);
      
      // Setup tab interactions
      setupSongTabs();
  }
  
  // Helper to update songs list
  function updateSongsList(selector, songs) {
      const container = document.querySelector(selector);
      if (!container) return;
      
      // Clear container
      container.innerHTML = '';
      
      // Add songs
      const isYourSongs = selector.includes('your');
      const color = isYourSongs ? 'indigo' : 'pink';
      
      songs.forEach((song, index) => {
          const songElement = document.createElement('div');
          songElement.className = `flex items-center space-x-3 p-2 ${index === 0 ? `bg-${color}-50 rounded-lg` : ''}`;
          
          songElement.innerHTML = `
              <div class="w-6 h-6 bg-${color}-100 rounded-full flex items-center justify-center text-xs font-bold text-${color}-700">#${index + 1}</div>
              <div class="overflow-hidden">
                  <p class="text-sm font-medium text-gray-800 truncate">${song.title || 'Unknown'}</p>
                  <p class="text-xs text-gray-500 truncate">${song.artist || 'Unknown'}</p>
              </div>
          `;
          
          container.appendChild(songElement);
      });
  }
  
  // Setup song tabs
  function setupSongTabs() {
      const yourTab = document.getElementById('yourTopSongsTab');
      const friendTab = document.getElementById('friendTopSongsTab');
      const yourSongs = document.querySelector('.your-top-songs');
      const friendSongs = document.querySelector('.friend-top-songs');
      
      if (!yourTab || !friendTab || !yourSongs || !friendSongs) return;
      
      // Remove existing listeners by cloning and replacing
      const newYourTab = yourTab.cloneNode(true);
      const newFriendTab = friendTab.cloneNode(true);
      
      yourTab.parentNode.replaceChild(newYourTab, yourTab);
      friendTab.parentNode.replaceChild(newFriendTab, friendTab);
      
      // Add new event listeners
      newYourTab.addEventListener('click', function(e) {
          e.preventDefault();
          yourSongs.classList.remove('hidden');
          friendSongs.classList.add('hidden');
          newYourTab.classList.add('text-indigo-600', 'active');
          newYourTab.classList.remove('text-gray-500');
          newFriendTab.classList.add('text-gray-500');
          newFriendTab.classList.remove('text-pink-600', 'active');
      });
      
      newFriendTab.addEventListener('click', function(e) {
          e.preventDefault();
          friendSongs.classList.remove('hidden');
          yourSongs.classList.add('hidden');
          newFriendTab.classList.add('text-pink-600', 'active');
          newFriendTab.classList.remove('text-gray-500');
          newYourTab.classList.add('text-gray-500');
          newYourTab.classList.remove('text-indigo-600', 'active');
      });
      
      // Set initial active state
      if (!yourSongs.classList.contains('hidden')) {
          newYourTab.classList.add('active');
      } else if (!friendSongs.classList.contains('hidden')) {
          newFriendTab.classList.add('active');
      } else {
          // Default to showing your songs
          yourSongs.classList.remove('hidden');
          friendSongs.classList.add('hidden');
          newYourTab.classList.add('active');
      }
  }
  
  // Try to restore previous selections
  function restorePreviousSelections() {
      const yourId = localStorage.getItem('yourPlaylistId');
      const friendId = localStorage.getItem('friendPlaylistId');
      
      let yourFound = false;
      let friendFound = false;
      
      if (yourId && yourPlaylistSelect) {
          for (let i = 0; i < yourPlaylistSelect.options.length; i++) {
              if (yourPlaylistSelect.options[i].value === yourId) {
                  yourPlaylistSelect.selectedIndex = i;
                  yourFound = true;
                  break;
              }
          }
      }
      
      if (friendId && friendPlaylistSelect) {
          for (let i = 0; i < friendPlaylistSelect.options.length; i++) {
              if (friendPlaylistSelect.options[i].value === friendId) {
                  friendPlaylistSelect.selectedIndex = i;
                  friendFound = true;
                  break;
              }
          }
      }
      
      // If both found, trigger the selection
      if (yourFound && friendFound) {
          updateGradientStyles();
          checkSelections();
      }
  }
  
  // Initialize tabs and restore previous selections
  setupSongTabs();
  restorePreviousSelections();
});