DEFAULT_BRANDING = {
    'name': 'CCMS',
    'tagline': 'Courier & Cargo Management',
    'logo_url': None,
    'primary_color': '#3b82f6',
    'primary_dark': '#2563eb',
    'primary_light': '#60a5fa',
    'sidebar_color': '#1e2a4a',
    'sidebar_hover': '#253358',
    'sidebar_active': '#2d3f6e',
}


def _clamp(value):
    return max(0, min(255, int(value)))


def _darken_hex(hex_color, factor=0.82):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return DEFAULT_BRANDING['primary_dark']
    r = _clamp(int(hex_color[0:2], 16) * factor)
    g = _clamp(int(hex_color[2:4], 16) * factor)
    b = _clamp(int(hex_color[4:6], 16) * factor)
    return f'#{r:02x}{g:02x}{b:02x}'


def _lighten_hex(hex_color, factor=0.25):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return DEFAULT_BRANDING['primary_light']
    r = _clamp(int(hex_color[0:2], 16) + (255 - int(hex_color[0:2], 16)) * factor)
    g = _clamp(int(hex_color[2:4], 16) + (255 - int(hex_color[2:4], 16)) * factor)
    b = _clamp(int(hex_color[4:6], 16) + (255 - int(hex_color[4:6], 16)) * factor)
    return f'#{r:02x}{g:02x}{b:02x}'


def _sidebar_tint(hex_color, factor=0.12):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return DEFAULT_BRANDING['sidebar_hover']
    r = _clamp(int(hex_color[0:2], 16) + (255 - int(hex_color[0:2], 16)) * factor)
    g = _clamp(int(hex_color[2:4], 16) + (255 - int(hex_color[2:4], 16)) * factor)
    b = _clamp(int(hex_color[4:6], 16) + (255 - int(hex_color[4:6], 16)) * factor)
    return f'#{r:02x}{g:02x}{b:02x}'


def get_tenant_branding(tenant=None):
    branding = DEFAULT_BRANDING.copy()

    if tenant is None:
        return branding

    branding['name'] = tenant.display_name or tenant.name or branding['name']
    branding['tagline'] = tenant.tagline or branding['tagline']

    if tenant.logo:
        branding['logo_url'] = tenant.logo.url

    primary = tenant.primary_color or DEFAULT_BRANDING['primary_color']
    sidebar = tenant.sidebar_color or DEFAULT_BRANDING['sidebar_color']

    branding['primary_color'] = primary
    branding['primary_dark'] = _darken_hex(primary)
    branding['primary_light'] = _lighten_hex(primary)
    branding['sidebar_color'] = sidebar
    branding['sidebar_hover'] = _sidebar_tint(sidebar, 0.10)
    branding['sidebar_active'] = _sidebar_tint(sidebar, 0.18)

    return branding
