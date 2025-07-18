"""Tests for pypylon contrib sequencer module."""

from unittest.mock import Mock


def test_sequencer_module_import():
    """Test that sequencer module and classes can be imported."""
    from pypylon.contrib.sequencer.sequencer import CameraSequence, SequencerTransition, SinglePathSet

    assert SequencerTransition is not None
    assert SinglePathSet is not None
    assert CameraSequence is not None


def test_sequencer_transition_creation():
    """Test SequencerTransition creation and basic functionality."""
    from pypylon.contrib.sequencer.sequencer import SequencerTransition

    # Default values
    transition = SequencerTransition()
    assert transition.trigger_source == "Off"
    assert transition.trigger_activation == "NA"

    # Custom values
    transition2 = SequencerTransition(trigger_source="SoftwareSignal1", trigger_activation="RisingEdge")
    assert transition2.trigger_source == "SoftwareSignal1"
    assert transition2.trigger_activation == "RisingEdge"


def test_single_path_set_creation():
    """Test SinglePathSet creation and auto-increment behavior."""
    from pypylon.contrib.sequencer.sequencer import SinglePathSet

    path_set = SinglePathSet(feature_set={"ExposureTime": 1000}, set_number=0)

    assert path_set.feature_set == {"ExposureTime": 1000}
    assert path_set.set_number == 0
    assert path_set.next_set_number == 1  # Auto-increment


def test_camera_sequence_basic_operations():
    """Test CameraSequence basic list operations."""
    from pypylon.contrib.sequencer.sequencer import CameraSequence, SinglePathSet

    # Mock camera
    mock_camera = Mock()
    mock_camera.SequencerMode = Mock()
    mock_camera.SequencerMode.Value = "Off"

    sequence = CameraSequence(camera=mock_camera)

    # Test initial state
    assert len(sequence) == 0

    # Test append
    path_set = SinglePathSet(feature_set={"ExposureTime": 1000}, set_number=0)
    sequence.append(path_set)
    assert len(sequence) == 1
    assert sequence[0] == path_set
