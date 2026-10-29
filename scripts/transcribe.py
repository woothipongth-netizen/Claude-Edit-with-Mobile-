"""ถอดเสียงภาษาไทยเป็นข้อความพร้อมเวลา (Whisper)

ใช้: python3 -I scripts/transcribe.py <ไฟล์เสียงหรือวิดีโอ> <โฟลเดอร์ผลลัพธ์> [--model small]

เขียน transcript.json (มีเวลาของแต่ละประโยค) และ transcript.txt
ขนาดโมเดลบนเครื่อง cloud 4 core ไม่มีการ์ดจอ (เสียง 61 วินาที):
  small    ~4.5 นาที  ผิดหลายคำ ต้องแก้ด้วยบริบท
  medium   ~10 นาที   แม่นขึ้น
  large-v3 >20 นาที   แม่นสุด แต่ช้าเกินใช้
ผลลัพธ์จากโมเดลเล็กต้องให้คนตรวจทุกครั้ง โดยเฉพาะชื่อเฉพาะและศัพท์อาชีพ
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("audio")
ap.add_argument("out_dir")
ap.add_argument("--model", default="small")
ap.add_argument("--language", default="th")
args = ap.parse_args()

out = Path(args.out_dir)
out.mkdir(parents=True, exist_ok=True)

# faster-whisper เปิดไฟล์เองแล้วพังกับ PyAV บางเวอร์ชัน จึงแปลงเป็น PCM 16 kHz ด้วย ffmpeg ก่อน
pcm = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", args.audio, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"],
    capture_output=True, check=True,
).stdout
audio = np.frombuffer(pcm, dtype=np.float32)

model = WhisperModel(args.model, device="cpu", compute_type="int8", cpu_threads=4)
segments, _ = model.transcribe(audio, language=args.language, beam_size=1, vad_filter=True)

rows = []
for s in segments:
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}", flush=True)
    rows.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})

(out / "transcript.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
(out / "transcript.txt").write_text(
    "\n".join(f"{r['start']:6.2f}-{r['end']:6.2f} {r['text']}" for r in rows) + "\n"
)
print(f"TRANSCRIPT: {out / 'transcript.json'}")
