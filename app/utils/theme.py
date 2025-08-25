"""
Centralized theme configuration for FeedForward.
Uses CSS custom properties for dynamic theming.
"""

from fasthtml import common as fh

# CSS custom properties for consistent theming
THEME_CSS = """
:root {
    /* Primary colors */
    --color-primary: rgb(37 99 235);        /* blue-600 */
    --color-primary-dark: rgb(29 78 216);   /* blue-700 */
    --color-primary-light: rgb(59 130 246);  /* blue-500 */
    --color-primary-50: rgb(239 246 255);    /* blue-50 */
    --color-primary-100: rgb(219 234 254);   /* blue-100 */
    
    /* Secondary colors */
    --color-secondary: rgb(20 184 166);      /* teal-500 */
    --color-secondary-dark: rgb(13 148 136); /* teal-600 */
    --color-secondary-light: rgb(45 212 191); /* teal-400 */
    
    /* Neutral colors */
    --color-slate-50: rgb(248 250 252);
    --color-slate-100: rgb(241 245 249);
    --color-slate-600: rgb(71 85 105);
    --color-slate-700: rgb(51 65 85);
    --color-slate-800: rgb(30 41 59);
    --color-slate-900: rgb(15 23 42);
    
    /* Gray scale */
    --color-gray-50: rgb(249 250 251);
    --color-gray-100: rgb(243 244 246);
    --color-gray-200: rgb(229 231 235);
    --color-gray-300: rgb(209 213 219);
    --color-gray-400: rgb(156 163 175);
    --color-gray-500: rgb(107 114 128);
    --color-gray-600: rgb(75 85 99);
    --color-gray-700: rgb(55 65 81);
    --color-gray-800: rgb(31 41 55);
    
    /* Semantic colors */
    --color-success: rgb(34 197 94);         /* green-500 */
    --color-warning: rgb(245 158 11);        /* amber-500 */
    --color-error: rgb(239 68 68);           /* red-500 */
    --color-info: rgb(59 130 246);           /* blue-500 */
    
    /* Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 1.5rem;
    --spacing-lg: 2rem;
    --spacing-xl: 3rem;
    
    /* Border radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    --radius-full: 9999px;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
    
    /* Transitions */
    --transition-fast: 150ms ease-in-out;
    --transition-normal: 300ms ease-in-out;
    --transition-slow: 500ms ease-in-out;
}

/* Dark mode variables (future enhancement) */
@media (prefers-color-scheme: dark) {
    :root {
        /* Override colors for dark mode here */
    }
}
"""

# Component classes using CSS variables
COMPONENT_CLASSES = {
    # Headers
    "header_main": "bg-gradient-to-r from-slate-700 to-slate-800 text-white py-4 shadow-md",
    "header_light": "bg-white border-b border-gray-200 py-4 shadow-sm",
    
    # Buttons - using fixed Tailwind classes that exist
    "btn_primary": "bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5",
    "btn_secondary": "bg-white hover:bg-blue-50 text-blue-600 border-2 border-blue-600 hover:border-blue-700 px-8 py-4 rounded-xl font-semibold transition-all shadow-sm hover:shadow-md",
    "btn_ghost": "text-blue-600 hover:text-blue-700 hover:bg-blue-50 px-4 py-2 rounded-lg transition-all font-medium",
    "btn_success": "bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-all shadow-sm hover:shadow-md",
    "btn_danger": "bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-all shadow-sm hover:shadow-md",
    "btn_warning": "bg-amber-500 hover:bg-amber-600 text-white px-6 py-3 rounded-lg font-medium transition-all shadow-sm hover:shadow-md",
    
    # Cards
    "card_default": "bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100",
    "card_elevated": "bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow",
    "card_bordered": "bg-white rounded-xl border-2 border-gray-200 hover:border-blue-300 transition-colors",
    
    # Forms
    "input_default": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
    "input_error": "w-full px-3 py-2 border border-red-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500",
    "input_success": "w-full px-3 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500",
    "input_disabled": "w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-600 cursor-not-allowed",
    
    "label_default": "block text-sm font-medium text-gray-700 mb-1",
    "label_required": "block text-sm font-medium text-gray-700 mb-1 after:content-['*'] after:ml-0.5 after:text-red-500",
    
    # Typography
    "text_hero": "text-4xl md:text-6xl font-bold leading-tight",
    "text_h1": "text-3xl md:text-4xl font-bold leading-tight text-slate-800",
    "text_h2": "text-2xl md:text-3xl font-semibold leading-snug text-slate-800",
    "text_h3": "text-xl md:text-2xl font-semibold leading-snug text-slate-700",
    "text_body": "text-base leading-relaxed text-gray-600",
    "text_body_lg": "text-lg leading-relaxed text-gray-700",
    "text_small": "text-sm leading-normal text-gray-600",
    "text_muted": "text-gray-500",
    
    # Alerts/Messages
    "alert_success": "bg-green-100 text-green-700 p-3 rounded-lg",
    "alert_error": "bg-red-100 text-red-700 p-3 rounded-lg",
    "alert_warning": "bg-amber-100 text-amber-700 p-3 rounded-lg",
    "alert_info": "bg-blue-100 text-blue-700 p-3 rounded-lg",
    
    # Badges
    "badge_primary": "bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium",
    "badge_secondary": "bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium",
    "badge_success": "bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium",
    "badge_warning": "bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-sm font-medium",
    "badge_error": "bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-medium",
    
    # Navigation
    "nav_link": "text-white px-4 py-2 mx-1 transition-colors hover:text-blue-200",
    "nav_link_active": "text-white bg-blue-700 px-4 py-2 rounded-lg mx-1 font-medium shadow-sm",
    
    # Sections/Containers
    "section_light": "bg-gray-50",
    "section_white": "bg-white",
    "section_gradient": "bg-gradient-to-br from-slate-50 via-blue-50 to-teal-50",
    
    # Footer
    "footer_main": "bg-gray-50",
    "footer_dark": "bg-slate-800 text-white",
}

