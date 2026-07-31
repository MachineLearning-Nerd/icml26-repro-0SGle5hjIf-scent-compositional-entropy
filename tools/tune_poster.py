"""Solve the per-column balance spacers so posterly's alignment gate passes."""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRATCH = Path("/private/tmp/claude-501/-Users-dineshjinjala-Documents-AllCode-ICMLPapers/"
               "8657cd16-a2c9-4a7c-821e-e589ccee3f0c/scratchpad")
BUILD = SCRATCH / "poster_build"
PY = str(SCRATCH / "posterly-venv" / "bin" / "python")
SRC = REPO / "tools" / "build_poster.py"
PX_PER_MM = 96 * 60 / 1524.0  # 60 in canvas at 96 dpi, 1524 mm wide
TARGET = 3010.0


def set_balance(vals):
    t = SRC.read_text()
    t = re.sub(r"BALANCE = \[[^\]]*\]", "BALANCE = " + str(list(vals)), t, count=1)
    SRC.write_text(t)


def measure():
    subprocess.run([PY, str(SRC)], cwd=REPO, capture_output=True, check=True)
    out = subprocess.run([PY, str(SCRATCH / "posterly/tools/poster_check.py"),
                          "measure", "poster.html"],
                         cwd=BUILD, capture_output=True, text=True).stdout
    return [float(m) for m in re.findall(r"last-card-bottom =\s+([0-9.]+) px", out)], out


def main():
    vals = [0, 0, 0, 0]
    for it in range(8):
        set_balance(vals)
        bottoms, out = measure()
        spread = max(bottoms) - min(bottoms)
        print(f"iter {it}: balance={vals} bottoms={[round(b,1) for b in bottoms]} "
              f"spread={spread:.2f}")
        if spread < 5.0 and all(3000 <= b <= 3020 for b in bottoms):
            print(out[out.index("[measure]"):][:400])
            return 0
        new = []
        for i, b in enumerate(bottoms):
            need = (TARGET - b) / PX_PER_MM
            new.append(max(-40, min(60, round(vals[i] + need))))
        if new == vals:
            break
        vals = new
    print("did not converge; last measure output:")
    print(out)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
