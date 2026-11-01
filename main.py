"""
로또 6/45 역대 통계 데이터 기반 번호 생성기 및 분석기 (메인 실행 파일)
"""

import sys

# Windows 콘솔 인코딩 대응
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from lotto_data import LOTTO_FREQUENCY_1247, TOTAL_DRAWS, AVERAGE_FREQUENCY
from analyzer import is_statistically_sound, analyze_combination
from generator import (
    generate_lotto_slip,
    generate_golden_balanced,
    generate_hot_weighted,
    generate_cold_reversion,
    generate_hybrid_ensemble,
    HOT_NUMBERS,
    COLD_NUMBERS
)

def format_lotto_numbers(nums):
    """로또 번호 출력 포맷팅 (2자리 정렬)"""
    return "  ".join(f"[{n:02d}]" for n in nums)

def print_header():
    print("=" * 65)
    print("      [★] 로또 6/45 역대 빅데이터 분석 & 번호 생성기 [★]")
    print(f"      (제1회 ~ 제{TOTAL_DRAWS}회 누적 통계 분석 데이터 탑재)")
    print("=" * 65)

def print_stats_summary():
    print("\n[■ 역대 로또 통계 핵심 요약]")
    print(f"- 누적 분석 회차: 총 {TOTAL_DRAWS}회")
    print(f"- 번호당 평균 출현 횟수: 약 {AVERAGE_FREQUENCY:.1f}회")
    print(f"- 역대 최다 출현 TOP 5: {', '.join(f'{n}번({LOTTO_FREQUENCY_1247[n]}회)' for n in HOT_NUMBERS[:5])}")
    print(f"- 역대 최소 출현 TOP 5: {', '.join(f'{n}번({LOTTO_FREQUENCY_1247[n]}회)' for n in COLD_NUMBERS[:5])}")
    print("- 1등 당첨 표준 황금 비율:")
    print("  * 총합: 100 ~ 175 (전체 당첨의 약 78%)")
    print("  * 홀짝 비율: 3:3 또는 4:2, 2:4 (약 80%)")
    print("  * 산술적 복잡도(AC값): 7 이상 (약 82%)")
    print("  * 연속 번호: 0쌍 또는 1쌍 포함 (약 85%)")
    print("=" * 65)

def run_generate_slip(fixed=None, excluded=None):
    print("\n[◆ 역대 데이터 기반 5게임(1세트) 추천 번호 생성 결과]")
    if fixed:
        print(f"  * 고정수: {fixed}")
    if excluded:
        print(f"  * 제외수: {excluded}")
    print("-" * 65)

    slip = generate_lotto_slip(fixed_numbers=fixed, excluded_numbers=excluded)
    for game in slip:
        num_str = format_lotto_numbers(game["numbers"])
        print(f"[{game['label']}]")
        print(f"  -> 번호: {num_str}")
        print(f"     [분석] 합계: {game['sum']:3d} | 홀짝: {game['odd_even']} | 고저: {game['low_high']} | AC값: {game['ac_value']} | 연번: {game['consecutive_pairs']}쌍 | 평균출현: {game['avg_historical_frequency']}회")
        print()
    print("=" * 65)

def main():
    print_header()
    print_stats_summary()

    # 기본 5게임 자동 생성 실행
    run_generate_slip()

    while True:
        print("\n[메뉴 선택]")
        print("1. 새 5게임 번호 다시 뽑기")
        print("2. 고정수/제외수 지정하여 번호 생성")
        print("3. 종료")
        choice = input("선택하세요 (1-3): ").strip()

        if choice == "1":
            run_generate_slip()
        elif choice == "2":
            try:
                fixed_raw = input("고정할 번호를 쉼표로 입력 (없으면 엔터): ").strip()
                fixed = [int(x.strip()) for x in fixed_raw.split(",") if x.strip()]

                excluded_raw = input("제외할 번호를 쉼표로 입력 (없으면 엔터): ").strip()
                excluded = [int(x.strip()) for x in excluded_raw.split(",") if x.strip()]

                run_generate_slip(fixed=fixed, excluded=excluded)
            except Exception as e:
                print(f"입력 오류: {e}")
        elif choice == "3":
            print("\n행운을 빕니다! 프로그램을 종료합니다.")
            break
        else:
            print("올바른 번호를 입력해주세요.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print_header()
        print_stats_summary()
        run_generate_slip()
    else:
        main()
