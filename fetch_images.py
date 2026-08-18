#!/usr/bin/env python3
# 네이버 이미지 검색 -> assets/cars/{slug}.jpg
# 후보 여러 개를 받아 "가로형 외관 사진"(aspect 1.25~2.0, 폭>=380)을 자동 채택.
import urllib.parse, urllib.request, re, os, sys, io, time
from PIL import Image

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "cars")
os.makedirs(DIR, exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# (slug, query) — index.html POOL과 1:1. query에 '외관' 자동 부가.
ITEMS = [
 ("morning","기아 모닝 2022"),("ray","기아 레이 2023"),("casper","현대 캐스퍼"),
 ("venue","현대 베뉴"),("k3","기아 K3 2022"),("avante","현대 아반떼 CN7"),
 ("kona","현대 코나 2023"),("seltos","기아 셀토스"),("niro","기아 니로 2세대"),
 ("sonata","현대 쏘나타 디엣지"),("k5","기아 K5 3세대"),("tucson","현대 투싼 NX4"),
 ("torres","KG모빌리티 토레스"),("sportage","기아 스포티지 5세대"),("stinger","기아 스팅어"),
 ("ioniq5","현대 아이오닉5"),("santafe","현대 싼타페 MX5"),("sorento","기아 쏘렌토 MQ4"),
 ("ev6","기아 EV6"),("k8","기아 K8"),("grandeur","현대 그랜저 GN7"),
 ("carnival","기아 카니발 4세대"),("palisade","현대 팰리세이드"),("gv70","제네시스 GV70"),
 ("g80","제네시스 G80"),("gv80","제네시스 GV80"),("ev9","기아 EV9"),("g90","제네시스 G90"),
 ("mini","미니 쿠퍼 3도어"),("golf","폭스바겐 골프 8세대"),("camry","토요타 캠리 8세대"),
 ("model3","테슬라 모델3 하이랜드"),("audi-a4","아우디 A4 B9"),("bmw3","BMW 3시리즈 G20"),
 ("modely","테슬라 모델Y"),("benz-c","벤츠 C클래스 W206"),("lexus-es","렉서스 ES 7세대"),
 ("mustang","포드 머스탱 6세대"),("xc60","볼보 XC60 2세대"),("audi-a6","아우디 A6 C8"),
 ("bmw5","BMW 5시리즈 G30"),("benz-e","벤츠 E클래스 W213"),("benz-glc","벤츠 GLC"),
 ("discovery","랜드로버 디스커버리 스포츠"),("panamera","포르쉐 파나메라"),("bmwx5","BMW X5 G05"),
 ("cayenne","포르쉐 카이엔"),("amggt","벤츠 AMG GT"),
 # --- 국산 확장 ---
 ("spark","쉐보레 스파크"),("tivoli","KG모빌리티 티볼리"),("maxcruz","현대 맥스크루즈"),
 ("sm6","르노 SM6"),("malibu","쉐보레 말리부"),("xm3","르노 XM3"),
 ("trailblazer","쉐보레 트레일블레이저"),("casper-ev","현대 캐스퍼 일렉트릭"),("qm6","르노 QM6"),
 ("korando","KG모빌리티 코란도"),("trax","쉐보레 트랙스 크로스오버"),("veloster-n","현대 벨로스터 N"),
 ("kona-ev","현대 코나 일렉트릭"),("rexton-sports","KG모빌리티 렉스턴 스포츠"),("avante-n","현대 아반떼 N"),
 ("ev3","기아 EV3"),("equinox","쉐보레 이쿼녹스"),("torres-evx","KG모빌리티 토레스 EVX"),
 ("g70","제네시스 G70"),("rexton","KG모빌리티 렉스턴"),("staria","현대 스타리아 라운지"),
 ("k9","기아 K9"),("ioniq6","현대 아이오닉6"),("colorado","쉐보레 콜로라도"),
 ("traverse","쉐보레 트래버스"),("mohave","기아 모하비 더 마스터"),("gv60","제네시스 GV60"),
 ("carnival-hev","기아 카니발 하이브리드"),("nexo","현대 넥쏘"),("ioniq5-n","현대 아이오닉5 N"),
 ("ioniq9","현대 아이오닉9"),("gv80-coupe","제네시스 GV80 쿠페"),
 # --- 수입 확장 ---
 ("peugeot-3008","푸조 3008"),("tiguan","폭스바겐 티구안"),("prius","토요타 프리우스 5세대"),
 ("accord","혼다 어코드"),("rav4","토요타 RAV4"),("arteon","폭스바겐 아테온"),
 ("crv","혼다 CR-V"),("benz-cla","벤츠 CLA"),("countryman","미니 컨트리맨"),
 ("bmw4","BMW 4시리즈 쿠페"),("benz-glb","벤츠 GLB"),("bmwx3","BMW X3 G01"),
 ("audi-q5","아우디 Q5"),("wrangler","지프 랭글러 루비콘"),("lexus-rx","렉서스 RX 5세대"),
 ("xc90","볼보 XC90"),("cayman","포르쉐 718 케이맨"),("benz-gle","벤츠 GLE"),
 ("bmw7","BMW 7시리즈 G70"),("benz-s","벤츠 S클래스 W223"),
]

def fetch(url, ref=None, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent":UA,"Accept-Language":"ko-KR,ko;q=0.9"})
    if ref: req.add_header("Referer", ref)
    return urllib.request.urlopen(req, timeout=timeout).read()

def candidates(query):
    q = urllib.parse.quote(query + " 외관")
    html = fetch("https://search.naver.com/search.naver?where=image&query="+q).decode("utf-8","ignore")
    srcs = re.findall(r'src=(http[^&"\\]+)', html)
    seen, out = set(), []
    for s in srcs:
        if s in seen: continue
        seen.add(s); out.append(s)
    return out[:14]

def good(data):
    try:
        im = Image.open(io.BytesIO(data)); w,h = im.size
    except Exception:
        return None
    if w < 380: return None
    ar = w/h
    if ar < 1.25 or ar > 2.05: return None   # 로고(정사각)/인물(세로)/일부 실내 배제
    return im.convert("RGB")

force = "-f" in sys.argv
only = [a for a in sys.argv[1:] if not a.startswith("-")]
for slug, query in ITEMS:
    if only and slug not in only: continue
    out = os.path.join(DIR, slug+".jpg")
    if not force and os.path.exists(out) and os.path.getsize(out) > 8000:
        print("skip ", slug); continue
    try:
        cands = candidates(query)
    except Exception as e:
        print("ERR  ", slug, e); continue
    picked = False
    for src in cands:
        u = "https://search.pstatic.net/common/?src="+src+"&type=b400"
        try:
            data = fetch(u, ref="https://search.naver.com/")
            im = good(data)
            if im:
                im.save(out, "JPEG", quality=88); print("OK   ", slug, f"({query}) {im.size}"); picked=True; break
        except Exception:
            continue
    if not picked: print("FAIL ", slug, f"({query})")
    time.sleep(0.3)
print("done ->", DIR)
