import ipaddress
import json
import csv
import maxminddb
from pathlib import Path

IPINFO_CSV = "ipinfo_lite.csv"
MAXMIND_MMDB = "maxmind.mmdb"

WANTED = {"RU", "BY"}

KEYWORDS_AS = ["yandex", "kaspersky", "VKontakte", "LLC VK", "Rostelecom", "GRCHC", "ru-center", "EdgeCenter LLC", "EdgeAm", 
               "Vimpelcom", "CDNvideo", "Sovkombank", "Sberbank", "Alfa-Bank", "Russian Agricultural Bank", "ngenix", "SERVICEPIPE", 
               "DDOS-GUARD", "Moscow city telephone network", "ALEF-BANK", "Ruform LLC", "Nauka-Svyaz", "Sovremennye setevye tekhnologii",
               "JSC IOT"]
               
KEYWORDS_DOMAIN = ["yandex", "kaspersky", "beeline", "stormwall", "edgecenter", "ngenix", "servicepipe", "rutube"]

FULL_DOMAIN = ["ya.ru", "yandex.net", "reg.ru", "mail.ru", "cloud.ru", "majordomo.ru", "megafon.ru", "beeline.ru", "corbina.net", "mts.ru", "net.ru",
               "t2.ru", "rt.ru", "rostelecom.ru", "rtcomm.ru", "ertelecom.ru", "curator.pro", "nic.ru", "nichost.ru", "edgecenter.ru", "ddos-guard.net", "kaspersky.com", "drweb.com", "drweb.ru", "avito.ru"
               "sputnik.ru", "ok.ru", "rambler.ru", "ozon.ru", "reg.ru", "tinkoff.ru", "tbank.ru", "vk.com", "vk.ru", "vkontakte.ru", "vk.company", "cdnvideo.com", "cdnvideo.ru"
               "vtb.ru", "vtb.com", "vtb.ge", "vtb-bank.by", "vtb.am", "rshb.ru", "cft.ru", "variti.io", "koronapay.com", "mid.ru", "gov.ru", "rfc-cfa.ru", "farline.net",
               "donsattv.ru", "mobile-win.ru", "crelcom.ru", "xn--80ahgneri.net", "crimea-com.net", "crimea-com.ru", "ardinvest.net", "redi.su",
               "miranda-media.ru", "realnet.ru", "d-group.online", "mageal.ru", "m3x.org", "liveproxy.ru", "meshnet.su", "mytrinet.ru",
               "bestline.su", "tkmotel.ru", "skymaxsib.ru", "crimea.com", "sevstar.net", "sevtelecom.ru", "ubsnet.ru", "komfort21vek.ru", "avanta-telecom.ru", "reconn.ru"
               "airee.ru", "rusety.ru", "1city.org", "naukanet.ru", "ekma.is", "ekma-is.ru", "ugletele.com", "lds.online", "evpanet.com", "maximusnet.ru", "my-trinity.com",
               "antiddos.solutions", "miran.ru", "spd-mgts.ru", "volnamobile.ru", "yaltanet.ru"]

