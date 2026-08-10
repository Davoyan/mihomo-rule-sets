import ipaddress
import json
import csv
import maxminddb
from pathlib import Path

IPINFO_CSV = "ipinfo_lite.csv"
MAXMIND_MMDB = "maxmind.mmdb"
GEOFEED_GLOB = "geofeeds/*.csv"

WANTED = {"RU", "BY"}

KEYWORDS_AS = ["yandex", "kaspersky", "VKontakte", "LLC VK", "Rostelecom", "GRCHC", "ru-center", "EdgeCenter LLC", "EdgeAm", 
               "Vimpelcom", "CDNvideo", "Sovkombank", "Sberbank", "Alfa-Bank", "Russian Agricultural Bank", "ngenix", "SERVICEPIPE", 
               "DDOS-GUARD", "Moscow city telephone network", "ALEF-BANK", "Ruform LLC", "Nauka-Svyaz", "Sovremennye setevye tekhnologii",
               "JSC IOT"]
               
KEYWORDS_DOMAIN = ["yandex", "kaspersky", "beeline", "stormwall", "edgecenter", "ngenix", "servicepipe", "rutube"]

FULL_DOMAIN = ["ya.ru", "yandex.net", "reg.ru", "mail.ru", "cloud.ru", "majordomo.ru", "megafon.ru", "beeline.ru", "corbina.net", "mts.ru", "net.ru",
               "t2.ru", "rt.ru", "rostelecom.ru", "rtcomm.ru", "ertelecom.ru", "curator.pro", "nic.ru", "nichost.ru", "edgecenter.ru", "ddos-guard.net", "kaspersky.com", "drweb.com", "drweb.ru", "avito.ru",
               "sputnik.ru", "ok.ru", "rambler.ru", "ozon.ru", "reg.ru", "tinkoff.ru", "tbank.ru", "vk.com", "vk.ru", "vkontakte.ru", "vk.company", "cdnvideo.com", "cdnvideo.ru",
               "vtb.ru", "vtb.com", "vtb.ge", "vtb-bank.by", "vtb.am", "rshb.ru", "cft.ru", "variti.io", "koronapay.com", "mid.ru", "gov.ru", "rfc-cfa.ru", "farline.net",
               "donsattv.ru", "mobile-win.ru", "crelcom.ru", "xn--80ahgneri.net", "crimea-com.net", "crimea-com.ru", "ardinvest.net", "redi.su",
               "miranda-media.ru", "realnet.ru", "d-group.online", "mageal.ru", "m3x.org", "liveproxy.ru", "meshnet.su", "mytrinet.ru",
               "bestline.su", "tkmotel.ru", "skymaxsib.ru", "crimea.com", "sevstar.net", "sevtelecom.ru", "ubsnet.ru", "komfort21vek.ru", "avanta-telecom.ru", "reconn.ru",
               "airee.ru", "rusety.ru", "1city.org", "naukanet.ru", "ekma.is", "ekma-is.ru", "ugletele.com", "lds.online", "evpanet.com", "maximusnet.ru", "my-trinity.com",
               "antiddos.solutions", "miran.ru", "spd-mgts.ru", "volnamobile.ru", "yaltanet.ru", "onlinedn.ru", "novotelecom.ru", "profintel.ru",]

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
    "AS208117",  # SBERINSUR Insurance company "Sberbank life insurance" LLC
    "AS43396",  # Sber-NSK-AS Sberbank of Russia PJSC
    "AS42628",  # NPFSBERBANKA-AS Joint Stock Company Non-state Pension Fund of Sberbank
    "AS45000",  # Sber-EKB-AS Sberbank of Russia PJSC
    "AS211631",  # SBERINS Insurance company Sberbank Insurance, LLC
    "AS42974",  # NET-SBERBANK-AST JSC Sberbank-AST
    "AS208165",  # SberLeasing AKCIONERNOYE OBSCHESTVO SBERBANK LIZING
    "AS205158",  # SBRF-CAPITAL Sberbank Capital LLC
    "AS205161",  # Sber-SPB-AS Sberbank of Russia PJSC
    "AS209701",  # SBERBANK-FACTORING Sberbank-factoring Ltd.
    "AS62170",  # ASBPSSBERBANK JSC Sberbank
    "AS208677", # Sberbank cloud.ru / Cloud.ru ASN found in resource list

    # Yandex
    "AS13238",  # YANDEX LLC
    "AS207304", # Y. Izdeu men Jarnama LLP (Yandex)
    "AS200350",  # YandexCloud Yandex.Cloud LLC
    "AS44534",  # yandex-office YANDEX LLC
    "AS212066",  # Y-COM-TR Buyuk Reklam Cozumleri LLC
    "AS208398",  # TELETECH Edge Technology Plus d.o.o. Beograd
    "AS202611",  # YCTL Yandex.Telecom LLC
    "AS207207",  # YL30 Yandex.OFD LLC
    "AS208722",  # GLOBAL_DC Nebius DC Oy
    "AS215013",  # YCCDN Yandex.Cloud LLC
    "AS208795",  # YANDEXCLOUDKZ "Cloud Services Kazakhstan" LLP
    "AS210656",  # YACLOUDBMS Yandex.Cloud LLC

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

    # Other / Infra / Services
    "AS51115",  # HLL-AS HLL LLC
    "AS59467",  # TEST-LAB HLL LLC
    "AS197068",  # CURATOR HLL LLC
    "AS201012",  # Avito KEH eCommerce LLC
    "AS61178",  # CYMRG-AS2 Digital Transformation Plus LLC
    "AS201706", # SERVICEPIPE LLC
    "AS207986", # LLC OZON BANK
    "AS57073",  # Wildberries-AS LLC Wildberries
    "AS201512",  # AS_WILDBERRIES_CDN LLC Wildberries
    "AS215070",  # AS_WILDBERRIES_BY LLC Wildberries
    "AS201513",  # AS_WILDBERRIES_KZ LLC Wildberries
    "AS211517",  # AS_WILDBERRIES_GE LLC Wildberries
    "AS49053",  # AS_WB-TECH LLC Wildberries
    "AS213105",  # AS_eAPTEKA LLC Wildberries
    "AS44704",  # X5-RETAIL-GROUP-AS Perekrestok-2000 LLC
    "AS62222",  # QS-AS QuickSoft LLC
    "AS20919",  # DF DataFort LLC

    # Rostelecom
    "AS12389",  # ROSTELECOM-AS PJSC Rostelecom
    "AS42610",  # NCNET-AS PJSC Rostelecom
    "AS12332",  # PRIMORYE-AS PJSC Rostelecom
    "AS15468",  # KLGELECS-AS PJSC Rostelecom
    "AS25515",  # CTCNET-AS PJSC Rostelecom
    "AS21378",  # CTCTVER PJSC Rostelecom
    "AS6828",  # USI PJSC Rostelecom
    "AS25490",  # STC-AS PJSC Rostelecom
    "AS6863",  # ROSNET-AS PJSC Rostelecom
    "AS12730",  # INECO_AS PJSC Rostelecom
    "AS21487",  # SAKHATELECOM-AS PJSC Rostelecom
    "AS41691",  # SUMTEL-AS-RIPE PJSC Rostelecom
    "AS12683",  # STATEL-AS PJSC Rostelecom
    "AS35177",  # ASI-AS PJSC Rostelecom
    "AS34168",  # ELCOM-ISP-AS PJSC Rostelecom
    "AS13118",  # ASN-YARTELECOM PJSC Rostelecom
    "AS33934",  # VolgogradEC-AS PJSC Rostelecom
    "AS35154",  # TELENET-AS PJSC Rostelecom
    "AS13056",  # RT-TMB-AS PJSC Rostelecom
    "AS12685",  # SIBITEX PJSC Rostelecom
    "AS48421",  # ATLAS-AS PJSC Rostelecom
    "AS29456",  # BELSVYAZ-AS PJSC Rostelecom
    "AS24810",  # TELESET-KAZAN PJSC Rostelecom
    "AS39229",  # SAN-AS PJSC Rostelecom
    "AS34974",  # KAMCHATKA-AS PJSC Rostelecom
    "AS34267",  # DEBRYANSK-AS-1 PJSC Rostelecom
    "AS42548",  # KCHR-AS PJSC Rostelecom
    "AS34892",  # INFOLINK-AS PJSC Rostelecom
    "AS21479",  # ROSTOV-TELEGRAF-AS PJSC Rostelecom
    "AS8828",  # BURNET-AS PJSC Rostelecom
    "AS29069",  # TLK-AS PJSC Rostelecom
    "AS41190",  # IDEATELECOM PJSC Rostelecom
    "AS24873",  # ELLINK-AS PJSC Rostelecom
    "AS34137",  # RUAMUR-AS PJSC Rostelecom
    "AS28860",  # PARMA-INFORM-AS PJSC Rostelecom
    "AS43574",  # DAGSV-AS PJSC Rostelecom
    "AS35516",  # KURSKNET-RU-AS PJSC Rostelecom
    "AS5573",  # KRASNET-AS PJSC Rostelecom
    "AS15934",  # ZEBRA-AS PJSC Rostelecom
    "AS8382",  # IRTEL-AS PJSC Rostelecom
    "AS44412",  # INGUSHELECTROSVYAZ-AS PJSC Rostelecom
    "AS8443",  # SKHDSV-AS PJSC Rostelecom
    "AS30749",  # VOLOGDA-AS PJSC Rostelecom
    "AS196747",  # Electronic-government PJSC Rostelecom
    "AS43132",  # KBT-AS PJSC Rostelecom
    "AS42358",  # INSYS-AS PJSC Rostelecom
    "AS204354",  # MBSAMARA-AS PJSC Rostelecom
    "AS8675",  # AS_TULATEL PJSC Rostelecom
    "AS21017",  # VSI-AS PJSC Rostelecom
    "AS34205",  # MRBD-AS PJSC Rostelecom
    "AS8568",  # MMT-AS PJSC Rostelecom
    "AS24789",  # NOVGORODTELECOM-AS PJSC Rostelecom
    "AS12380",  # LENSVYAZ PJSC Rostelecom
    "AS48044",  # ROSTELECOMIT-AS Rostelecom Information Technologies LTd
    "AS42362",  # ALANIA-AS PJSC Rostelecom
    "AS38951",  # TKT-AS PJSC Rostelecom
    "AS16301",  # DATACOM-AS PJSC Rostelecom
    "AS15759",  # DIN-AS PJSC Rostelecom
    "AS35125",  # SMOLENSK-AS PJSC Rostelecom
    "AS12846",  # PJSC Rostelecom
    "AS39407",  # CHITATELECOM-AS PJSC Rostelecom
    "AS42091",  # KHAKAS-AS PJSC Rostelecom
    "AS24699",  # IVTELECOM-AS PJSC Rostelecom
    "AS31496",  # ATNET-AS PJSC Rostelecom
    "AS8570",  # LES PJSC Rostelecom
    "AS25531",  # INTFRM-AS PJSC Rostelecom
    "AS34584",  # KHBDSV PJSC Rostelecom
    "AS24783",  # ASN-MELS-MurmanElectroSviaz PJSC Rostelecom
    "AS44467",  # IRN-STC-AS PJSC Rostelecom
    "AS8557",  # ELKATEL-AS PJSC Rostelecom
    "AS25436",  # KIROV-CAIT-AS PJSC Rostelecom
    "AS41134",  # CTC-OREL-AS PJSC Rostelecom

    # MTS
    "AS8359",   # MTS MTS PJSC
    "AS48176",  # OOOSET-AS MTS PJSC
    "AS28884",  # MR-SIB-MTSAS MTS PJSC
    "AS44895",  # ANTENNA-GARANT-AS MTS PJSC
    "AS209024", # MTS-CLOUD-A MTS PJSC
    "AS30922",  # MTS-FBN-Siberia-AS MTS PJSC
    "AS41822",  # TNGS-NORTH-AS MTS PJSC
    "AS42087",  # KANAL7-AS MTS PJSC
    "AS197023", # ASCOMTELTV MTS PJSC
    "AS15640",  # FPIC-AS MTS PJSC
    "AS39811",  # MTSNET-FAR-EAST-AS MTS PJSC
    "AS48123",  # STREAM-TV-KALUGA MTS PJSC
    "AS48612",  # RTC-ORENBURG-AS MTS PJSC
    "AS49350",  # TINET-AS MTS PJSC
    "AS29190",  # OVERTA-AS MTS PJSC
    "AS21365",  # INTELECA-AS MTS PJSC
    "AS42322",  # LLC-ZHANR-AS MTS PJSC
    "AS44731",  # MWS MTS PJSC
    "AS39001",  # MTS MTS PJSC
    "AS49154",  # MTS-DOM-AS MTS PJSC
    "AS41209",  # COMSTAR-VOLGA MTS PJSC
    "AS43148",  # MTS-KURGAN-AS MTS PJSC
    "AS48124",  # COMSTAR-Regions-TVER MTS PJSC
    "AS31558",  # ZGTK-AS MTS PJSC
    "AS51771",  # MTSBANK Public Joint-Stock Company "MTS Bank"
    "AS44677",  # MTS-NGCLOUD-AS MTS PJSC
    "AS30881",  # TENSOR-AS MTS PJSC
    "AS40993",  # AltairTula-AS MTS PJSC
    "AS60490",  # MTS-CLOUD MTS PJSC
    "AS48000",  # STREAM-TV-TAMBOV-AS MTS PJSC
    "AS20866",  # INTELECOM-AS MTS PJSC
    "AS50071",  # SRDV-AS MTS PJSC
    "AS49665",  # MKS-KISLOVODSK-AS MTS PJSC
    "AS34351",  # MTS-IVANOVO-AS MTS PJSC
    "AS48212",  # MKS-CHITA-AS MTS PJSC
    "AS48100",  # MKS-NSK MTS PJSC
    "AS60891",  # KORYAJMA-MTS-AS MTS PJSC
    "AS48541",  # NVKZ-STREAM-AS MTS PJSC
    "AS48322",  # SVSK-STREAM MTS PJSC
    "AS50240",  # EXTRACOM-AS MTS PJSC
    "AS8580",   # SANDY MTS PJSC
    "AS35728",  # MTS-PENZA-AS MTS PJSC
    "AS13155",  # MTS-IRK-AS MTS PJSC
    "AS49816",  # CMST-Volga-SimbirskAS MTS PJSC
    "AS39799",  # COMINTEL-AS MTS PJSC
    "AS43318",  # SERVTEL-AS MTS PJSC
    "AS13055",  # CSVLG-AS MTS PJSC
    "AS41771",  # MTS-BB-OMSK MTS PJSC
    "AS35473",  # MTSNET-URAL-AS MTS PJSC
    "AS47899",  # TMMTS-AS MTS PJSC
    "AS16012",  # MTSCenter-AS MTS PJSC
    "AS16256",  # ReCom-AS MTS PJSC
    "AS29209",  # SPBMTS-AS MTS PJSC
    "AS42115",  # BASHCELL-AS MTS PJSC
    "AS29194",  # ASN-TVT MTS PJSC
    "AS39858",  # Comstar-Volga-Arzamas MTS PJSC
    "AS44736",  # TSVRN-AS MTS PJSC
    "AS13174",  # MTSNet MTS PJSC
    "AS43720",  # TVK-AS MTS OJSC
    "AS43038",  # TVK-AS MTS PJSC
    "AS48796",  # COMSTAR-R-SML-AS MTS PJSC
    "AS41929",  # SISTEMY-SVYAZI-AS MTS PJSC
    "AS58100",  # DALCOMBANK-AS Public Joint-Stock Company "MTS Bank"
    "AS57681",  # ASN-MGTS-USPD2 PJSC Moscow city telephone network

    # MegaFon
    "AS31133",  # MF-MGSM-AS PJSC MegaFon
    "AS25159",  # SONICDUO-AS PJSC MegaFon
    "AS20632",  # PETERSTAR-AS PJSC MegaFon
    "AS31261",  # GARS-AS PJSC MegaFon
    "AS50928",  # SYNTSIB-AS PJSC MegaFon
    "AS29648",  # COMLINE-AS PJSC MegaFon
    "AS12714",  # MEGAFON-AS PJSC MegaFon
    "AS31195",  # MF-DV-AS PJSC MegaFon
    "AS31208",  # MF-CENTER-AS PJSC MegaFon
    "AS31163",  # MF-KAVKAZ-AS PJSC MegaFon
    "AS13075",  # MEGALABS-AS PJSC MegaFon
    "AS31205",  # MF-SIB-AS PJSC MegaFon
    "AS31213",  # MF-NWGSM-AS PJSC MegaFon
    "AS35298",  # MF-MGSM-AS PJSC MegaFon
    "AS31224",  # MF-UGSM-AS PJSC MegaFon
    "AS6854",   # SYNTERRA-AS PJSC MegaFon
    "AS34552",  # TKURAL-AS PJSC MegaFon
    "AS6850",   # MF-AS PJSC MegaFon
    "AS8263",   # Cloud-Megafon PJSC MegaFon
    "AS47395",  # SCARTEL-AS PJSC MegaFon
    "AS12396",  # MF-MSV-STF PJSC MegaFon
    "AS202804", # Inplat-AS PJSC MegaFon
    "AS24866",  # Cloud-Megafon PJSC MegaFon

    # Vimpelcom
    "AS3216",  # SOVAM-AS PJSC "Vimpelcom"
    "AS3235",  # GOLDENISP-AS PJSC "Vimpelcom"
    "AS8402",  # CORBINA-AS PJSC "Vimpelcom"
    "AS31359",  # FORATEC-AS PJSC "Vimpelcom"
    "AS34038",  # COMTEL-TMN-AS PJSC "Vimpelcom"
    "AS42842",  # HELIOS-TV-AS PJSC "Vimpelcom"
    "AS2599",  # PJSC "Vimpelcom"
    "AS20597",  # ELTEL-AS PJSC "Vimpelcom"
    "AS8350",  # COMBELLGA-AS PJSC "Vimpelcom"
    "AS31425",  # FORATEC-AS PJSC "Vimpelcom"
    "AS2766",  # GLASNET PJSC "Vimpelcom"
    "AS16345",  # BEE-AS PJSC "Vimpelcom"
    "AS8755",  # CITYLINESPB-AS PJSC "Vimpelcom"
    "AS29125",  # TATINT-AS PJSC "Vimpelcom"
    "AS8773",  # AS8773 PJSC "Vimpelcom"
    "AS49144",  # ITCOM-AS PJSC "Vimpelcom"
    "AS21332",  # NTC-AS PJSC "Vimpelcom"
    "AS3253",  # SOVINTEL-EF-AS PJSC "Vimpelcom"
    "AS43687",  # BTL-AS PJSC "Vimpelcom"
    "AS42110",  # STK-AS PJSC "Vimpelcom"
    "AS16043",  # SAMARA-TELECOM-AS PJSC "Vimpelcom"
    "AS21483",  # TEL-AS PJSC "Vimpelcom"
    "AS34644",  # EXTEL-AS PJSC "Vimpelcom"
    "AS20533",  # SAKHTEL-AS PJSC "Vimpelcom"
    "AS8371",  # Vimpelcom-NN PJSC "Vimpelcom"
    "AS34894",  # ATEL-AS PJSC "Vimpelcom"
    "AS34747",  # ISI-AS PJSC "Vimpelcom"
    "AS12543",  # PJSC "Vimpelcom"
    "AS13257",  # POLARCOM-AS PJSC "Vimpelcom"
    "AS28703",  # URAL-INTERCARD-AS PJSC "Vimpelcom"
    "AS42245",  # ITECH-AS PJSC "Vimpelcom"
    "AS13095",  # CTK-NET-AS PJSC "Vimpelcom"
    "AS43275",  # UNET-AS PJSC "Vimpelcom"
    "AS43970",  # magistraly-ru PJSC "Vimpelcom"
    "AS21480",  # WBT-AS PJSC "Vimpelcom"

    # ER-Telecom
    "AS9049",   # ERTH-TRANSIT-AS JSC "ER-Telecom Holding"
    "AS48858",  # Milecom-as JSC "ER-Telecom Holding"
    "AS13094",  # SFO-IX-AS JSC "ER-Telecom Holding"
    "AS25408",  # WESTCALL-SPB-AS JSC "ER-Telecom Holding"
    "AS51034",  # DSI-EAS JSC "ER-Telecom Holding"
    "AS43097",  # WEBRA JSC "ER-Telecom Holding"
    "AS31483",  # ERTELECOM-DC-AS JSC "ER-Telecom Holding"
    "AS62423",  # TCENTER-AS JSC "ER-Telecom Holding"
    "AS25446",  # ERTH-CLOUD-AS JSC "ER-Telecom Holding"
    "AS41733",  # ZTELECOM-AS JSC "ER-Telecom Holding"
    "AS31484",  # Westcall-AS JSC "ER-Telecom Holding"
    "AS49874",  # ERTH-DC JSC "ER-Telecom Holding"
    "AS41682",  # ERTH-TMN-AS JSC "ER-Telecom Holding"
    "AS20807",  # Credolink-ASN JSC "ER-Telecom Holding"
    "AS12772",  # ENFORTA-AS JSC "ER-Telecom Holding"
    "AS41002",  # ERTH-TRANSIT2-AS JSC "ER-Telecom Holding"
    "AS12768",  # ER-TELECOM-AS JSC "ER-Telecom Holding"
    "AS8331",   # RINET-AS JSC "ER-Telecom Holding"
    "AS16300",  # INTERTAX-AREA JSC "ER-Telecom Holding"
    "AS51035",  # UFA-AS JSC "ER-Telecom Holding"
    "AS197140", # DSSV-NET JSC "ER-Telecom Holding"
    "AS42682",  # ERTH-NNOV-AS JSC "ER-Telecom Holding"
    "AS51604",  # EKAT-AS JSC "ER-Telecom Holding"
    "AS31363",  # MOSCOW-AS JSC "ER-Telecom Holding"
    "AS39435",  # EVOLGOGRAD-AS JSC "ER-Telecom Holding"
    "AS50543",  # SARATOV-AS JSC "ER-Telecom Holding"
    "AS57044",  # BRYANSK-AS JSC "ER-Telecom Holding"
    "AS12690",  # MKSNET-AS JSC "ER-Telecom Holding"
    "AS51570",  # SPB-AS JSC "ER-Telecom Holding"
    "AS52207",  # TULA-AS JSC "ER-Telecom Holding"
    "AS43478",  # ERTH-NSK-AS JSC "ER-Telecom Holding"
    "AS56330",  # KURGAN-AS JSC "ER-Telecom Holding"
    "AS51819",  # YAR-AS JSC "ER-Telecom Holding"
    "AS50498",  # LIPETSK-AS JSC "ER-Telecom Holding"
    "AS56981",  # TOMSK-AS JSC "ER-Telecom Holding"
    "AS49048",  # TVER-AS JSC "ER-Telecom Holding"
    "AS50512",  # BARNAUL-AS JSC "ER-Telecom Holding"
    "AS57026",  # CHEB-AS JSC "ER-Telecom Holding"
    "AS42683",  # ERTH-OREN-AS JSC "ER-Telecom Holding"
    "AS24588",  # NETPROVODOV-AS JSC "ER-Telecom Holding"
    "AS50544",  # KRSK-AS JSC "ER-Telecom Holding"
    "AS41661",  # ERTH-CHEL-AS JSC "ER-Telecom Holding"
    "AS21447",  # TCENTER-2-AS JSC "ER-Telecom Holding"
    "AS41727",  # ERTH-KIROV-AS JSC "ER-Telecom Holding"
    "AS41754",  # ERTH-PENZA-AS JSC "ER-Telecom Holding"
    "AS51645",  # IRKUTSK-AS JSC "ER-Telecom Holding"
    "AS41843",  # JSC "ER-Telecom Holding" Omsk branch
    "AS34150",  # RU-ERTH-KRASNODAR-AS JSC "ER-Telecom Holding"
    "AS43314",  # DIANET-AS JSC "ER-Telecom Holding"
    "AS47111",  # RU-AKADO-SPB-AS JSC "ER-Telecom Holding"
    "AS5563",   # URAL JSC "ER-Telecom Holding"
    "AS56377",  # MGSK-AS JSC "ER-Telecom Holding"
    "AS39028",  # ULSK-AS JSC "ER-Telecom Holding"
    "AS8345",   # DSI-IAS JSC "ER-Telecom Holding"
    "AS42116",  # ERTH-NCHLN-AS JSC "ER-Telecom Holding"
    "AS56420",  # RYAZAN-AS JSC "ER-Telecom Holding"
    "AS57378",  # ROSTOV-AS JSC "ER-Telecom Holding"
    "AS198295", # BCI JSC "ER-Telecom Holding"
    "AS34590",  # IZHEVSK-AS JSC "ER-Telecom Holding"
    "AS50542",  # VORONEZH-AS JSC "ER-Telecom Holding"
    "AS34533",  # ESAMARA-AS JSC "ER-Telecom Holding"
    "AS21353",  # ARTCOMS-AS JSC "ER-Telecom Holding"
    "AS41786",  # ERTH-YOLA-AS JSC "ER-Telecom Holding"
    "AS59713",  # ERTH-KURSK-AS JSC "ER-Telecom Holding"
    "AS47911",  # ERTH-AS JSC "ER-Telecom Holding"
    "AS205971", # ASVOLSVL JSC "ER-Telecom Holding"
    "AS204952", # VCIOM JSC "ER-Telecom Holding"
    "AS62287",  # REGION-AS JSC "ER-Telecom Holding"
    "AS41403",  # ULAN-UDE-AS JSC "ER-Telecom Holding"
    "AS34925",  # VLADIVOSTOK-AS JSC "ER-Telecom Holding"
    "AS206661", # O1Telecom JSC "ER-Telecom Holding"

    # Comcor / Akado
    "AS8732",   # COMCOR-AS JSC Comcor
    "AS15582",  # AKADO-B2C-AS JSC Comcor
    "AS44096",  # BFT-AS JSC Comcor
    "AS9068",   # AKADO-AS JSC Comcor
    "AS51011",  # P-T-K-AS JSC Comcor
]


