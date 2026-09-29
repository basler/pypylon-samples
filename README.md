<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/pylon_basler_banner_dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/images/pylon_basler_banner.svg">
  <img alt="Basler pypylon banner" src="https://raw.githubusercontent.com/basler/pypylon-samples/main/docs/images/pylon_basler_banner.svg">
</picture>

<br>

Sample applications, Jupyter notebooks, and contrib utilities using [pypylon](https://github.com/basler/pypylon), the official Python language binding for the [Basler pylon C++ APIs](https://docs.baslerweb.com/pylonapi/cpp).

This is a companion repository to pypylon. The examples cover camera configuration, image acquisition, triggering, sequencers, and serial communication.

[![Build Status](https://github.com/basler/pypylon-samples/actions/workflows/build_and_test.yml/badge.svg?branch=main)](https://github.com/basler/pypylon-samples/actions/workflows/build_and_test.yml)

# Getting Started

The pypylon Programmer's Guide is available in the [Basler Product Documentation](https://docs.baslerweb.com/pypylon-introduction) and on [GitHub](https://github.com/basler/pypylon/tree/master/docs/programmers_guide).

1. Install [Python](https://www.python.org/) with pip. Installing the [pylon Software Suite](https://www.baslerweb.com/pylon) is also recommended; some camera interfaces require additional drivers. See the [pypylon installation instructions](https://github.com/basler/pypylon#installation) for platform and camera requirements.
2. Clone this repository and install the notebook dependencies:

   ```console
   git clone https://github.com/basler/pypylon-samples.git
   cd pypylon-samples
   python -m pip install -r requirements.txt
   ```

3. For example, start JupyterLab and open a notebook from the overview below:

   ```console
   jupyter lab
   ```

For the contrib examples, also install [pypylon-contrib](#contrib-examples-pypylon-contrib-required).

> **Note:** Camera features and names vary between models and interfaces. Check the requirements in each notebook before running it. Samples may not always reflect the latest pypylon API or coding style; refer to the [pypylon samples](https://github.com/basler/pypylon/tree/master/samples) and [changelog](https://github.com/basler/pypylon/blob/master/changelog.txt) for current guidance.

# Overview

 * Some of the content was part of the Basler webinar about pypylon. You can watch this to get more in depth information about pylon SDK and pypylon.
 Please check for the recording at [Basler PyPylon Webinar](https://www.baslerweb.com/en/learning/pypylon/)
 * The Python requirements to run the Jupyter notebooks and samples are listed in [requirements.txt](requirements.txt).


## Basic Examples (pypylon only)

These examples use pypylon directly and do not require pypylon-contrib. Notebook, visualization, and image-processing dependencies are included in [requirements.txt](requirements.txt).

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
```console
python -m pip install pypylon-contrib
```

### Notebooks

1. **Sequencer utilities** - Simplified interface for camera sequencer configuration
   [sequencer](notebooks/contrib-examples/sequencer.ipynb)

   Demonstrates how to configure camera sequences using the `CameraSequence`, `SinglePathSet`, and `SequencerTransition` classes from pypylon-contrib.

2. **Serial communication** - Communication with serial devices connected to Basler cameras
   [serial_communication](notebooks/contrib-examples/serial_communication.ipynb)

   Shows how to use the BaslerSerial class to communicate with serial devices connected to a Basler camera, enabling control of external hardware through the camera's serial interface.


# Development

Pull requests to pypylon-samples are very welcome.
e.g. generic samples that demonstrate interaction with GUI toolkits, as we typically only use Qt.

To work on the contrib utilities, install the local package with development and notebook dependencies:

```console
python -m pip install -e ".[dev,notebook]"
```

Run the unit tests with:

```console
python -m pytest tests
```

# Known Issues
 * info table missing that clearly identifies which samples work for which camera model

# Support

You are welcome to post any questions or issues on GitHub. For questions or issues related to these samples or the contrib utilities, 
please use [pypylon-samples issues](https://github.com/basler/pypylon-samples/issues). For issues with pypylon itself, please use [pypylon issues](https://github.com/basler/pypylon/issues).
For additional technical support for business customers, please reach out to our official [Support](https://www.baslerweb.com/en/support/contact) team.