WANTED_AS = [
    # VK AND MAILRU
    "AS49281",  # M100 LLC
    "AS47764",  # LLC VK (Mail.ru)
    "AS60476",  # LLC VK (Digital Transformation Plus LLC)
    "AS60863",  # LLC VK
    "AS49988",  # LLC VK
    "AS21051",  # ASTRUM LLC
    "AS199295", # LLC VK
    "AS205830", # LLC VK (Digital Transformation Plus LLC)
    "AS201817", # VK Tech Kazakhstan LLP
    "AS207970", # LLC VK
    "AS203502", # JOINT STOCK COMPANY "TELEGA"
    "AS47541",  # LLC VK
    "AS47542",  # LLC VK
    "AS28709",  # LLC VK
    "AS62243",  # LLC VK
    "AS207581", # LLC VK
    "AS57973",  # LLC VK

    # Sberbank
    "AS35237",  # Sberbank of Russia PJSC
    "AS206673", # Sberbank-Telecom LLC
    "AS33844",  # Sberbank of Russia PJSC
    "AS60122",  # Sberbank of Russia PJSC
    "AS47457",  # Sberbank of Russia PJSC
    "AS44408",  # Sberbank of Russia PJSC
    "AS58112",  # Sberbank of Russia PJSC

    # Yandex
    "AS13238",  # YANDEX LLC
    "AS207304", # Y. Izdeu men Jarnama LLP (Yandex)

    # Government / State infrastructure / Telecom
    "AS61280",  # FGUP "GRCHC"
    "AS196641", # Federal Unitary State Enterprise General Radio Frequency Center
    "AS57107",  # Federal State Unitary Enterprise "Russian Satellite Communications Company"
    "AS41853",  # Limited Liability Company NTCOM
    "AS12695",  # LLC Digital Network
    "AS8752",   # AO "ASVT"
    "AS213853", # FGUP "GRCHC"
    "AS210109", # LLC "Kurgan-Telecom"
    "AS44923",  # Saint-Petersburg Computer Networks Ltd.
    "AS59494",  # Enigma Telecom Ltd.
    "AS20702",  # JSC Russian Railways
    "AS43797",  # The Federal Guard Service of the Russian Federation

    "AS51115",
    "AS59467",
    "AS197068",
    "AS201012",
    "AS208117",
    "AS43396",
    "AS42628",
    "AS45000",
    "AS211631",
    "AS42974",
    "AS208165",
    "AS205158",
    "AS205161",
    "AS209701",
    "AS62170",
    "AS208677", # Sberbank cloud.ru / Cloud.ru ASN found in resource list
    "AS61178",
    "AS200350",
    "AS44534",
    "AS212066",
    "AS208398",
    "AS202611",
    "AS207207",
    "AS208722",
    "AS215013",
    "AS208795",
    "AS210656",
    "AS201706", # SERVICEPIPE LLC
    "AS207986", # LLC OZON BANK
    "AS57073",
    "AS201512",
    "AS215070",
    "AS201513",
    "AS211517",
    "AS49053",
    "AS213105",
    "AS44704",
    "AS62222",
    "AS12389",
    "AS42610",
    "AS12332",
    "AS15468",
    "AS25515",
    "AS21378",
    "AS6828",
    "AS25490",
    "AS6863",
    "AS12730",
    "AS21487",
    "AS41691",
    "AS12683",
    "AS35177",
    "AS34168",
    "AS13118",
    "AS33934",
    "AS35154",
    "AS13056",
    "AS12685",
    "AS48421",
    "AS29456",
    "AS24810",
    "AS39229",
    "AS34974",
    "AS34267",
    "AS42548",
    "AS34892",
    "AS21479",
    "AS8828",
    "AS29069",
    "AS41190",
    "AS24873",
    "AS34137",
    "AS28860",
    "AS43574",
    "AS35516",
    "AS5573",
    "AS15934",
    "AS8382",
    "AS44412",
    "AS8443",
    "AS30749",
    "AS196747",
    "AS43132",
    "AS42358",
    "AS204354",
    "AS8675",
    "AS21017",
    "AS34205",
    "AS8568",
    "AS24789",
    "AS12380",
    "AS48044",
    "AS42362",
    "AS38951",
    "AS16301",
    "AS15759",
    "AS35125",
    "AS12846",
    "AS39407",
    "AS42091",
    "AS24699",
    "AS31496",
    "AS8570",
    "AS25531",
    "AS34584",
    "AS24783",
    "AS44467",
    "AS8557",
    "AS25436",
    "AS41134",
    "AS8359",
    "AS48176",
    "AS28884",
    "AS44895",
    "AS209024",
    "AS30922",
    "AS41822",
    "AS42087",
    "AS197023",
    "AS15640",
    "AS39811",
    "AS48123",
    "AS48612",
    "AS49350",
    "AS29190",
    "AS21365",
    "AS42322",
    "AS44731",
    "AS39001",
    "AS49154",
    "AS41209",
    "AS43148",
    "AS48124",
    "AS31558",
    "AS51771",
    "AS44677",
    "AS30881",
    "AS40993",
    "AS60490",
    "AS48000",
    "AS20866",
    "AS50071",
    "AS49665",
    "AS34351",
    "AS48212",
    "AS48100",
    "AS60891",
    "AS48541",
    "AS48322",
    "AS50240",
    "AS8580",
    "AS35728",
    "AS13155",
    "AS49816",
    "AS39799",
    "AS43318",
    "AS13055",
    "AS41771",
    "AS35473",
    "AS47899",
    "AS16012",
    "AS16256",
    "AS29209",
    "AS42115",
    "AS29194",
    "AS39858",
    "AS44736",
    "AS13174",
    "AS43720",
    "AS43038",
    "AS48796",
    "AS41929",
    "AS58100",
    "AS57681",
    "AS31133",
    "AS25159",
    "AS20632",
    "AS31261",
    "AS50928",
    "AS43197",
    "AS29648",
    "AS12714",
    "AS31195",
    "AS31208",
    "AS31163",
    "AS13075",
    "AS31205",
    "AS31213",
    "AS35298",
    "AS31224",
    "AS6854",
    "AS34552",
    "AS6850",
    "AS8263",
    "AS47395",
    "AS12396",
    "AS202804",
    "AS24866",
    "AS3216",
    "AS3235",
    "AS8402",
    "AS31359",
    "AS34038",
    "AS42842",
    "AS2599",
    "AS20597",
    "AS8350",
    "AS31425",
    "AS2766",
    "AS16345",
    "AS8755",
    "AS29125",
    "AS8773",
    "AS49144",
    "AS21332",
    "AS3253",
    "AS43687",
    "AS42110",
    "AS16043",
    "AS21483",
    "AS34644",
    "AS20533",
    "AS8371",
    "AS34894",
    "AS34747",
    "AS12543",
    "AS13257",
    "AS28703",
    "AS42245",
    "AS13095",
    "AS43275",
    "AS43970",
    "AS21480",
    "AS20919",
    "AS9049",
    "AS48858",
    "AS13094",
    "AS25408",
    "AS51034",
    "AS43097",
    "AS31483",
    "AS62423",
    "AS25446",
    "AS41733",
    "AS31484",
    "AS49874",
    "AS41682",
    "AS20807",
    "AS12772",
    "AS41002",
    "AS12768",
    "AS8331",
    "AS16300",
    "AS51035",
    "AS197140",
    "AS42682",
    "AS51604",
    "AS31363",
    "AS39435",
    "AS50543",
    "AS57044",
    "AS12690",
    "AS51570",
    "AS52207",
    "AS43478",
    "AS56330",
    "AS51819",
    "AS50498",
    "AS56981",
    "AS49048",
    "AS50512",
    "AS57026",
    "AS42683",
    "AS24588",
    "AS50544",
    "AS41661",
    "AS21447",
    "AS41727",
    "AS41754",
    "AS51645",
    "AS41843",
    "AS34150",
    "AS43314",
    "AS47111",
    "AS5563",
    "AS56377",
    "AS39028",
    "AS8345",
    "AS42116",
    "AS56420",
    "AS57378",
    "AS198295",
    "AS34590",
    "AS50542",
    "AS34533",
    "AS21353",
    "AS41786",
    "AS59713",
    "AS47911",
    "AS205971",
    "AS204952",
    "AS62287",
    "AS41403",
    "AS34925",
    "AS206661",
    "AS8732",
    "AS15582",
    "AS44096",
    "AS9068",
    "AS51011",
]


