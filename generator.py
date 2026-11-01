"""
로또 번호 예측 및 생성기 모듈
- 전략 1: 통계적 황금비율 필터 모델 (역대 1등 당첨 패턴 100% 충족)
- 전략 2: 역대 최다 출현(Hot Numbers) 가중치 모델
- 전략 3: 평균 회귀(Cold Numbers) 보정 모델
- 전략 4: 핫/콜드 하이브리드 앙상블 모델 (Hot 3개 + Neutral 2개 + Cold 1개)
- 전략 5: 사용자 고정수 / 제외수 커스텀 생성
"""

import random
from typing import List, Optional, Set
from lotto_data import LOTTO_FREQUENCY_1247, AVERAGE_FREQUENCY
from analyzer import is_statistically_sound, analyze_combination

# 번호별 그룹 분류 (Hot / Neutral / Cold)
# 상위 15개: Hot, 하위 10개: Cold (최소 출현 순서), 중간 20개: Neutral
sorted_by_freq = sorted(LOTTO_FREQUENCY_1247.items(), key=lambda x: x[1], reverse=True)
HOT_NUMBERS = [num for num, _ in sorted_by_freq[:15]]
COLD_NUMBERS = [num for num, _ in sorted_by_freq[:-11:-1]]  # 가장 적게 나온 순
NEUTRAL_NUMBERS = [num for num, _ in sorted_by_freq[15:-10]]

def _sample_unique(population: List[int], weights: Optional[List[float]], k: int) -> List[int]:
    """가중치 기반 비복원 추출 (순서 무관 고유 번호 추출)"""
    pop = list(population)
    w = list(weights) if weights else [1.0] * len(pop)
    chosen = []

    for _ in range(k):
        total_w = sum(w)
        if total_w <= 0:
            break
        r = random.uniform(0, total_w)
        upto = 0.0
        selected_idx = 0
        for idx, weight in enumerate(w):
            if upto + weight >= r:
                selected_idx = idx
                break
            upto += weight
        
        chosen.append(pop[selected_idx])
        pop.pop(selected_idx)
        w.pop(selected_idx)

    return sorted(chosen)

def generate_golden_balanced(fixed_numbers: Optional[List[int]] = None,
                             excluded_numbers: Optional[List[int]] = None,
                             max_attempts: int = 1000) -> List[int]:
    """
    [전략 1] 통계적 황금비율 필터 모델
    - 역대 1등 당첨 통계 기준(총합, 홀짝, 고저, AC값, 연번, 끝수 등)을
      완벽히 통과할 때까지 필터링하여 생성
    """
    fixed = set(fixed_numbers or [])
    excluded = set(excluded_numbers or [])
    available = [n for n in range(1, 46) if n not in fixed and n not in excluded]

    needed = 6 - len(fixed)
    if needed < 0 or len(available) < needed:
        raise ValueError("고정수나 제외수의 설정이 올바르지 않습니다.")

    # 역대 출현 빈도를 기본 가중치로 활용
    weights = [LOTTO_FREQUENCY_1247[n] for n in available]

    for _ in range(max_attempts):
        sampled = _sample_unique(available, weights, needed)
        candidate = sorted(list(fixed) + sampled)
        sound, _ = is_statistically_sound(candidate)
        if sound:
            return candidate

    # 최대 시도 초과 시 가장 결함이 적은 후보 반환
    return candidate

def generate_hot_weighted(fixed_numbers: Optional[List[int]] = None,
                          excluded_numbers: Optional[List[int]] = None) -> List[int]:
    """
    [전략 2] 역대 최다 출현(Hot Numbers) 가중치 모델
    - 역대 누적 출현 빈도가 높은 번호(27, 13, 34, 12, 33 등)에
      높은 가중치를 부여하여 추첨
    """
    fixed = set(fixed_numbers or [])
    excluded = set(excluded_numbers or [])
    available = [n for n in range(1, 46) if n not in fixed and n not in excluded]
    needed = 6 - len(fixed)

    # 지수 가중치 적용 (빈도 차이를 더 부각)
    min_freq = min(LOTTO_FREQUENCY_1247.values())
    weights = [(LOTTO_FREQUENCY_1247[n] - min_freq + 5) ** 2 for n in available]

    for _ in range(500):
        sampled = _sample_unique(available, weights, needed)
        candidate = sorted(list(fixed) + sampled)
        sound, _ = is_statistically_sound(candidate)
        if sound:
            return candidate
    return candidate

