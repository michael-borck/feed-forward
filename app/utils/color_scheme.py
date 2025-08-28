"""
Modern color scheme for FeedForward application.
Using a softer, more accessible color palette.
"""

# Modern, softer color palette
MODERN_COLORS = {
    # Primary brand colors - softer blues
    "primary": "blue-600",           # Main brand color (softer than indigo-700)
    "primary-dark": "blue-700",      # Darker variant
    "primary-light": "blue-500",     # Lighter variant

    # Secondary colors - warm teal/cyan
    "secondary": "teal-500",         # Accent color
    "secondary-dark": "teal-600",
    "secondary-light": "teal-400",

    # Background colors - much softer
    "header-bg": "slate-800",        # Softer than indigo-900
    "header-gradient": "bg-gradient-to-r from-slate-700 to-slate-800",
    "hero-bg": "bg-gradient-to-br from-slate-50 via-blue-50 to-teal-50",
    "section-bg": "gray-50",

    # Text colors
    "text-primary": "gray-800",      # Main text
    "text-secondary": "gray-600",    # Secondary text
    "text-light": "gray-100",        # Light text on dark bg
    "text-muted": "gray-500",        # Muted text

    # UI elements
    "border": "gray-200",
    "border-hover": "blue-300",
    "shadow": "shadow-lg",
    "success": "green-500",
    "warning": "amber-500",
    "error": "red-500",
    "info": "blue-500",
}

# Alternative softer palette (can switch between themes)
SOFT_PALETTE = {
    # Gradient backgrounds for hero sections
    "hero-gradient-1": "bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50",
    "hero-gradient-2": "bg-gradient-to-br from-teal-50 via-cyan-50 to-blue-50",
    "hero-gradient-3": "bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50",

    # Soft header options
    "header-soft": "bg-gradient-to-r from-slate-600 to-slate-700",
    "header-light": "bg-white border-b border-gray-200",
    "header-gradient": "bg-gradient-to-r from-blue-600 to-indigo-600",
}

# Button styles with softer colors
BUTTON_STYLES = {
    "primary": "bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5",
    "secondary": "bg-white hover:bg-gray-50 text-blue-600 border-2 border-blue-600 hover:border-blue-700 px-8 py-4 rounded-xl font-semibold transition-all shadow-sm hover:shadow-md",
    "ghost": "text-blue-600 hover:text-blue-700 hover:bg-blue-50 px-4 py-2 rounded-lg transition-all font-medium",
    "success": "bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-all shadow-sm hover:shadow-md",
    "warning": "bg-amber-500 hover:bg-amber-600 text-white px-6 py-3 rounded-lg font-medium transition-all shadow-sm hover:shadow-md",
}

# Card styles with soft shadows
CARD_STYLES = {
    "default": "bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100",
    "elevated": "bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow",
    "bordered": "bg-white rounded-xl border-2 border-gray-200 hover:border-blue-300 transition-colors",
    "gradient": "bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-md",
}

# Typography with better contrast
TYPOGRAPHY = {
    "hero": "text-4xl md:text-6xl font-bold leading-tight",
    "h1": "text-3xl md:text-4xl font-bold leading-tight text-gray-800",
    "h2": "text-2xl md:text-3xl font-semibold leading-snug text-gray-800",
    "h3": "text-xl md:text-2xl font-semibold leading-snug text-gray-700",
    "body-lg": "text-lg leading-relaxed text-gray-700",
    "body": "text-base leading-relaxed text-gray-600",
    "body-sm": "text-sm leading-normal text-gray-600",
    "caption": "text-xs leading-normal text-gray-500",
}
