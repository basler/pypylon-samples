![pypylon](docs/images/Pypylon_grey_RZ_400px.png "pypylon")

Sample applications and jupyter notebooks using the official python wrapper for the Basler pylon Camera Software Suite.

This is a companion repository to [pypylon](https://github.com/basler/pypylon)

**Please Note:**
This project is offered with no technical support by Basler AG.
You are welcome to post any questions or issues on [GitHub](https://github.com/basler/pypylon-samples) or on [ImagingHub](https://www.imaginghub.com).

# Overview

 * Some of the content was part of the Basler webinar about pypylon. You can watch this to get more in depth information about pylon SDK and pypylon.
 Please check for the recording at [Basler PyPylon Webinar](https://www.baslerweb.com/en/company/news-press/webinar/pypylon-python-open-source-interface-emea/)
 * As the feature names of basler cameras differ slightly between e.g. Basler ace USB and Basler ace GEV, it is noted at the samples or notebooks for which camera family the sample applies.
 * The python requirements to run the jupyter notebooks and samples are listed in [requirements.txt](requirements.txt)
 

## Samples

1. Low overhead image capturing in a virtual line scan setup
   [USB_linescan_performance_demo_opencv](samples/USB_linescan_performance_demo_opencv.py)
   

## Notebooks

1. Device enumeration and configuration basics
   [deviceenumeration_and_configuration](notebooks/deviceenumeration_and_configuration.ipynb)
   
2. Demonstration of different grab strategies
   [grabstrategies](notebooks/grabstrategies.ipynb)

3. How to handle multicamera setups in pypylon
   [multicamera](notebooks/multicamera_handling.ipynb)

4. Using hardware trigger and access image chunks ( USB )
   [hw_trigger_and_chunks](notebooks/USB_hardware_trigger_and_chunks.ipynb)

5. Low overhead image capturing in a virtual line scan setup and display in notebook ( USB )
   [USB_linescan_performance_demo_opencv_notebook](notebooks/USB_linescan_performance_demo_opencv.ipynb)

6. Exposure bracketing using the sequencer feature of ace devices ( USB)
   [USB_HDR_exposure_sequencer](notebooks/USB_hdr_exposure_bracketing_using_sequencer.ipynb)

7. Exposure bracketing using the sequencer feature of ace2/boost-R devices ( USB)
   [USB_HDR_exposure_sequencer](notebooks/Ace2_USB_hdr_exposure_bracketing_using_sequencer.ipynb)


# Development

Pull requests to pypylon-samples are very welcome. 
e.g. generic samples that demonstrate interaction with GUI toolkits, as we typically only use Qt.

# Known Issues
 * info table missing that clearly identifies which samples work for which camera model
