"""Encode a test clip with 4 codecs at 5 bitrates and measure
quality, encoding time/energy and decoding time/energy.

    python measure.py        # 1080p -> results.csv
    python measure.py 720    # 720p  -> results_720p.csv

If you stop the script, start it again: runs already in the csv are skipped.
"""
import csv
import os
import re
import subprocess
import sys
import time

from codecarbon import OfflineEmissionsTracker

# ---------------------------------------------------------------- settings
HEIGHT = int(sys.argv[1]) if len(sys.argv) > 1 else 1080
WIDTH = HEIGHT * 16 // 9
CLIP_SECONDS = 5                           # length of the test clip
BITRATES = [200, 500, 1000, 3000, 5000]    # kbit/s

if HEIGHT == 1080:
    REF, OUT, RESULTS = "ref.y4m", "out", "results.csv"
else:
    REF, OUT, RESULTS = f"ref{HEIGHT}.y4m", f"out{HEIGHT}", f"results_{HEIGHT}p.csv"

# For every codec: (file extension, encode command, decode command)
# {i} = input clip, {b} = bitrate in kbit/s, {o} = encoded file
CODECS = {
    "libx264": ("mp4",
                "ffmpeg -y -v error -i {i} -c:v libx264 -b:v {b}k {o}",
                "ffmpeg -v error -i {o} -f null -"),
    "libx265": ("mp4",
                "ffmpeg -y -v error -i {i} -c:v libx265 -b:v {b}k -x265-params log-level=error {o}",
                "ffmpeg -v error -i {o} -f null -"),
    "SVT-AV1": ("mkv",
                "ffmpeg -y -v error -i {i} -c:v libsvtav1 -b:v {b}k {o}",
                "ffmpeg -v error -i {o} -f null -"),
    "vvenc":   ("266",
                "vvencapp -i {i} -b {b}k --preset faster -o {o} --verbosity 1",
                "vvdecapp -b {o} -o /dev/null --verbosity 1"),
}

COLUMNS = ["codec", "target_kbps", "actual_kbps", "psnr", "ssim", "vmaf",
           "enc_time_s", "enc_energy_wh", "dec_time_s", "dec_energy_wh"]


# ------------------------------------------------------------- helpers
def run(command):
    """Run a shell command and return the result (stdout/stderr as text)."""
    return subprocess.run(command, shell=True, capture_output=True, text=True)


def measure(command):
    """Run a command and return (seconds, energy in Wh)."""
    tracker = OfflineEmissionsTracker(country_iso_code="AUT", log_level="error",
                                      save_to_file=False)
    tracker.start()                       # energy meter on
    start = time.perf_counter()           # stopwatch on
    result = run(command)
    seconds = time.perf_counter() - start
    tracker.stop()
    assert result.returncode == 0, result.stderr
    return seconds, tracker._total_energy.kWh * 1000   # kWh -> Wh


def decode_to_y4m(encoded_file):
    """Decode an encoded file back to raw video (so it can be compared)."""
    decoded = f"{OUT}/decoded.y4m"
    if encoded_file.endswith(".266"):     # VVC: decode with vvdec, then convert
        run(f"vvdecapp -b {encoded_file} -o {OUT}/decoded.yuv --verbosity 1")
        run(f"ffmpeg -y -v error -f rawvideo -pix_fmt yuv420p10le -s {WIDTH}x{HEIGHT} "
            f"-r 30 -i {OUT}/decoded.yuv -pix_fmt yuv420p {decoded}")
    else:
        run(f"ffmpeg -y -v error -i {encoded_file} -pix_fmt yuv420p {decoded}")
    return decoded


def quality(encoded_file):
    """Return (PSNR, SSIM, VMAF) of the encoded file compared with the original."""
    decoded = decode_to_y4m(encoded_file)
    result = run(f"ffmpeg -i {decoded} -i {REF} -lavfi "
                 f"'[0:v][1:v]psnr;[0:v][1:v]ssim;[0:v][1:v]libvmaf' -f null -")
    text = result.stderr                  # ffmpeg prints the scores here

    def find(pattern):                    # cut one number out of the text
        return float(re.search(pattern, text).group(1))

    return (find(r"PSNR.*average:([\d.]+)"),
            find(r"SSIM.*All:([\d.]+)"),
            find(r"VMAF score: ([\d.]+)"))


def load_results():
    """Read the finished runs from the csv (empty list if there is none)."""
    if not os.path.exists(RESULTS):
        return []
    with open(RESULTS) as f:
        table = list(csv.reader(f))[1:]   # [1:] skips the header row
    return [[row[0], int(float(row[1]))] + [float(x) for x in row[2:]] for row in table]


def save_results(rows):
    with open(RESULTS, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        writer.writerows(rows)


# ------------------------------------------------------------------ main
os.makedirs(OUT, exist_ok=True)
rows = load_results()
finished = {(row[0], row[1]) for row in rows}

for codec, (extension, encode_cmd, decode_cmd) in CODECS.items():
    for bitrate in BITRATES:
        if (codec, bitrate) in finished:
            continue
        print(f"{codec} {bitrate}k ...", flush=True)
        encoded_file = f"{OUT}/{codec}_{bitrate}k.{extension}"

        enc_time, enc_energy = measure(encode_cmd.format(i=REF, b=bitrate, o=encoded_file))
        dec_time, dec_energy = measure(decode_cmd.format(o=encoded_file))
        psnr, ssim, vmaf = quality(encoded_file)

        # real bitrate of the file: bytes -> bits -> per second -> kbit/s
        actual_kbps = round(os.path.getsize(encoded_file) * 8 / CLIP_SECONDS / 1000)

        rows.append([codec, bitrate, actual_kbps, psnr, ssim, vmaf,
                     enc_time, enc_energy, dec_time, dec_energy])
        save_results(rows)                # save after every run

print(f"done -> {RESULTS}")
