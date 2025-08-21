![pypylon](docs/images/Pypylon_grey_RZ_400px.png "pypylon")

Sample applications and jupyter notebooks using the official python wrapper for the Basler pylon Camera Software Suite.

This is a companion repository to [pypylon](https://github.com/basler/pypylon)

**Please Note:**
This project is offered with no technical support by Basler AG.
You are welcome to post any questions or issues on [GitHub](https://github.com/basler/pypylon-samples) or on [ImagingHub](https://www.imaginghub.com).

# Overview

 * Some of the content was part of the Basler webinar about pypylon. You can watch this to get more in depth information about pylon SDK and pypylon.
 Please check for the recording at [Basler PyPylon Webinar](https://www.baslerweb.com/en/learning/pypylon/)
 * As the feature names of basler cameras differ slightly between e.g. Basler ace USB and Basler ace GEV, it is noted at the samples or notebooks for which camera family the sample applies.
 * The python requirements to run the jupyter notebooks and samples are listed in [requirements.txt](requirements.txt)


## Basic Examples (pypylon only)

These examples use only the basic pypylon library and can be run without additional dependencies.

### Notebooks

1. Device enumeration and configuration basics
   [deviceenumeration_and_configuration](notebooks/basic-examples/deviceenumeration_and_configuration.ipynb)

2. Demonstration of different grab strategies
   [grabstrategies](notebooks/basic-examples/grabstrategies.ipynb)

3. How to handle multicamera setups in pypylon
   [multicamera](notebooks/basic-examples/multicamera_handling.ipynb)

4. Using hardware trigger and access image chunks ( USB )
   [hw_trigger_and_chunks](notebooks/basic-examples/USB_hardware_trigger_and_chunks.ipynb)

5. Low overhead image capturing in a virtual line scan setup and display in notebook ( USB )
   [USB_linescan_performance_demo_opencv_notebook](notebooks/basic-examples/USB_linescan_performance_demo_opencv.ipynb)

6. Exposure bracketing using the sequencer feature of ace devices ( USB)
   [USB_HDR_exposure_sequencer](notebooks/basic-examples/USB_hdr_exposure_bracketing_using_sequencer.ipynb)

7. Exposure bracketing using the sequencer feature of ace2/boost-R devices ( USB)
   [USB_Ace2_BoostR_HDR_exposure_sequencer](notebooks/basic-examples/Ace2_USB_hdr_exposure_bracketing_using_sequencer.ipynb)

8. Full HDR multi-exposure example
   [full_HDR_multiexposure_example](notebooks/basic-examples/full_HDR_multiexposure_example.ipynb)

## Contrib Examples (pypylon-contrib required)

These examples require the pypylon-contrib library which provides additional utilities and helper functions. Install it using:
```bash
pip install pypylon-contrib
```

### Notebooks

1. **Sequencer utilities** - Simplified interface for camera sequencer configuration
   [sequencer](notebooks/contrib-examples/sequencer.ipynb)

   Demonstrates how to use the SequencerUtils from pypylon-contrib to easily configure camera sequences with the CameraSequence, SinglePathSet, and SequencerTransition classes.

2. **Serial communication** - Communication with serial devices connected to Basler cameras
   [serial_communication](notebooks/contrib-examples/serial_communication.ipynb)

   Shows how to use the BaslerSerial class to communicate with serial devices connected to a Basler camera, enabling control of external hardware through the camera's serial interface.


# Development

Pull requests to pypylon-samples are very welcome.
e.g. generic samples that demonstrate interaction with GUI toolkits, as we typically only use Qt.

# Known Issues
 * info table missing that clearly identifies which samples work for which camera model
