"""Tests for pypylon contrib namespace."""


def test_contrib_namespace_accessible():
    """Test that contrib namespace can be accessed."""
    import pypylon.contrib

    assert pypylon.contrib is not None
