"""
로또 번호 예측 및 생성기 모듈 (TOP N 순위 풀 필터링 지원)
"""

import random
from typing import List, Optional, Set
import lotto_data
from analyzer import is_statistically_sound, analyze_combination

def get_ranked_pool(top_n: int = 45) -> List[int]:
    """출현 빈도 순위 상위 top_n개 번호 리스트 반환"""
    freq, _, _, _ = lotto_data.load_data()
    sorted_by_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [num for num, _ in sorted_by_freq[:top_n]]

def _sample_unique(population: List[int], weights: Optional[List[float]], k: int) -> List[int]:
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
                             top_n_rank: int = 45,
                             max_attempts: int = 1000) -> List[int]:
    """[전략 1] 통계적 황금비율 필터 모델 (지정 TOP N 순위 풀 내 조합)"""
    fixed = set(fixed_numbers or [])
    excluded = set(excluded_numbers or [])
    freq, _, _, _ = lotto_data.load_data()

    pool = get_ranked_pool(top_n_rank)
    available = [n for n in pool if n not in fixed and n not in excluded]

    needed = 6 - len(fixed)
    if len(available) < needed:
        available = [n for n in range(1, 46) if n not in fixed and n not in excluded]

    weights = [freq[n] for n in available]

    for _ in range(max_attempts):
        sampled = _sample_unique(available, weights, needed)
        candidate = sorted(list(fixed) + sampled)
        sound, _ = is_statistically_sound(candidate)
        if sound:
            return candidate

    return sorted(list(fixed) + _sample_unique(available, weights, needed))

def generate_hot_weighted(fixed_numbers: Optional[List[int]] = None,
                          excluded_numbers: Optional[List[int]] = None,
                          top_n_rank: int = 45) -> List[int]:
    """[전략 2] 역대 최다 출현(Hot Numbers) 가중치 모델"""
    fixed = set(fixed_numbers or [])
    excluded = set(excluded_numbers or [])
    freq, _, _, _ = lotto_data.load_data()

    pool = get_ranked_pool(top_n_rank)
    available = [n for n in pool if n not in fixed and n not in excluded]
    needed = 6 - len(fixed)
    if len(available) < needed:
        available = [n for n in range(1, 46) if n not in fixed and n not in excluded]

    min_freq = min(freq.values())
    weights = [(freq[n] - min_freq + 5) ** 2 for n in available]

    for _ in range(500):
        sampled = _sample_unique(available, weights, needed)
        candidate = sorted(list(fixed) + sampled)
        sound, _ = is_statistically_sound(candidate)
        if sound:
            return candidate
    return sorted(list(fixed) + _sample_unique(available, weights, needed))

def generate_cold_reversion(fixed_numbers: Optional[List[int]] = None,
                            excluded_numbers: Optional[List[int]] = None,
                            top_n_rank: int = 45) -> List[int]:
    """[전략 3] 풀 내 평균 회귀(Cold Numbers) 보정 모델"""
    fixed = set(fixed_numbers or [])
    excluded = set(excluded_numbers or [])
    freq, _, _, _ = lotto_data.load_data()

    pool = get_ranked_pool(top_n_rank)
    available = [n for n in pool if n not in fixed and n not in excluded]
    needed = 6 - len(fixed)
    if len(available) < needed:
        available = [n for n in range(1, 46) if n not in fixed and n not in excluded]

    max_freq = max(freq.values())
    weights = [(max_freq - freq[n] + 5) ** 2 for n in available]

    for _ in range(500):
        sampled = _sample_unique(available, weights, needed)
        candidate = sorted(list(fixed) + sampled)
        sound, _ = is_statistically_sound(candidate)
        if sound:
            return candidate
    return sorted(list(fixed) + _sample_unique(available, weights, needed))

def generate_hybrid_ensemble(fixed_numbers: Optional[List[int]] = None,
                             excluded_numbers: Optional[List[int]] = None,
                             top_n_rank: int = 45) -> List[int]:
    """[전략 4] 핫/콜드 하이브리드 앙상블 모델"""
    fixed = set(fixed_numbers or [])
    excluded = set(excluded_numbers or [])

    pool = get_ranked_pool(top_n_rank)
    h_pool = [n for n in pool[:len(pool)//2] if n not in fixed and n not in excluded]
    c_pool = [n for n in pool[len(pool)//2:] if n not in fixed and n not in excluded]

    for _ in range(500):
        h = random.sample(h_pool, min(4, len(h_pool)))
        c = random.sample(c_pool, min(2, len(c_pool)))
        candidate = sorted(list(fixed) + h + c)
        if len(candidate) > 6:
            candidate = candidate[:6]
        elif len(candidate) < 6:
            rest = [n for n in pool if n not in candidate and n not in excluded]
            if len(rest) >= 6 - len(candidate):
                candidate.extend(random.sample(rest, 6 - len(candidate)))
            candidate.sort()

        sound, _ = is_statistically_sound(candidate)
        if sound:
            return candidate

    return candidate

def generate_lotto_slip(fixed_numbers: Optional[List[int]] = None,
                        excluded_numbers: Optional[List[int]] = None,
                        top_n_rank: int = 45) -> List[dict]:
    """로또 1장 (5게임) 생성"""
    strategies = [
        ("Game A (황금 통계 모델)", generate_golden_balanced),
        ("Game B (최상위 빈도 핫넘버)", generate_hot_weighted),
        ("Game C (풀 내 평균 회귀)", generate_cold_reversion),
        ("Game D (하이브리드 앙상블)", generate_hybrid_ensemble),
        ("Game E (종합 복합도 밸런스)", generate_golden_balanced)
    ]

    slip = []
    for label, generator_fn in strategies:
        numbers = generator_fn(fixed_numbers=fixed_numbers,
                               excluded_numbers=excluded_numbers,
                               top_n_rank=top_n_rank)
        analysis = analyze_combination(numbers)
        analysis["label"] = label
        slip.append(analysis)

    return slip
