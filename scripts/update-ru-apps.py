#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path


DEFAULT_URL = "https://raw.githubusercontent.com/legiz-ru/mihomo-rule-sets/main/other/ru-app-list.yaml"


def detect_newline(text: str) -> str:
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def download_text(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            status = getattr(resp, "status", None) or resp.getcode()
            raw = resp.read()
    except Exception as e:
        raise RuntimeError(f"Не удалось скачать файл: {e}") from e

    if status != 200:
        raise RuntimeError(f"Скачивание вернуло HTTP {status}")

    if not raw:
        raise RuntimeError("Скачанный файл пустой")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        raise RuntimeError(f"Скачанный файл не UTF-8: {e}") from e

    if "payload:" not in text:
        raise RuntimeError("Скачанный файл не похож на ожидаемый ru-app-list.yaml: нет 'payload:'")

    return text


def extract_packages(text: str) -> list[str]:
    pattern = re.compile(r"^\s*-\s*PROCESS-NAME\s*,\s*([A-Za-z0-9._-]+)\s*$")
    result: list[str] = []
    seen: set[str] = set()

    for line in text.splitlines():
        match = pattern.match(line)
        if not match:
            continue

        package_name = match.group(1).strip()
        if not package_name:
            continue

        if package_name not in seen:
            seen.add(package_name)
            result.append(package_name)

    if not result:
        raise RuntimeError("В скачанном файле не найдено ни одной строки с PROCESS-NAME")

    return result


def find_tun_block(lines: list[str]) -> tuple[int, int]:
    tun_start = None

    for i, line in enumerate(lines):
        if re.match(r"^tun:\s*(#.*)?$", line):
            tun_start = i
            break

    if tun_start is None:
        raise RuntimeError("В YAML не найден блок 'tun:'")

    tun_end = len(lines)
    top_level_key = re.compile(r"^[^\s#][^:]*:\s*(#.*)?$")

    for i in range(tun_start + 1, len(lines)):
        if top_level_key.match(lines[i]):
            tun_end = i
            break

    return tun_start, tun_end


def find_exclude_package_block(lines: list[str], tun_start: int, tun_end: int) -> tuple[int, int]:
    start = None

    for i in range(tun_start + 1, tun_end):
        line = lines[i]
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)

        if indent == 2 and stripped.startswith("exclude-package:"):
            start = i
            break

    if start is None:
        raise RuntimeError("В блоке 'tun' не найден ключ 'exclude-package:'")

    end = start + 1

    while end < tun_end:
        line = lines[end]

        if not line.strip():
            end += 1
            continue

        if re.match(r"^\s*#", line):
            end += 1
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent <= 2:
            break

        end += 1

    return start, end


def build_exclude_package_block(packages: list[str], newline: str) -> list[str]:
    joined = ", ".join(f'"{pkg}"' for pkg in packages)
    return [f"  exclude-package: [{joined}]{newline}"]


def write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(text)


def main() -> int:
    current_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(description="Обновить tun.exclude-package в ultimate-mihomo-ru.yaml")
    parser.add_argument(
        "--yaml",
        type=Path,
        default=current_dir.parent / "remnawave-templates" / "ultimate-mihomo-ru.yaml",
        help="Путь к целевому YAML-файлу",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="URL со списком ru apps",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Не создавать .bak файл перед записью",
    )
    args = parser.parse_args()

    yaml_path = args.yaml.resolve()

    if not yaml_path.exists():
        raise RuntimeError(f"YAML файл не найден: {yaml_path}")

    source_text = download_text(args.url)
    packages = extract_packages(source_text)

    original_text = yaml_path.read_text(encoding="utf-8")
    newline = detect_newline(original_text)
    lines = original_text.splitlines(keepends=False)

    tun_start, tun_end = find_tun_block(lines)
    block_start, block_end = find_exclude_package_block(lines, tun_start, tun_end)

    new_block = build_exclude_package_block(packages, newline)
    updated_lines = lines[:block_start] + [line.rstrip("\r\n") for line in new_block]
    updated_lines += lines[block_end:]
    updated_text = newline.join(updated_lines)

    if not updated_text.endswith(newline):
        updated_text += newline

    if not args.no_backup:
        backup_path = yaml_path.with_suffix(yaml_path.suffix + ".bak")
        write_text(backup_path, original_text)

    write_text(yaml_path, updated_text)

    print(f"Готово: {yaml_path}")
    print(f"Загружено пакетов: {len(packages)}")
    if not args.no_backup:
        print(f"Backup создан: {yaml_path.with_suffix(yaml_path.suffix + '.bak')}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        raise SystemExit(1)