def iso_from_maxmind(record: dict) -> str | None:
    if not isinstance(record, dict):
        return None
    country = record.get("country")
    if isinstance(country, dict):
        iso = country.get("iso_code")
        if isinstance(iso, str) and iso:
            return iso
    return None


def ipinfo_matches(row: dict) -> bool:
    if (row.get("country_code") or "").casefold() in {x.casefold() for x in WANTED}:
        return True

    row_asn = (row.get("asn") or "").casefold()
    if row_asn and row_asn in (x.casefold() for x in WANTED_AS):
        return True

    as_name = (row.get("as_name") or "").casefold()
    as_domain = (row.get("as_domain") or "").casefold()

    for kw in KEYWORDS_AS:
        if kw.casefold() in as_name:
            return True

    for kw in KEYWORDS_DOMAIN:
        if kw.casefold() in as_domain:
            return True

    for kw in FULL_DOMAIN:
        if kw.casefold() == as_domain:
            return True

    return False


def main() -> None:
    base = Path(__file__).resolve().parent

    v4: list[ipaddress.IPv4Network] = []
    v6: list[ipaddress.IPv6Network] = []

    # IPinfo CSV
    ipinfo_path = base / IPINFO_CSV
    if not ipinfo_path.exists():
        raise FileNotFoundError(f"File not found: {ipinfo_path}")

    with ipinfo_path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if not ipinfo_matches(row):
                continue

            net_s = row.get("network")
            if not net_s:
                continue

            net = ipaddress.ip_network(net_s, strict=False)
            if net.version == 4:
                v4.append(net)
            elif net.version == 6:
                v6.append(net)
            else:
                raise ValueError(f"Unknown IP version: {net.version}")

    # MaxMind MMDB
    mmdb_path = base / MAXMIND_MMDB
    if not mmdb_path.exists():
        raise FileNotFoundError(f"File not found: {mmdb_path}")

    with maxminddb.open_database(str(mmdb_path)) as reader:
        for network, record in reader:
            if iso_from_maxmind(record) not in WANTED:
                continue

            net = ipaddress.ip_network(network, strict=False)
            if net.version == 4:
                v4.append(net)
            elif net.version == 6:
                v6.append(net)
            else:
                raise ValueError(f"Unknown IP version: {net.version}")

    v4 = list(ipaddress.collapse_addresses(v4))
    v6 = list(ipaddress.collapse_addresses(v6))

    all_nets = [*map(str, v4), *map(str, v6)]
    
    listsdir = base / "lists"
    
    # txt lst
    (listsdir / "ips-for-ru.lst").write_text("\n".join(all_nets) + ("\n" if all_nets else ""), encoding="utf-8")
    (listsdir / "ips-for-ru.txt").write_text("\n".join(all_nets) + ("\n" if all_nets else ""), encoding="utf-8")

    # json snippet
    payload = [
        {
            "ip": all_nets,
            "outboundTag": "RU",
        }
    ]
    (listsdir / "ips-for-ru-snippet.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # json snippet blancer
    payload = [
        {
            "ip": all_nets,
            "balancerTag": "BAL-RU",
        }
    ]
    (listsdir / "ips-for-ru-snippet-balancer.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
  
    # json singbox
    payload = {
      "version": 2,
      "rules": [
        {
          "ip_cidr": all_nets,
        }
      ]
    }
    (listsdir / "ips-for-ru-singbox.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    
    # yaml
    yaml_file = listsdir / "ips-for-ru.yaml"
    with yaml_file.open("w", encoding="utf-8", newline="\n") as f:
        f.write("payload:\n")
        for net in all_nets:
            f.write(f"    - {net}\n")

    print(f"IPv4: {len(v4)}")
    print(f"IPv6: {len(v6)}")
    print(f"Total: {len(all_nets)}")


if __name__ == "__main__":
    main()
