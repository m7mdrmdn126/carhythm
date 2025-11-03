# MCQ Troubleshooting Guide

## Quick Fixes Applied

### 1. CSS Improvements
- ✅ Added `!important` to `.mcq-container` display property
- ✅ Added explicit visibility and opacity rules
- ✅ Fixed z-index stacking for pseudo-elements
- ✅ Added `.question-input` container styling
- ✅ Removed duplicate CSS rules
- ✅ Made `.selected` class more robust with `!important`
- ✅ Added min-height to ensure options are visible
- ✅ Fixed overflow property

### 2. JavaScript Enhancements
- ✅ Enhanced MCQ selection handler
- ✅ Added console logging for debugging
- ✅ Improved click event handling
- ✅ Better support for both radio and checkbox types
- ✅ Auto-marking selected options on page load

## How to Debug

### Step 1: Open Browser Console
1. Press F12 to open Developer Tools
2. Go to Console tab
3. Look for these messages:
   - "Found MCQ containers: X"
   - "Found MCQ options: X"
   - "MCQ input found: ..."

### Step 2: Check if MCQs Exist in HTML
In Console, run:
```javascript
document.querySelectorAll('.mcq-container').length
document.querySelectorAll('.mcq-option').length
```

If both return 0, the issue is in the backend (questions not being passed to template).
If they return numbers > 0, the issue is CSS/visibility.

### Step 3: Check CSS Applied
In Console, run:
```javascript
const option = document.querySelector('.mcq-option');
console.log(getComputedStyle(option).display);
console.log(getComputedStyle(option).visibility);
console.log(getComputedStyle(option).opacity);
```

Should show:
- display: "block"
- visibility: "visible"
- opacity: "1"

### Step 4: Check if Options Have Content
In Console, run:
```javascript
document.querySelectorAll('.mcq-option').forEach((opt, i) => {
    console.log(`Option ${i}:`, opt.textContent.trim());
});
```

### Step 5: Force Visibility (Emergency CSS)
If still not visible, in Console run:
```javascript
document.querySelectorAll('.mcq-option').forEach(opt => {
    opt.style.cssText = 'display: block !important; visibility: visible !important; opacity: 1 !important; background: yellow; padding: 20px; border: 2px solid red; margin: 10px 0;';
});
```

## Common Issues & Solutions

### Issue 1: MCQs Exist but Not Visible
**Symptoms**: Console shows options found, but not visible on screen.
**Solution**: Check for CSS conflicts, parent overflow: hidden

### Issue 2: MCQs Don't Exist at All
**Symptoms**: Console shows 0 mcq-containers
**Solution**: 
1. Check if questions have `question_type = 'mcq'`
2. Check if `mcq_options` is populated
3. Check if `mcq_options_parsed` is being set

### Issue 3: MCQs Show But Can't Select
**Symptoms**: Options visible but clicking doesn't work
**Solution**: Check z-index, pointer-events, and JavaScript errors

### Issue 4: Radio Buttons Don't Deselect Others
**Symptoms**: Multiple radio buttons can be selected
**Solution**: Ensure all radio buttons have the same `name` attribute

## Testing Checklist

- [ ] Open examination page
- [ ] Open browser console (F12)
- [ ] Check for MCQ-related console logs
- [ ] Look for MCQ questions on the page
- [ ] Try hovering over MCQ options (should see animation)
- [ ] Try clicking MCQ options (should select)
- [ ] Check if selection is visually indicated
- [ ] Try selecting different options
- [ ] Check if form data includes MCQ answers

## Quick Test Code

Run this in console to verify everything:
```javascript
// Test MCQ System
console.log('=== MCQ Debug Info ===');
console.log('Containers:', document.querySelectorAll('.mcq-container').length);
console.log('Options:', document.querySelectorAll('.mcq-option').length);
console.log('Radio inputs:', document.querySelectorAll('.mcq-option input[type="radio"]').length);
console.log('Checkbox inputs:', document.querySelectorAll('.mcq-option input[type="checkbox"]').length);

// Test selection
const firstOption = document.querySelector('.mcq-option');
if (firstOption) {
    console.log('First option display:', getComputedStyle(firstOption).display);
    console.log('First option visibility:', getComputedStyle(firstOption).visibility);
    console.log('First option text:', firstOption.textContent.trim().substring(0, 50));
}

// Test inputs
document.querySelectorAll('.mcq-option input').forEach((input, i) => {
    console.log(`Input ${i}:`, input.type, input.name, input.value, 'checked:', input.checked);
});
```

## Backend Verification

### Check Question Data
In Python, verify:
```python
# In examination router or service
questions = question_service.get_questions_by_page(db, page_id)
for q in questions:
    if q.question_type == 'mcq':
        print(f"MCQ Question: {q.id}")
        print(f"Options: {q.mcq_options}")
        print(f"Parsed: {q.mcq_options_parsed}")
```

### Check Template Context
Add to examination.html temporarily:
```html
<!-- DEBUG: Show MCQ questions -->
{% for question in questions %}
    {% if question.question_type.value == 'mcq' %}
        <div style="background: yellow; padding: 10px; margin: 10px;">
            <strong>DEBUG MCQ:</strong>
            <p>ID: {{ question.id }}</p>
            <p>Options: {{ question.mcq_options_parsed }}</p>
            <p>Count: {{ question.mcq_options_parsed|length }}</p>
        </div>
    {% endif %}
{% endfor %}
```

## Expected Behavior

### When Working Correctly:
1. MCQ questions appear as white boxes with borders
2. Each option is a separate clickable box
3. Hovering slides the option to the right with colored border
4. Clicking selects the option (changes background to light gradient)
5. For radio: previous selection is deselected
6. For checkbox: multiple can be selected
7. Selected options have coral/yellow gradient background

### Visual Indicators:
- ✅ Border: 2px solid #E1E8ED (default), #FF6B6B (selected)
- ✅ Background: white (default), gradient (selected)
- ✅ Transform: translateX(8px) on hover/select
- ✅ Shadow: colored left border (-4px)

## Files Modified
- `app/static/css/student.css` - MCQ styles enhanced
- `app/static/js/student.js` - MCQ handler improved

## Next Steps if Still Not Working

1. **Clear Browser Cache**: Ctrl+Shift+R
2. **Check Network Tab**: Verify CSS/JS files load (200 status)
3. **Test in Different Browser**: Rule out browser-specific issues
4. **Check Database**: Verify MCQ questions exist with options
5. **Add Temporary Debug HTML**: See template debug code above
6. **Contact Support**: Provide console output and screenshots

---

**Status**: ✅ Fixes Applied
**Last Updated**: November 3, 2025
