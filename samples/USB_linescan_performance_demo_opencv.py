import pypylon.pylon as py
import numpy as np
import cv2

# this sample has been tested with a Basler acA1920-155uc
# type 'q' or 'ESC' in the window to close it

# the camera is configured to run at high framerate with only two lines hight
# the acquired rows are concatenated as a virtual frame and this frame is displayed

SCANLINE_HEIGHT = 2
VIRTUAL_FRAME_HEIGHT = 1000

tlf = py.TlFactory.GetInstance()

cam = py.InstantCamera(tlf.CreateFirstDevice())
cam.Open()

# setup center scan line
cam.Height = SCANLINE_HEIGHT
cam.Width = cam.Width.Max
cam.CenterX = True
cam.CenterY = True

# setup for
cam.PixelFormat = "BGR8"
cam.Gain = 20
cam.ExposureTime = 900
print("Resulting framerate:", cam.ResultingFrameRate.Value)

cam.StartGrabbing()

img = np.ones((VIRTUAL_FRAME_HEIGHT, cam.Width.Value, 3), dtype=np.uint8)
missing_line = np.ones(
    (SCANLINE_HEIGHT, cam.Width.Value, 3), dtype=np.uint8)*255
image_idx = 0
while True:
    for idx in range(VIRTUAL_FRAME_HEIGHT // SCANLINE_HEIGHT):
        with cam.RetrieveResult(2000) as result:
            if result.GrabSucceeded():
                with result.GetArrayZeroCopy() as out_array:
                    img[idx * SCANLINE_HEIGHT:idx *
                        SCANLINE_HEIGHT + SCANLINE_HEIGHT] = out_array
            else:
                img[idx * SCANLINE_HEIGHT:idx * SCANLINE_HEIGHT +
                    SCANLINE_HEIGHT] = missing_line
                print(idx)

    img_rgb = img

    # Display the resulting frame
    cv2.imshow('Linescan View', img_rgb)

    image_idx += 1
    if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
        break

# When everything done, release the capture
cam.StopGrabbing()
cv2.destroyAllWindows()

cam.Close()
