# What we did

Everything is in the folder `codecs/`. Run all commands from there.

## 1. DASH vs HLS
- First exercise (15 Oct): DASH (`../DASH`, `../manifest.mpd`), published on GitHub Pages: https://chriz133.github.io/
- This exercise (19 Oct): repeated with the other format, HLS (`../HLS`, `master.m3u8`).
- Same 5 bitrates both times: 200k, 500k, 1M, 3M, 5M (1080p).

| | HLS | DASH |
|---|---|---|
| Manifest | `.m3u8` (text playlist) | `.mpd` (XML) |
| Segments | `.ts` / fMP4 | `.m4s` (fMP4) + `init.mp4` |
| Standard | Apple, proprietary | ISO/MPEG, open |
| Browser support | Native on Safari/iOS, else hls.js | Needs dash.js (not on iOS) |
| Codecs | Mostly H.264/HEVC | Any codec |

## 2. Setup (once)
```
brew install vvenc vvdec                       # VVC encoder + decoder (ffmpeg cannot encode VVC)
python3 -m venv ../.venv                       # a private Python folder for this project
../.venv/bin/pip install codecarbon pandas matplotlib
```
- `codecarbon` measures energy, `pandas` reads the result table, `matplotlib` draws the plots.

## 3. Make the test clips (first 5 s of input.mp4)
```
ffmpeg -i ../input.mp4 -t 5 -an -pix_fmt yuv420p -r 30 ref.y4m                                  # 1080p
ffmpeg -i ../input.mp4 -t 5 -an -vf scale=1280:720 -pix_fmt yuv420p -r 30 ref720.y4m            # 720p
```
| Parameter | Meaning |
|---|---|
| `-i file` | input file |
| `-t 5` | only take 5 seconds (vvenc is very slow, so we keep it short) |
| `-an` | no audio |
| `-vf scale=1280:720` | resize the picture to 1280x720 (the 1080p clip is not resized) |
| `-pix_fmt yuv420p` | standard colour format that every encoder understands |
| `-r 30` | 30 frames per second |
| `ref.y4m` | raw, uncompressed video = the "perfect original" we compare against |

## 4. Encode, decode and measure (`measure.py`)
```
../.venv/bin/python measure.py        # 1080p -> results.csv
../.venv/bin/python measure.py 720    # 720p  -> results_720p.csv
```
4 codecs x 5 bitrates = 20 encodes per resolution. The commands inside the script:
```
ffmpeg -i ref.y4m -c:v libx264   -b:v 1000k out.mp4            # x264  (H.264)
ffmpeg -i ref.y4m -c:v libx265   -b:v 1000k out.mp4            # x265  (H.265)
ffmpeg -i ref.y4m -c:v libsvtav1 -b:v 1000k out.mkv            # SVT-AV1
vvencapp -i ref.y4m -b 1000k --preset faster -t 0 -o out.266   # vvenc (H.266 / VVC)
```
| Parameter | Meaning |
|---|---|
| `-c:v libx264` | which video codec (encoder) to use |
| `-b:v 1000k` / `-b 1000k` | target bitrate: 1000 kbit/s (the encoder aims for it but misses a bit) |
| `--preset faster` | vvenc speed setting: faster = quicker but a little worse compression |
| `-t 0` | vvenc threads. **0 = one thread only.** Careful: the other codecs use several CPU cores, so vvenc's time and energy are higher than they would be with its default. We used the same setting for 1080p and 720p, so those two are still comparable. |
| `-o out.266` | output file |

Decoding (what we time and measure):
```
ffmpeg -i out.mp4 -f null -                  # decode and throw the result away
vvdecapp -b out.266 -o /dev/null             # same for VVC
```
- `-f null -` = decode everything but write nothing. `/dev/null` = the same idea (a trash bin).
- `-b` = the compressed file to read, `-o` = where to write the decoded video.

How we measure:
- **Time** = Python `time.perf_counter()` around the command.
- **Energy** = CodeCarbon `OfflineEmissionsTracker` around the command, in Wh. On a Mac it is only an estimate (no real power sensors), so it mostly follows the run time.
- **Quality** = we decode the file again and compare it with `ref.y4m` using ffmpeg filters:
```
ffmpeg -i decoded.y4m -i ref.y4m -lavfi "[0:v][1:v]psnr;[0:v][1:v]ssim;[0:v][1:v]libvmaf" -f null -
```
| Parameter | Meaning |
|---|---|
| `[0:v][1:v]` | first input (encoded) vs second input (original) |
| `psnr` | pixel error in dB, higher = better (simple, but not how people see) |
| `ssim` | structural similarity 0 to 1, 1 = identical |
| `libvmaf` | Netflix's VMAF score 0 to 100, closest to what people see |
| `-lavfi` | "filter graph": run these filters on the videos |

## 5. Plots (`plot.py`)
```
../.venv/bin/python plot.py            # 1080p: 1_quality.png ... 5_decoding_energy.png
../.venv/bin/python plot.py 720        # 720p:  720p_1_quality.png ... 720p_5_decoding_energy.png
../.venv/bin/python plot.py compare    # 6_compare_1080p_vs_720p.png
```
- `1_quality`: PSNR, SSIM, VMAF vs bitrate. `2/3`: encoding time and energy. `4/5`: decoding time and energy.
- X axis = the real bitrate of each file (not the target), on a log scale.
- Comparison plot: solid line = 1080p, dashed line = 720p.

## 6. Put it on GitHub Pages
The site is the repo `chriz133/chriz133.github.io`. We added a folder `codecs/` with `index.html`, the PNGs, `results*.csv` and this file:
```
git clone https://github.com/chriz133/chriz133.github.io.git
cp codecs/{index.html,*.png,results*.csv,WHAT_WE_DID.md} chriz133.github.io/codecs/
cd chriz133.github.io && git add codecs && git commit -m "Update codec page" && git push
```
Live at https://chriz133.github.io/codecs/

## Notes
- vvenc is slow (about 1 frame/s at 1080p with one thread), so the clip is only 5 s.
- If `measure.py` is stopped, start it again: it skips runs that are already in the csv.
- Encoders do not hit the target bitrate exactly (e.g. SVT-AV1 asked 5000k, got 5546k).
