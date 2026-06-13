COLORS_DARK = {
    "bg": "#0B0E14",
    "bg2": "#11151F",
    "panel": "#151A27",
    "panel2": "#1A2132",
    "panel3": "#1F283C",
    "border": "#2A3650",
    "border2": "#3B4764",
    "text": "#F8FAFC",
    "muted": "#94A3B8",
    "subtle": "#CBD5E1",
    "accent": "#8B5CF6",
    "accent_hover": "#7C3AED",
    "button_dark": "#1E293B",
    "button_dark_hover": "#334155",
    "success": "#10B981",
    "danger": "#F43F5E",
    "info": "#3B82F6",
    "log_bg": "#08101d",
    "log_fg": "#dbeafe"
}

COLORS_LIGHT = {
    "bg": "#F8FAFC",
    "bg2": "#F1F5F9",
    "panel": "#FFFFFF",
    "panel2": "#F8FAFC",
    "panel3": "#F1F5F9",
    "border": "#E2E8F0",
    "border2": "#CBD5E1",
    "text": "#0F172A",
    "muted": "#64748B",
    "subtle": "#475569",
    "accent": "#8B5CF6",
    "accent_hover": "#7C3AED",
    "button_dark": "#E2E8F0",
    "button_dark_hover": "#CBD5E1",
    "success": "#10B981",
    "danger": "#F43F5E",
    "info": "#3B82F6",
    "log_bg": "#F1F5F9",
    "log_fg": "#0F172A"
}

def get_theme(is_dark):
    return COLORS_DARK if is_dark else COLORS_LIGHT
