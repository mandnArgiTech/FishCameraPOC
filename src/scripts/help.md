# 📖 Calibration & Dewarping Help

This document explains how to use the two main scripts:

- `calibrate_fisheye_multi.py` → **Calibrate the camera** using checkerboard images.  
- `dewarp_fisheye_multi.py` → **Remove fisheye distortion** from images or videos using calibration results.

---

## 1️⃣ Calibration (`calibrate_fisheye_multi.py`)

### Supported Checkerboard Patterns
- **10x7**   squares → 9x6   inner corners  
- **10x14**  squares → 9x13  inner corners  
- **10x16**  squares → 9x15  inner corners  
- **16x22**  squares → 15x21 inner corners  

⚠️ Remember: inner corners = (columns-1, rows-1).

### Example Command
```bash
# Calibrate with 10x14 checkerboard images (30 mm squares)
python calibrate_fisheye_multi.py --images "./calib/*.jpg" --pattern 10x14 --square-mm 30 --debug
```

### Options
- `--images "./calib/*.jpg"` → glob path to your captured calibration images.  
- `--pattern 10x14` → choose one of {10x7, 10x14, 10x16, 16x22}.  
- `--square-mm 30` → (optional) size of one checker square in millimeters (adds real-world scale).  
- `--debug` → saves debug images with detected corners in `calib_debug/`.  

### Outputs
- `calib_fisheye_<pattern>.npz` → contains K, D, image_size, rms.  
- `calib_fisheye_<pattern>.yaml` → same values in YAML format (for OpenCV tools).  

---

## 2️⃣ Dewarping (`dewarp_fisheye_multi.py`)

This script removes fisheye distortion from images and videos using the calibration file.

### Example (Image)
```bash
python dewarp_fisheye_multi.py --pattern 10x14 --input img.jpg --output undist.jpg --balance 0.85
```

### Example (Video)
```bash
python dewarp_fisheye_multi.py --pattern 16x22 --input fisheye.mp4 --output dewarped.mp4 --balance 0.8 --fps 30
```

### Options
- `--pattern 10x14` → must match the checkerboard pattern you used for calibration.  
- `--calib calib_fisheye_10x14.npz` → optional path (default auto-loads `calib_fisheye_<pattern>.npz`).  
- `--input` / `--output` → file paths for input and output.  
- `--balance 0.85` → tradeoff FOV vs straightness (0 = crop more, 1 = full FOV).  
- `--fps 30` → only needed if source video lacks frame rate.  

### Output
- Image: undistorted version of the input image.  
- Video: undistorted video written to MP4.  

---

## 🔑 Workflow Summary
1. Print checkerboard (A3 recommended for fisheye, e.g., 10x14 or 16x22).  
2. Capture 20–30 images from different angles.  
3. Run **calibration script** with matching pattern.  
4. Use **dewarp script** to undistort your images or videos.  
5. Adjust `--balance` to tune between cropping and field of view.  

---

## 🛠️ Troubleshooting
- If calibration fails: ensure good lighting, sharp focus, no glare on the checkerboard.  
- If results look warped: verify you used the **same pattern** for calibration and dewarping.  
- If video FPS looks wrong: add `--fps` when dewarping.  

---
