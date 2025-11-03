# 🎨 Quick Reference Guide - Student Interface Animations

## CSS Animation Classes

### Fade In Animations
```css
/* Usage: Add to any element */
animation: fadeInUp 0.8s ease-out;

/* With delay */
animation: fadeInUp 0.8s ease-out 0.5s both;
```

### Slide Animations
```css
/* Slide from right */
animation: slide-in-right 0.8s ease-out;

/* Slide from left */
animation: slide-in-left 0.8s ease-out;
```

### Continuous Animations
```css
/* Float effect */
animation: float 3s ease-in-out infinite;

/* Pulse glow */
animation: pulse-glow 2s ease-in-out infinite;

/* Gradient shift */
animation: gradient-shift 6s ease infinite;
```

---

## JavaScript Functions

### Add Ripple Effect to Button
```javascript
const button = document.querySelector('.my-button');
button.addEventListener('click', createRipple);
```

### Initialize Scroll Animations
```javascript
// Called automatically on DOMContentLoaded
initScrollAnimations();
```

### Manual Element Animation
```javascript
// Add to element when it should animate
element.classList.add('animate-in');
```

### Show Save Indicator
```javascript
showSaveIndicator('Message here', 'success'); // or 'error', 'info'
```

---

## Color Variables

```css
/* Primary Colors */
var(--primary-aubergine)      /* #6D3B8E */
var(--primary-aubergine-dark) /* #4A2C5F */
var(--accent-coral)           /* #FF6B6B */
var(--accent-yellow)          /* #F9C74F */

/* Backgrounds */
var(--background-light)       /* #F8F9FA */
var(--background-white)       /* #FFFFFF */

/* Text */
var(--text-dark)              /* #2C3E50 */
var(--text-light)             /* #7F8C8D */

/* Shadows */
var(--shadow-soft)            /* Subtle shadow */
var(--shadow-medium)          /* Enhanced shadow */
```

---

## Spacing Variables

```css
var(--spacing-sm)   /* 16px */
var(--spacing-md)   /* 24px */
var(--spacing-lg)   /* 40px */
var(--spacing-xl)   /* 64px */
```

---

## Border Radius

```css
var(--radius-sm)    /* 6px */
var(--radius-md)    /* 12px */
var(--radius-lg)    /* 18px */
```

---

## Common Patterns

### Glassmorphism Effect
```css
.element {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(20px) saturate(180%);
    border-radius: var(--radius-lg);
    box-shadow: 0 8px 32px rgba(109, 59, 142, 0.1);
}
```

### 3D Card Hover
```css
.card {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
    transform: translateY(-12px) scale(1.02);
    box-shadow: 0 20px 60px rgba(109, 59, 142, 0.25);
}
```

### Gradient Text
```css
.text {
    background: linear-gradient(135deg, var(--primary-aubergine), var(--accent-coral));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
```

### Animated Border
```css
.element::after {
    content: '';
    position: absolute;
    inset: -2px;
    background: linear-gradient(45deg, var(--accent-coral), var(--accent-yellow));
    border-radius: inherit;
    opacity: 0;
    transition: opacity 0.4s ease;
    z-index: -1;
}

.element:hover::after {
    opacity: 1;
}
```

---

## Timing Functions

```css
/* Smooth ease */
cubic-bezier(0.4, 0, 0.2, 1)

/* Bounce */
cubic-bezier(0.68, -0.55, 0.265, 1.55)

/* Fast out, slow in */
cubic-bezier(0.4, 0.0, 0.2, 1)
```

---

## Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 480px) { }

/* Tablet */
@media (max-width: 768px) { }

/* Desktop */
@media (min-width: 769px) { }
```

---

## Best Practices

### Performance
- Use `transform` and `opacity` for animations (GPU accelerated)
- Avoid animating `width`, `height`, `top`, `left`
- Use `will-change` sparingly

### Accessibility
- Always provide reduced motion alternatives
- Ensure focus states are visible
- Maintain color contrast ratios

### Timing
- Fast interactions: 0.2s - 0.3s
- Medium transitions: 0.4s - 0.6s
- Slow animations: 0.8s - 1.2s
- Never exceed 1.5s

---

## Testing Commands

### Run the application
```bash
python run.py
```

### Access student interface
```
http://localhost:8000/student/welcome
```

### Clear browser cache
```
Ctrl + Shift + Delete (Chrome)
Cmd + Shift + Delete (Safari)
```

---

## Browser DevTools Tips

### View Animations
1. Chrome DevTools > More Tools > Animations
2. Slow down animations to debug
3. Inspect animation timeline

### Test Responsiveness
1. Toggle device toolbar (Ctrl + Shift + M)
2. Select device or custom dimensions
3. Test touch interactions

### Performance Profiling
1. Performance tab
2. Record while interacting
3. Check for 60fps
4. Look for long tasks

---

## Common Customizations

### Change Primary Color
```css
:root {
    --primary-aubergine: #YOUR_COLOR;
}
```

### Adjust Animation Speed
```css
.element {
    animation-duration: 1.5s; /* Change from default */
}
```

### Disable Specific Animation
```css
.no-float {
    animation: none !important;
}
```

### Add Custom Animation
```css
@keyframes myAnimation {
    from { /* start state */ }
    to { /* end state */ }
}

.element {
    animation: myAnimation 1s ease;
}
```

---

## Troubleshooting

### Animations Not Working
- Check browser support
- Verify CSS is loaded
- Check for syntax errors
- Clear browser cache

### Performance Issues
- Reduce number of simultaneous animations
- Use `will-change` property
- Check for memory leaks in DevTools

### Ripple Effect Not Showing
- Verify JavaScript is loaded
- Check button has `position: relative`
- Ensure overflow is not hidden on parent

### Scroll Animations Not Triggering
- Check Intersection Observer support
- Verify elements have animation classes
- Check threshold values

---

## File Locations

```
app/
├── static/
│   ├── css/
│   │   ├── common.css      # Shared styles
│   │   └── student.css     # Student-specific styles
│   └── js/
│       └── student.js      # Student interactions
└── templates/
    └── student/
        ├── welcome.html
        ├── examination.html
        └── completion.html
```

---

## Resources

- [MDN Web Animations](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API)
- [CSS Tricks - Animation Guide](https://css-tricks.com/almanac/properties/a/animation/)
- [Can I Use](https://caniuse.com/) - Browser compatibility
- [Cubic Bezier Generator](https://cubic-bezier.com/)

---

**Last Updated**: November 3, 2025
**Version**: 1.0
**Maintained By**: Development Team
