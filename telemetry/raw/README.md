# Quetzal-1 Raw Beacons

This directory contains the raw beacon data for Quetzal-1, split by week of operation (`beacons_week_1.hex` to `beacons_week_30.hex`). These are the files from which the processed [telemetry](../telemetry.xlsx) was generated. To decode them, use the [processing scripts](../scripts/).

## Origin

The frames were received by ground stations of the [SatNOGS](https://satnogs.org/) network and downloaded from the SatNOGS DB (NORAD ID 45598) using [quetzal1-satnogs](https://github.com/alicjamusial/quetzal1-satnogs). That tool:

1. Keeps only the frames that start with the AX.25 header `404040404040604040404040406103F0` and are exactly 157 bytes long.
2. Strips the first 20 bytes of each frame (16 bytes of AX.25 header + 4 bytes of CSP header).
3. Writes the remaining 137-byte beacons back to back into the output file.

## Format

The files are **binary** and each file contains subsequent **137-byte frames** with no separators, which means every file size is a multiple of 137. The layout of each record is described in [gr-quetzal1](https://github.com/danalvarez/gr-quetzal1/blob/master/docs/Beacon_Package_Data.xlsx). A valid beacon starts with the ASCII identifier `QUETZAL1` and ends with the message `UVG a Guatemala, SI se pudo`.

## Examples

The two records below are consecutive in [beacons_week_4.hex](./beacons_week_4.hex). Record *n* of a file starts at byte offset *n* × 137, so they can be found in any hex editor by going to the offsets shown on the left column.

**Normal beacon** (record 1475, offset `0x3155B`). It starts with `QUETZAL1`, followed by the telemetry fields and the final message. Bytes 8 to 13 (`10 03 01 1a 00 00`) are the satellite's real-time clock (26 days, 16 h 3 min 1 s since launch), which the [processing scripts](../scripts/) convert to `25/5/2020 07:20:59` UTC.

```
0003155B  51 55 45 54 5a 41 4c 31 10 03 01 1a 00 00 0f 45   QUETZAL1.......E
0003156B  96 53 53 00 00 00 00 00 44 de 00 00 00 00 00 00   .SS.....D.......
0003157B  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ................
0003158B  00 00 00 00 00 00 00 00 7f 7e 89 79 6a 85 04 86   .........~.yj...
0003159B  2c 59 1a 0b 12 10 4b 56 16 0c 12 0e 49 04 00 04   ,Y....KV....I...
000315AB  0f 00 00 04 6a 00 00 00 0a 06 3c 1e 32 46 1e 01   ....j.....<.2F..
000315BB  01 01 3c 04 1e 1e 01 05 1e 01 03 01 03 00 55 56   ..<...........UV
000315CB  47 20 61 20 47 75 61 74 65 6d 61 6c 61 2c 20 53   G a Guatemala, S
000315DB  49 20 73 65 20 70 75 64 00                        I se pud.
```

**Non-beacon frame** (record 1476, offset `0x315E4`). It does not start with `QUETZAL1` and does not have the structure of a beacon. Its origin is unknown. Decoded as a beacon, it gives meaningless values, such as the timestamp `13/4/2085 17:18:40`. There are 99 such frames.

```
000315E4  00 66 e3 c9 fb 0a 39 f2 eb c0 c0 00 40 40 40 40   .f....9.....@@@@
000315F4  40 40 60 40 40 40 40 40 40 61 03 f0 42 b7 4f 56   @@`@@@@@@a..B.OV
00031604  a9 16 53 38 7d 01 9f bf 71 c0 c0 00 40 40 40 40   ..S8}...q...@@@@
00031614  40 40 60 40 40 40 40 40 40 61 03 f0 c2 b7 4f 56   @@`@@@@@@a....OV
00031624  2f c5 ae e4 a7 4b 33 ec 76 c0 c0 00 40 40 40 40   /....K3.v...@@@@
00031634  40 40 60 40 40 40 40 40 40 61 03 f0 42 b7 4f 56   @@`@@@@@@a..B.OV
00031644  52 61 55 6d 59 0c 94 50 fc c0 c0 00 40 40 40 40   RaUmY..P....@@@@
00031654  40 40 60 40 40 40 40 40 40 61 03 f0 c2 b7 4f 56   @@`@@@@@@a....OV
00031664  be 92 44 a8 65 25 28 77 00                        ..D.e%(w.
```

## Notes

1. **Duplicates:** The same beacon was often heard by several ground stations, so it appears more than once (usually in adjacent records). This is cleaned up by the `--filter` flag in [Telemetry_Filter.py](../scripts/Telemetry_Filter.py).
