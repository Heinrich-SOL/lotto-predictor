"""
로또 6/45 역대 통계 데이터 모듈
- 제1회 ~ 1248회 공식 전수 데이터셋 (historical_draws.json) 연동
- 역대 1등 당첨 조합(6개 일치) 전수 중복 검증 엔진
- 실시간 최신 회차 자동 동기화 (신규 동행복권 API 대응)
"""

import os
import json
import urllib.request
from typing import List, Tuple, Dict, Set, Optional

DATA_DIR = os.path.dirname(__file__)
HISTORICAL_DRAWS_FILE = os.path.join(DATA_DIR, "historical_draws.json")
CUSTOM_DRAWS_FILE = os.path.join(DATA_DIR, "custom_draws.json")

# 오프라인/파일 부재 시 백업용 기본 빈도표 (1~1248회 기준)
FALLBACK_LOTTO_FREQUENCY = {
    1: 204,  2: 193,  3: 204,  4: 199,  5: 179,
    6: 201,  7: 203,  8: 184,  9: 165, 10: 192,
    11: 194, 12: 208, 13: 212, 14: 196, 15: 196,
    16: 202, 17: 204, 18: 200, 19: 193, 20: 202,
    21: 193, 22: 170, 23: 171, 24: 203, 25: 178,
    26: 198, 27: 216, 28: 185, 29: 174, 30: 190,
    31: 203, 32: 181, 33: 207, 34: 211, 35: 194,
    36: 191, 37: 200, 38: 205, 39: 193, 40: 196,
    41: 170, 42: 192, 43: 202, 44: 190, 45: 198
}

def load_data():
    """
    역대 전수 당첨 데이터(historical_draws.json) 및 추가 회차를 로드하여
    빈도수, 총 회차수, 평균 빈도, 전수 당첨목록 및 O(1) 중복조회용 Set을 반환합니다.
    """
    draws_list = []
    freq = {i: 0 for i in range(1, 46)}
    
    # 1. historical_draws.json 로드
    if os.path.exists(HISTORICAL_DRAWS_FILE):
        try:
            with open(HISTORICAL_DRAWS_FILE, "r", encoding="utf-8") as f:
                draws_list = json.load(f)
        except Exception:
            draws_list = []

    # 2. custom_draws.json (추가 회차) 병합
    if os.path.exists(CUSTOM_DRAWS_FILE):
        try:
            with open(CUSTOM_DRAWS_FILE, "r", encoding="utf-8") as f:
                custom_draws = json.load(f)
                existing_nos = {d["draw_no"] for d in draws_list}
                for c in custom_draws:
                    if c["draw_no"] not in existing_nos:
                        draws_list.append(c)
        except Exception:
            pass

    draws_list.sort(key=lambda x: x["draw_no"])

    # 빈도수 계산
    if draws_list:
        for d in draws_list:
            for n in d.get("numbers", []):
                if 1 <= n <= 45:
                    freq[n] += 1
            bonus = d.get("bonus")
            if bonus and 1 <= bonus <= 45:
                freq[bonus] += 1
        total_draws = len(draws_list)
    else:
        freq = dict(FALLBACK_LOTTO_FREQUENCY)
        total_draws = 1248

    avg_freq = sum(freq.values()) / 45.0
    
    # O(1) 6개 일치 조회용 frozenset 집합
    combos_set = {frozenset(d["numbers"]) for d in draws_list if "numbers" in d}

    return freq, total_draws, avg_freq, draws_list, combos_set