SOURCE_IPINFO = "IPINFO"
SOURCE_MAXMIND = "MAXMIND"
GEOFEED_PREFIX = "GEOFEED:"

_WANTED_AS_CF = {asn.casefold(): asn for asn in WANTED_AS}
_KEYWORDS_AS_CF = [(kw, kw.casefold()) for kw in KEYWORDS_AS]
_KEYWORDS_DOMAIN_CF = [(kw, kw.casefold()) for kw in KEYWORDS_DOMAIN]
_FULL_DOMAIN_CF = {kw.casefold(): kw for kw in FULL_DOMAIN}


def iso_from_maxmind(record: dict) -> str | None:
    if not isinstance(record, dict):
        return None
    country = record.get("country")
    if isinstance(country, dict):
        iso = country.get("iso_code")
        if isinstance(iso, str) and iso:
            return iso
    return None


def iso_from_geofeed(row: list[str]) -> str | None:
    # RFC 8805: prefix,country,region,city,postal
    if len(row) < 2:
        return None
    iso = row[1].strip().upper()
    return iso or None


def country_rules(value: str) -> list[str]:
    iso = value.strip().upper()
    return [f"{{{iso}}}"] if iso in WANTED else []


def ipinfo_as_rules(asn_value: str, as_name_value: str, as_domain_value: str) -> list[str]:
    rules: list[str] = []

    asn = _WANTED_AS_CF.get(asn_value.strip().casefold())
    if asn:
        rules.append(asn)

    as_name = as_name_value.casefold()
    for kw, kw_cf in _KEYWORDS_AS_CF:
        if kw_cf in as_name:
            rules.append(f"AS-NAME:{kw}")

    as_domain = as_domain_value.strip().casefold()
    for kw, kw_cf in _KEYWORDS_DOMAIN_CF:
        if kw_cf in as_domain:
            rules.append(f"AS-DOMAIN:{kw}")

    full_domain = _FULL_DOMAIN_CF.get(as_domain)
    if full_domain:
        rules.append(f"DOMAIN-FULL:{full_domain}")

    return rules


