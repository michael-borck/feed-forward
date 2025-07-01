# FeedForward Styling Fixes

## Table Contrast Improvements

### Issue Fixed
Tables in the instructor feedback interfaces had poor contrast due to dark text on dark backgrounds.

### Specific Changes Made

**File:** `app/routes/instructor.py`
**Location:** Line 4284 (Score Comparison Table)

**Before:**
```python
row_cells.append(Td(agg_cell, cls="px-4 py-3 bg-indigo-50"))
```

**After:**
```python
row_cells.append(Td(agg_cell, cls="px-4 py-3 bg-gray-100"))
```

**Text Color Update:**
- Changed aggregated score text from `text-indigo-600` to `text-gray-800` for better contrast on the new gray background

### Color Scheme Consistency

The new styling makes table backgrounds consistent with other UI elements:
- **Tables:** `bg-gray-100` (light gray background)
- **Buttons:** `bg-gray-600` (medium gray for buttons)
- **Text:** `text-gray-800` (dark gray for good contrast)

### WCAG Compliance
The new color combination `text-gray-800` on `bg-gray-100` provides:
- **Better contrast ratio** for accessibility
- **Consistent visual hierarchy** with other gray elements
- **Professional appearance** matching the overall design system

### Tables Affected
- **Score Comparison Table** in individual submission detail view
- **Aggregated Score Column** highlighting
- Any other tables using similar color schemes

### Testing
To verify the fix:
1. Start the application: `python app.py`
2. Login as instructor: `instructor@demo.com` / `instructor123`
3. Navigate to course CS101
4. View any assignment submissions
5. Check the "Aggregated" column in the score comparison table

The aggregated scores should now have much better contrast and readability.