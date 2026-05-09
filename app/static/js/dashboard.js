
document.addEventListener('DOMContentLoaded', function() {
    // Theme colors for charts
    const themeColors = {
        dashboardBg: '#1a1e21', // Matches --dashboard-bg
        cardBg: '#2c3034',       // Matches --card-bg
        textPrimaryDark: '#e9ecef',
        textSecondaryDark: '#adb5bd',
        accentRed: getComputedStyle(document.documentElement).getPropertyValue('--primary-red').trim() || '#dc3545',
        accentLightRed: '#ff6b6b',
        positiveGreen: '#1cc88a',
        gridColor: '#495057', // Matches --card-border
        // Define a color array for pie/donut charts
        pieChartColors: ['#dc3545', '#ff6b6b', '#f6c23e', '#1cc88a', '#36b9cc', '#6f42c1', '#fd7e14'] // Red, LightRed, Yellow, Green, InfoBlue, Purple, Orange
    };


    // Function to show error message in a chart container
    function showChartErrorMessage(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `<div class="chart-error-message"><i class="fas fa-exclamation-triangle me-2"></i>${message}</div>`;
        }
    }

    // Function to show loading spinner
    function showLoadingSpinner(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            // Ensure spinner is not duplicated if already there
            if (!container.querySelector('.loading-spinner')) {
                 container.innerHTML = `
                    <div class="loading-spinner" style="display: flex; justify-content: center; align-items: center; height: 100%; color: ${themeColors.accentRed}; min-height: 200px;">
                        <i class="fas fa-spinner fa-spin fa-3x"></i>
                    </div>`;
            } else {
                 const spinner = container.querySelector('.loading-spinner');
                 spinner.style.display = 'flex'; // Ensure it's visible
            }
        }
    }
    function hideLoadingSpinner(containerId) {
        const container = document.getElementById(containerId);
        if (container && container.querySelector('.loading-spinner')) {
            container.querySelector('.loading-spinner').style.display = 'none';
        }
    }


    // Fonction pour charger les données et mettre à jour les graphiques
    function loadDashboardData() {
        document.querySelectorAll('.chart-container > div[id$="-chart"], #top-suppliers-container').forEach(el => {
            // Show spinner only if it's not the top-suppliers-container (it has its own direct spinner)
            // or if the element is empty (meaning it needs a spinner)
            if (el.id !== 'top-suppliers-container' || el.innerHTML.trim() === '' || el.querySelector('.loading-spinner')) {
                 showLoadingSpinner(el.id);
            }
        });


        // Charger les données de résumé
        fetch('/api/dashboard/summary')
            .then(response => response.json())
            .then(data => {
                document.getElementById('active-suppliers').textContent = data.active_suppliers !== undefined ? data.active_suppliers : 'N/A';
                document.getElementById('active-interns').textContent = data.active_interns !== undefined ? data.active_interns : 'N/A';
                document.getElementById('current-suppliers').textContent = data.current_suppliers !== undefined ? data.current_suppliers : 'N/A';
                document.getElementById('current-interns').textContent = data.current_interns !== undefined ? data.current_interns : 'N/A';
                document.getElementById('current-visitors').textContent = data.current_visitors !== undefined ? data.current_visitors : 'N/A';
                
                const todayTotal = (data.total_suppliers_today || 0) + (data.total_interns_today || 0) + (data.total_visitors_today || 0);
                document.getElementById('total-today').textContent = todayTotal;
                
                // Simulated change updates (replace with actual data if available)
                // updateChanges(data); 
            })
            .catch(error => {
                console.error('Erreur lors du chargement des données de résumé:', error);
                // Optionally update UI elements to show error
                ['active-suppliers', 'active-interns', 'current-suppliers', 'current-interns', 'current-visitors', 'total-today'].forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = 'Erreur';
                });
            });

        // Charger les données des top fournisseurs (maintenant top entreprises)
    fetch('/api/dashboard/top-suppliers')
        .then(response => response.json())
        .then(data => {
        const container = document.getElementById('top-suppliers-container');
        hideLoadingSpinner('top-suppliers-container');
        container.innerHTML = ''; // Nettoyer

        if (!data || data.length === 0) {
            container.innerHTML = '<p class="text-center text-muted p-3">Aucune donnée disponible pour les top fournisseurs.</p>';
            return;
        }
        
        const list = document.createElement('ul');
        list.className = 'top-suppliers-list';
        
        // The data is already limited to 10 by the backend
        data.forEach((item, index) => { // Changed 'suppliers.forEach' to 'data.forEach' and 'supplier' to 'item'
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="badge-rank">${index + 1}</span>
                <div style="flex-grow: 1;">
                    <span class="supplier-name">${item.company || 'N/A'}</span>
                </div>
                <div class="supplier-hours">${item.hours !== undefined ? item.hours.toFixed(2) : 'N/A'} h</div>
            `;
            list.appendChild(li);
        });
        container.appendChild(list);
    })
    .catch(error => {
        console.error('Erreur lors du chargement des top fournisseurs (par entreprise):', error);
        showChartErrorMessage('top-suppliers-container', 'Erreur de chargement (Top Fournisseurs)');
    });

        // Charger les données des tendances de présence
        fetch('/api/dashboard/attendance-trend')
            .then(response => response.json())
            .then(data => {
                const chartId = 'attendance-trend-chart';
                hideLoadingSpinner(chartId);
                const container = document.getElementById(chartId);
                container.innerHTML = ''; // Nettoyer
                
                if (!data || data.length === 0) {
                     showChartErrorMessage(chartId, 'Aucune donnée de tendance disponible.');
                     return;
                }

                const dates = data.map(item => item.date);
                const suppliersData = data.map(item => item.suppliers);
                const internsData = data.map(item => item.interns);
                const visitorsData = data.map(item => item.visitors);

                const traces = [
                    {
                        x: dates, y: suppliersData, type: 'scatter', mode: 'lines+markers', name: 'Fournisseurs',
                        line: { color: themeColors.accentRed, width: 2, shape: 'spline' },
                        marker: { size: 6, color: themeColors.accentRed, line: { color: themeColors.cardBg, width: 1 }}
                    },
                    {
                        x: dates, y: internsData, type: 'scatter', mode: 'lines+markers', name: 'Stagiaires',
                        line: { color: themeColors.positiveGreen, width: 2, shape: 'spline' },
                        marker: { size: 6, color: themeColors.positiveGreen, line: { color: themeColors.cardBg, width: 1 }}
                    },
                    {
                        x: dates, y: visitorsData, type: 'scatter', mode: 'lines+markers', name: 'Visiteurs',
                        line: { color: themeColors.accentLightRed, width: 2, shape: 'spline' }, // Changed from black
                        marker: { size: 6, color: themeColors.accentLightRed, line: { color: themeColors.cardBg, width: 1 }}
                    }
                ];
                
                const layout = {
                    margin: { t: 30, l: 50, r: 30, b: 70 },
                    paper_bgcolor: themeColors.cardBg,
                    plot_bgcolor: themeColors.cardBg,
                    font: { color: themeColors.textPrimaryDark },
                    xaxis: {
                        tickangle: -45,
                        gridcolor: themeColors.gridColor,
                        linecolor: themeColors.gridColor,
                        zerolinecolor: themeColors.gridColor,
                        automargin: true,
                    },
                    yaxis: {
                        title: 'Nombre de présences',
                        gridcolor: themeColors.gridColor,
                        linecolor: themeColors.gridColor,
                        zerolinecolor: themeColors.gridColor,
                        automargin: true,
                    },
                    legend: {
                        orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'right', x: 1,
                        bgcolor: 'rgba(0,0,0,0.1)', bordercolor: themeColors.gridColor, borderwidth: 1
                    },
                    hovermode: 'closest'
                };
                Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: false });
            })
            .catch(error => {
                console.error('Erreur lors du chargement des tendances de présence:', error);
                showChartErrorMessage('attendance-trend-chart', 'Erreur de chargement (Tendances)');
            });

        // Charger les données des fournisseurs par type
        fetch('/api/dashboard/suppliers-by-type')
            .then(response => response.json())
            .then(data => {
                const chartId = 'suppliers-by-type-chart';
                hideLoadingSpinner(chartId);
                const container = document.getElementById(chartId);
                container.innerHTML = '';

                if (!data || data.length === 0) {
                    showChartErrorMessage(chartId, 'Aucune donnée de répartition par type.');
                    return;
                }
                
                const trace = {
                    labels: data.map(item => item.type),
                    values: data.map(item => item.count),
                    type: 'pie',
                    hole: 0.4,
                    marker: { colors: themeColors.pieChartColors.slice(0, data.length) },
                    textinfo: 'label+percent',
                    textposition: 'outside',
                    automargin: true,
                    hoverinfo: 'label+percent+value',
                };
                
                const layout = {
                    margin: { t: 20, l: 20, r: 20, b: 20 },
                    paper_bgcolor: themeColors.cardBg,
                    plot_bgcolor: themeColors.cardBg,
                    font: { color: themeColors.textPrimaryDark },
                    showlegend: true,
                    legend: {
                        orientation: 'h', yanchor: 'bottom', y: -0.1, xanchor: 'center', x: 0.5
                    },
                     annotations: [{
                        font: { size: 16, color: themeColors.textPrimaryDark },
                        showarrow: false, text: 'Types', x: 0.5, y: 0.5
                    }]
                };
                Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
            })
            .catch(error => {
                console.error('Erreur lors du chargement des fournisseurs par type:', error);
                showChartErrorMessage('suppliers-by-type-chart', 'Erreur (Répartition Fourn.)');
            });

        // Charger les données des stagiaires par département
        fetch('/api/dashboard/interns-by-department')
            .then(response => response.json())
            .then(data => {
                const chartId = 'interns-by-department-chart';
                hideLoadingSpinner(chartId);
                const container = document.getElementById(chartId);
                container.innerHTML = '';

                if (!data || data.length === 0) {
                    showChartErrorMessage(chartId, 'Aucune donnée de répartition des stagiaires.');
                    return;
                }

                const trace = {
                    labels: data.map(item => item.department),
                    values: data.map(item => item.count),
                    type: 'pie',
                    hole: 0.4,
                    marker: { colors: themeColors.pieChartColors.slice(0, data.length) },
                    textinfo: 'label+percent',
                    textposition: 'outside',
                    automargin: true,
                    hoverinfo: 'label+percent+value',
                };
                
                const layout = {
                    margin: { t: 20, l: 20, r: 20, b: 20 },
                    paper_bgcolor: themeColors.cardBg,
                    plot_bgcolor: themeColors.cardBg,
                    font: { color: themeColors.textPrimaryDark },
                    showlegend: true,
                    legend: {
                        orientation: 'h', yanchor: 'bottom', y: -0.1, xanchor: 'center', x: 0.5
                    },
                    annotations: [{
                        font: { size: 16, color: themeColors.textPrimaryDark },
                        showarrow: false, text: 'Départ.', x: 0.5, y: 0.5
                    }]
                };
                Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
            })
            .catch(error => {
                console.error('Erreur lors du chargement des stagiaires par département:', error);
                showChartErrorMessage('interns-by-department-chart', 'Erreur (Répartition Stag.)');
            });
            
        // Charger les données des fournisseurs par entreprise (TRANSFORMED TO PIE CHART)
        fetch('/api/dashboard/suppliers-by-company')
            .then(response => response.json())
            .then(data => {
                const chartId = 'suppliers-by-company-chart';
                hideLoadingSpinner(chartId);
                const container = document.getElementById(chartId);
                container.innerHTML = '';

                if (!data || data.length === 0) {
                    showChartErrorMessage(chartId, 'Aucune donnée de répartition par entreprise.');
                    return;
                }
                
                data.sort((a, b) => b.count - a.count); // Sort for consistent pie chart segment order
                
                const trace = {
                    labels: data.map(item => item.company),
                    values: data.map(item => item.count),
                    type: 'pie',
                    hole: 0.4, // For a donut chart
                    marker: { colors: themeColors.pieChartColors.slice(0, data.length) },
                    textinfo: 'label+percent',
                    textposition: 'outside', // 'inside' or 'outside' or 'auto'
                    automargin: true,
                    hoverinfo: 'label+percent+value',
                };
                
                const layout = {
                    margin: { t: 20, l: 20, r: 20, b: 20 },
                    paper_bgcolor: themeColors.cardBg,
                    plot_bgcolor: themeColors.cardBg,
                    font: { color: themeColors.textPrimaryDark },
                    showlegend: true,
                    legend: {
                         orientation: 'h', yanchor: 'bottom', y: -0.1, xanchor: 'center', x: 0.5
                    },
                    annotations: [{
                        font: { size: 16, color: themeColors.textPrimaryDark },
                        showarrow: false, text: 'Entrep.', x: 0.5, y: 0.5
                    }]
                };
                Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
            })
            .catch(error => {
                console.error('Erreur lors du chargement des fournisseurs par entreprise:', error);
                showChartErrorMessage('suppliers-by-company-chart', 'Erreur (Top Entreprises)');
            });
    }

    // Load data on page load
    loadDashboardData();

    // Refresh button functionality
    const refreshButton = document.getElementById('refresh-dashboard');
    if (refreshButton) {
        refreshButton.addEventListener('click', loadDashboardData);
    }

    // Section navigation active state handling (simple version)
    const navItems = document.querySelectorAll('.section-nav-item');
    const sections = document.querySelectorAll('.dashboard-section');

    function setActiveNav() {
        let currentSectionId = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            // Adjust scrollY if you have a sticky navbar: window.scrollY + stickyNavbarHeight
            if (window.scrollY >= sectionTop - sectionHeight / 3) { 
                currentSectionId = section.getAttribute('id');
            }
        });

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${currentSectionId}`) {
                item.classList.add('active');
            }
        });
        // Fallback to first if no section is "active" (e.g. scrolled to top)
        if (!document.querySelector('.section-nav-item.active') && navItems.length > 0) {
             if (window.scrollY < sections[0].offsetTop) { // Only if above the first section
                navItems[0].classList.add('active');
            }
        }
    }
    
    window.addEventListener('scroll', setActiveNav);
    setActiveNav(); // Initial call

    // Optional: Auto-refresh data (e.g., every 5 minutes)
    // setInterval(loadDashboardData, 300000); 
});