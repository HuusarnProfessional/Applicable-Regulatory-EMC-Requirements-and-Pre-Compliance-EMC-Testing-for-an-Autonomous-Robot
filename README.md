# Identifying Applicable Regulatory EMC Requirements and Pre-Compliance EMC Testing for an Autonomous Robot
*Author: Hampus Huus*

## Introduction

Electromagnetic compatibility (EMC) is an important consideration when developing autonomous robotic systems, because such systems often combine several electronic functions that can generate both conducted and radiated electromagnetic disturbances. If these disturbances are not properly considered, they may cause unacceptable interference with other equipment in the intended environment. European Union regulatory requirements therefore exist to limit such interference, and failure to meet them may prevent the product from being placed on the market or, if already made available on the market, may lead to corrective actions such as withdrawal or even recall. This report investigates which European Union (EU) regulatory EMC requirements and harmonised standards are relevant for this type of system. Because full standard documents are typically licence-based and costly, the project focuses on pre-compliance instead, using a limited set of operating modes and a small number of measurements and mitigation experiments.

## System description and EMC-relevant hardware

The autonomous robot platform consists of two NiMH batteries connected in series and a control system built around a mainboard, four separate H-bridge PCBs, sensors, and wireless communication modules. An adjustable LM2596S-based switching regulator is connected directly after the batteries and provides the supply for the H bridge PCBs. The mainboard contains an STM32-based controller for motor control and sensor acquisition, an ESP32-based controller for higher-level communication, and an LMR36520 buck converter for the 3.3 V logic supply. The platform also includes a DWM1001 UWB module, an LSM9DS1 IMU, four AS5600 wheel-position sensors, and ultrasonic distance sensors, all of which are connected to the mainboard using ribbon cables.

### Encoders

The four AS5600 wheel-position sensors are read using 230 Hz PWM outputs. Each sensor is connected to the mainboard by an approximately 20 cm cable carrying 3.3 V, GND, and PWM. For later EMC analysis, the relevant output parameters from the datasheet [ref:as5600-datasheet] are a PWM slew rate of 0.5 to 2 V/$\mu$s and an output current of 0.5 mA. The corresponding rise-time-based frequency estimate is:

$$
f_r = \frac{dV/dt}{3.3} = \frac{0.5 \text{ to } 2}{3.3} = 152 \text{ to } 606 \mathrm{kHz}
$$

These values are an indication of the frequency range over which the encoder signal could still have a relevant amplitude.

The wavelength is:

$$
\lambda = \frac{c}{f} = \frac{299\,792\,458}{230} = 1\,303\,445.47 \mathrm{m}
$$

We know that the radiated power is

$$
P_{\mathrm{rad}} \propto \left(\frac{L}{\lambda}\right)^2 ]}
$$

This means

$$
P_{\mathrm{rad}} \propto \left(\frac{0.2}{1\,303\,445.47}\right)^2 = 2.35 \times 10^{-14}
$$

This is very low, meaning that EMC emissions from the encoder cables are very unlikely.

### IMU

The LSM9DS1 IMU is connected to the mainboard through an SPI interface with a ribbon cable that is at maximum 20cm. In the present design, the SPI clock is set by

$$
\frac{170 \mathrm{MHz}}{64} = 2.65625 \mathrm{MHz}
$$

The wavelength is

$$
\lambda = \frac{c}{f} = \frac{299\,792\,458}{2\,656\,250} = 112.86 \mathrm{m}
$$

This means

$$
P_{\mathrm{rad}} \propto \left(\frac{0.2}{112.86}\right)^2 = 3.14 \times 10^{-6} = 3.14 \mu\mathrm{W}
$$

The SPI clock frequency is known, but the slew rate of the SPI signals is not currently known. The slew rate must therefore be measured in order to estimate up to which harmonic numbers the SPI interface may still have relevant spectral amplitudes.

### Ultrasonic

