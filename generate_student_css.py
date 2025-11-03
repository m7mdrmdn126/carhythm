# Generate CaRhythm student.css

css_content = """/* CaRhythm Student Interface Styles */

.header {
    padding: var(--spacing-md) 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    background: white;
    position: sticky;
    top: 0;
    z-index: 100;
}

.footer {
    text-align: center;
    padding: var(--spacing-lg) 0;
    color: var(--text-light);
    font-size: 14px;
}

.footer em {
    color: var(--primary-aubergine);
    font-style: italic;
}

/* Welcome Page Hero */
.welcome-hero {
    min-height: calc(100vh - 200px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-xl) 0;
}

.welcome-container {
    max-width: 900px;
    margin: 0 auto;
}

.welcome-content {
    text-align: center;
    animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.welcome-title {
    font-size: clamp(2.5rem, 6vw, 4rem);
    margin-bottom: var(--spacing-sm);
    background: linear-gradient(135deg, var(--primary-aubergine), var(--accent-coral));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.welcome-subtitle {
    font-size: 1.5rem;
    color: var(--accent-coral);
    font-weight: 500;
    margin-bottom: var(--spacing-md);
    font-style: italic;
}

.welcome-description {
    font-size: 1.125rem;
    line-height: 1.8;
    color: var(--text-dark);
    margin-bottom: var(--spacing-lg);
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

/* Feature Cards */
.welcome-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-md);
    margin: var(--spacing-lg) 0;
}

.feature-card {
    padding: var(--spacing-md);
    background: linear-gradient(135deg, rgba(109, 59, 142, 0.03), rgba(249, 199, 79, 0.03));
    border-radius: var(--radius-md);
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-sm);
}

.feature-card h3 {
    font-size: 1.25rem;
    margin-bottom: var(--spacing-xs);
    color: var(--primary-aubergine-dark);
}

.feature-card p {
    font-size: 0.95rem;
    color: var(--text-light);
}

/* Info List */
.welcome-info {
    text-align: left;
    max-width: 600px;
    margin: var(--spacing-lg) auto;
    padding: var(--spacing-md);
    background: rgba(109, 59, 142, 0.02);
    border-radius: var(--radius-md);
    border-left: 4px solid var(--accent-yellow);
}

.welcome-info h3 {
    margin-bottom: var(--spacing-sm);
    color: var(--primary-aubergine);
}

.info-list {
    list-style: none;
    padding: 0;
}

.info-list li {
    padding: var(--spacing-xs) 0;
    font-size: 1rem;
    color: var(--text-dark);
}

/* Actions */
.welcome-actions {
    margin: var(--spacing-lg) 0;
}

.btn-large {
    padding: 18px 48px;
    font-size: 1.125rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.privacy-notice {
    margin-top: var(--spacing-md);
    color: var(--text-light);
}

/* Examination Page */
.exam-container {
    max-width: 800px;
    margin: var(--spacing-lg) auto;
}

.progress-bar {
    height: 8px;
    background: var(--border-color);
    border-radius: 4px;
    overflow: hidden;
    margin: var(--spacing-md) 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary-aubergine), var(--accent-coral));
    transition: width 0.3s ease;
}

.question-card {
    margin-bottom: var(--spacing-md);
}

.question-text {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--primary-aubergine-dark);
    margin-bottom: var(--spacing-sm);
}

.question-required {
    color: var(--accent-coral);
}

/* Slider Question */
.slider-container {
    padding: var(--spacing-md) 0;
}

.slider-labels {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--spacing-xs);
    font-size: 0.9rem;
    color: var(--text-light);
}

input[type="range"] {
    width: 100%;
    height: 8px;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--accent-coral), var(--accent-yellow), var(--primary-aubergine));
    outline: none;
    -webkit-appearance: none;
}

input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    border: none;
}

.slider-value {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-aubergine);
    margin-top: var(--spacing-sm);
}

/* MCQ Questions */
.mcq-options {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.mcq-option {
    display: flex;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.3s ease;
}

.mcq-option:hover {
    border-color: var(--primary-aubergine);
    background: rgba(109, 59, 142, 0.02);
}

.mcq-option input {
    margin-right: var(--spacing-sm);
}

.mcq-option.selected {
    border-color: var(--primary-aubergine);
    background: rgba(109, 59, 142, 0.05);
}

/* Navigation */
.exam-navigation {
    display: flex;
    justify-content: space-between;
    gap: var(--spacing-md);
    margin-top: var(--spacing-lg);
    padding-top: var(--spacing-md);
    border-top: 1px solid var(--border-color);
}

/* Completion Page */
.completion-container {
    max-width: 700px;
    margin: var(--spacing-xl) auto;
    text-align: center;
}

.completion-icon {
    font-size: 5rem;
    animation: bounce 1s ease-in-out;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
}

.completion-title {
    font-size: 2.5rem;
    margin: var(--spacing-md) 0;
}

.completion-message {
    font-size: 1.125rem;
    color: var(--text-light);
    margin-bottom: var(--spacing-lg);
}

/* Responsive */
@media (max-width: 768px) {
    .welcome-features {
        grid-template-columns: 1fr;
    }
    
    .exam-navigation {
        flex-direction: column;
    }
    
    .exam-navigation .btn {
        width: 100%;
    }
}
"""

with open('app/static/css/student.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

print("✅ student.css created successfully!")
