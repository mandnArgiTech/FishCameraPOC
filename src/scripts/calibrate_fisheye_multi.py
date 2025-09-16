
#!/usr/bin/env python3

Fisheye calibration script that supports multiple checkerboard sizes.

Supported sizes (squares → inner corners):
- 10x7   squares → 9x6   inner corners
- 10x14  squares → 9x13  inner corners
- 10x16  squares → 9x15  inner corners
- 16x22  squares → 15x21 inner corners

Usage:
  python calibrate_fisheye_multi.py --images "./calib/*.jpg" --pattern 10x14 --square-mm 30 --debug

Outputs:
  - calib_fisheye_<pattern>.npz  (K, D, image_size, rms)
  - calib_fisheye_<pattern>.yaml (same in YAML for OpenCV tools)

import argparse, glob, os, sys
import cv2
import numpy as np

PATTERN_MAP = {
    "10x7":  (9, 6),
    "10x14": (9, 13),
    "10x16": (9, 15),
    "16x22": (15, 21),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", default="./calib/*.jpg", help="Glob for calibration images")
    ap.add_argument("--pattern", choices=PATTERN_MAP.keys(), required=True, help="Checkerboard squares (choose one)")
    ap.add_argument("--square-mm", type=float, default=None, help="Square size in mm (optional)")
    ap.add_argument("--debug", action="store_true", help="Save corner debug overlays")
    args = ap.parse_args()

    pattern_size = PATTERN_MAP[args.pattern]
    print(f"Using pattern {args.pattern}, inner corners {pattern_size}")

    img_paths = sorted(glob.glob(args.images))
    if not img_paths:
        raise SystemExit(f"No images matched: {args.images}")

    objp = np.zeros((1, pattern_size[0]*pattern_size[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
    if args.square_mm:
        objp *= args.square_mm

    objpoints, imgpoints = [], []
    imsize = None

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE

    os.makedirs("calib_debug", exist_ok=True)

    kept = 0
    for i, path in enumerate(img_paths, 1):
        img = cv2.imread(path)
        if img is None:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if imsize is None:
            imsize = gray.shape[::-1]

        ret, corners = cv2.findChessboardCorners(gray, pattern_size, flags)
        if not ret:
            print(f"[INFO] No pattern in {os.path.basename(path)}")
            continue
        corners = cv2.cornerSubPix(gray, corners, (3,3), (-1,-1), criteria)
        objpoints.append(objp)
        imgpoints.append(corners)
        kept += 1

        if args.debug:
            dbg = img.copy()
            cv2.drawChessboardCorners(dbg, pattern_size, corners, ret)
            cv2.imwrite(os.path.join("calib_debug", f"corners_{i:03d}.jpg"), dbg)

    if kept < 8:
        raise SystemExit(f"Not enough good detections: {kept}")

    K = np.zeros((3,3))
    D = np.zeros((4,1))
    rms, _, _, _, _ = cv2.fisheye.calibrate(
        objectPoints=objpoints,
        imagePoints=imgpoints,
        image_size=imsize,
        K=K,
        D=D,
        rvecs=None,
        tvecs=None,
        flags=cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW,
        criteria=criteria
    )

    print("=== Calibration results (fisheye) ===")
    print("Image size:", imsize)
    print("RMS error:", rms)
    print("K:\n", K)
    print("D:\n", D.ravel())

    base = f"calib_fisheye_{args.pattern}"
    np.savez(f"{base}.npz", K=K, D=D, image_size=np.array(imsize), rms=np.array([rms]))

    try:
        import yaml
        with open(f"{base}.yaml", "w") as f:
            yaml.safe_dump({
                "image_width": imsize[0],
                "image_height": imsize[1],
                "camera_matrix": {"data": K.flatten().tolist()},
                "distortion_coefficients": {"data": D.flatten().tolist()},
                "rms": float(rms),
                "pattern": args.pattern,
                "inner_corners": pattern_size,
                "square_size_mm": args.square_mm if args.square_mm else None
            }, f, sort_keys=False)
    except Exception as e:
        print("[WARN] Could not write YAML:", e)

    print(f"\nSaved {base}.npz and {base}.yaml")

if __name__ == "__main__":
    main()
