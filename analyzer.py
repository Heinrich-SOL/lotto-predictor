"""
로또 번호 통계 분석 모듈
- AC값(산술적 복합도)
- 총합 분포 (100 ~ 175)
- 홀짝 비율
- 고저 비율 (1~22 vs 23~45)
- 연속 번호 패턴
- 끝수(동일 1의 자리) 패턴
- 번호대(구간) 분산도
"""

from typing import List, Tuple, Dict
from lotto_data import LOTTO_FREQUENCY_1247

def calculate_ac_value(numbers: List[int]) -> int:
    """
    AC값(Arithmetic Complexity, 산술적 복잡도) 계산
    6개 번호 사이의 모든 차이값 종류 수 - (6 - 1)
    - AC값이 7 이상인 조합이 역대 당첨의 80% 이상을 차지
    """
    sorted_nums = sorted(numbers)
    diffs = set()
    for i in range(len(sorted_nums)):
        for j in range(i + 1, len(sorted_nums)):
            diffs.add(sorted_nums[j] - sorted_nums[i])
    return len(diffs) - (len(sorted_nums) - 1)

def get_odd_even_ratio(numbers: List[int]) -> Tuple[int, int]:
    """홀수/짝수 개수 반환 (홀, 짝)"""
    odd_count = sum(1 for n in numbers if n % 2 == 1)
    return odd_count, len(numbers) - odd_count

def get_low_high_ratio(numbers: List[int]) -> Tuple[int, int]:
    """저번호(1~22)/고번호(23~45) 비율 반환"""
    low_count = sum(1 for n in numbers if 1 <= n <= 22)
    return low_count, len(numbers) - low_count

def get_consecutive_stats(numbers: List[int]) -> Tuple[int, int]:
    """
    연속 번호 통계 반환:
    - pairs: 연속 번호 쌍의 개수 (예: [12, 13] -> 1)
    - max_streak: 최장 연속 길이 (예: [12, 13, 14] -> 3)
    """
    sorted_nums = sorted(numbers)
    pairs = 0
    max_streak = 1
    current_streak = 1

    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i + 1] - sorted_nums[i] == 1:
            pairs += 1
            current_streak += 1
            if current_streak > max_streak:
                max_streak = current_streak
        else:
            current_streak = 1

    return pairs, max_streak

def get_section_distribution(numbers: List[int]) -> Dict[str, int]:
    """10단위 구간별 번호 출현 개수 반환"""
    sections = {
        "1~10": 0,
        "11~20": 0,
        "21~30": 0,
        "31~40": 0,
        "41~45": 0
    }
    for n in numbers:
        if 1 <= n <= 10:
            sections["1~10"] += 1
        elif 11 <= n <= 20:
            sections["11~20"] += 1
        elif 21 <= n <= 30:
            sections["21~30"] += 1
        elif 31 <= n <= 40:
            sections["31~40"] += 1
        else:
            sections["41~45"] += 1
    return sections

def get_max_same_last_digit(numbers: List[int]) -> int:
    """동일한 끝자리(1의 자리 수)의 최대 개수 반환"""
    last_digits = [n % 10 for n in numbers]
    from collections import Counter
    counts = Counter(last_digits)
    return max(counts.values()) if counts else 0

def analyze_combination(numbers: List[int]) -> dict:
    """조합의 종합 분석 결과 딕셔너리 반환"""
    sorted_nums = sorted(numbers)
    num_sum = sum(sorted_nums)
    odd, even = get_odd_even_ratio(sorted_nums)
    low, high = get_low_high_ratio(sorted_nums)
    ac = calculate_ac_value(sorted_nums)
    pairs, max_streak = get_consecutive_stats(sorted_nums)
    sections = get_section_distribution(sorted_nums)
    active_sections = sum(1 for count in sections.values() if count > 0)
    max_last_digit = get_max_same_last_digit(sorted_nums)

    # 역대 빈도 점수 (평균 출현 횟수 대비 점수)
    avg_freq = sum(LOTTO_FREQUENCY_1247[n] for n in sorted_nums) / 6.0

    return {
        "numbers": sorted_nums,
        "sum": num_sum,
        "odd_even": f"{odd}:{even}",
        "low_high": f"{low}:{high}",
        "ac_value": ac,
        "consecutive_pairs": pairs,
        "max_consecutive_streak": max_streak,
        "active_sections": active_sections,
        "sections": sections,
        "max_same_last_digit": max_last_digit,
        "avg_historical_frequency": round(avg_freq, 1)
    }

def is_statistically_sound(numbers: List[int]) -> Tuple[bool, List[str]]:
    """
    역대 1등 당첨 통계 필터 검증
    1) 총합: 100 ~ 175 구간
    2) 홀짝 비율: 3:3, 4:2, 2:4
    3) 고저 비율: 3:3, 4:2, 2:4
    4) AC값: 7 이상 (최소 6 이상)
    5) 연속번호: 3연속 이상 금지 (최대 2연속 1쌍 이하 권장)
    6) 동일 끝수: 3개 초과 금지 (예: 3, 13, 23, 33 금지)
    7) 구간 분산: 최소 3개 이상 구간 분산
    """
    issues = []
    res = analyze_combination(numbers)

    # 1) 총합 검증
    if not (100 <= res["sum"] <= 175):
        issues.append(f"총합 이상 ({res['sum']} - 권장: 100~175)")

    # 2) 홀짝 비율 검증
    odd, even = map(int, res["odd_even"].split(":"))
    if (odd, even) not in [(3, 3), (4, 2), (2, 4)]:
        issues.append(f"극단적인 홀짝 비율 ({odd}:{even})")

    # 3) 고저 비율 검증
    low, high = map(int, res["low_high"].split(":"))
    if (low, high) not in [(3, 3), (4, 2), (2, 4)]:
        issues.append(f"극단적인 고저 비율 ({low}:{high})")

    # 4) AC값 검증
    if res["ac_value"] < 7:
        issues.append(f"낮은 산술적 복잡도 (AC {res['ac_value']} - 권장: 7 이상)")

    # 5) 연속 번호 검증
    if res["max_consecutive_streak"] >= 3:
        issues.append(f"3개 이상 연속 번호 발생 (스트릭 {res['max_consecutive_streak']})")

    # 6) 동일 끝수 검증
    if res["max_same_last_digit"] >= 3:
        issues.append(f"동일 끝자리 과다 ({res['max_same_last_digit']}개)")

    # 7) 구간 분산 검증
    if res["active_sections"] < 3:
        issues.append(f"특정 번호대 쏠림 (활성 구간 {res['active_sections']}개)")

    return len(issues) == 0, issues
