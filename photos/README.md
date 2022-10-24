# Quetzal-1: a story in pictures

The second half of Quetzal-1's life in orbit was spent testing the Payload, which comprised a camera and a carrousel of light filters. Tests were conducted gradually, as hurdles were cleared in obtaining usable images.

The journey was long, arduous and a lesson in patience. Adequate passes over Guatemala were scarce, with several days, sometimes weeks, going between every such pass. We had our share of misfires: like when our Ground Control Station (GCS) antenna would stop tracking the satellite mid-pass, and we would end up with an incomplete picture.

Then, came the issue of the harsh lighting conditions while in-orbit. Due to timing constraints during development, our camera could only operate in automatic exposure mode. This meant many pictures were initially received either [pitch-black](./jpg/4-UVG-2020-09-07-131315.jpg) or in [blinding light](./jpg/1-UVG-2020-07-25-204853.jpg). With the camera being unable to adapt to the lighting conditions, we spent many weeks trying to find workaround.

|||
|-|-|
| <img src="./jpg/3-UVG-2020-08-20-104736 (2).jpg"><br>**Credit: Universidad del Valle de Guatemala** | Not all was bad news, though. Approximately a month into our first download attempt, in late August, we received the first image that was neither black nor white. An alluring kind of glare: the sun reflecting off of what we believe to be one of our light filters, or possibly the camera lens. The first image with any detail, and the first to be received with no corruption at all: no lost packets. A momentous win for the whole team, and one that would fill us with expectation and faith. |

The going got harder after that, though. Although we had perfected the communications process with the satellite, being able to download up to two pictures per pass, all of September saw us receiving only-black, or all-white pictures. How would we solve this? We were unable to change any of the camera's settings (a lesson that we will definitely take to heart for future missions). If only we could tell the satellite to wait longer to capture the image, to let the camera adapt. Our hands were tied...

Or were they? If we could not control the camera, maybe we could control the lighting conditions. That coveted *Golden Hour*, maybe it could be our saving grace. Adequate passes for sunset or sunrise were scarce, to say the least. But, with patience, we found a couple slots.

We took our time to prepare. The team wrote a procedure, detailing the exact times at which picture capture should be executed, trying to balance twilight: the very delicate (and short) span of space and time where the satellite was departing light, entering darkness. And so everything was set: On the 17th of November, 2020, we would try to fight the curse.

|||
|-|-|
| <img src="./jpg/14-UVG-2020-11-17-231416.jpg"><br>**Credit: Universidad del Valle de Guatemala** | We took three pictures that day. Timing was critical, absolute and unforgiving. The first, taken at 17:14:16 local time (GMT-6) was white. All white.
| <img src="./jpg/15-UVG-2020-11-17-231511 (Repaired).jpg"><br>**Credit: Universidad del Valle de Guatemala** | But we knew it was too soon. No need to worry. We knew that real twilight, that sought-after dusk would kick in at 15:15 local time. And so, with hope, with the satellite almost overhead, we sent that second capture-and-downlink command. The transmission came soon after, and what eventually came to be in our monitors (after some quick processing becaused the JPEG header was lost in transmission) was that historic first: the first picture ever taken by a Guatemalan satellite in Earth orbit. At a time when Guatemala and the Central American region was being devastated by Hurricane Iota, Quetzal-1 flew high above, looking at us: an eye above the storm. |
| <img src="./jpg/16-UVG-2020-11-17-231626 (1) (Original).jpg"><br>**Credit: Universidad del Valle de Guatemala** | As if that wasn't enough, on its last legs, with the satellite over 700 kilometers away, we tried a final capture and download command. Our antenna, its amplifiers maxxed out and listening as intently as it could, received the third and final image that day. More corrupted, given the impressive distance over which it had been transmitted (the final packets came in at over 1,300 km), it gifted us with another perspective: one with less clouds, more water, with the satellite well over the Atlantic at this point. |

