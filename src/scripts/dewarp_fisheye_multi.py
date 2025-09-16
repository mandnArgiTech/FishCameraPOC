
#!/usr/bin/env python3

Defisheye/undistort script supporting multiple checkerboard calibration patterns.

Supported patterns (squares → calibration file expected):
- 10x7   → calib_fisheye_10x7.npz
- 10x14  → calib_fisheye_10x14.npz
- 10x16  → calib_fisheye_10x16.npz
- 16x22  → calib_fisheye_16x22.npz

Usage examples:
  python dewarp_fisheye_multi.py --pattern 10x14 --input fish.jpg --output undist.jpg --balance 0.8
  python dewarp_fisheye_multi.py --pattern 16x22 --input video.mp4 --output undist.mp4 --balance 0.9 --fps 30

import argparse, os, sys
import cv2, numpy as np

PATTERN_FILES = {
    "10x7": "calib_fisheye_10x7.npz",
    "10x14": "calib_fisheye_10x14.npz",
    "10x16": "calib_fisheye_10x16.npz",
    "16x22": "calib_fisheye_16x22.npz",
}

def build_maps(K, D, size, balance):
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
        K, D, size, np.eye(3), balance=balance
    )
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K, D, np.eye(3), new_K, size, cv2.CV_16SC2
    )
    return map1, map2

def process_image(inp, out, K, D, balance):
    img = cv2.imread(inp)
    if img is None:
        raise SystemExit(f"Could not read {inp}")
    h, w = img.shape[:2]
    map1, map2 = build_maps(K, D, (w, h), balance)
    undist = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR)
    cv2.imwrite(out, undist)
    print(f"[OK] Wrote {out}")

def process_video(inp, out, K, D, balance, fps):
    cap = cv2.VideoCapture(inp)
    if not cap.isOpened():
        raise SystemExit(f"Could not open {inp}")
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    in_fps = cap.get(cv2.CAP_PROP_FPS) or fps or 30
    if not fps: fps = in_fps

    map1, map2 = build_maps(K, D, (w, h), balance)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    outw = cv2.VideoWriter(out, fourcc, fps, (w, h))
    if not outw.isOpened():
        raise SystemExit("Could not open output writer")

    i = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        und = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR)
        outw.write(und)
        i += 1
        if i % 100 == 0:
            print(f"[Info] processed {i} frames...")

    cap.release()
    outw.release()
    print(f"[OK] Wrote {out}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", choices=PATTERN_FILES.keys(), required=True, help="Checkerboard pattern used for calibration")
    ap.add_argument("--input", required=True, help="Input image or video path")
    ap.add_argument("--output", required=True, help="Output image or video path")
    ap.add_argument("--balance", type=float, default=0.8, help="0..1 (lower=straighter, more crop)")
    ap.add_argument("--fps", type=float, default=None, help="Output FPS for video if source has none")
    args = ap.parse_args()

    calib_file = PATTERN_FILES[args.pattern]
    if not os.path.exists(calib_file):
        raise SystemExit(f"Calibration file not found: {calib_file}")

    data = np.load(calib_file)
    K, D = data["K"], data["D"]

    ext = os.path.splitext(args.input)[1].lower()
    is_image = ext in (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    if is_image:
        process_image(args.input, args.output, K, D, args.balance)
    else:
        process_video(args.input, args.output, K, D, args.balance, args.fps)

if __name__ == "__main__":
    main()
