/**
 * VibeShare Dashboard Charts
 * This script handles initialization and updating of charts
 */

// Access data from window variables defined in the HTML
let valenceAcousticnessData = window.valenceAcousticnessData || [];
let danceabilityEnergyData = window.danceabilityEnergyData || [];
let moodProfileData = window.moodProfileData || [];
let modeCountData = window.modeCountData || [];

// Initialize chart objects
let valenceAcousticnessChart;
let danceabilityEnergyChart;
let moodProfileChart;
let modeChart;

// Set up initial charts
function initializeCharts() {
    console.log("Initializing charts with data:", {
        valenceAcousticness: valenceAcousticnessData,
        danceabilityEnergy: danceabilityEnergyData,
        moodProfile: moodProfileData,
        modeCount: modeCountData
    });

    if (!document.getElementById('valenceAcousticness')) {
        console.error("Canvas element 'valenceAcousticness' not found");
        return;
    }

    // Valence vs Acousticness (Scatter Chart)
    const valenceAcousticnessCtx = document.getElementById('valenceAcousticness').getContext('2d');
    // Custom plugin for quadrant lines and labels
    const quadrantPlugin = {
        id: 'quadrantLinesAndLabels',
        afterDraw: function(chart) {
            const ctx = chart.ctx;
            const xAxis = chart.scales.x;
            const yAxis = chart.scales.y;
            ctx.save();
            ctx.strokeStyle = 'rgba(99, 102, 241, 0.25)';
            ctx.lineWidth = 1;
            ctx.setLineDash([5, 5]);
            // Vertical line at x=0.5
            const xMid = xAxis.getPixelForValue(0.5);
            ctx.beginPath();
            ctx.moveTo(xMid, yAxis.top);
            ctx.lineTo(xMid, yAxis.bottom);
            ctx.stroke();
            // Horizontal line at y=0.5
            const yMid = yAxis.getPixelForValue(0.5);
            ctx.beginPath();
            ctx.moveTo(xAxis.left, yMid);
            ctx.lineTo(xAxis.right, yMid);
            ctx.stroke();
            ctx.setLineDash([]);
            // Quadrant labels
            ctx.font = 'bold 12px Inter, system-ui, sans-serif';
            ctx.fillStyle = 'rgba(79, 70, 229, 0.7)';
            ctx.textAlign = 'center';
            ctx.fillText('Happy & electronic', xAxis.getPixelForValue(0.25), yAxis.getPixelForValue(0.75));
            ctx.fillText('Uplifting & acoustic', xAxis.getPixelForValue(0.75), yAxis.getPixelForValue(0.75));
            ctx.fillText('Sad & electronic', xAxis.getPixelForValue(0.25), yAxis.getPixelForValue(0.25));
            ctx.fillText('Mellow & acoustic', xAxis.getPixelForValue(0.75), yAxis.getPixelForValue(0.25));
            ctx.restore();
        }
    };
    valenceAcousticnessChart = new Chart(valenceAcousticnessCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Tracks',
                data: valenceAcousticnessData,
                backgroundColor: function(context) {
                    const value = context.raw;
                    if (!value) return 'rgba(139, 92, 246, 0.8)';
                    // Create a gradient based on valence (y-value)
                    if (value.y > 0.7) return 'rgba(99, 102, 241, 0.8)'; // More happy - indigo
                    if (value.y > 0.4) return 'rgba(139, 92, 246, 0.8)'; // Moderate - purple
                    return 'rgba(236, 72, 153, 0.8)'; // Less happy - pink
                },
                pointRadius: 6,
                pointHoverRadius: 8,
                borderWidth: 1,
                borderColor: 'rgba(255, 255, 255, 0.5)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 12 },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const dataPoint = context.raw;
                            if (!dataPoint) return ['No data'];
                            return [
                                `Title: ${dataPoint.title || 'Unknown'}`,
                                `Artist: ${dataPoint.artist || 'Unknown'}`,
                                `Valence: ${dataPoint.y.toFixed(2)}`,
                                `Acousticness: ${dataPoint.x.toFixed(2)}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { text: 'Acousticness', display: true, font: { size: 14, weight: 'bold' }, color: '#4B5563' },
                    min: 0,
                    max: 1,
                    ticks: { stepSize: 0.1, color: '#6B7280' },
                    grid: { color: 'rgba(243, 244, 246, 0.8)' }
                },
                y: {
                    title: { text: 'Valence', display: true, font: { size: 14, weight: 'bold' }, color: '#4B5563' },
                    min: 0,
                    max: 1,
                    ticks: { stepSize: 0.1, color: '#6B7280' },
                    grid: { color: 'rgba(243, 244, 246, 0.8)' }
                }
            }
        },
        plugins: [quadrantPlugin]
    });
    
    // Danceability vs Energy (Bubble Chart)
    const danceabilityEnergyCtx = document.getElementById('danceabilityEnergy').getContext('2d');
    danceabilityEnergyChart = new Chart(danceabilityEnergyCtx, {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Tracks',
                data: danceabilityEnergyData,
                backgroundColor: function(context) {
                    const value = context.raw;
                    if (!value) return 'rgba(139, 92, 246, 0.7)';
                    const energyDance = value.x + value.y; // Combined energy and danceability
                    
                    if (energyDance > 1.5) return 'rgba(99, 102, 241, 0.8)'; // High energy & dance
                    if (energyDance > 1.2) return 'rgba(139, 92, 246, 0.7)'; // Medium
                    return 'rgba(236, 72, 153, 0.6)'; // Lower energy & dance
                },
                borderColor: 'rgba(255, 255, 255, 0.5)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 12 },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const dataPoint = context.raw;
                            if (!dataPoint) return ['No data'];
                            return [
                                `Title: ${dataPoint.title || 'Unknown'}`,
                                `Artist: ${dataPoint.artist || 'Unknown'}`,
                                `Danceability: ${dataPoint.x.toFixed(2)}`,
                                `Energy: ${dataPoint.y.toFixed(2)}`,
                                `Minutes: ${dataPoint.r / 5 || 'Unknown'}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { text: 'Danceability', display: true, font: { size: 14, weight: 'bold' }, color: '#4B5563' },
                    min: 0.4,
                    max: 0.85,
                    ticks: { stepSize: 0.05, color: '#6B7280' },
                    grid: { color: 'rgba(243, 244, 246, 0.8)' }
                },
                y: {
                    title: { text: 'Energy', display: true, font: { size: 14, weight: 'bold' }, color: '#4B5563' },
                    min: 0.5,
                    max: 0.9,
                    ticks: { stepSize: 0.05, color: '#6B7280' },
                    grid: { color: 'rgba(243, 244, 246, 0.8)' }
                }
            }
        }
    });

    // Mood Profile (Radar Chart)
    const moodProfileCtx = document.getElementById('moodProfile').getContext('2d');
    moodProfileChart = new Chart(moodProfileCtx, {
        type: 'radar',
        data: {
            labels: ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Liveness'],
            datasets: [{
                label: 'Your Mood Profile',
                data: moodProfileData,
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                borderColor: '#8B5CF6',
                pointBackgroundColor: '#6366F1',
                pointBorderColor: '#FFFFFF',
                pointHoverBackgroundColor: '#EC4899',
                pointHoverBorderColor: '#FFFFFF',
                pointRadius: 4,
                pointHoverRadius: 6,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { 
                    position: 'top', 
                    align: 'center',
                    labels: { 
                        boxWidth: 12, 
                        padding: 15, 
                        font: { size: 13, weight: 'bold' },
                        color: '#4B5563'
                    } 
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 12 },
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: { display: false, stepSize: 0.2 },
                    pointLabels: { font: { size: 11, weight: 'bold' }, color: '#4B5563' },
                    grid: { color: 'rgba(243, 244, 246, 0.8)' },
                    angleLines: { color: 'rgba(243, 244, 246, 0.8)' }
                }
            }
        }
    });

    // Mode Analysis (Bar Chart)
    const modeCtx = document.getElementById('modeChart').getContext('2d');
    modeChart = new Chart(modeCtx, {
        type: 'bar',
        data: {
            labels: ['Major', 'Minor'],
            datasets: [{
                label: 'Song Count',
                data: modeCountData,
                backgroundColor: ['#6366F1', '#EC4899'],
                borderRadius: 10,
                borderWidth: 1,
                borderColor: ['rgba(99, 102, 241, 0.2)', 'rgba(236, 72, 153, 0.2)'],
                maxBarThickness: 100
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 12 },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y + ' songs';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { display: true, color: 'rgba(243, 244, 246, 0.8)' },
                    title: { text: 'Number of Songs', display: true, font: { size: 13, weight: 'bold' }, color: '#4B5563' },
                    ticks: { 
                        color: '#6B7280',
                        precision: 0,  // Force whole numbers
                        stepSize: 1    // Ensure steps are whole numbers
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#6B7280', font: { weight: 'bold' } }
                }
            }
        }
    });
}