We didn't know, at the time, this would become the final image ever taken by Quetzal-1. We attempted to download this last image four days later, on November 21st. Unfortunately for us, and for our strong satellite up above, a communications error ocurred between our Payload module and the On-Board Computer during picture transmission. We received the first 6 packets of the picture, and then a repetition of that last packet, replicated over the length of the picture.

Then, silence: We did not hear back from Quetzal-1, and were, despite our most arduous attempts, unable to regain communications. We said goodbye to our fearless companion, and its 211 days of successful operation in orbit, with nothing but pride in what we'd managed to build, in what that corageous satellite had undergone. We anthropomorphize because that satellite had life. And because, during 6 months, we spoke to it daily, listened to its inspiring, adventurous chirp.

Long live Quetzal-1, our great gig in the sky :heart:

![the-final-picture](./processed/16-UVG-2020-11-17-231626%20(1)%20(Repaired).jpg?raw=true "The final picture taken by Quetzal-1 (processed)")
**Credit: Universidad del Valle de Guatemala**

## File Description

All image files follow the format `N-UVG-yyyy-mm-dd-hhmmss`, where:

1. `N` represents the picture number, where 1 is the first picture taken and downloaded from the satellite. If picture numbers repeat, it is because the same picture was downloaded on a different date (possibly due to corruption on the first try due to ambient RF noise).
2. `yyyy-mm-dd` is the date the picture was captured.
3. `hhmmss` is the exact time of picture capture in UTC.

## Directory Description

1. [raw](./raw/): contains the raw pictures as transmitted by the satellite. Although the pictures were transmitted in `.jpg` format, they were decoded and put together into `.dat` binary files. See *Note 1* regarding how pictures were put together in [the Ground Control Station decoder](https://github.com/danalvarez/gr-quetzal1/blob/master/apps/receiver/write_photo.py).
    * [raw/metadata](./raw/metadata/): contains metadata for each picture. Of interest, the value of the on-board RTC at the time of picture capture and the number of each received packet (i.e., if a packet number is missing in the list, it means it was not received). Further information on the construction of each packet is available in [the photo packet description in gr-quetzal1](https://github.com/danalvarez/gr-quetzal1/tree/master/docs).
2. [jpg](./jpg/): same images as in `raw`, but converted to `.jpg`. See *Note 2* below.
3. [processed](./processed/): contains some processed images, that were edited using image manipulation software to compensate for packet loss or to make them easier to interpret. See *Note 3* below.

Finally, the [locations](./locations.csv) file contains the approximate location for the satellite at the moment of picture capture for the last two pictures (15 and 16). These were obtained by propagating the satellite TLE. It may be useful if any further geographical processing of the pictures is desired.

---
:information_source: **NOTES**

1. Sometimes, image packets were lost due to ambient RF noise. To indicate where this ocurred in a given picture, a block of zeroes was inserted programatically for every lost packet. This can be seen by opening a picture in a binary editor, such as [Sublime Text](https://www.sublimetext.com/), and looking for packets with rows of `0000 0000 0000 0000 0000 0000 0000 0000`. 
2. The file [15-UVG-2020-11-17-231511 (Original).dat](./raw/15-UVG-2020-11-17-231511%20(Original).dat) will not open because part of the JPEG header was lost during reception. The file can be opened if the header is replaced with that of [16-UVG-2020-11-17-231626 (1) (Original).dat](./raw/16-UVG-2020-11-17-231626%20(1)%20(Original).dat). This was done to produce [15-UVG-2020-11-17-231511 (Repaired).jpg](./processed/15-UVG-2020-11-17-231511%20(Repaired).jpg).
3. The file [16-UVG-2020-11-17-231626 (1) (Original).dat](./raw/16-UVG-2020-11-17-231626%20(1)%20(Original).dat) was received incomplete due to loss of some packets. Due to how JPEG encoding works, packet loss results in some parts of the image appearing "shifted", in incorrect places or with different coloring. This was fixed manually to produce [16-UVG-2020-11-17-231626%20(1)%20(Repaired).jpg](./processed/16-UVG-2020-11-17-231626%20(1)%20(Repaired).jpg).

---