def get_theme_styles():
    """Return the theme CSS as a Style component."""
    return fh.Style(THEME_CSS)

def themed(component_type: str, *children, **kwargs):
    """
    Create a themed component with predefined classes.
    
    Args:
        component_type: Key from COMPONENT_CLASSES
        *children: Child elements
        **kwargs: Additional HTML attributes
        
    Example:
        themed('btn_primary', 'Click me', onclick='handleClick()')
    """
    # Get the default classes for this component type
    default_cls = COMPONENT_CLASSES.get(component_type, "")
    
    # Allow overriding or extending classes
    if 'cls' in kwargs:
        kwargs['cls'] = f"{default_cls} {kwargs['cls']}"
    else:
        kwargs['cls'] = default_cls
    
    # Determine the HTML element based on component type
    if 'btn' in component_type:
        return fh.Button(*children, **kwargs)
    elif 'card' in component_type:
        return fh.Div(*children, **kwargs)
    elif 'text' in component_type or component_type.startswith('h'):
        return fh.Div(*children, **kwargs)
    elif 'alert' in component_type:
        return fh.Div(*children, **kwargs)
    elif 'badge' in component_type:
        return fh.Span(*children, **kwargs)
    elif 'input' in component_type:
        return fh.Input(**kwargs)
    elif 'label' in component_type:
        return fh.Label(*children, **kwargs)
    else:
        return fh.Div(*children, **kwargs)

# Specific component builders for common patterns
def PrimaryButton(text, **kwargs):
    """Create a primary button with consistent styling."""
    return fh.Button(text, cls=COMPONENT_CLASSES['btn_primary'], **kwargs)

def SecondaryButton(text, **kwargs):
    """Create a secondary button with consistent styling."""
    return fh.Button(text, cls=COMPONENT_CLASSES['btn_secondary'], **kwargs)

def Card(title=None, *children, **kwargs):
    """Create a card with optional title."""
    card_content = []
    if title:
        card_content.append(
            fh.H3(title, cls="text-lg font-bold text-slate-800 mb-4 pb-3 border-b border-gray-100")
        )
    card_content.extend(children)
    
    return fh.Div(*card_content, cls=COMPONENT_CLASSES['card_default'], **kwargs)

def Alert(message, type='info', **kwargs):
    """Create an alert message."""
    alert_class = COMPONENT_CLASSES.get(f'alert_{type}', COMPONENT_CLASSES['alert_info'])
    return fh.Div(message, cls=alert_class, **kwargs)

def Badge(text, type='primary', **kwargs):
    """Create a badge."""
    badge_class = COMPONENT_CLASSES.get(f'badge_{type}', COMPONENT_CLASSES['badge_primary'])
    return fh.Span(text, cls=badge_class, **kwargs)

def FormInput(name, label=None, type='text', required=False, error=None, **kwargs):
    """Create a form input with label and error handling."""
    elements = []
    
    # Add label if provided
    if label:
        label_class = COMPONENT_CLASSES['label_required'] if required else COMPONENT_CLASSES['label_default']
        elements.append(fh.Label(label, for_=name, cls=label_class))
    
    # Determine input class based on error state
    input_class = COMPONENT_CLASSES['input_error'] if error else COMPONENT_CLASSES['input_default']
    
    # Create input
    elements.append(
        fh.Input(type=type, id=name, name=name, cls=input_class, **kwargs)
    )
    
    # Add error message if present
    if error:
        elements.append(fh.P(error, cls="text-sm text-red-500 mt-1"))
    
    return fh.Div(*elements, cls="mb-4")

# Export theme as a dictionary for use in templates
THEME = {
    'colors': {
        'primary': 'blue-600',
        'primary_dark': 'blue-700',
        'primary_light': 'blue-500',
        'secondary': 'teal-500',
        'secondary_dark': 'teal-600',
        'secondary_light': 'teal-400',
        'success': 'green-600',
        'warning': 'amber-500',
        'error': 'red-600',
        'info': 'blue-500',
        'text_primary': 'slate-800',
        'text_secondary': 'gray-600',
        'text_muted': 'gray-500',
        'border': 'gray-200',
        'bg_light': 'gray-50',
        'bg_white': 'white',
    },
    'classes': COMPONENT_CLASSES,
    'css': THEME_CSS
}