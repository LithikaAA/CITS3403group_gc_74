document.addEventListener('DOMContentLoaded', () => {
    // Generate pastel colors based on a seed (username)
    function generatePastelColors(count, seed) {
      // simple hash to number
      let hash = 0;
      for (let i = 0; i < seed.length; i++) {
        hash = seed.charCodeAt(i) + ((hash << 5) - hash);
      }
      const baseHue = Math.abs(hash) % 360;
      const colors = [];
      for (let i = 0; i < count; i++) {
        const hue = (baseHue + (i * (360 / count))) % 360;
        colors.push(`hsl(${hue},60%,80%)`);
      }
      return colors;
    }
  
    // Create Chart Helper
    function createChart(ctx, type, data, options = {}) {
      return new Chart(ctx, { type, data, options });
    }
  
    // Mood Radar Chart
    const moodCtx = document.getElementById('sharedMoodRadar').getContext('2d');
    const moodColors = generatePastelColors(moodData.labels.length, themeSeed);
    createChart(moodCtx, 'radar', {
      labels: moodData.labels,
      datasets: [{
        label: 'Mood Intensity',
        data: moodData.values,
        backgroundColor: moodColors.map(c => c.replace('80%','50%')),
        borderColor: moodColors,
        fill: true,
        borderWidth: 2
      }]
    }, { responsive: true, maintainAspectRatio: false });
  
    // Tempo Bar Chart
    const tempoCtx = document.getElementById('sharedTempoBar').getContext('2d');
    const tempoColors = generatePastelColors(tempoData.labels.length, themeSeed + 'tempo');
    createChart(tempoCtx, 'bar', {
      labels: tempoData.labels,
      datasets: [{
        label: 'Tempo (BPM)',
        data: tempoData.values,
        backgroundColor: tempoColors,
        borderColor: tempoColors,
        borderWidth: 1
      }]
    }, { responsive: true, maintainAspectRatio: false });
  
    // Genre Pie Chart
    const genreCtx = document.getElementById('sharedGenrePie').getContext('2d');
    const genreColors = generatePastelColors(genreData.labels.length, themeSeed + 'genre');
    createChart(genreCtx, 'pie', {
      labels: genreData.labels,
      datasets: [{
        label: 'Genre Distribution',
        data: genreData.values,
        backgroundColor: genreColors,
        borderColor: '#fff',
        borderWidth: 1
      }]
    }, { responsive: true, maintainAspectRatio: false });
  });
  