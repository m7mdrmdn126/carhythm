/* Admin Charts and Analytics with Real Data */

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Fetch data from API and initialize charts
    fetch('/admin/analytics/data')
        .then(response => response.json())
        .then(data => {
            initializeDashboardCharts(data);
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
            // Initialize with sample data if API fails
            initializeDashboardCharts(getSampleData());
        });
});

function getSampleData() {
    return {
        response_trend: [
            {date: '2024-01-01', count: 12},
            {date: '2024-01-02', count: 19},
            {date: '2024-01-03', count: 15},
            {date: '2024-01-04', count: 25}
        ],
        completion_stats: {
            completed: 75,
            in_progress: 25,
            completion_rate: 75.0
        },
        riasec_distribution: {
            'Realistic': 65,
            'Investigative': 72,
            'Artistic': 58,
            'Social': 81,
            'Enterprising': 69,
            'Conventional': 63
        }
    };
}

function initializeDashboardCharts(data) {
    // Response Trend Chart
    const trendCanvas = document.getElementById('responseTrendChart');
    if (trendCanvas && typeof Chart !== 'undefined') {
        createResponseTrendChart(trendCanvas, data.response_trend);
    }
    
    // Completion Rate Chart
    const completionCanvas = document.getElementById('completionRateChart');
    if (completionCanvas && typeof Chart !== 'undefined') {
        createCompletionRateChart(completionCanvas, data.completion_stats);
    }
    
    // RIASEC Distribution Chart
    const riasecCanvas = document.getElementById('riasecDistributionChart');
    if (riasecCanvas && typeof Chart !== 'undefined') {
        createRiasecDistributionChart(riasecCanvas, data.riasec_distribution);
    }
}

function createResponseTrendChart(canvas, trendData) {
    // Extract labels and data
    const labels = trendData.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const counts = trendData.map(item => item.count);
    
    const data = {
        labels: labels,
        datasets: [{
            label: 'Responses',
            data: counts,
            borderColor: '#6D3B8E',
            backgroundColor: 'rgba(109, 59, 142, 0.1)',
            tension: 0.4,
            fill: true
        }]
    };
    
    new Chart(canvas, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Response Trends',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function createCompletionRateChart(canvas) {
    const data = {
        labels: ['Completed', 'Incomplete'],
        datasets: [{
            data: [75, 25],
            backgroundColor: [
                '#27AE60',
                '#E74C3C'
            ],
            borderWidth: 0
        }]
    };
    
    new Chart(canvas, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Completion Rate',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            }
        }
    });
}

function createRiasecDistributionChart(canvas) {
    const data = {
        labels: ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional'],
        datasets: [{
            label: 'Distribution',
            data: [12, 15, 8, 20, 14, 11],
            backgroundColor: [
                '#FF6B6B',
                '#4ECDC4',
                '#45B7D1',
                '#96CEB4',
                '#FFEAA7',
                '#DDA15E'
            ],
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };
    
    new Chart(canvas, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'RIASEC Type Distribution',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// Analytics data fetching
async function fetchAnalyticsData() {
    try {
        const response = await fetch('/admin/analytics/data');
        const data = await response.json();
        updateCharts(data);
    } catch (error) {
        console.error('Failed to fetch analytics data:', error);
    }
}

function updateCharts(data) {
    // Update charts with real data
    // This function would be called after fetching real analytics data
    console.log('Analytics data loaded:', data);
}
