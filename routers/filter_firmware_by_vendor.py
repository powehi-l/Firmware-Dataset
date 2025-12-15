#!/usr/bin/env python3
"""
从 firmware_download_list.csv 按 vendor 关键字筛选并导出新的 CSV。

使用示例：
  python filter_firmware_by_vendor.py --vendor zyxel \
      --input /home/yongjun/firmwares/datasets/Firmware-Dataset/dat/firmware_download_list.csv \
      --output /home/yongjun/firmwares/filtered_zyxel.csv
"""

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List, TextIO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="按 vendor 列筛选 firmware_download_list.csv 并写出新的 CSV"
    )
    vendor_group = parser.add_mutually_exclusive_group(required=True)
    vendor_group.add_argument(
        "--vendor",
        help="单个 vendor 关键字（不区分大小写，按整单元格匹配）",
    )
    vendor_group.add_argument(
        "--vendors",
        nargs="+",
        help="多个 vendor 关键字（空格分隔，不区分大小写，按整单元格匹配）",
    )
    parser.add_argument(
        "--input",
        default="/home/yongjun/firmwares/datasets/Firmware-Dataset/dat/firmware_download_list.csv",
        help="输入 CSV 路径，默认为仓库中的 firmware_download_list.csv",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="单 vendor 模式下的输出 CSV 路径，默认在当前目录生成 <vendor>_firmware_download_list.csv",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="多 vendor 模式下输出目录，默认当前目录",
    )
    return parser.parse_args()


def open_csv_writer(path: Path) -> TextIO:
    # newline='' 避免多余空行，encoding 默认 UTF-8
    return path.open("w", newline="", encoding="utf-8")


def normalize_vendors(vendors: Iterable[str]) -> List[str]:
    normalized = []
    for v in vendors:
        key = v.strip().lower()
        if not key:
            continue
        normalized.append(key)
    if not normalized:
        raise ValueError("vendor 关键字不能为空")
    return normalized


def filter_single_vendor(input_path: Path, output_path: Path, vendor: str) -> int:
    """只写一个 vendor，适合小批量调用。"""
    vendor_key = normalize_vendors([vendor])[0]

    written = 0
    with input_path.open("r", newline="", encoding="utf-8") as fin, open_csv_writer(
        output_path
    ) as fout:
        reader = csv.DictReader(fin)
        if "vendor" not in reader.fieldnames:
            raise ValueError("输入文件缺少 vendor 列")

        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            if row.get("vendor", "").strip().lower() == vendor_key:
                writer.writerow(row)
                written += 1

    return written


def filter_multi_vendor(
    input_path: Path, output_dir: Path, vendors: Iterable[str]
) -> Dict[str, int]:
    """
    一次读取文件，按多个 vendor 分类写出，避免重复扫描大文件。
    返回 {vendor: 写出行数}
    """
    vendor_keys = normalize_vendors(vendors)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 准备 writer 映射
    writers: Dict[str, csv.DictWriter] = {}
    files: Dict[str, TextIO] = {}
    counts: Dict[str, int] = {v: 0 for v in vendor_keys}

    with input_path.open("r", newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        if "vendor" not in reader.fieldnames:
            raise ValueError("输入文件缺少 vendor 列")

        for vendor in vendor_keys:
            out_path = output_dir / f"{vendor}_firmware_download_list.csv"
            f = open_csv_writer(out_path)
            files[vendor] = f
            w = csv.DictWriter(f, fieldnames=reader.fieldnames)
            w.writeheader()
            writers[vendor] = w

        for row in reader:
            key = row.get("vendor", "").strip().lower()
            if key in writers:
                writers[key].writerow(row)
                counts[key] += 1

    # 关闭文件
    for f in files.values():
        f.close()

    return counts


def main() -> None:
    args = parse_args()

    input_path = Path(args.input).expanduser()
    if args.vendor:
        if args.output:
            output_path = Path(args.output).expanduser()
        else:
            output_path = Path.cwd() / f"{args.vendor}_firmware_download_list.csv"
        count = filter_single_vendor(input_path, output_path, args.vendor)
        print(f"写出 {count} 行到 {output_path}")
    else:
        output_dir = Path(args.output_dir).expanduser() if args.output_dir else Path.cwd()
        counts = filter_multi_vendor(input_path, output_dir, args.vendors)
        for vendor, count in counts.items():
            out_path = output_dir / f"{vendor}_firmware_download_list.csv"
            print(f"{vendor}: 写出 {count} 行到 {out_path}")


if __name__ == "__main__":
    main()

