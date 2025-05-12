/**
 * Shared Playlist Dropdown JS
 * Handles the functionality for the playlist selection dropdowns in the shared dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get references to the dropdown elements
    const yourPlaylistSelect = document.getElementById('yourPlaylistSelect');
    const friendPlaylistSelect = document.getElementById('friendPlaylistSelect');
    const chooseMessage = document.getElementById('choose-message');
    const comparisonContainer = document.getElementById('comparison-container');
    
    // Initialize chart objects
    let valenceChart, danceabilityChart, moodChart, modeChart;
    
    // Add event listeners to both dropdowns
    if (yourPlaylistSelect && friendPlaylistSelect) {
      yourPlaylistSelect.addEventListener('change', checkSelections);
      friendPlaylistSelect.addEventListener('change', checkSelections);
    }
    
    // Function to check if both dropdowns have selections
    function checkSelections() {
      if (yourPlaylistSelect.value && friendPlaylistSelect.value) {
        if (chooseMessage) {
          chooseMessage.style.display = 'none';
        }
        if (comparisonContainer) {
          comparisonContainer.style.display = 'block';
        }
        loadComparisonData();
      }
    }
    
    // Function to load comparison data
    function loadComparisonData() {
      // Show loading state on charts
      document.querySelectorAll('.chart-container').forEach(container => {
        container.classList.add('loading');
      });
      
      // Make AJAX request to get comparison data
      fetch(`/share/compare-playlists?your_id=${yourPlaylistSelect.value}&friend_id=${friendPlaylistSelect.value}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // Process the data with enhanced visualizations
          enhancedDataHandling(data);
          
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
    
    // Enhanced data handling function
    function enhancedDataHandling(data) {
      // Initialize or update basic charts and data
      initializeOrUpdateCharts(data);
      updateSummary(data.shared_summary);
      updatePopularSongs(data.top_popular_songs);
      
      // Update additional insights if available
      if (data.similar_tracks || data.comparative_stats || data.recommendations || data.mood_difference) {
        updateAdditionalInsights(data);
      }
    }
    
    // Initialize or update all charts
    function initializeOrUpdateCharts(data) {
      initializeOrUpdateValenceChart(data.valence_acousticness);
      initializeOrUpdateDanceabilityChart(data.comparison_bubble);
      initializeOrUpdateMoodChart(data.comparison_mood);
      initializeOrUpdateModeChart(data.comparison_mode);
    }
    
    // Valence vs Acousticness chart
    function initializeOrUpdateValenceChart(data) {
      const canvas = document.getElementById('valenceAcousticness');
      if (!canvas) return;
      
      if (valenceChart) {
        // Update existing chart
        valenceChart.data.datasets[0].data = data.you;
        valenceChart.data.datasets[1].data = data.friend;
        valenceChart.update();
      } else {
        // Initialize new chart
        const ctx = canvas.getContext('2d');
        valenceChart = new Chart(ctx, {
          type: 'scatter',
          data: {
            datasets: [
              {
                label: 'Your Songs',
                data: data.you,
                backgroundColor: 'rgba(99, 102, 241, 0.7)',
                pointRadius: 8,
                pointHoverRadius: 10
              },
              {
                label: 'Friend\'s Songs',
                data: data.friend,
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
            }
          }
        });
      }
    }
    
    // Danceability vs Energy bubble chart
    function initializeOrUpdateDanceabilityChart(data) {
      const canvas = document.getElementById('danceabilityEnergy');
      if (!canvas) return;

      const ctx = canvas.getContext('2d');

      // ✅ Always destroy the previous chart if it exists
      if (Chart.getChart(canvas)) { // Check if a chart instance exists
        Chart.getChart(canvas).destroy(); // Destroy the previous instance
      }

      // ✅ Create a fresh chart
      danceabilityChart = new Chart(ctx, {
        type: 'bubble',
        data: {
          datasets: [
            {
              label: 'Your Songs',
              data: data.you,
              backgroundColor: 'rgba(99, 102, 241, 0.7)',
              borderColor: '#6366F1'
            },
            {
              label: "Friend's Songs",
              data: data.friend,
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
                label: function (context) {
                  const point = context.raw;
                  return [
                    `${point.title || 'Song'} - ${point.artist || 'Artist'}`,
                    `Danceability: ${point.x.toFixed(2)}`,
                    `Energy: ${point.y.toFixed(2)}`,
                    `Minutes: ${(point.r / 5).toFixed(1)}`
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
    // function initializeOrUpdateDanceabilityChart(data) {
    //   const canvas = document.getElementById('danceabilityEnergy');
    //   if (!canvas) return;
      
    //   if (danceabilityChart) {
    //     // Update existing chart
    //     danceabilityChart.data.datasets[0].data = data.you;
    //     danceabilityChart.data.datasets[1].data = data.friend;
    //     danceabilityChart.update();
    //   } else {
    //     // Initialize new chart
    //     const ctx = canvas.getContext('2d');
    //     danceabilityChart = new Chart(ctx, {
    //       type: 'bubble',
    //       data: {
    //         datasets: [
    //           {
    //             label: 'Your Songs',
    //             data: data.you,
    //             backgroundColor: 'rgba(99, 102, 241, 0.7)',
    //             borderColor: '#6366F1'
    //           },
    //           {
    //             label: 'Friend\'s Songs',
    //             data: data.friend,
    //             backgroundColor: 'rgba(244, 114, 182, 0.7)',
    //             borderColor: '#F472B6'
    //           }
    //         ]
    //       },
    //       options: {
    //         responsive: true,
    //         maintainAspectRatio: false,
    //         plugins: {
    //           legend: { position: 'top' },
    //           tooltip: {
    //             callbacks: {
    //               label: function(context) {
    //                 const point = context.raw;
    //                 return [
    //                   `${point.title || 'Song'} - ${point.artist || 'Artist'}`, 
    //                   `Danceability: ${point.x.toFixed(2)}`, 
    //                   `Energy: ${point.y.toFixed(2)}`,
    //                   `Minutes: ${(point.r/5).toFixed(1)}`
    //                 ];
    //               }
    //             }
    //           }
    //         },
    //         scales: {
    //           x: {
    //             title: { 
    //               display: true, 
    //               text: 'Danceability',
    //               color: '#718096'
    //             },
    //             min: 0.4,
    //             max: 0.9,
    //             grid: {
    //               color: 'rgba(0, 0, 0, 0.05)'
    //             }
    //           },
    //           y: {
    //             title: { 
    //               display: true, 
    //               text: 'Energy',
    //               color: '#718096'
    //             },
    //             min: 0.4,
    //             max: 0.9,
    //             grid: {
    //               color: 'rgba(0, 0, 0, 0.05)'
    //             }
    //           }
    //         }
    //       }
    //     });
    //   }
    // }
    
    // Mood Profile radar chart
    function initializeOrUpdateMoodChart(data) {
      const canvas = document.getElementById('moodProfile');
      if (!canvas) return;

      // ✅ Destroy previous chart instance on this canvas, if it exists
      if (Chart.getChart(canvas)) {
        Chart.getChart(canvas).destroy();
      }

      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'radar',
        data: {
          labels: ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Liveness'],
          datasets: [
            {
              label: 'Your Profile',
              data: data.you,
              backgroundColor: 'rgba(99, 102, 241, 0.2)',
              borderColor: '#6366F1',
              pointBackgroundColor: '#6366F1'
            },
            {
              label: "Friend's Profile",
              data: data.friend,
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

    // function initializeOrUpdateMoodChart(data) {
    //   const canvas = document.getElementById('moodProfile');
    //   if (!canvas) return;
      
    //   if (moodChart) {
    //     // Update existing chart
    //     moodChart.data.datasets[0].data = data.you;
    //     moodChart.data.datasets[1].data = data.friend;
    //     moodChart.update();
    //   } else {
    //     // Initialize new chart
    //     const ctx = canvas.getContext('2d');
    //     moodChart = new Chart(ctx, {
    //       type: 'radar',
    //       data: {
    //         labels: ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Liveness'],
    //         datasets: [
    //           {
    //             label: 'Your Profile',
    //             data: data.you,
    //             backgroundColor: 'rgba(99, 102, 241, 0.2)',
    //             borderColor: '#6366F1',
    //             pointBackgroundColor: '#6366F1'
    //           },
    //           {
    //             label: 'Friend\'s Profile',
    //             data: data.friend,
    //             backgroundColor: 'rgba(244, 114, 182, 0.2)',
    //             borderColor: '#F472B6',
    //             pointBackgroundColor: '#F472B6'
    //           }
    //         ]
    //       },
    //       options: {
    //         responsive: true,
    //         maintainAspectRatio: false,
    //         scales: {
    //           r: {
    //             beginAtZero: true,
    //             max: 1,
    //             ticks: {
    //               display: false
    //             }
    //           }
    //         }
    //       }
    //     });
    //   }
    // }
    
    // Mode comparison bar chart
    function initializeOrUpdateModeChart(data) {
      const canvas = document.getElementById('modeChart');
      if (!canvas) return;

      // ✅ Destroy previous chart instance on this canvas, if it exists
      if (Chart.getChart(canvas)) {
        Chart.getChart(canvas).destroy();
      }

      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Major', 'Minor'],
          datasets: [
            {
              label: 'Your Songs',
              data: data.you,
              backgroundColor: '#6366F1'
            },
            {
              label: "Friend's Songs",
              data: data.friend,
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

    // function initializeOrUpdateModeChart(data) {
    //   const canvas = document.getElementById('modeChart');
    //   if (!canvas) return;
      
    //   if (modeChart) {
    //     // Update existing chart
    //     modeChart.data.datasets[0].data = data.you;
    //     modeChart.data.datasets[1].data = data.friend;
    //     modeChart.update();
    //   } else {
    //     // Initialize new chart
    //     const ctx = canvas.getContext('2d');
    //     modeChart = new Chart(ctx, {
    //       type: 'bar',
    //       data: {
    //         labels: ['Major', 'Minor'],
    //         datasets: [
    //           {
    //             label: 'Your Songs',
    //             data: data.you,
    //             backgroundColor: '#6366F1'
    //           },
    //           {
    //             label: 'Friend\'s Songs',
    //             data: data.friend,
    //             backgroundColor: '#F472B6'
    //           }
    //         ]
    //       },
    //       options: {
    //         responsive: true,
    //         maintainAspectRatio: false,
    //         plugins: {
    //           legend: { position: 'top' }
    //         },
    //         scales: {
    //           y: {
    //             beginAtZero: true,
    //             title: { 
    //               display: true, 
    //               text: 'Number of Songs',
    //               color: '#718096'
    //             },
    //             grid: {
    //               color: 'rgba(0, 0, 0, 0.05)'
    //             }
    //           },
    //           x: {
    //             grid: {
    //               display: false
    //             }
    //           }
    //         }
    //       }
    //     });
    //   }
    // }
    
    // Update summary section
    function updateSummary(data) {
      if (!data) return;
  
      // Update summary values using data attributes or IDs
      const summaryElements = {
        'common-track': data.common_track,
        'your-avg-tempo': `${data.your_avg_tempo} BPM`,
        'friend-avg-tempo': `${data.friend_avg_tempo} BPM`,
        'your-total-minutes': data.your_total_minutes,
        'friend-total-minutes': data.friend_total_minutes,
        'your-mood': data.your_mood,
        'friend-mood': data.friend_mood,
        'top-song': data.top_song || '',
        'total-minutes': data.your_total_minutes || '',
        'avg-tempo': `${data.your_avg_tempo} BPM` || '',
        'mood': data.your_mood || ''
      };
  
      // Update using both data-summary attributes and IDs for compatibility
      Object.keys(summaryElements).forEach(key => {
        // Try to find by data attribute
        const dataAttrElement = document.querySelector(`[data-summary="${key}"]`);
        if (dataAttrElement) {
          dataAttrElement.textContent = summaryElements[key];
        }
        
        // Also try to find by ID
        const idElement = document.getElementById(key);
        if (idElement) {
          idElement.textContent = summaryElements[key];
        }
      });
    }
    
    // Update popular songs lists
    function updatePopularSongs(data) {
      if (!data) return;
      
      // Update using existing classes or IDs
      updateSongsList('your-popular-songs', data.you, '#6366F1');
      updateSongsList('friend-popular-songs', data.friend, '#F472B6');
      
      // Also try to update the directly embedded songs list if it exists
      const popularSongsList = document.querySelector('.popular-songs-list');
      if (popularSongsList && data.you && data.you.length > 0) {
        popularSongsList.innerHTML = '';
        
        // Add first two songs from your playlist
        for (let i = 0; i < Math.min(2, data.you.length); i++) {
          const song = data.you[i];
          const songItem = document.createElement('div');
          songItem.className = 'song-item';
          songItem.innerHTML = `
            <span class="song-rank">#${i+1}</span>
            <span class="song-title">${song.title}</span>
            <span class="song-artist">${song.artist}</span>
          `;
          popularSongsList.appendChild(songItem);
        }
      }
    }
    
    // Helper to update a songs list
    function updateSongsList(containerId, songs, color) {
      const container = document.getElementById(containerId);
      if (!container || !songs) return;
      
      container.innerHTML = '';
      
      songs.forEach((song, index) => {
        const songItem = document.createElement('div');
        songItem.className = 'song-item';
        songItem.innerHTML = `
          <div class="song-rank" style="background-color: ${color};">#${index + 1}</div>
          <div class="song-details">
            <div class="song-title">${song.title}</div>
            <div class="song-artist">${song.artist}</div>
          </div>
        `;
        container.appendChild(songItem);
      });
    }
    
    // Update additional insights
    function updateAdditionalInsights(data) {
      // Create or update similar tracks section
      if (data.similar_tracks && data.similar_tracks.length > 0) {
        renderSimilarTracks(data.similar_tracks);
      }
      
      // Update comparative stats section
      if (data.comparative_stats) {
        renderComparativeStats(data.comparative_stats);
      }
      
      // Update recommendations section
      if (data.recommendations && data.recommendations.length > 0) {
        renderRecommendations(data.recommendations);
      }
      
      // Update the valence vs acousticness chart with annotations
      if (data.chart_annotations && valenceChart) {
        updateChartAnnotations(valenceChart, data.chart_annotations);
      }
      
      // Update mood difference text
      if (data.mood_difference) {
        const moodDiffElement = document.getElementById('mood-difference');
        if (moodDiffElement) {
          moodDiffElement.textContent = data.mood_difference;
        } else {
          // Create the element if it doesn't exist
          const moodProfileCard = document.querySelector('.chart-card:nth-child(2)');
          if (moodProfileCard) {
            const moodDiffPara = document.createElement('p');
            moodDiffPara.id = 'mood-difference';
            moodDiffPara.className = 'text-sm text-gray-600 mt-2';
            moodDiffPara.textContent = data.mood_difference;
            moodProfileCard.appendChild(moodDiffPara);
          }
        }
      }
    }
    
    // Render similar tracks section
    function renderSimilarTracks(similarTracks) {
      const container = document.getElementById('similar-tracks-container');
      
      if (!container) {
        // Create the container if it doesn't exist
        const similarTracksCard = document.createElement('div');
        similarTracksCard.className = 'chart-card mt-6';
        similarTracksCard.innerHTML = `
          <h2 class="chart-title">Similar Tracks You Both Might Enjoy</h2>
          <p class="chart-subtitle">Tracks with similar mood and feel from both playlists</p>
          <div id="similar-tracks-container" class="mt-3"></div>
        `;
        
        // Find a good place to add this
        const comparisonContainer = document.getElementById('comparison-container') || 
                                   document.querySelector('.dashboard-container');
        if (comparisonContainer) {
          comparisonContainer.appendChild(similarTracksCard);
        }
        
        // Call again after creating the container
        renderSimilarTracks(similarTracks);
        return;
      }
      
      // Clear current content
      container.innerHTML = '';
      
      // Add each similar track pair
      similarTracks.forEach((pair, index) => {
        const pairElement = document.createElement('div');
        pairElement.className = 'flex items-center justify-between p-2 border-b border-gray-100';
        
        pairElement.innerHTML = `
          <div class="flex items-center">
            <span class="w-6 h-6 rounded-full bg-indigo-100 text-indigo-800 flex items-center justify-center text-xs mr-2">${index + 1}</span>
            <div>
              <div class="font-medium">${pair.your_track.title}</div>
              <div class="text-xs text-gray-500">${pair.your_track.artist}</div>
            </div>
          </div>
          <div class="mx-2 text-gray-400">matches</div>
          <div class="flex items-center">
            <div class="text-right">
              <div class="font-medium">${pair.friend_track.title}</div>
              <div class="text-xs text-gray-500">${pair.friend_track.artist}</div>
            </div>
            <span class="w-6 h-6 rounded-full bg-pink-100 text-pink-800 flex items-center justify-center text-xs ml-2">${index + 1}</span>
          </div>
        `;
        
        container.appendChild(pairElement);
      });
    }
    
    // Render comparative stats
    function renderComparativeStats(stats) {
      const comparisonContainer = document.getElementById('comparison-container') || 
                                 document.querySelector('.dashboard-container');
      if (!comparisonContainer) return;
      
      const statsContainer = document.getElementById('comparative-stats-container');
      
      if (!statsContainer) {
        // Create the container if it doesn't exist
        const statsCard = document.createElement('div');
        statsCard.className = 'chart-card mt-6';
        statsCard.innerHTML = `
          <h2 class="chart-title">Music Taste Comparison</h2>
          <p class="chart-subtitle">How your music taste compares with your friend's</p>
          <div id="comparative-stats-container" class="mt-3 space-y-4"></div>
        `;
        
        comparisonContainer.appendChild(statsCard);
        
        // Call again after creating the container
        renderComparativeStats(stats);
        return;
      }
      
      // Clear current content
      statsContainer.innerHTML = '';
      
      // Add comparative stat items
      
      // Tempo comparison
      if (stats.tempo) {
        const tempoEl = document.createElement('div');
        tempoEl.className = 'stat-item';
        tempoEl.innerHTML = `
          <div class="font-medium mb-1">Tempo</div>
          <div class="text-sm">${stats.tempo.description}</div>
          <div class="flex items-center mt-2">
            <div class="w-1/2 pr-2">
              <div class="text-xs text-gray-500">You</div>
              <div class="h-4 bg-indigo-100 rounded-full overflow-hidden">
                <div class="h-full bg-indigo-500" style="width: ${(stats.tempo.your_tempo / 180) * 100}%"></div>
              </div>
              <div class="text-xs text-right mt-1">${stats.tempo.your_tempo} BPM</div>
            </div>
            <div class="w-1/2 pl-2">
              <div class="text-xs text-gray-500">Friend</div>
              <div class="h-4 bg-pink-100 rounded-full overflow-hidden">
                <div class="h-full bg-pink-500" style="width: ${(stats.tempo.friend_tempo / 180) * 100}%"></div>
              </div>
              <div class="text-xs text-right mt-1">${stats.tempo.friend_tempo} BPM</div>
            </div>
          </div>
        `;
        statsContainer.appendChild(tempoEl);
      }
      
      // Mood similarity
      if (stats.mood_similarity) {
        const moodEl = document.createElement('div');
        moodEl.className = 'stat-item';
        moodEl.innerHTML = `
          <div class="font-medium mb-1">Overall Similarity</div>
          <div class="text-sm">${stats.mood_similarity.description}</div>
          <div class="mt-2">
            <div class="flex justify-between text-xs text-gray-500 mb-1">
              <span>Very Different</span>
              <span>Very Similar</span>
            </div>
            <div class="h-4 bg-gray-100 rounded-full overflow-hidden">
              <div class="h-full bg-green-500" style="width: ${(1 - stats.mood_similarity.average_difference) * 100}%"></div>
            </div>
          </div>
        `;
        statsContainer.appendChild(moodEl);
      }
    }
    
    // Render recommendations
    function renderRecommendations(recommendations) {
      const comparisonContainer = document.getElementById('comparison-container') || 
                                 document.querySelector('.dashboard-container');
      if (!comparisonContainer) return;
      
      const recsContainer = document.getElementById('recommendations-container');
      
      if (!recsContainer) {
        // Create the container if it doesn't exist
        const recsCard = document.createElement('div');
        recsCard.className = 'chart-card mt-6';
        recsCard.innerHTML = `
          <h2 class="chart-title">Music Recommendations</h2>
          <p class="chart-subtitle">Suggestions based on your music comparison</p>
          <div id="recommendations-container" class="mt-3 space-y-4"></div>
        `;
        
        comparisonContainer.appendChild(recsCard);
        
        // Call again after creating the container
        renderRecommendations(recommendations);
        return;
      }
      
      // Clear current content
      recsContainer.innerHTML = '';
      
      // Add recommendations
      recommendations.forEach(rec => {
        const recEl = document.createElement('div');
        recEl.className = 'recommendation-item p-3 border border-gray-100 rounded-lg';
        
        if (rec.type === 'track_recommendation' && rec.tracks) {
          let tracksHTML = '';
          rec.tracks.forEach((track, i) => {
            tracksHTML += `
              <div class="flex items-center mt-2 p-2 bg-gray-50 rounded-md">
                <span class="text-xs font-bold w-5 h-5 flex items-center justify-center bg-indigo-100 text-indigo-800 rounded-full mr-2">${i+1}</span>
                <div>
                  <div class="font-medium">${track.title}</div>
                  <div class="text-xs text-gray-500">${track.artist}</div>
                </div>
              </div>
            `;
          });
          
          recEl.innerHTML = `
            <div class="font-medium text-indigo-600">${rec.title}</div>
            <div class="text-sm text-gray-600 mb-2">${rec.description}</div>
            ${tracksHTML}
          `;
        } else {
          recEl.innerHTML = `
            <div class="font-medium text-indigo-600">${rec.title}</div>
            <div class="text-sm text-gray-600">${rec.description}</div>
          `;
        }
        
        recsContainer.appendChild(recEl);
      });
    }
    
    // Update chart annotations
    function updateChartAnnotations(chart, annotations) {
      if (!chart || !chart.options || !annotations) return;
      
      // Check if Chart.js annotation plugin is available
      if (!chart.options.plugins) {
        chart.options.plugins = {};
      }
      
      try {
        // Set annotations
        chart.options.plugins.annotation = annotations.annotations;
        
        // Update chart
        chart.update();
      } catch (e) {
        console.warn('Failed to add annotations to chart:', e);
      }
    }
    
    // Initialize initial chart view if data is available
    // This handles existing template that passes data in global variables
    if (window.initialBubbleData) {
      // If the template provides initial data, initialize charts
      initializeOrUpdateCharts({
        valence_acousticness: { 
          you: [], 
          friend: [] 
        },
        comparison_bubble: window.initialBubbleData,
        comparison_mood: window.initialMoodData || { you: [0.5, 0.5, 0.5, 0.5, 0.5], friend: [0.5, 0.5, 0.5, 0.5, 0.5] },
        comparison_mode: window.initialModeData || { you: [0, 0], friend: [0, 0] },
      });
    }
  });