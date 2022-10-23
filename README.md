# Quetzal-1 Telemetry

<p align="center">
<img width="300" src="./media/quetzal_1_badge.png">
</p>

For an overview of Quetzal-1, [read our profile!](https://github.com/Quetzal-1-CubeSat-Team)

## Directory Description

This repository serves as the central location for all data transmitted by the Quetzal-1 satellite, including telemetry and all downlinked photos!

The files are organized as follows:

1. [data/telemetry](./data/telemetry/): contains all the telemetry for Quetzal-1. For an explanation of each variable, see [the README](./data/telemetry/README.md) within this directory.
2. [data/photos](./data/photos/): contains all the photos downloaded from Quetzal-1. For background information on each image, see [the README](./data/photos/README.md) within this directory.
3. [media](./media/): contains miscellanous images used throughout this repository.

## Visualizing this data

Data is cool, but what about those sweet, sweet graphs? :grin:

During its operations phase, all data was aggregated by the wonderful [SatNOGS](https://satnogs.org/) network. With the help of their amazing collaborators and volunteers, especially [DL4PD](https://github.com/DL4PD), we were able to setup a live telemetry dashboard on their site! Check it out [here](https://dashboard.satnogs.org/d/js5kQceWz/quetzal-1-telemetry).

## How does this relate to [gr-quetzal1](https://github.com/danalvarez/gr-quetzal1)?

The gr-quetzal1 repository contains the receivers and transmitters that were developed internally (using GNURadio and the wonderful [gr-satellites](https://github.com/daniestevez/gr-satellites)) to communicate with Quetzal-1. It's what we used on a day-to-day basis to issue commands to the satellite and process incoming data.

However, all data visualized in the aforementioned SatNOGS dashboard is decoded via the satnogs decoder, available in [the satnogs-decoders repository](https://gitlab.com/librespacefoundation/satnogs/satnogs-decoders/-/blob/master/ksy/quetzal1.ksy). The result of the decoder is the same, but the definition is far more standard, using [Kaitai](https://kaitai.io/) structs. Also, [Daniel Estevez](https://github.com/daniestevez) wrote a [SatYAML file](https://gr-satellites.readthedocs.io/en/latest/satyaml.html) for Quetzal-1, which can be used to decode within gr-satellites. Find it [here](https://github.com/daniestevez/gr-satellites/blob/main/python/telemetry/quetzal1.py).

Finally, please note that only telemetry was decoded in SatNOGS and made live. All photos were processed internally by the Quetzal-1 team, using [the photo decoder](https://github.com/danalvarez/gr-quetzal1/blob/master/apps/receiver/write_photo.py) available in gr-quetzal1.

## Available Repositories

| Repository               | Description                                                                                                             |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------|
| [quetzal1-hardware](https://github.com/Quetzal-1-CubeSat-Team/quetzal1-hardware)        | Contains the hardware design files for Quetzal-1 and its subsystems.                                                    |
| [quetzal1-flight-software](https://github.com/Quetzal-1-CubeSat-Team/quetzal1-flight-software) | Contains the software for Quetzal-1 and its subsystems.                                                                 |
| quetzal1-telemetry             | This repository. |
| [gr-quetzal1](https://github.com/danalvarez/gr-quetzal1)              | Contains the software used on the Ground Control Station for Quetzal-1, based on GNURadio. |