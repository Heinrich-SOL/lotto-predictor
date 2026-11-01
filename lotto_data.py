"""
로또 6/45 역대 통계 데이터 (제1회 ~ 1247회 기본 누적 통계 + 수동/자동 추가 회차 자동 병합)
"""

import os
import json
import urllib.request

# 기본 누적 출현 횟수 (1회 ~ 1247회 기준)
BASE_LOTTO_FREQUENCY = {
    1: 204,  2: 193,  3: 204,  4: 199,  5: 179,
    6: 201,  7: 204,  8: 184,  9: 165, 10: 191,
    11: 194, 12: 208, 13: 212, 14: 196, 15: 196,
    16: 201, 17: 204, 18: 199, 19: 193, 20: 202,
    21: 193, 22: 169, 23: 171, 24: 203, 25: 178,
    26: 198, 27: 215, 28: 185, 29: 174, 30: 190,
    31: 203, 32: 181, 33: 207, 34: 211, 35: 194,
    36: 190, 37: 200, 38: 204, 39: 193, 40: 196,
    41: 170, 42: 191, 43: 202, 44: 190, 45: 198
}

BASE_TOTAL_DRAWS = 1247
CUSTOM_DRAWS_FILE = os.path.join(os.path.dirname(__file__), "custom_draws.json")

def load_data():
    """기본 데이터와 사용자가 수동/자동으로 추가한 custom_draws.json을 병합하여 반환"""
    freq = dict(BASE_LOTTO_FREQUENCY)
    total_draws = BASE_TOTAL_DRAWS
    custom_list = []

    if os.path.exists(CUSTOM_DRAWS_FILE):
        try:
            with open(CUSTOM_DRAWS_FILE, "r", encoding="utf-8") as f:
                custom_list = json.load(f)
                for item in custom_list:
                    total_draws += 1
                    for n in item.get("numbers", []):
                        if n in freq:
                            freq[n] += 1
                    bonus = item.get("bonus")
                    if bonus and bonus in freq:
                        freq[bonus] += 1
        except Exception:
            custom_list = []

    avg_freq = sum(freq.values()) / 45.0
    return freq, total_draws, avg_freq, custom_list

def add_custom_draw(draw_no: int, numbers: list, bonus: int, date: str = ""):
    """새로운 회차 데이터를 custom_draws.json에 영구 저장"""
    _, _, _, custom_list = load_data()
    custom_list = [item for item in custom_list if item.get("draw_no") != draw_no]
    custom_list.append({
        "draw_no": draw_no,
        "numbers": sorted(numbers),
        "bonus": bonus,
        "date": date
    })
    custom_list.sort(key=lambda x: x["draw_no"])

    with open(CUSTOM_DRAWS_FILE, "w", encoding="utf-8") as f:
        json.dump(custom_list, f, ensure_ascii=False, indent=2)

def fetch_online_draw(draw_no: int):
    """동행복권 API에서 특정 회차 당첨결과 자동 조회 (인터넷 연결 시)"""
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get("returnValue") == "success":
                nums = [data[f"drwtNo{i}"] for i in range(1, 7)]
                bonus = data.get("bnusNo")
                date = data.get("drwNoDate", "")
                return nums, bonus, date
    except Exception:
        pass
    return None

# 초기 전역 변수
LOTTO_FREQUENCY_1247, TOTAL_DRAWS, AVERAGE_FREQUENCY, CUSTOM_DRAWS = load_data()
