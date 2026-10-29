#!/usr/bin/env bash
# ดาวน์โหลดไฟล์จาก Google Drive ทีละหลายไฟล์พร้อมกัน
#
# ใช้: scripts/drive_download.sh <ids.txt> <โฟลเดอร์ปลายทาง>
# ids.txt หนึ่งบรรทัดต่อไฟล์: "<ชื่อไฟล์ปลายทาง> <Drive file id>"
#   C0001.mov <file id>
# หา file id ได้จากตัวเชื่อม Google Drive (search_files ด้วย parentId = '<folder id>')
# หรือจากลิงก์ https://drive.google.com/file/d/<file id>/view
set -euo pipefail
IDS="$1"; OUT="$2"
mkdir -p "$OUT"
xargs -P 4 -L 1 sh -c '
  curl -sSL --retry 3 -m 1800 -o "'"$OUT"'/$0" \
    "https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t" \
  && echo "ok   $0" || echo "FAIL $0"
' < "$IDS"
echo "ดาวน์โหลดแล้ว: $(ls "$OUT" | wc -l) ไฟล์, $(du -sh "$OUT" | cut -f1)"
