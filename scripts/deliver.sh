#!/usr/bin/env bash
# ทำไฟล์เล็ก (720p, ~13MB ต่อนาที) สำหรับส่งให้ดูบนมือถือ หรือใส่ในหน้า Artifact ที่รับไฟล์ไม่เกิน 15MB
# ไฟล์สำหรับโพสต์จริงให้ใช้ตัวเต็มที่ render ออกมา (แอปโซเชียลบีบไฟล์ซ้ำอยู่แล้ว)
#
# ใช้: scripts/deliver.sh <ไฟล์เต็ม.mp4> <ไฟล์เล็ก.mp4>
set -euo pipefail
ffmpeg -v error -y -i "$1" -vf scale=720:1280 -c:v libx264 -b:v 1600k -maxrate 2000k -bufsize 4000k \
  -preset slow -c:a aac -b:a 128k -movflags +faststart "$2"
ls -lh "$2" | awk '{print "ไฟล์เล็ก:", $5}'
