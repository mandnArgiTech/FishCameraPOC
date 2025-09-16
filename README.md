# FishCameraPOC - Fisheye Camera Calibration and Dewarping

A Python-based computer vision project for calibrating fisheye cameras and correcting lens distortion in images and videos.

## 🎯 Overview

This project provides tools to:
- **Calibrate fisheye cameras** using checkerboard patterns
- **Remove fisheye distortion** from images and videos
- **Support multiple checkerboard patterns** for different use cases

Perfect for robotics, surveillance, 360-degree imaging, and any application requiring wide-angle lens correction.

## 📁 Project Structure

```
FishCameraPOC/
├── doc/                           # Documentation and reference materials
│   ├── checkerboard_*.pdf        # Various checkerboard patterns (A3/A4)
│   ├── Checker Board.png         # Sample checkerboard image
│   ├── commands tested.txt       # Tested command examples
│   ├── gemini.md                 # Additional documentation
│   └── RaspberryPi_IMX378_Stream.md
└── src/scripts/                   # Main Python scripts
    ├── calibrate_fisheye_multi.py # Camera calibration script
    ├── dewarp_fisheye_multi.py   # Distortion correction script
    └── help.md                   # Detailed usage guide
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
pip install opencv-python numpy pyyaml
```

### 2. Calibrate Your Camera

```bash
# Print a checkerboard (A3 recommended)
# Use one of the patterns in doc/ folder

# Capture 20-30 images from different angles
# Place images in a calib/ folder

# Run calibration
python src/scripts/calibrate_fisheye_multi.py \
    --images "./calib/*.jpg" \
    --pattern 10x14 \
    --square-mm 30 \
    --debug
```

### 3. Correct Distortion

```bash
# For images
python src/scripts/dewarp_fisheye_multi.py \
    --pattern 10x14 \
    --input fisheye_image.jpg \
    --output corrected_image.jpg \
    --balance 0.8

# For videos
python src/scripts/dewarp_fisheye_multi.py \
    --pattern 10x14 \
    --input fisheye_video.mp4 \
    --output corrected_video.mp4 \
    --balance 0.8 \
    --fps 30
```

## 📋 Supported Checkerboard Patterns

| Pattern | Squares | Inner Corners | Use Case |
|---------|---------|---------------|----------|
| 10x7    | 10×7    | 9×6           | Small field of view |
| 10x14   | 10×14   | 9×13          | **Recommended** for most fisheye lenses |
| 10x16   | 10×16   | 9×15          | Wide field of view |
| 16x22   | 16×22   | 15×21         | High resolution calibration |

## 🛠️ Scripts Documentation

### `calibrate_fisheye_multi.py`

Calibrates fisheye cameras using checkerboard images.

**Usage:**
```bash
python calibrate_fisheye_multi.py --images GLOB --pattern PATTERN [OPTIONS]
```

**Options:**
- `--images`: Glob pattern for calibration images (default: `"./calib/*.jpg"`)
- `--pattern`: Checkerboard pattern (`10x7`, `10x14`, `10x16`, `16x22`)
- `--square-mm`: Square size in millimeters (optional, adds real-world scale)
- `--debug`: Save debug images with detected corners

**Outputs:**
- `calib_fisheye_<pattern>.npz` - Camera parameters (NumPy format)
- `calib_fisheye_<pattern>.yaml` - Camera parameters (YAML format)
- `calib_debug/` - Debug images (if `--debug` enabled)

### `dewarp_fisheye_multi.py`

Removes fisheye distortion from images and videos.

**Usage:**
```bash
python dewarp_fisheye_multi.py --pattern PATTERN --input INPUT --output OUTPUT [OPTIONS]
```

**Options:**
- `--pattern`: Checkerboard pattern used for calibration
- `--input`: Input image or video path
- `--output`: Output image or video path
- `--balance`: Balance between FOV and straightness (0.0-1.0, default: 0.8)
- `--fps`: Output FPS for video (if source lacks frame rate)

## 📖 Detailed Documentation

For comprehensive usage instructions, troubleshooting, and advanced features, see:
- `src/scripts/help.md` - Complete user guide
- `doc/` folder - Reference materials and checkerboard patterns

## 🔧 Troubleshooting

### Calibration Issues
- **Not enough detections**: Ensure good lighting, sharp focus, and no glare on checkerboard
- **Poor corner detection**: Use `--debug` flag to visualize detected corners
- **Pattern mismatch**: Verify you're using the correct pattern size

### Dewarping Issues
- **Warped results**: Ensure you're using the same pattern for calibration and dewarping
- **Video FPS issues**: Add `--fps` parameter when processing videos
- **Balance tuning**: Adjust `--balance` parameter (lower = more crop, higher = more FOV)

## 📊 Technical Details

- **OpenCV fisheye calibration** algorithms
- **Sub-pixel corner detection** for high accuracy
- **Multiple output formats** (NumPy, YAML)
- **Real-time video processing** with progress updates
- **Configurable balance** between field of view and straightness

## 🤝 Contributing

This is a proof-of-concept project. Feel free to:
- Report issues
- Suggest improvements
- Add support for additional patterns
- Enhance documentation

## 📄 License

This project is provided as-is for educational and research purposes.

---

**Note**: This project is specifically designed for fisheye lens calibration and correction. For regular camera calibration, consider using standard OpenCV calibration tools.
