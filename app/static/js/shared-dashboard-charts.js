/**
 * Shared Dashboard Charts JS
 * Handles the initialization of charts in the shared dashboard
 */

// Global chart objects
let valenceChart, danceabilityChart, moodChart, modeChart, minutesChart;

// Initialize all charts once the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Set up dropdown event listeners first
  setupDropdownListeners();
  
  // Set up top songs tabs
  setupTopSongsTabs();
  
  // Initialize error message handling
  setupErrorHandling();
  
  // Initialize the charts with placeholder data
  initializeCharts();
});

// Handle top songs tabs
function setupTopSongsTabs() {
  const yourTab = document.getElementById('yourTopSongsTab');
  const friendTab = document.getElementById('friendTopSongsTab');
  const yourSongs = document.querySelector('.your-top-songs');
  const friendSongs = document.querySelector('.friend-top-songs');
  
  if (!yourTab || !friendTab) return;
  
  yourTab.addEventListener('click', function(e) {
    e.preventDefault();
    yourSongs.classList.remove('hidden');
    friendSongs.classList.add('hidden');
    yourTab.classList.add('text-indigo-600');
    yourTab.classList.remove('text-gray-500');
    friendTab.classList.add('text-gray-500');
    friendTab.classList.remove('text-pink-600');
  });
  
  friendTab.addEventListener('click', function(e) {
    e.preventDefault();
    friendSongs.classList.remove('hidden');
    yourSongs.classList.add('hidden');
    friendTab.classList.add('text-pink-600');
    friendTab.classList.remove('text-gray-500');
    yourTab.classList.add('text-gray-500');
    yourTab.classList.remove('text-indigo-600');
  });
}

// Set up error handling
function setupErrorHandling() {
  const errorMessage = document.getElementById('errorMessage');
  const closeError = document.getElementById('closeError');
  
  if (closeError) {
    closeError.addEventListener('click', function() {
      errorMessage.classList.add('hidden');
    });
  }
}

// Initialize charts with placeholder or initial data
function initializeCharts() {
  initializeValenceAcousticnessChart();
  initializeDanceabilityEnergyChart();
  initializeMoodProfileChart();
  initializeModeChart();
}

// Initialize Valence vs Acousticness chart
function initializeValenceAcousticnessChart() {
  const canvas = document.getElementById('valenceAcousticness');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  
  // Check if we have any initial data
  const hasInitialData = window.initialBubbleData && 
                        window.initialBubbleData.you && 
                        window.initialBubbleData.you.length > 0;
  
  // Placeholder data if no initial data is available
  const placeholderData = [
    { x: 0.25, y: 0.5, title: "Your Song", artist: "Artist" }
  ];
  
  valenceChart = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Your Songs',
          data: hasInitialData ? window.initialBubbleData.you : placeholderData,
          backgroundColor: 'rgba(99, 102, 241, 0.8)',
          pointRadius: 8,
          pointHoverRadius: 10,
          borderColor: '#6366F1',
          borderWidth: 1
        },
        {
          label: 'Friend\'s Songs',
          data: hasInitialData ? window.initialBubbleData.friend : [],
          backgroundColor: 'rgba(236, 72, 153, 0.8)',
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
          align: 'center',
          labels: {
            usePointStyle: true,
            padding: 15,
            boxWidth: 8,
            font: { 
              size: 11
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#1F2937',
          bodyColor: '#4B5563',
          borderColor: '#E5E7EB',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
          titleFont: {
            size: 12,
            weight: 'bold'
          },
          bodyFont: {
            size: 12
          },
          callbacks: {
            label: function(context) {
              const point = context.raw;
              return [
                `${point.title || 'Unknown'} - ${point.artist || 'Unknown'}`,
                `Valence: ${point.y.toFixed(2)}`,
                `Acousticness: ${point.x.toFixed(2)}`
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
            font: {
              size: 10
            }
          },
          min: 0,
          max: 1,
          grid: {
            color: 'rgba(243, 244, 246, 0.6)',
            borderColor: 'rgba(243, 244, 246, 0.9)'
          },
          ticks: {
            color: '#9CA3AF',
            font: {
              size: 9
            }
          }
        },
        y: {
          title: { 
            display: true, 
            text: 'Valence',
            color: '#9CA3AF',
            font: {
              size: 10
            }
          },
          min: 0,
          max: 1,
          grid: {
            color: 'rgba(243, 244, 246, 0.6)',
            borderColor: 'rgba(243, 244, 246, 0.9)'
          },
          ticks: {
            color: '#9CA3AF',
            font: {
              size: 9
            }
          }
        }
      }
    }
  });
  
  // Create divider lines
  drawChartDividers(ctx, valenceChart);
}

