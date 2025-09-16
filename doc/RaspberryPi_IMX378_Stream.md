# Raspberry Pi 5 + IMX378 Camera Streaming Project

## 📌 Overview

This project documents the setup of an **IMX378 12.3MP fisheye camera**
on a **Raspberry Pi 5**, including configuration, testing, and real-time
streaming to a PC.\
The process covered: - Enabling camera support on Raspberry Pi OS
(Bookworm, `rpicam-apps`). - Testing with stills and video. - Handling
fisheye lens distortion (optional). - Streaming live video over the
network. - Fixing playback issues with VLC/FFmpeg.

------------------------------------------------------------------------

## ⚙️ Environment

-   **Hardware**: Raspberry Pi 5 + IMX378 fisheye camera.\
-   **Software**: Raspberry Pi OS (Bookworm), `rpicam-apps`, `ffmpeg`
    (on both Pi & PC), VLC (on PC).\
-   **Network**: Local LAN, Pi and PC on same subnet.

------------------------------------------------------------------------

## 🖼️ Camera Setup & Testing

Enable and test the camera:

``` bash
# Test preview (5s)
rpicam-hello -t 5000

# Capture still
rpicam-still -o test.jpg

# Record 10s video
rpicam-vid -t 10000 -o test.h264
```

------------------------------------------------------------------------

## 🎥 Video Quality Tuning

1080p @ 30fps, with tuned parameters for clarity:

``` bash
rpicam-vid --width 1920 --height 1080 --framerate 30   --bitrate 12000000 --codec h264   --sharpness 1.5 --contrast 1.2 --saturation 1.2   -t 10000 -o video.mp4
```

-   `--sharpness 1.5` → sharper details.\
-   `--contrast 1.2` → better tonal separation.\
-   `--saturation 1.2` → more vivid colors.\
-   `--bitrate 12000000` → ensures crisp quality at 1080p.

------------------------------------------------------------------------

## 🌐 Network Streaming

After testing multiple methods (UDP, RTSP, TCP), the final **working
pipeline** was:

### On the Raspberry Pi (server):

``` bash
rpicam-vid --width 1920 --height 1080 --framerate 30   --bitrate 12000000 --codec h264   --sharpness 1.5 --contrast 1.2 --saturation 1.2   --inline --intra 30 --listen -t 0   -o tcp://0.0.0.0:8554
```

-   `--inline` → embeds SPS/PPS headers in stream (VLC/FFmpeg need
    this).\
-   `--intra 30` → forces keyframe every \~1s for faster lock.\
-   `--listen` → Pi acts as a TCP server.\
-   `tcp://0.0.0.0:8554` → listen on all interfaces, port 8554.

------------------------------------------------------------------------

### On the PC (client, using FFmpeg):

``` bat
ffmpeg -fflags +genpts -f h264 -r 30   -i tcp://192.168.68.63:8554   -c copy -movflags +faststart out2.mp4
```

-   `-fflags +genpts` → generates timestamps for proper playback.\
-   `-r 30` → sets expected framerate.\
-   `-movflags +faststart` → optimizes MP4 for streaming/seeking.\
-   Output is saved as **out2.mp4**.

------------------------------------------------------------------------

### On the PC (client, using VLC):

    tcp/h264://192.168.68.63:8554

------------------------------------------------------------------------

## 🚀 Key Lessons

-   **`rpicam-apps`** replaces old `libcamera-*` commands on Pi 5.\
-   `--inline` and `--intra` are essential for reliable streaming.\
-   MP4 requires valid timestamps → fix with `-fflags +genpts`.\
-   **TCP pull (VLC/FFmpeg client)** is more stable than UDP on Windows
    networks.\
-   MKV is safer for live capture; remux to MP4 later if needed.

------------------------------------------------------------------------

## ✅ Final Working Commands

### Raspberry Pi:

``` bash
rpicam-vid --width 1920 --height 1080 --framerate 30   --bitrate 12000000 --codec h264   --sharpness 1.5 --contrast 1.2 --saturation 1.2   --inline --intra 30 --listen -t 0   -o tcp://0.0.0.0:8554
```

### Windows PC (FFmpeg capture):

``` bat
ffmpeg -fflags +genpts -f h264 -r 30   -i tcp://192.168.68.63:8554   -c copy -movflags +faststart out2.mp4
```
