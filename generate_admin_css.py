# Generate CaRhythm admin.css

css_content = """/* CaRhythm Admin Panel Styles */

/* Admin Navigation */
.admin-nav {
    background: linear-gradient(135deg, var(--primary-aubergine-dark), var(--primary-aubergine));
    color: white;
    padding: 0;
    box-shadow: var(--shadow-medium);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.nav-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--spacing-md) var(--spacing-lg);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.admin-nav .logo {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.admin-nav .logo-img {
    height: 40px;
    filter: brightness(0) invert(1);
}

.admin-nav .logo-text {
    color: white;
    font-size: 1.5rem;
}

.admin-badge {
    margin-left: var(--spacing-xs);
}

.nav-links {
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
}

.nav-link {
    color: white;
    text-decoration: none;
    padding: 10px 18px;
    border-radius: var(--radius-md);
    transition: all 0.3s ease;
    font-weight: 500;
    font-size: 14px;
}

.nav-link:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
}

.nav-link.logout {
    background: var(--accent-coral);
    margin-left: var(--spacing-sm);
}

.nav-link.logout:hover {
    background: var(--accent-coral-hover);
}

/* Main Content */
.main-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--spacing-lg);
    min-height: calc(100vh - 200px);
}

/* Dashboard */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.stat-card {
    background: white;
    padding: var(--spacing-lg);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-soft);
    text-align: center;
    transition: transform 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-medium);
}

.stat-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-sm);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary-aubergine);
    margin-bottom: var(--spacing-xs);
}

.stat-label {
    font-size: 1rem;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Tables */
.data-table {
    width: 100%;
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-soft);
    overflow: hidden;
}

.data-table table {
    width: 100%;
    border-collapse: collapse;
}

.data-table thead {
    background: linear-gradient(135deg, var(--primary-aubergine), var(--primary-aubergine-dark));
    color: white;
}

.data-table th {
    padding: var(--spacing-sm) var(--spacing-md);
    text-align: left;
    font-weight: 600;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.data-table td {
    padding: var(--spacing-sm) var(--spacing-md);
    border-bottom: 1px solid var(--border-color);
}

.data-table tbody tr {
    transition: background 0.2s ease;
}

.data-table tbody tr:hover {
    background: rgba(109, 59, 142, 0.02);
}

/* Forms */
.admin-form {
    background: white;
    padding: var(--spacing-lg);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-soft);
}

.form-section {
    margin-bottom: var(--spacing-lg);
}

.form-section:last-child {
    margin-bottom: 0;
}

.form-section-title {
    font-size: 1.25rem;
    color: var(--primary-aubergine-dark);
    margin-bottom: var(--spacing-md);
    padding-bottom: var(--spacing-sm);
    border-bottom: 2px solid var(--accent-yellow);
}

.form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-md);
}

/* Action Buttons */
.action-buttons {
    display: flex;
    gap: var(--spacing-sm);
    flex-wrap: wrap;
}

.btn-icon {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.btn-sm {
    padding: 8px 16px;
    font-size: 13px;
    min-width: auto;
}

/* Admin Login */
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--primary-aubergine-dark), var(--primary-aubergine));
}

.login-card {
    max-width: 450px;
    width: 100%;
    background: white;
    padding: var(--spacing-xl);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-strong);
}

.login-logo {
    text-align: center;
    margin-bottom: var(--spacing-lg);
}

.login-logo img {
    height: 80px;
    margin-bottom: var(--spacing-sm);
}

.login-title {
    text-align: center;
    margin-bottom: var(--spacing-lg);
}

/* Question Pool */
.pool-filters {
    background: white;
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-soft);
    margin-bottom: var(--spacing-md);
    display: flex;
    gap: var(--spacing-sm);
    flex-wrap: wrap;
}

.filter-group {
    flex: 1;
    min-width: 200px;
}

/* Category Tags */
.category-tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 600;
    margin-right: var(--spacing-xs);
}

/* Status Badges */
.status-active {
    background: rgba(39, 174, 96, 0.1);
    color: var(--success-color);
    padding: 4px 12px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 600;
}

.status-inactive {
    background: rgba(127, 140, 141, 0.1);
    color: var(--secondary-gray);
    padding: 4px 12px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 600;
}

/* Footer */
.admin-footer {
    text-align: center;
    padding: var(--spacing-lg);
    background: rgba(109, 59, 142, 0.02);
    color: var(--text-light);
    font-size: 14px;
    border-top: 1px solid var(--border-color);
}

.admin-footer em {
    color: var(--primary-aubergine);
    font-style: italic;
}

/* Responsive */
@media (max-width: 1024px) {
    .nav-container {
        flex-direction: column;
        gap: var(--spacing-sm);
    }
    
    .nav-links {
        flex-wrap: wrap;
        justify-content: center;
    }
}

@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .data-table {
        overflow-x: auto;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .action-buttons {
        flex-direction: column;
    }
    
    .action-buttons .btn {
        width: 100%;
    }
}
"""

with open('app/static/css/admin.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

print("✅ admin.css created successfully!")