// Draw chart divider lines
function drawChartDividers(ctx, chart) {
  const originalDraw = chart.draw;
  
  chart.draw = function() {
    originalDraw.apply(this, arguments);
    
    const chartArea = this.chartArea;
    const xAxis = this.scales.x;
    const yAxis = this.scales.y;
    
    // Convert data value 0.5 to pixel value for both axes
    const xMid = xAxis.getPixelForValue(0.5);
    const yMid = yAxis.getPixelForValue(0.5);
    
    ctx.save();
    ctx.strokeStyle = 'rgba(203, 213, 225, 0.5)';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    
    // Draw vertical line at x=0.5
    ctx.beginPath();
    ctx.moveTo(xMid, chartArea.top);
    ctx.lineTo(xMid, chartArea.bottom);
    ctx.stroke();
    
    // Draw horizontal line at y=0.5
    ctx.beginPath();
    ctx.moveTo(chartArea.left, yMid);
    ctx.lineTo(chartArea.right, yMid);
    ctx.stroke();
    
    ctx.restore();
  };
}

// Initialize Danceability vs Energy bubble chart
function initializeDanceabilityEnergyChart() {
  const canvas = document.getElementById('danceabilityEnergy');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  
  // Check if we have any initial data
  const hasInitialData = window.initialBubbleData && 
                        window.initialBubbleData.you && 
                        window.initialBubbleData.you.length > 0;
  
  // Placeholder data if no initial data is available
  const placeholderData = [
    { x: 0.75, y: 0.75, r: 15, title: "Your Song", artist: "Artist" }
  ];
  
  danceabilityChart = new Chart(ctx, {
    type: 'bubble',
    data: {
      datasets: [
        {
          label: 'Your Songs',
          data: hasInitialData ? window.initialBubbleData.you : placeholderData,
          backgroundColor: 'rgba(129, 140, 248, 0.7)',
          borderColor: '#6366F1',
          borderWidth: 1
        },
        {
          label: 'Friend\'s Songs',
          data: hasInitialData ? window.initialBubbleData.friend : [],
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
          align: 'center',
          labels: {
            usePointStyle: true,
            padding: 15,
            boxWidth: 8,
            font: { 
              size: 11
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#1F2937',
          bodyColor: '#4B5563',
          borderColor: '#E5E7EB',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: function(context) {
              const point = context.raw;
              return [
                `${point.title || 'Unknown'} - ${point.artist || 'Unknown'}`, 
                `Danceability: ${point.x.toFixed(2)}`, 
                `Energy: ${point.y.toFixed(2)}`,
                `Minutes: ${(point.r/5).toFixed(1)}`
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
            font: {
              size: 10
            }
          },
          min: 0.4,
          max: 0.9,
          grid: {
            color: 'rgba(243, 244, 246, 0.6)',
            borderColor: 'rgba(243, 244, 246, 0.9)'
          },
          ticks: {
            color: '#9CA3AF',
            font: {
              size: 9
            }
          }
        },
        y: {
          title: { 
            display: true, 
            text: 'Energy',
            color: '#9CA3AF',
            font: {
              size: 10
            }
          },
          min: 0.5,
          max: 0.9,
          grid: {
            color: 'rgba(243, 244, 246, 0.6)',
            borderColor: 'rgba(243, 244, 246, 0.9)'
          },
          ticks: {
            color: '#9CA3AF',
            font: {
              size: 9
            }
          }
        }
      }
    }
  });
}

// Initialize Mood Profile radar chart
function initializeMoodProfileChart() {
  const canvas = document.getElementById('moodProfile');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  
  // Check if we have any initial data
  const hasInitialData = window.initialMoodData && 
                        window.initialMoodData.you && 
                        window.initialMoodData.you.length > 0;
  
  // Placeholder data if no initial data is available
  const placeholderData = [0.7, 0.6, 0.5, 0.4, 0.6];
  
  moodChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Liveness'],
      datasets: [
        {
          label: 'Your Profile',
          data: hasInitialData ? window.initialMoodData.you : placeholderData,
          backgroundColor: 'rgba(99, 102, 241, 0.2)',
          borderColor: '#6366F1',
          pointBackgroundColor: '#6366F1',
          pointBorderColor: '#fff',
          borderWidth: 2,
          pointRadius: 3
        },
        {
          label: 'Friend\'s Profile',
          data: hasInitialData ? window.initialMoodData.friend : [],
          backgroundColor: 'rgba(236, 72, 153, 0.2)',
          borderColor: '#EC4899',
          pointBackgroundColor: '#EC4899',
          pointBorderColor: '#fff',
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
          align: 'center',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            padding: 15,
            font: { 
              size: 11
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#1F2937',
          bodyColor: '#4B5563',
          borderColor: '#E5E7EB',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8
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
            font: {
              size: 9
            }
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

// Initialize Mode comparison bar chart
function initializeModeChart() {
  const canvas = document.getElementById('modeChart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  
  // Check if we have any initial data
  const hasInitialData = window.initialModeData && 
                        window.initialModeData.you && 
                        window.initialModeData.you.length > 0;
  
  // Placeholder data if no initial data is available
  const placeholderYou = [2, 4];
  const placeholderFriend = [3, 2];
  
  modeChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Major', 'Minor'],
      datasets: [
        {
          label: 'Your Songs',
          data: hasInitialData ? window.initialModeData.you : placeholderYou,
          backgroundColor: '#6366F1',
          borderRadius: 6,
          maxBarThickness: 40
        },
        {
          label: 'Friend\'s Songs',
          data: hasInitialData ? window.initialModeData.friend : placeholderFriend,
          backgroundColor: '#EC4899',
          borderRadius: 6,
          maxBarThickness: 40
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          align: 'center',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            padding: 15,
            font: { 
              size: 11
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#1F2937',
          bodyColor: '#4B5563',
          borderColor: '#E5E7EB',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
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
            font: {
              size: 9
            },
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
            font: {
              size: 10
            }
          }
        }
      }
    }
  });
}

// Set up dropdown event listeners for updating charts
function setupDropdownListeners() {
  const yourPlaylistSelect = document.getElementById('yourPlaylistSelect');
  const friendPlaylistSelect = document.getElementById('friendPlaylistSelect');
  const selectedPlaylists = document.getElementById('selectedPlaylists');
  
  if (yourPlaylistSelect && friendPlaylistSelect) {
    yourPlaylistSelect.addEventListener('change', updateSelectedPlaylist);
    friendPlaylistSelect.addEventListener('change', updateSelectedPlaylist);
  }
  
  function updateSelectedPlaylist() {
    const yourPlaylistId = yourPlaylistSelect.value;
    const friendPlaylistId = friendPlaylistSelect.value;
    
    if (yourPlaylistId && friendPlaylistId) {
      // Update selected playlist display
      if (selectedPlaylists) {
        const yourPlaylistName = yourPlaylistSelect.options[yourPlaylistSelect.selectedIndex].text;
        const friendOption = friendPlaylistSelect.options[friendPlaylistSelect.selectedIndex];
        const friendPlaylistFullName = friendOption.text;
        const friendUsername = friendOption.getAttribute('data-username') || 'Friend';
        
        document.getElementById('yourPlaylistName').textContent = yourPlaylistName;
        document.getElementById('friendPlaylistName').textContent = friendPlaylistFullName;
        
        // Set friend's initial
        const friendInitial = document.getElementById('friendInitial');
        if (friendInitial && friendUsername) {
          friendInitial.textContent = friendUsername.charAt(0).toUpperCase();
        }
        
        selectedPlaylists.classList.remove('hidden');
      }
      
      // Fetch comparison data
      fetchComparisonData(yourPlaylistId, friendPlaylistId);
    }
  }
}

// Function to fetch comparison data
function fetchComparisonData(yourPlaylistId, friendPlaylistId) {
  const errorMessage = document.getElementById('errorMessage');
  
  // Show loading state on charts
  document.querySelectorAll('canvas').forEach(canvas => {
    canvas.parentNode.classList.add('opacity-50');
  });
  
  // Make AJAX request to get comparison data
  fetch(`/share/compare-playlists?your_id=${yourPlaylistId}&friend_id=${friendPlaylistId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Remove loading state
      document.querySelectorAll('canvas').forEach(canvas => {
        canvas.parentNode.classList.remove('opacity-50');
      });
      
      // Hide error message if shown
      if (errorMessage) {
        errorMessage.classList.add('hidden');
      }
      
      // Update all charts with the new data
      updateValenceAcousticnessChart(data.valence_acousticness);
      updateDanceabilityEnergyChart(data.comparison_bubble);
      updateMoodProfileChart(data.comparison_mood);
      updateModeChart(data.comparison_mode);
      updateSummary(data.shared_summary);
      updatePopularSongs(data.top_popular_songs);
      
      console.log('Charts updated successfully with new data');
    })
    .catch(error => {
      console.error('Error fetching comparison data:', error);
      
      // Remove loading state
      document.querySelectorAll('canvas').forEach(canvas => {
        canvas.parentNode.classList.remove('opacity-50');
      });
      
      // Show error message
      if (errorMessage) {
        errorMessage.classList.remove('hidden');
      }
    });
}

// Function to update the Valence vs Acousticness chart
function updateValenceAcousticnessChart(data) {
  if (!valenceChart || !data) return;
  
  // Ensure data has the expected properties
  const yourData = data.you || [];
  const friendData = data.friend || [];
  
  valenceChart.data.datasets[0].data = yourData;
  valenceChart.data.datasets[1].data = friendData;
  valenceChart.update();
}

// Function to update the Danceability vs Energy chart
function updateDanceabilityEnergyChart(data) {
  if (!danceabilityChart || !data) return;
  
  // Ensure data has the expected properties
  const yourData = data.you || [];
  const friendData = data.friend || [];
  
  danceabilityChart.data.datasets[0].data = yourData;
  danceabilityChart.data.datasets[1].data = friendData;
  danceabilityChart.update();
}

// Function to update the Mood Profile chart
function updateMoodProfileChart(data) {
  if (!moodChart || !data) return;
  
  // Ensure data has the expected properties
  const yourData = data.you || [];
  const friendData = data.friend || [];
  
  moodChart.data.datasets[0].data = yourData;
  moodChart.data.datasets[1].data = friendData;
  moodChart.update();
}

// Function to update the Mode chart
function updateModeChart(data) {
  if (!modeChart || !data) return;
  
  // Ensure data has the expected properties
  const yourData = data.you || [];
  const friendData = data.friend || [];
  
  modeChart.data.datasets[0].data = yourData;
  modeChart.data.datasets[1].data = friendData;
  modeChart.update();
}

// Function to update the summary section
function updateSummary(data) {
  if (!data) return;
  
  const yourAvgTempo = document.querySelector('[data-summary="your-avg-tempo"]');
  const friendAvgTempo = document.querySelector('[data-summary="friend-avg-tempo"]');
  const yourMood = document.querySelector('[data-summary="your-mood"]');
  const friendMood = document.querySelector('[data-summary="friend-mood"]');

  if (yourAvgTempo) yourAvgTempo.textContent = `${data.your_avg_tempo || 0} BPM`;
  if (friendAvgTempo) friendAvgTempo.textContent = `${data.friend_avg_tempo || 0} BPM`;
  if (yourMood) yourMood.textContent = data.your_mood || 'N/A';
  if (friendMood) friendMood.textContent = data.friend_mood || 'N/A';
}

// Function to update popular songs list
function updatePopularSongs(data) {
  if (!data) return;
  
  const yourList = document.querySelector('.your-top-songs');
  const friendList = document.querySelector('.friend-top-songs');

  if (!yourList || !friendList) return;

  // Update your top songs
  updateSongsList(yourList, data.you || [], 'indigo');
  
  // Update friend's top songs
  updateSongsList(friendList, data.friend || [], 'pink');
}

// Helper function to update a songs list
function updateSongsList(container, songs, color) {
  container.innerHTML = '';
  
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