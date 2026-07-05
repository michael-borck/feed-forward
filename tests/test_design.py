"""Tests for the design-tokens module (shape + button composition)."""

from app.utils import design

# ---- tokens have the expected keys ----


def test_colour_has_primary_accent_and_wordmark_tokens():
    required = {
        "primary",
        "primary_hover",
        "primary_subtle",
        "accent",
        "accent_hover",
        "accent_subtle",
        "surface",
        "surface_alt",
        "text_strong",
        "text_body",
        "text_muted",
        "border",
        "danger",
        "danger_hover",
        "wordmark_first",
        "wordmark_second",
        "wordmark_first_dark",
        "wordmark_second_dark",
    }
    assert required <= set(design.COLOR)


def test_text_scale_has_hero_h1_h2_h3_body_meta_numeric():
    required = {"hero", "h1", "h2", "h3", "body", "body_sm", "meta", "numeric"}
    assert required <= set(design.TEXT)


def test_pad_and_gap_share_size_keys():
    assert set(design.PAD) >= {"xs", "sm", "md", "lg", "xl"}
    assert set(design.GAP) >= {"xs", "sm", "md", "lg"}


def test_density_tokens_are_tight():
    """Density audit found pages overflowed — these tokens are the fix."""
    # Body padding shrunk from py-16 to py-6 (single biggest density win).
    assert design.BODY_VPAD == "py-6"
    assert design.DASHBOARD_BODY_PAD == "p-4"
    # Default card padding is 4 (was 6).
    assert design.PAD["md"] == "4"


def test_single_radius_value():
    # Editorial direction (2026-07): one small radius everywhere.
    assert design.RADIUS == "rounded"
    assert design.RADIUS_PILL == "rounded-full"


def test_editorial_has_no_shadows():
    """Editorial depth comes from hairlines, never shadows."""
    assert design.SHADOW_REST == "shadow-none"
    assert design.SHADOW_HOVER == "shadow-none"
    assert "shadow" not in design.button_classes()


def test_editorial_serif_display_and_label_token():
    """Headings are serif (Fraunces); the small-caps label is a core token."""
    for key in ("hero", "h1", "h2", "h3"):
        assert "font-serif" in design.TEXT[key], key
    assert "uppercase" in design.TEXT["label"]
    assert "tracking-" in design.TEXT["label"]


# ---- button_classes composition ----


def test_button_classes_primary_default():
    out = design.button_classes()
    # Base + medium size + primary intent (editorial: small-caps rectangle)
    assert "inline-flex" in out
    assert "px-5 py-2.5" in out
    assert f"bg-{design.COLOR['primary']}" in out
    assert "uppercase" in out
    assert design.RADIUS in out


def test_button_classes_secondary_uses_border_not_fill():
    out = design.button_classes(intent="secondary")
    assert f"border-{design.COLOR['primary']}" in out
    assert "bg-transparent" in out


def test_button_classes_ghost_has_no_background_at_rest():
    out = design.button_classes(intent="ghost")
    assert "bg-" not in out.split(f"text-{design.COLOR['primary']}")[0]


def test_button_classes_danger_uses_red():
    out = design.button_classes(intent="danger")
    assert f"bg-{design.COLOR['danger']}" in out


def test_button_classes_size_sm_smaller_than_md():
    sm = design.button_classes(size="sm")
    md = design.button_classes(size="md")
    assert "px-3" in sm and "py-1.5" in sm
    assert "px-5" in md and "py-2.5" in md


def test_button_classes_unknown_intent_falls_back_to_primary():
    fallback = design.button_classes(intent="nonsense")
    primary = design.button_classes(intent="primary")
    # Same intent classes appended; nothing raises.
    assert f"bg-{design.COLOR['primary']}" in fallback
    assert fallback == primary


def test_button_classes_unknown_size_falls_back_to_md():
    assert design.button_classes(size="zzz") == design.button_classes(size="md")
