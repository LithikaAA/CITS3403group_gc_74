/**
 * Shared Dashboard Charts JS
 * Handles the initialization of charts in the shared dashboard
 */

// Global chart objects
let valenceChart, danceabilityChart, moodChart, modeChart, minutesChart;

// Initialize all charts once the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize the charts
  initializeMinutesByTrackChart();
  initializeValenceAcousticnessChart();
  initializeDanceabilityEnergyChart();
  initializeMoodProfileChart();
  initializeModeChart();
  
  // Set up dropdown event listeners
  setupDropdownListeners();
});

function initializeMinutesByTrackChart() {
  const canvas = document.getElementById('minutesByTrack');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  minutesChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: window.initialMinutesData ? window.initialMinutesData.labels : [],
      datasets: [
        {
          label: 'Your Minutes',
          data: window.initialMinutesData ? window.initialMinutesData.yourData : [],
          backgroundColor: '#6366F1'
        },
        {
          label: "Friend's Minutes",
          data: window.initialMinutesData ? window.initialMinutesData.friendData : [],
          backgroundColor: '#F472B6'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Minutes Played',
            color: '#718096'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

// Initialize Valence vs Acousticness scatter chart
function initializeValenceAcousticnessChart() {
  const canvas = document.getElementById('valenceAcousticness');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  valenceChart = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Your Songs',
          data: [
            { x: 0.1, y: 0.5 },
            { x: 0.2, y: 0.3 }
          ],
          backgroundColor: 'rgba(99, 102, 241, 0.7)',
          pointRadius: 8,
          pointHoverRadius: 10
        },
        {
          label: 'Friend\'s Songs',
          data: [
            { x: 0.6, y: 0.2 },
            { x: 0.7, y: 0.4 }
          ],
          backgroundColor: 'rgba(244, 114, 182, 0.7)',
          pointRadius: 8,
          pointHoverRadius: 10
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: function(context) {
              const point = context.raw;
              return [
                `${point.title || 'Song'} - ${point.artist || 'Artist'}`,
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
            color: '#718096'
          },
          min: 0,
          max: 1,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          title: { 
            display: true, 
            text: 'Valence',
            color: '#718096'
          },
          min: 0,
          max: 1,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        }
      },
      annotation: {
        annotations: {
          quadrants: {
            type: 'line',
            xMin: 0.5,
            xMax: 0.5,
            yMin: 0,
            yMax: 1,
            borderColor: 'rgba(0, 0, 0, 0.1)',
            borderWidth: 1,
            borderDash: [5, 5]
          },
          horizontalCenter: {
            type: 'line',
            yMin: 0.5,
            yMax: 0.5,
            xMin: 0,
            xMax: 1,
            borderColor: 'rgba(0, 0, 0, 0.1)',
            borderWidth: 1,
            borderDash: [5, 5]
          }
        }
      }
    }
  });
}

