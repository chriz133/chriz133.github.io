# What we did

## 1. DASH vs HLS
- First exercise (15 Oct): DASH (`../DASH`, `../manifest.mpd`), published on GitHub Pages: https://chriz133.github.io/
- This exercise (19 Oct): repeated with the other format, HLS (`../HLS`, `master.m3u8`).
- Same 5 bitrates both times: 200k, 500k, 1M, 3M, 5M (1080p).
- Comparison:

| | HLS | DASH |
|---|---|---|
| Manifest | `.m3u8` (text playlist) | `.mpd` (XML) |
| Segments | `.ts` / fMP4 | `.m4s` (fMP4) + `init.mp4` |
| Standard | Apple, proprietary | ISO/MPEG, open |
| Browser support | Native on Safari/iOS, else hls.js | Needs dash.js (not on iOS) |
| Codecs | Mostly H.264/HEVC | Any codec |

## 2. Setup
```
brew install vvenc vvdec                 # VVC encoder + decoder
python3 -m venv ../.venv
../.venv/bin/pip install codecarbon pandas matplotlib
```

## 3. Test clip (first 5 s of input.mp4, 1080p, 30 fps)
```
ffmpeg -i ../input.mp4 -t 5 -an -pix_fmt yuv420p -r 30 ref.y4m
```
Only 5 s because vvenc is very slow (~1 fps).

## 4. Encode, decode, measure (`measure.py`)
4 codecs x 5 bitrates = 20 encodes. Commands used:
```
ffmpeg -i ref.y4m -c:v libx264   -b:v 1000k out.mp4     # x264
ffmpeg -i ref.y4m -c:v libx265   -b:v 1000k out.mp4     # x265
ffmpeg -i ref.y4m -c:v libsvtav1 -b:v 1000k out.mkv     # SVT-AV1
vvencapp -i ref.y4m -b 1000k --preset faster -t 0 -o out.266   # VVC
```
Decoding: `ffmpeg -i out.mp4 -f null -` (VVC: `vvdecapp -b out.266 -o /dev/null`)

- Time = `time.perf_counter()` around the command.
- Energy = CodeCarbon `OfflineEmissionsTracker` around the command (Wh).
- Quality = ffmpeg `psnr`, `ssim`, `libvmaf` filters (decoded vs. `ref.y4m`).
- Result table: `results.csv`

## 5. Plots (`plot.py`)
```
../.venv/bin/python plot.py
```
- `1_quality.png` PSNR / SSIM / VMAF vs bitrate
- `2_encoding_time.png`, `3_encoding_energy.png`
- `4_decoding_time.png`, `5_decoding_energy.png`

## Notes
- Run everything: `../.venv/bin/python measure.py && ../.venv/bin/python plot.py`
- Energy on a Mac is only an estimate (CodeCarbon has no hardware power counters there).
- Encoder presets: x264/x265/SVT-AV1 defaults, vvenc `faster` (for speed).