The HC-SR04 ultrasonic sensor is connected to the mainboard through VCC, GND, Trigger, and Echo. The Trigger input is a TTL pulse of at least 10 $\mu$s, and the Echo output is a TTL pulse whose width is proportional to the measured distance. The module operates from 5 $\mathrm{V}$ with a typical working current of 15 $\mathrm{mA}$. The 40 $\mathrm{kHz}$ ultrasonic burst is generated internally by the module after the Trigger pulse, rather than being directly carried on the interface cable. The datasheet does not specify the rise time, fall time, or slew rate of the Trigger and Echo signals. For later radiated-EMC analysis, these edge rates must therefore be measured on the implemented hardware.

### Batteries

The platform is powered by two NiMH batteries connected in series. The batteries themselves are not expected to generate high frequency electromagnetic disturbances, since they are not switching circuits. From an EMC perspective, their main importance is instead that they supply the parts of the system that can generate disturbances, especially the motor drive and the switching regulators.

The battery cables can carry relatively large and rapidly changing currents when the motors change speed or direction. These current changes can create conducted voltage drops and current loops in the power wiring. The battery connection is therefore relevant for conducted EMC, even though the batteries themselves are not an active source of switching noise. Bulk capacitance placed close to the regulator and motor drive inputs can reduce these effects by providing a local energy reservoir, thereby reducing the transient current that must flow through the battery leads. However, bulk capacitance does not eliminate the problem completely, and its effectiveness depends on component choice and physical placement.

The battery wiring can be approximated as a current loop. If the motor current changes quickly, a voltage disturbance is produced by the parasitic inductance of the wiring:

$$
V_L = L \frac{\mathrm{d}i}{\mathrm{d}t}
$$

For a rough estimate, a straight wire has an inductance in the order of $1\,\mu\mathrm{H}/\mathrm{m}$. If the total battery supply and return path is assumed to be $0.4\,\mathrm{m}$, the loop inductance is approximately:

$$
L \approx 0.4\,\mu\mathrm{H}
$$

If the motor current changes by $2\,\mathrm{A}$ in $1\,\mu\mathrm{s}$, the induced voltage becomes:

$$
V_L = 0.4\,\mu\mathrm{H} \cdot \frac{2\,\mathrm{A}}{1\,\mu\mathrm{s}} = 0.8\,\mathrm{V}
$$

### Mainboard

The mainboard is the common PCB for the STM32 controller, ESP32 controller, sensor connectors, UWB connector, and motor-control connections. It also includes the LMR36520 buck converter for the 3.3 V logic supply. The individual circuits are described in later sections, so the EMC focus here is the routing on the mainboard and how the signal return currents are handled.

The mainboard carries several different signal types. The AS5600 encoder signals are captured as PWM signals at approximately $230\,Hz$. The motor control PWM signals are approximately $20\,kHz$. The DWM1001 UWB module communicates over UART at $115200\,baud$, and the UART between the ESP32 and STM32 also uses $115200\,baud$. The LSM9DS1 IMU is connected over SPI. In the present design the STM32 SPI clock is:

$$
f_{SPI} = \frac{170\,MHz}{64} = 2.65625\,MHz
$$

The nominal frequencies are therefore:

$$
f_{encoder} = 230\,Hz
$$

$$
f_{motorPWM} = 20\,kHz
$$

$$
f_{UART} \approx 115.2\,kHz
$$

$$
f_{SPI} = 2.65625\,MHz
$$

For the mainboard traces themselves, these frequencies are not high enough to make a short PCB trace an efficient radiator by length alone. This can be checked using the wavelength relation:

$$
\lambda = \frac{v}{f}
$$

This relation is used when discussing electrical dimensions, where the important quantity is conductor length compared with wavelength rather than physical length alone. For the highest nominal mainboard signal frequency, $2.65625\,MHz$, the wavelength is:

$$
\lambda_{SPI} = \frac{3 \cdot 10^8}{2.65625 \cdot 10^6} = 112.9\,m
$$