// Initialize Danceability vs Energy bubble chart
function initializeDanceabilityEnergyChart() {
  const canvas = document.getElementById('danceabilityEnergy');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  danceabilityChart = new Chart(ctx, {
    type: 'bubble',
    data: {
      datasets: [
        {
          label: 'Your Songs',
          data: window.initialBubbleData ? window.initialBubbleData.you : [
            { x: 0.7, y: 0.9, r: 15 }
          ],
          backgroundColor: 'rgba(99, 102, 241, 0.7)',
          borderColor: '#6366F1'
        },
        {
          label: 'Friend\'s Songs',
          data: window.initialBubbleData ? window.initialBubbleData.friend : [
            { x: 0.55, y: 0.65, r: 15 }
          ],
          backgroundColor: 'rgba(244, 114, 182, 0.7)',
          borderColor: '#F472B6'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: function(context) {
              const point = context.raw;
              return [
                `${point.title || 'Song'} - ${point.artist || 'Artist'}`, 
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
            color: '#718096'
          },
          min: 0.4,
          max: 0.9,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          title: { 
            display: true, 
            text: 'Energy',
            color: '#718096'
          },
          min: 0.4,
          max: 0.9,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
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
  moodChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Liveness'],
      datasets: [
        {
          label: 'Your Profile',
          data: window.initialMoodData ? window.initialMoodData.you : [0.7, 0.6, 0.8, 0.3, 0.5],
          backgroundColor: 'rgba(99, 102, 241, 0.2)',
          borderColor: '#6366F1',
          pointBackgroundColor: '#6366F1'
        },
        {
          label: 'Friend\'s Profile',
          data: window.initialMoodData ? window.initialMoodData.friend : [0.5, 0.7, 0.6, 0.4, 0.6],
          backgroundColor: 'rgba(244, 114, 182, 0.2)',
          borderColor: '#F472B6',
          pointBackgroundColor: '#F472B6'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 1,
          ticks: {
            display: false
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
  modeChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Major', 'Minor'],
      datasets: [
        {
          label: 'Your Songs',
          data: window.initialModeData ? window.initialModeData.you : [5, 3],
          backgroundColor: '#6366F1'
        },
        {
          label: 'Friend\'s Songs',
          data: window.initialModeData ? window.initialModeData.friend : [2, 7],
          backgroundColor: '#F472B6'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { 
            display: true, 
            text: 'Number of Songs',
            color: '#718096'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
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
  
  if (yourPlaylistSelect && friendPlaylistSelect) {
    yourPlaylistSelect.addEventListener('change', updateCharts);
    friendPlaylistSelect.addEventListener('change', updateCharts);
  }
}

// Function to update all charts when playlist selection changes
function updateCharts() {
  const yourPlaylistId = document.getElementById('yourPlaylistSelect').value;
  const friendPlaylistId = document.getElementById('friendPlaylistSelect').value;
  
  if (!yourPlaylistId || !friendPlaylistId) return;
  
  // Show loading state on charts
  document.querySelectorAll('.chart-container').forEach(container => {
    container.classList.add('loading');
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
      // Update all charts with the new data
      updateMinutesByTrackChart(data.comparison_minutes);
      updateValenceAcousticnessChart(data.valence_acousticness);
      updateDanceabilityEnergyChart(data.comparison_bubble);
      updateMoodProfileChart(data.comparison_mood);
      updateModeChart(data.comparison_mode);
      updateSummary(data.shared_summary);
      updatePopularSongs(data.top_popular_songs);
      
      // Remove loading state
      document.querySelectorAll('.chart-container').forEach(container => {
        container.classList.remove('loading');
      });
    })
    .catch(error => {
      console.error('Error fetching comparison data:', error);
      // Remove loading state
      document.querySelectorAll('.chart-container').forEach(container => {
        container.classList.remove('loading');
      });
      
      // Show error message
      alert('Error loading comparison data. Please try again.');
    });
}

// Function to update the Valence vs Acousticness chart
function updateValenceAcousticnessChart(data) {
  if (!valenceChart) return;
  valenceChart.data.datasets[0].data = data.you;
  valenceChart.data.datasets[1].data = data.friend;
  valenceChart.update();
}

// Function to update the Danceability vs Energy chart
function updateDanceabilityEnergyChart(data) {
  if (!danceabilityChart) return;
  danceabilityChart.data.datasets[0].data = data.you;
  danceabilityChart.data.datasets[1].data = data.friend;
  danceabilityChart.update();
}

// Function to update the Mood Profile chart
function updateMoodProfileChart(data) {
  if (!moodChart) return;
  moodChart.data.datasets[0].data = data.you;
  moodChart.data.datasets[1].data = data.friend;
  moodChart.update();
}

// Function to update the Mode chart
function updateModeChart(data) {
  if (!modeChart) return;
  modeChart.data.datasets[0].data = data.you;
  modeChart.data.datasets[1].data = data.friend;
  modeChart.update();
}

function updateMinutesByTrackChart(data) {
  if (!minutesChart) return;
  minutesChart.data.labels = data.labels;
  minutesChart.data.datasets[0].data = data.your_data;
  minutesChart.data.datasets[1].data = data.friend_data;
  minutesChart.update();
}

// Function to update the summary section
function updateSummary(data) {
  const topSong = document.querySelector('[data-summary="common-track"]');
  const yourAvgTempo = document.querySelector('[data-summary="your-avg-tempo"]');
  const friendAvgTempo = document.querySelector('[data-summary="friend-avg-tempo"]');
  const yourTotal = document.querySelector('[data-summary="your-total-minutes"]');
  const friendTotal = document.querySelector('[data-summary="friend-total-minutes"]');
  const yourMood = document.querySelector('[data-summary="your-mood"]');
  const friendMood = document.querySelector('[data-summary="friend-mood"]');

  if (topSong) topSong.textContent = data.common_track;
  if (yourAvgTempo) yourAvgTempo.textContent = `${data.your_avg_tempo} BPM`;
  if (friendAvgTempo) friendAvgTempo.textContent = `${data.friend_avg_tempo} BPM`;
  if (yourTotal) yourTotal.textContent = data.your_total_minutes;
  if (friendTotal) friendTotal.textContent = data.friend_total_minutes;
  if (yourMood) yourMood.textContent = data.your_mood;
  if (friendMood) friendMood.textContent = data.friend_mood;
}


// Function to update popular songs list
function updatePopularSongs(data) {
  const yourList = document.querySelector('.your-top-songs');
  const friendList = document.querySelector('.friend-top-songs');

  if (!yourList || !friendList) return;

  yourList.innerHTML = '';
  friendList.innerHTML = '';

  data.you.forEach((song, index) => {
    const li = document.createElement('li');
    li.className = 'flex items-center py-1';
    li.innerHTML = `
      <span class="w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0">#${index + 1}</span>
      <span class="truncate">${song.title} - ${song.artist}</span>
    `;
    yourList.appendChild(li);
  });

  data.friend.forEach((song, index) => {
    const li = document.createElement('li');
    li.className = 'flex items-center py-1';
    li.innerHTML = `
      <span class="w-6 h-6 rounded-full bg-pink-100 text-pink-800 flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0">#${index + 1}</span>
      <span class="truncate">${song.title} - ${song.artist}</span>
    `;
    friendList.appendChild(li);
  });
}