// Function to update charts with new data
function updateCharts(data) {
    console.log("Updating charts with new data:", data);
    
    // Ensure the data object has all required properties to avoid errors
    if (!data || !data.valence_acousticness || !data.danceability_energy || 
        !data.mood_profile || !data.mode_count || !data.top_summary || !data.top_popular_songs) {
        console.error("Missing required data properties:", data);
        return;
    }

    try {
        // Update Valence vs Acousticness chart
        valenceAcousticnessChart.data.datasets[0].data = data.valence_acousticness.data;
        valenceAcousticnessChart.update();
        
        // Update Danceability vs Energy chart
        danceabilityEnergyChart.data.datasets[0].data = data.danceability_energy.data;
        danceabilityEnergyChart.update();
        
        // Update Mood Profile chart
        moodProfileChart.data.datasets[0].data = data.mood_profile.data;
        moodProfileChart.update();
        
        // Update Mode chart
        modeChart.data.datasets[0].data = data.mode_count.data;
        modeChart.update();
        
        // Update Summary Card
        document.getElementById('top-duration-songs').textContent = data.top_summary.most_played;
        document.getElementById('total-minutes').textContent = data.top_summary.total_minutes;
        document.getElementById('avg-tempo').textContent = data.top_summary.avg_tempo + " BPM";
        
        // Update Top Mood
        const topMood = document.getElementById('top-mood');
        if (data.mode_count.data[0] > data.mode_count.data[1]) {
            topMood.textContent = "Happy";
        } else if (data.mode_count.data[0] < data.mode_count.data[1]) {
            topMood.textContent = "Emotional";
        } else {
            topMood.textContent = "Balanced";
        }
        
        // Update Top Popular Songs
        const topSongsContainer = document.getElementById('top-songs-container');
        if (topSongsContainer) {
            topSongsContainer.innerHTML = '';
            
            data.top_popular_songs.forEach((song, index) => {
                if (index < 5) {
                    const songElement = document.createElement('div');
                    songElement.className = `flex items-center space-x-4 p-2 rounded-lg ${index === 0 ? 'bg-gradient-to-r from-indigo-50 to-purple-50' : ''}`;
                    
                    songElement.innerHTML = `
                        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center shadow-md">
                            <span class="text-white text-sm font-bold">#${index + 1}</span>
                        </div>
                        <div>
                            <p class="text-base font-semibold ${index === 0 ? 'text-indigo-700' : 'text-gray-800'}">${song.title}</p>
                            <p class="text-sm text-gray-500">${song.artist}</p>
                        </div>
                    `;
                    
                    topSongsContainer.appendChild(songElement);
                }
            });
        }
        
        console.log("Charts updated successfully");
    } catch (error) {
        console.error("Error updating charts:", error);
    }
}

// Make updateCharts function globally available
window.updateCharts = updateCharts;

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, initializing charts");
    initializeCharts();
});