For a typical $50\,mm$ mainboard trace this gives:

$$
\frac{L}{\lambda} = \frac{0.05}{112.9} = 4.43 \cdot 10^{-4}
$$

This is far below $0.1\lambda$, which Paul et al. use as a rule of thumb for when a structure can be treated as electrically small [ref:paul-emc]. Therefore, the SPI trace length itself is not expected to be the dominant radiated-emission problem. The encoder PWM, motor PWM logic signal, and UART traces have even lower nominal frequencies, so their wavelength-based trace-length risk is lower than the SPI case.

This does not mean that the mainboard layout is irrelevant. Paul et al. also describe that digital signals contain high-frequency components depending on rise and fall time, and that PCB design must control return paths and loop areas [ref:paul-emc]. Therefore, the important mainboard issue is not the nominal frequency alone, but whether the outgoing trace and its return current stay close together. If a signal trace crosses a weak or broken ground return, the return current must take a longer path. This increases loop area and can increase magnetic coupling and radiated emission.

The pre-compliance measurements for the mainboard should therefore focus on signal quality and coupling, rather than treating the short PCB traces as antennas.

The main EMC concern on the mainboard is therefore the LMR36520 buck layout rather than the short logic traces. The buck has a local high-frequency current loop between the input capacitor, the switching path, ground, and back to the input capacitor. This loop should be kept small, because loop inductance creates voltage disturbance when the current changes quickly:

$$
V_L = L \frac{di}{dt}
$$

For this mainboard, the return path is made with copper pours and several vias instead of a continuous ground plane. This makes via placement important, especially around the buck. The input capacitor is placed close to the buck, and the buck ground return to the input capacitor ground through several nearby vias instead of one shared narrow return path. This reduces common impedance and local ground bounce in the switching current path.

The SW node copper area should be kept small, because it has the fastest voltage transitions on the mainboard. The SW node should also be kept away from SPI, UART, encoder, UWB, and feedback traces. This follows the PCB EMC guidance in Paul et al., where return-current path, ground grid/vias, power distribution, and loop area are treated as key layout factors.

### H-bridge PCBs

The robot uses four separate self designed H bridge PCBs for motor driving. Each full bridge is built from two half bridges, using IRS2008S gate drivers and IPD220N06L3GATMA1 N channel MOSFETs. The IRS2008S is a high and low side MOSFET driver, while the IPD220N06L3GATMA1 is a 60 V power MOSFET. This makes the H bridge PCBs one of the more important EMC risk areas in the AGV, because they combine fast gate drive, MOSFET switching, motor current, and external motor wiring.

The motor PWM frequency is approximately $20\,kHz$. This frequency is not the main radiated concern by itself. The larger EMC risk comes from the switching edges and the current loop formed by the H bridge, motor cable, motor winding, and return path. These loops can create radiated emissions, while the same switching current can also create conducted disturbances on the supply wiring.

### LM2596S-based switching regulator

The LM2596S-based switching regulator is a purchased buck module used between the batteries and the H bridge PCBs and mainboard. Like the LMR36520, the regulator IC itself is considered a lower-probability EMC problem than the surrounding power wiring and implementation, since it is a commercial regulator IC rather than a self-designed switching stage. It is still notable that the module switches at approximately $150\,kHz$, which can create conducted ripple on the supply wiring.

### STM32-based controller

The STM32-based controller uses an STM32G474RE microcontroller. This is a commercial microcontroller from STMicroelectronics, not a self-designed digital circuit. According to the datasheet, the STM32G474RE can operate at up to $170\,MHz$. This makes it one of the highest-frequency digital devices in the AGV, and therefore EMC relevant even though the controller itself is not expected to be the same type of emission source as the motor drive or switching regulators.

### ESP32-based controller

The ESP32 based controller uses an ESP32 WROOM 32 module. The module contains the ESP32 microcontroller and the RF parts needed for 2.4 GHz WiFi and Bluetooth communication. In this project, the ESP32 runs at $240\,MHz$, which makes it one of the highest frequency digital components in the AGV.

