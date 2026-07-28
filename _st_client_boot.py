"""Streamlit istemci ayarları — `import streamlit as st` öncesi `apply()`; sonra `inject_sidebar_hidden(st)`."""

from __future__ import annotations

import json

HIDE_SIDEBAR_NAV_HTML = """
<style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"] {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
    }
</style>
"""

_HIDE_SIDEBAR_JS_CSS = (
    '[data-testid="stSidebar"],[data-testid="stSidebarNav"],'
    '[data-testid="collapsedControl"]'
    "{display:none!important;width:0!important;min-width:0!important;}"
)


def apply() -> None:
    try:
        from streamlit import config

        try:
            config.set_option("client.showSidebarNavigation", False)
        except Exception:
            pass
        try:
            config.set_option("client.toolbarMode", "minimal")
        except Exception:
            pass
    except Exception:
        pass


def _inject_style_into_parent_app() -> None:
    """iframe içinden ana Streamlit dokümanına <style> ekler; markdown'dan önce boyanma şansı artar."""
    try:
        import streamlit.components.v1 as components

        css_literal = json.dumps(_HIDE_SIDEBAR_JS_CSS)
        html = f"""
<div style="height:0;width:0;overflow:hidden;"></div>
<script>
(function() {{
  try {{
    var d = window.parent && window.parent.document;
    if (!d) return;
    if (d.getElementById('randevu-hide-streamlit-chrome')) return;
    var el = d.createElement('style');
    el.id = 'randevu-hide-streamlit-chrome';
    el.textContent = {css_literal};
    (d.head || d.documentElement).appendChild(el);
  }} catch (e) {{}}
}})();
</script>
"""
        components.html(html, height=0, scrolling=False)
    except Exception:
        pass


def inject_sidebar_hidden(st) -> None:
    _inject_style_into_parent_app()
    st.markdown(HIDE_SIDEBAR_NAV_HTML.strip(), unsafe_allow_html=True)
