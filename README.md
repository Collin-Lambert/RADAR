# Setup

To install on a linux machine, change the permissions of both "install.sh" and "run.sh" by running `sudo chmod +x install.sh`
Next, install by running `sudo ./install.sh`

# Run

To run, run `sudo ./run.sh`



# MMWave Radar User Manual

#### SFT-004, Rev A
#### April 2025

## Table of Contents

<ul>

<li>Overview
<li>Quick Start Guide
<li>Software Installation
<li>Hardware Specifications
<li>Safety
<li>Troubleshooting

</ul>

## Overview

The millimeter wave radar system is designed to measure the velocity of projectiles of at least 7.62mm diameter travelling between 30m/s and 2000m/s within 5% resolution at a distance of at least half a meter. 

## Quick Start Guide

To turn on the radar, follow the steps below.

1. Install the radar software using the bash script or by following the detailed guide under the software installation section.

1. Place the radar with the antenna pointing toward or away from what you want to measure.

2. Plug the radar into 120VAC power.

3. Flip the red power switch on the back, the switch should light up, and the radar LED should turn on red. 

4. Connect the radar to the computer using a USB 3.0 cable. Do not use a USB 2.0 cable or the drivers for the radar may get corrupted. If this is the case, refer to the troubleshooting guide for instructions on how to reinstall the drivers.

5. If using a hardware trigger, connect a BNC cable to the port on the outside of the radar. 

7. Flip the black Radar Switch to On. The LED on the radar will turn Blue for a short time, then turn green. When the LED is green, the radar is on and radiating. See the Safety section for guidelines on radar emmisions. 

To use the radar, follow the steps below.

6. Open the radar software, a GUI will open up with prefilled value for radar parameters. 

8. In the Software, when ready to use the radar, press the "ARM" button. This starts the radar software. 

9. To trigger the radar, press the "Manual Trigger" button or assert an external trigger. This will continue to run the radar for a bit, and then save the buffer to a file. This ensures that data is captured both before and after the event. If the "Show Spectrogram" checkbox is checked, a spectrogram of the recorded data will be shown. The highest speed will be shown in the "Max Velocity" textbox. 

To turn off the radar, follow the steps below. 

1. Turn off the radar emission by flipping the black radar switch. The LED should turn red. 

2. Close the radar software.

3. Unplug the USB 3.0 cable from the radar. 

4. Flip the the red power switch to turn off the radar. 

5. Unplug the radar from the 120VAC power if desired.

## Software Installation

There are two methods to install the software:

<ol>
<li>Run the bash script provided on GitHub
<li>Install the dependencies separately (refer to software artifacts for further details)
</ol>

## Hardware Specifications

The radar is contained in an electrical box, with each part assembled according to the attached hardware artifacts. The power and data connections are located on one side of the box, with a wall-power connection and BNC connector for an input signal. The aperture for the horn antennae is located on the other side. See hardware artifacts for further details and specifications.

## Safety

Remain at least 25.4cm (10 inches) from the antennae while the device is powered on. Refer to REQ-004 for a brief Safety Memo.

## Troubleshooting

<table>
    <thead>
        <tr>
            <th>Issue</th>
            <th>Cause</th>
            <th>Solution</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan=4>No object detected on spectrogram, detected top speed is obviously inaccurate</td>
            <td>Radar is not powered on, or power-on sequence was not completed</td>
            <td>Ensure radar is powered on and LED indicator is green</td>
        </tr>
        <tr>
            <td>Radar is not transmitting a signal at time of test</td>
            <td>Ensure radar is armed before firing</td>
        </tr>
        <tr>
            <td rowspan=2>Object is moving too fast, radar cannot get enough data to properly analyze Doppler shift</td>
            <td>Increase sample rate</td>
        </tr>
        <tr>
            <td>Increase gain</td>
        </tr>
        <tr>
            <td>Object is detected on spectrogram, but detected top speed is obviously inaccurate</td>
            <td>DSP script is diluting target frequency over too many frequency bins, reducing power of target signal</td>
            <td>Decrease FFT bin size</td>
        </tr>
        <tr>
            <td>Input is overfilled and clips, output is saturated</td>
            <td>Gain is too high</td>
            <td>Decrease gain</td>
        </tr>
    </tbody>
</table>
