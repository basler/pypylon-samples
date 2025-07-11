"""Sequencer Control Class for Basler Cameras Ace2/BoostR"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Literal

from pypylon import pylon as py

logging.basicConfig(level=logging.INFO)


@dataclass(frozen=True)
class SequencerTransition:
    """Dataclass to handle the Transitions between two sets,
    without rewriting it for every set
    """
    trigger_source: str = "Off"
    trigger_activation: Literal["NA", "RisingEdge", "FallingEdge", "AnyEdge", "LevelHigh", "LevelLow"] = "NA"

    def __repr__(self):
        """String representation of the SequencerTransition"""
        ta = "Event" if self.trigger_activation == "NA" else self.trigger_activation
        return f"{ta} on {self.trigger_source}"

@dataclass()
class SinglePathSet:
    """Dataclass to handle the Information of one Set of a sequence,
    configured with one path only"""
    feature_set: Dict[str, any]
    set_number: int
    name: str = ""
    next_set_number: int = None
    transition: SequencerTransition = SequencerTransition()

    def __post_init__(self):
        """Post init to ensure the next_set_number is set if not given"""
        if self.next_set_number is None:
            self.next_set_number: int = self.set_number + 1

    def __repr__(self):
        """String representation of the SinglePathSet"""
        if self.name == "":
            description = f"[{self.set_number}] (Features: {self.feature_set})"
        else:
            description = f"[{self.set_number}] (Name: {self.name})"

        return f"{description} switch to [{self.next_set_number}] if {self.transition}"


class CameraSequence:
    """This Class provides a list-like object to control the sequencer of a Basler camera"""

    def __init__(self, camera: py.InstantCamera):
        """Constructor

        :param camera: Instance of a Basler Camera
        """
        self._camera = camera
        try:
            self._camera.SequencerMode.Value = "Off"
        except py.LogicalErrorException as error:
            raise RuntimeError("The camera did not support sequencing!") from error

        self._sequence: List[SinglePathSet] = []

    def __getitem__(self, item):
        return self._sequence[item]

    def __len__(self):
        return len(self._sequence)

    def __iter__(self):
        return iter(self._sequence)

    def append(self, seq_set: SinglePathSet):
        """Append a new set to the sequence"""
        self._sequence.append(seq_set)

    def __delitem__(self, index):
        del self._sequence[index]

    def clear(self, only_cam=True):
        """Clear the sequencer settings
        Warning: use load defaults, most of the features will be set to initial state.

        :param only_cam: If True, only the camera will be changed, otherwise the stored sequencer will be reset, too.
        :return: None
        """
        cam = self._camera
        cam.SequencerMode.Value = "Off"
        cam.SequencerConfigurationMode.Value = "Off"
        cam.UserSetSelector.Value = "Default"
        cam.UserSetLoad.Execute()
        cam.SequencerConfigurationMode.Value = "On"
        cam.SequencerSetStart.Value = 0
        for set_number in range(cam.SequencerSetSelector.Max + 1):
            cam.SequencerSetSelector.Value = set_number
            for path in range(cam.SequencerPathSelector.Max + 1):
                cam.SequencerPathSelector.Value = path
                cam.SequencerSetNext.Value = 0
                cam.SequencerTriggerSource.Value = "Off"
            cam.SequencerPathSelector.Value = cam.SequencerPathSelector.Min
            cam.SequencerSetSave()
        cam.SequencerConfigurationMode.Value = "Off"
        logging.debug("Camera Sequencer cleared, default user set loaded")

        if not only_cam:
            self._sequence = []
            logging.debug("Internal Sequence cleared")

    def close_open_loops(self) -> int:
        """Close open end(s) to the lowest sequencer set

        :return: The amount of closed ends
        """

        ids = [seq.set_number for seq in self._sequence]
        closed_ends = 0
        for seq in self._sequence:
            if seq.next_set_number not in ids:
                logging.debug(f"Open loop in set {seq.set_number}")
                seq.next_set_number = min(ids)
                closed_ends += 1
        return closed_ends

    def configure(self, auto_close_loop=True):
        """Configure the sequencer inside the camera

        :param auto_close_loop: Close open ends automatically to the lowest sequencer set
        :return: None
        """
        if auto_close_loop:
            logging.debug(f"Close {self.close_open_loops()} loops implicit")

        cam = self._camera

        cam.SequencerMode.Value = "Off"
        cam.SequencerConfigurationMode.Value = "On"
        for item in self._sequence:
            item: SinglePathSet
            cam.SequencerSetSelector.Value = item.set_number
            cam.SequencerSetLoad.Execute()
            for key, value in item.feature_set.items():
                node = getattr(cam, key)
                if node is None:
                    raise ValueError(f"Feature {key} does not exist")
                try:
                    node.Value = value
                except Exception as e:
                    raise ValueError(f"Could not set feature {key}, due to error: {e}. May can't be in a set?") from e

            try:
                cam.SequencerSetNext.Value = item.next_set_number
                cam.SequencerTriggerSource.Value = item.transition.trigger_source
                if item.transition.trigger_activation != "NA":
                    cam.SequencerTriggerActivation.Value = item.transition.trigger_activation
            except Exception as e:
                raise ValueError(f"Could not set the requested transition {item.transition}, due to error: {e}") from e
            cam.SequencerSetSave.Execute()

        cam.SequencerConfigurationMode.Value = "Off"
        logging.debug(f"Sequencer configured with {len(self)} sequences")

    def activate(self):
        """Activate the sequencer mode of the camera
        Warning: This will block the access to all sequencable features!
        """
        self._camera.SequencerMode.Value = "On"
        logging.debug("Sequencer activated")

    def deactivate(self):
        """Deactivate the sequencer mode of the camera"""
        self._camera.SequencerMode.Value = "Off"
        logging.debug("Sequencer deactivated")

if __name__ == '__main__':
    my_cam = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
    my_cam.Open()

    # Example how to configure 3 Exposure Times, i.E. for HDR with the helper class

    sequence = CameraSequence(camera=my_cam)

    #  transition will change the sequencer to the next set
    # - if a software signal is triggerd (manual control)
    software_transition = SequencerTransition(trigger_source="SoftwareSignal1", trigger_activation="NA")
    # - if an exposure is started (change every frame)
    next_frame_transition = SequencerTransition(trigger_source="ExposureStart", trigger_activation="NA")

    # Setup three sets, remain in the "Medium" set until a software signal occur, than do a set with a "Low",
    # and a set with a "High" exposure time
    sequence.append(
        SinglePathSet(name="Medium", set_number=0, feature_set={"ExposureTime": 1000}, transition=software_transition))
    sequence.append(
        SinglePathSet(name="Low", set_number=1, feature_set={"ExposureTime": 100}, transition=next_frame_transition))
    sequence.append(
        SinglePathSet(name="High", set_number=2, feature_set={"ExposureTime": 5000}, transition=next_frame_transition))

    # By using auto close loop, we return into the "Medium" Set after leaving set: "High" automatically.
    # This could also be done by setting the next set in the SetConstructor, like:
    # SinglePathSet(name="High",
    #               set_number=2,
    #               next_set_number=0,
    #               feature_set={"ExposureTime": 5000},
    #               transition=next_frame_transition)
    sequence.configure(auto_close_loop=True)
    sequence.activate()
