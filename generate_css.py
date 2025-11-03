# Generate CaRhythm CSS files

css_content = """/* CaRhythm Brand Identity - "Your Career, Your Rhythm" */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=Poppins:wght@300;400;500;600;700&display=swap');

:root {
    --primary-aubergine: #6D3B8E;
    --primary-aubergine-dark: #4A2C5F;
    --secondary-gray: #7F8C8D;
    --accent-coral: #FF6B6B;
    --accent-coral-hover: #E74C3C;
    --accent-yellow: #F9C74F;
    --background-light: #F8F9FA;
    --background-white: #FFFFFF;
    --text-dark: #2C3E50;
    --text-light: #7F8C8D;
    --border-color: #E1E8ED;
    --success-color: #27AE60;
    --warning-color: #F39C12;
    --error-color: #E74C3C;
    --shadow-soft: 0 4px 20px rgba(109, 59, 142, 0.08);
    --shadow-medium: 0 8px 30px rgba(109, 59, 142, 0.12);
    --radius-sm: 6px;
    --radius-md: 12px;
    --radius-lg: 18px;
    --font-display: 'Playfair Display', serif;
    --font-body: 'Poppins', sans-serif;
    --spacing-sm: 16px;
    --spacing-md: 24px;
    --spacing-lg: 40px;
    --spacing-xl: 64px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--font-body);
    line-height: 1.7;
    color: var(--text-dark);
    background: linear-gradient(135deg, var(--background-light) 0%, #FFFFFF 100%);
    min-height: 100vh;
}

h1, h2, h3 {
    font-family: var(--font-display);
    font-weight: 700;
    color: var(--primary-aubergine-dark);
    line-height: 1.2;
}

.btn {
    display: inline-block;
    padding: 14px 32px;
    border: none;
    border-radius: var(--radius-md);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-primary {
    background: linear-gradient(135deg, var(--accent-coral), var(--accent-coral-hover));
    color: white;
    box-shadow: var(--shadow-soft);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-medium);
}

.card {
    background: white;
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    box-shadow: var(--shadow-soft);
}

.form-control {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    font-family: var(--font-body);
}

.form-control:focus {
    outline: none;
    border-color: var(--primary-aubergine);
    box-shadow: 0 0 0 3px rgba(109, 59, 142, 0.1);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-md);
}

.logo {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.logo-img {
    height: 50px;
    width: auto;
}

.logo-text {
    font-family: var(--font-display);
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--primary-aubergine-dark);
}
"""

with open('app/static/css/common.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

print("✅ common.css created successfully!")