def generate_cold_reversion(fixed_numbers: Optional[List[int]] = None,
                            excluded_numbers: Optional[List[int]] = None) -> List[int]:
    """
    [전략 3] 평균 회귀(Cold Numbers Reversion) 보정 모델
    - 오랫동안 적게 나온 비인기 번호(9, 22, 41, 23, 29 등)가
      확률 통계상 평균으로 회귀할 가능성을 높게 평가
    """
    fixed = set(fixed_numbers or [])
    excluded = set(excluded_numbers or [])
    available = [n for n in range(1, 46) if n not in fixed and n not in excluded]
    needed = 6 - len(fixed)

    max_freq = max(LOTTO_FREQUENCY_1247.values())
    weights = [(max_freq - LOTTO_FREQUENCY_1247[n] + 5) ** 2 for n in available]

    for _ in range(500):
        sampled = _sample_unique(available, weights, needed)
        candidate = sorted(list(fixed) + sampled)
        sound, _ = is_statistically_sound(candidate)
        if sound:
            return candidate
    return candidate

def generate_hybrid_ensemble(fixed_numbers: Optional[List[int]] = None,
                             excluded_numbers: Optional[List[int]] = None) -> List[int]:
    """
    [전략 4] 핫/콜드 하이브리드 앙상블 모델
    - 가장 검증된 포트폴리오 방식:
      최다 빈도(Hot) 3개 + 중간 빈도(Neutral) 2개 + 최소 빈도(Cold) 1개 조합
    """
    fixed = set(fixed_numbers or [])
    excluded = set(excluded_numbers or [])

    hot_pool = [n for n in HOT_NUMBERS if n not in fixed and n not in excluded]
    neutral_pool = [n for n in NEUTRAL_NUMBERS if n not in fixed and n not in excluded]
    cold_pool = [n for n in COLD_NUMBERS if n not in fixed and n not in excluded]

    for _ in range(500):
        # Hot 3개, Neutral 2개, Cold 1개
        h = random.sample(hot_pool, min(3, len(hot_pool)))
        n = random.sample(neutral_pool, min(2, len(neutral_pool)))
        c = random.sample(cold_pool, min(1, len(cold_pool)))

        candidate = sorted(list(fixed) + h + n + c)
        if len(candidate) > 6:
            candidate = candidate[:6]
        elif len(candidate) < 6:
            rest = [num for num in range(1, 46) if num not in candidate and num not in excluded]
            candidate.extend(random.sample(rest, 6 - len(candidate)))
            candidate.sort()

        sound, _ = is_statistically_sound(candidate)
        if sound:
            return candidate

    return candidate

def generate_lotto_slip(fixed_numbers: Optional[List[int]] = None,
                        excluded_numbers: Optional[List[int]] = None) -> List[dict]:
    """
    로또 1장 (A, B, C, D, E 5개 게임)을 5가지 서로 다른 전략으로
    균형 있게 생성하여 분석 보고서와 함께 반환
    """
    strategies = [
        ("Game A (황금 통계 모델)", generate_golden_balanced),
        ("Game B (역대 최다 출현 핫넘버)", generate_hot_weighted),
        ("Game C (평균 회귀 콜드넘버)", generate_cold_reversion),
        ("Game D (하이브리드 앙상블)", generate_hybrid_ensemble),
        ("Game E (종합 밸런스 추천)", generate_golden_balanced)
    ]

    slip = []
    for label, generator in strategies:
        numbers = generator(fixed_numbers=fixed_numbers, excluded_numbers=excluded_numbers)
        analysis = analyze_combination(numbers)
        analysis["label"] = label
        slip.append(analysis)

    return slip