def check_history_overlap(numbers: List[int], draws_list: Optional[List[dict]] = None) -> dict:
    """
    생성된 6개 번호 조합이 역대 당첨번호와 얼마나 일치하는지 전수 검증
    - is_exact_duplicate: 역대 1등 당첨번호(6개 일치)와 100% 동일한지 여부
    - exact_draw_no: 동일한 경우 해당 회차 번호
    - max_match_count: 역대 최대 일치 개수 (예: 3개, 4개, 5개)
    - max_matches: 최대 일치한 회차 정보 목록 [{'draw_no': 540, 'matched': [3, 14, 25, 33]}]
    """
    if draws_list is None:
        draws_list = HISTORICAL_DRAWS

    num_set = set(numbers)
    exact_draw_no = None
    max_match_count = 0
    max_matches = []
    five_matches = []

    for d in draws_list:
        d_nums = set(d.get("numbers", []))
        intersection = num_set & d_nums
        cnt = len(intersection)
        
        if cnt == 6:
            exact_draw_no = d.get("draw_no")
            max_match_count = 6
        
        if cnt > max_match_count:
            max_match_count = cnt
            max_matches = [{
                "draw_no": d.get("draw_no"),
                "date": d.get("date", ""),
                "matched": sorted(list(intersection))
            }]
        elif cnt == max_match_count and cnt >= 4:
            max_matches.append({
                "draw_no": d.get("draw_no"),
                "date": d.get("date", ""),
                "matched": sorted(list(intersection))
            })

        if cnt == 5:
            five_matches.append({
                "draw_no": d.get("draw_no"),
                "date": d.get("date", ""),
                "matched": sorted(list(intersection))
            })

    is_exact_duplicate = (exact_draw_no is not None)

    return {
        "is_exact_duplicate": is_exact_duplicate,
        "exact_draw_no": exact_draw_no,
        "max_match_count": max_match_count,
        "max_matches": max_matches[:5],  # 상위 5개 표시
        "five_match_count": len(five_matches),
        "five_matches": five_matches[:5]
    }

def add_custom_draw(draw_no: int, numbers: list, bonus: int, date: str = "",
                     first_win_amount: int = 0, first_win_count: int = 0):
    """새로운 회차 데이터를 저장 및 갱신"""
    item = {
        "draw_no": draw_no,
        "numbers": sorted(numbers),
        "bonus": bonus,
        "date": date,
        "first_win_amount": first_win_amount,
        "first_win_count": first_win_count
    }

    # historical_draws.json이 있으면 거기에 업데이트
    if os.path.exists(HISTORICAL_DRAWS_FILE):
        try:
            with open(HISTORICAL_DRAWS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            data = [d for d in data if d.get("draw_no") != draw_no]
            data.append(item)
            data.sort(key=lambda x: x["draw_no"])
            with open(HISTORICAL_DRAWS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # custom_draws.json에도 백업
    custom_list = []
    if os.path.exists(CUSTOM_DRAWS_FILE):
        try:
            with open(CUSTOM_DRAWS_FILE, "r", encoding="utf-8") as f:
                custom_list = json.load(f)
        except Exception:
            custom_list = []
    custom_list = [d for d in custom_list if d.get("draw_no") != draw_no]
    custom_list.append(item)
    custom_list.sort(key=lambda x: x["draw_no"])
    with open(CUSTOM_DRAWS_FILE, "w", encoding="utf-8") as f:
        json.dump(custom_list, f, ensure_ascii=False, indent=2)

    # 전역 변수 갱신
    refresh_data()

def fetch_online_draw(draw_no: int):
    """동행복권 신규 및 기존 API에서 특정 회차 당첨결과 자동 조회"""
    # 1. 신규 API 엔드포인트 시도
    new_url = f"https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do?srchLtEpsd={draw_no}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        req = urllib.request.Request(new_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            items = res_data.get("data", {}).get("list", [])
            if items:
                row = items[0]
                nums = [row[f"tm{i}WnNo"] for i in range(1, 7)]
                bonus = row.get("bnsWnNo")
                date_str = str(row.get("ltRflYmd", ""))
                if len(date_str) == 8:
                    date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                amt = row.get("rnk1WnAmt", 0)
                cnt = row.get("rnk1WnNope", 0)
                return nums, bonus, date_str, amt, cnt
    except Exception:
        pass

    # 2. 구형 API 엔드포인트 폴백
    old_url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
    try:
        req = urllib.request.Request(old_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get("returnValue") == "success":
                nums = [data[f"drwtNo{i}"] for i in range(1, 7)]
                bonus = data.get("bnusNo")
                date = data.get("drwNoDate", "")
                amt = data.get("firstWinamnt", 0)
                cnt = data.get("firstPrzwnerCo", 0)
                return nums, bonus, date, amt, cnt
    except Exception:
        pass

    return None

def refresh_data():
    global LOTTO_FREQUENCY_1248, TOTAL_DRAWS, AVERAGE_FREQUENCY, HISTORICAL_DRAWS, HISTORICAL_COMBOS_SET
    LOTTO_FREQUENCY_1248, TOTAL_DRAWS, AVERAGE_FREQUENCY, HISTORICAL_DRAWS, HISTORICAL_COMBOS_SET = load_data()

# 초기 전역 변수 초기화
LOTTO_FREQUENCY_1248, TOTAL_DRAWS, AVERAGE_FREQUENCY, HISTORICAL_DRAWS, HISTORICAL_COMBOS_SET = load_data()