def rule_sort_key(rule: str) -> tuple[int, str]:
    if rule.startswith("{"):
        return (0, rule)
    if rule.startswith("AS-NAME:"):
        return (2, rule)
    if rule.startswith("AS-DOMAIN:"):
        return (3, rule)
    if rule.startswith("DOMAIN-FULL:"):
        return (4, rule)
    return (1, rule)


def source_sort_key(source: str) -> tuple[int, str]:
    if source == SOURCE_IPINFO:
        return (0, "")
    if source == SOURCE_MAXMIND:
        return (1, "")
    return (2, source)


def format_reasons(reasons: set[tuple[str, str]]) -> str:
    by_source: dict[str, set[str]] = {}
    for source, rule in reasons:
        by_source.setdefault(source, set()).add(rule)

    return "; ".join(
        f"{source} {', '.join(sorted(by_source[source], key=rule_sort_key))}"
        for source in sorted(by_source, key=source_sort_key)
    )


def record(store: dict, net, source: str, rules: list[str]) -> None:
    reasons = store.setdefault(net, set())
    for rule in rules:
        reasons.add((source, rule))


def attribute(store: dict, collapsed: list) -> list[set[tuple[str, str]]]:
    reasons: list[set[tuple[str, str]]] = [set() for _ in collapsed]
    bounds = [int(net.broadcast_address) for net in collapsed]
    limit = len(bounds)

    items = [(int(net.network_address), net) for net in store]
    items.sort(key=lambda item: item[0])

    i = 0
    for start, net in items:
        while i < limit and bounds[i] < start:
            i += 1
        if i == limit:
            break
        reasons[i] |= store[net]

    return reasons


