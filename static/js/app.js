


console.log("Charts loaded");

// Read data the template injected
const { months, monthVals, dailyLabels, dailyVals, roleLabels, roleVals } = window.chartData;
const dailyLabs = dailyLabels.map(label => label.slice(5)); // Trim 'YYYY-' from 'YYYY-MM-DD'
  // === BAR CHART: Monthly ===
  new Chart(document.getElementById('monthChart'), {
    type: 'bar',
    data: {
      labels: months,
      datasets: [{
        label: 'Submissions',
        data: monthVals,
        backgroundColor: '#0d6efd99',
        borderColor: '#0d6efd',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true } }
    }
  });

  // === LINE CHART: Last 7 Days ===
  new Chart(document.getElementById('dailyChart'), {
    type: 'line',
    data: {
      labels: dailyLabs,
      datasets: [{
        label: 'Daily',
        data: dailyVals,
        fill: true,
        borderColor: '#6610f2',
        backgroundColor: '#6610f233',
        borderWidth: 2,
        tension: .3,
      }]
    },
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true } }
    }
  });

  // === DOUGHNUT CHART: Roles ===
  new Chart(document.getElementById('roleChart'), {
    type: 'doughnut',
    data: {
      labels: roleLabels,
      datasets: [{
        data: roleVals,
        backgroundColor: [
          '#0d6efd', '#6610f2', '#198754',
          '#dc3545', '#ffc107', '#20c997'
        ]
      }]
    },
    options: { responsive: true }
  });