The ESP32 is used for Bluetooth communication and for UART communication with the STM32 at $115200\,baud$. The UART interface is not expected to be a dominant emission source by frequency, but the ESP32 module is still EMC relevant because it contains both a high frequency digital controller and a 2.4 GHz radio.

The radio regulatory part is outside the scope of this report. In the emission analysis, Bluetooth activity is therefore treated separately from the unintentional emissions of the AGV electronics. Emissions around $2.4\,GHz$ are expected from the ESP32 Bluetooth radio when it is active, while the motor drive, buck regulators, and wiring are treated as the relevant sources for unintentional emissions.

### LMR36520 buck converter

The LMR36520 is a documented commercial synchronous buck regulator from Texas Instruments, not a self-designed switching stage. According to the datasheet, it includes integrated high side and low side MOSFETs, internal compensation, and operates as a 4.2 V to 65 V, 2 A step down converter. The datasheet does not state that the IC itself meets EU EMC emission limits, and the responsibility for meeting EMC requirements is still on the final AGV product.

Nevertheless, since the LMR36520 is a commercial IC from a major semiconductor manufacturer and is intended to be used in many different products, it is reasonable to assume that the IC itself is less likely to be the main EMC problem than the surrounding buck implementation. For this project, the more probable EMC problem areas are therefore the PCB layout around the buck, especially the input loop, SW node, inductor, output capacitors, and return path.

### DWM1001 UWB module

The DWM1001 UWB module is a commercial radio module used for global positioning. Since the regulatory radio part, such as EU RED compliance for the UWB transmitter, is outside the scope of this project, the UWB module is not connected during the pre-compliance emission measurements.

## Intended environment and practical classification

The AGV is intended to operate as an autonomous parking robot in an indoor parking garage. The parking garage is intended to be fully automated, meaning that the customer leaves the vehicle at an entrance area before the AGV picks it up and parks it inside the garage. The robot is therefore not intended to operate freely in a normal public area with pedestrians around it, but in a controlled area inside the parking facility.

This makes the intended environment a light industrial environment in this project. The parking facility is a commercial service, but the robot operates in a restricted technical area where automated equipment is expected to be used. The environment is therefore more demanding than a normal office or home environment, but it is probably not treated as a heavy industrial environment such as a factory, welding area, or production line.

For this reason, the AGV is practically classified in this report as equipment intended for a light industrial indoor environment.

## Applicable standards and how they are identified

To identify the applicable harmonised EMC emission standards, the European Commission webpage for harmonised standards under the EMC Directive 2014/30/EU was used as the starting point. This page provides a ``Summary list of titles and references of harmonised standards under Directive 2014/30/EU for EMC'', available as a downloadable PDF or spreadsheet. The summary list contains, among other information, the reference number of each standard and the title of the standard.

The list was first reviewed by comparing the standard titles with the intended environment and function of the AGV. some candidates are: The following candidate standards were selected from the summary list for further comparison:

**Candidate harmonised EMC standards selected from the summary list under Directive 2014/30/EU.**

| **Standard** | **Title in the summary list** | **Reason for inclusion** |
| --- | --- | --- |
| EN 61800-3:2004+A1:2012 | Adjustable speed electrical power drive systems, Part 3: EMC requirements and specific test methods | Relevant because the AGV contains motor drive electronics. It is included as a technology-related candidate, but it may only apply to the drive system rather than the complete AGV. |
| EN 61000-6-3:2007+A1:2011 | Electromagnetic compatibility (EMC), Part 6-3: Generic standards, Emission standard for residential, commercial and light-industrial environments | Relevant as a generic emission candidate because the intended environment has been classified as light industrial. |
| EN 61000-6-4:2007+A1:2011 | Electromagnetic compatibility (EMC) - Part 6-4: Generic standards - Emission standard for industrial environments | Relevant as the second generic emission candidate. It is included for comparison because the AGV operates in a technical automated environment, although the environment is probably not treated as heavy industrial. |
| EN 14010:2003+A1:2009 | Safety of machinery, Equipment for power driven parking of motor vehicles, Safety and EMC requirements for design, manufacturing, erection and commissioning stages | Relevant as the strongest product-related candidate because the AGV is intended for automated parking of motor vehicles. |

