import sys
import urllib.request


URLS = [
    "https://core.telegram.org/resources/cidr.txt",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/asn/AS1273.list",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/asn/AS44893.list",
]

BASE_IPS = [
    "139.59.210.98/32",
    "5.28.192.0/18",
    "91.108.0.0/16",
    "109.239.140.0/24",
    "2001:b28:f23c::/47",
    "2a0a:f280::/29",
]


def download(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            if resp.status != 200:
                raise Exception(f"Bad status: {resp.status}")
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"[ERROR] Failed to download {url}: {e}")
        sys.exit(1)


def parse_lines(text):
    result = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        result.append(line)
    return result


def main():
    if "--path" not in sys.argv:
        print("Usage: script.py --path output.txt")
        sys.exit(1)

    path = sys.argv[sys.argv.index("--path") + 1]

    all_ips = set(BASE_IPS)

    for url in URLS:
        data = download(url)
        ips = parse_lines(data)
        all_ips.update(ips)

    all_ips = sorted(all_ips)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("payload:\n")
            for ip in all_ips:
                f.write(f"  - IP-CIDR,{ip}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()