def main() -> None:
    base = Path(__file__).resolve().parent

    v4: dict[ipaddress.IPv4Network, set[tuple[str, str]]] = {}
    v6: dict[ipaddress.IPv6Network, set[tuple[str, str]]] = {}

    def store_for(net):
        if net.version == 4:
            return v4
        if net.version == 6:
            return v6
        raise ValueError(f"Unknown IP version: {net.version}")

    # IPinfo CSV
    ipinfo_path = base / IPINFO_CSV
    if not ipinfo_path.exists():
        raise FileNotFoundError(f"File not found: {ipinfo_path}")

    ipinfo_count = 0

    with ipinfo_path.open("r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        i_net = header.index("network")
        i_country = header.index("country_code")
        i_asn = header.index("asn")
        i_as_name = header.index("as_name")
        i_as_domain = header.index("as_domain")

        country_cache: dict[str, list[str]] = {}
        as_cache: dict[tuple[str, str, str], list[str]] = {}

        for row in r:
            country_value = row[i_country]
            country = country_cache.get(country_value)
            if country is None:
                country = country_rules(country_value)
                country_cache[country_value] = country

            as_key = (row[i_asn], row[i_as_name], row[i_as_domain])
            as_rules = as_cache.get(as_key)
            if as_rules is None:
                as_rules = ipinfo_as_rules(*as_key)
                as_cache[as_key] = as_rules

            if not country and not as_rules:
                continue

            net_s = row[i_net]
            if not net_s:
                continue

            net = ipaddress.ip_network(net_s, strict=False)
            record(store_for(net), net, SOURCE_IPINFO, country + as_rules)
            ipinfo_count += 1

    # MaxMind MMDB
    mmdb_path = base / MAXMIND_MMDB
    if not mmdb_path.exists():
        raise FileNotFoundError(f"File not found: {mmdb_path}")

    maxmind_count = 0

    with maxminddb.open_database(str(mmdb_path)) as reader:
        for net, mm_record in reader:
            iso = iso_from_maxmind(mm_record)
            if iso not in WANTED:
                continue

            record(store_for(net), net, SOURCE_MAXMIND, [f"{{{iso}}}"])
            maxmind_count += 1

    # Geofeed CSVs
    geofeed_paths = sorted(base.glob(GEOFEED_GLOB))
    if not geofeed_paths:
        raise FileNotFoundError(f"No files matched: {base / GEOFEED_GLOB}")

    geofeed_counts: dict[str, int] = {}

    for geofeed_path in geofeed_paths:
        source = f"{GEOFEED_PREFIX}{geofeed_path.stem}"
        count = 0

        with geofeed_path.open("r", encoding="utf-8", newline="") as f:
            r = csv.reader(f)
            for row in r:
                if not row or row[0].lstrip().startswith("#"):
                    continue

                iso = iso_from_geofeed(row)
                if iso not in WANTED:
                    continue

                try:
                    net = ipaddress.ip_network(row[0].strip(), strict=False)
                except ValueError:
                    continue

                record(store_for(net), net, source, [f"{{{iso}}}"])
                count += 1

        geofeed_counts[geofeed_path.name] = count

    v4_collapsed = list(ipaddress.collapse_addresses(v4))
    v6_collapsed = list(ipaddress.collapse_addresses(v6))

    all_reasons = [*attribute(v4, v4_collapsed), *attribute(v6, v6_collapsed)]
    all_nets = [*map(str, v4_collapsed), *map(str, v6_collapsed)]

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

    annotated = [
        f"{net} [{format_reasons(reasons)}]"
        for net, reasons in zip(all_nets, all_reasons)
    ]
    annotateddir = base / "annotated"
    annotateddir.mkdir(exist_ok=True)
    (annotateddir / "ips-for-ru-annotated.txt").write_text(
        "\n".join(annotated) + ("\n" if annotated else ""),
        encoding="utf-8",
    )

    print(f"IPinfo: {ipinfo_count}")
    print(f"MaxMind: {maxmind_count}")
    for name, count in geofeed_counts.items():
        print(f"{name}: {count}")
    print(f"IPv4: {len(v4_collapsed)}")
    print(f"IPv6: {len(v6_collapsed)}")
    print(f"Total: {len(all_nets)}")


if __name__ == "__main__":
    main()