The best fit is EN 14010:2003+A1:2009, *Safety of machinery --- Equipment for power driven parking of motor vehicles --- Safety and EMC requirements for design, manufacturing, erection and commissioning stages*.

As this standard is lincence based it cant be refrence direclty but EN 14010 does not itself conatain EMC standard instead it stats that: "The electromagnetic disturbances generated by the power driven parking equipment shall not exceed the levels specified in generic emission standard EN 61000-6-3"

There for focus will be on EN 61000-6-3, *Electromagnetic compatibility (EMC), Part 6-3: Generic standards, Emission standard for residential, commercial and light-industrial environments*.

Since EN 61000-6-3 standard also is licence-based, this test report does not claim formal conformity with the standard. The standard cant be used directly, instead it is used only as a practical pre-compliance reference, and the numerical limits used in the measurements are taken from publicly available secondary sources that reference EN 61000-6-3.

**Secondary sources used for practical radiated-emission reference limits.**

| **Frequency range** | **Limit** | **Page / section** | **Source** |
| --- | --- | --- | --- |
| $30\,MHz$ to $230\,MHz$ | $40\,dB\mu V/m$ QP at $3\,m$ | p. 4, standards table | Crouzet official datasheet, IEC 61000-6-3 / IEC 61000-6-4, CISPR 16-2-3 [crouzet_timer_datasheet] |
| $230\,MHz$ to $1000\,MHz$ | $47\,dB\mu V/m$ QP at $3\,m$ | p. 4, standards table | Crouzet official datasheet, IEC 61000-6-3 / IEC 61000-6-4, CISPR 16-2-3 [crouzet_timer_datasheet] |
| $30\,MHz$ to $230\,MHz$ | $40\,dB\mu V/m$ QP at $3\,m$ | p. 2, EMC table | OEM Automatic Sweden / Crouzet datasheet, IEC 61000-6-3 / IEC 61000-6-4, CISPR 16-2-3 [oem_crouzet_datasheet] |
| $230\,MHz$ to $1000\,MHz$ | $47\,dB\mu V/m$ QP at $3\,m$ | p. 2, EMC table | OEM Automatic Sweden / Crouzet datasheet, IEC 61000-6-3 / IEC 61000-6-4, CISPR 16-2-3 [oem_crouzet_datasheet] |

## Method and measurement plan

## Pre-compliance measurements and results

## Mitigation actions and evaluation

## Discussion

AI-assisted search was used as a support tool for locating possible public secondary sources, as this deviates from the official way of accessing the standard.

AI-assisted search was used as a support tool for locating possible public secondary sources, as this deviates from the official way of accessing the standard. AI-assistens was also use for spelling and latex formating.

## Conclusions and future work

## References

1. Paul, Clayton R., Scully, Robert C., and Steffka, Mark A., *Introduction to Electromagnetic Compatibility*, 3rd ed., Wiley, 2022.
2. European Commission, ``Electromagnetic Compatibility (EMC) Directive'': [single-market-economy.ec.europa.eu/.../electromagnetic-compatibility-emc-directive_en](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/electromagnetic-compatibility-emc-directive_en)
3. [AS5600 datasheet (look.ams-osram.com)](https://look.ams-osram.com/m/7059eac7531a86fd/original/AS5600-DS000365.pdf?) AI-assisted search was used as a support tool for locating possible public secondary sources, as this deviates from the official way of accessing the standard. AI-assistens was also use for spelling and latex formating.

> This README is generated from the LaTeX source files. Edit the `.tex` files, not this document.
