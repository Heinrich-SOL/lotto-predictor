"""
로또 6/45 역대 통계 데이터 기반 번호 생성기 및 분석기 (메인 실행 파일)
"""

import sys

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import lotto_data
from analyzer import is_statistically_sound, analyze_combination
import generator

def format_lotto_numbers(nums):
    return "  ".join(f"[{n:02d}]" for n in nums)

def print_header():
    print("=" * 65)
    print("      [★] 로또 6/45 역대 빅데이터 분석 & 번호 생성기 [★]")
    print(f"      (제1회 ~ 제{lotto_data.TOTAL_DRAWS}회 역대 1등 당첨번호 중복 배제 필터 가동)")
    print("=" * 65)

def print_stats_summary():
    freq, total_draws, avg_freq, custom_draws, _ = lotto_data.load_data()
    sorted_by_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    hot = [num for num, _ in sorted_by_freq[:5]]
    cold = [num for num, _ in sorted_by_freq[:-6:-1]]

    print("\n[■ 역대 로또 통계 핵심 요약]")
    print(f"- 누적 분석 회차: 총 {total_draws}회 (수동/자동 추가: {len(custom_draws)}건)")
    print(f"- 번호당 평균 출현 횟수: 약 {avg_freq:.1f}회")
    print(f"- 역대 최다 출현 TOP 5: {', '.join(f'{n}번({freq[n]}회, {(freq[n]/total_draws)*100:.1f}%)' for n in hot)}")
    print(f"- 역대 최소 출현 TOP 5: {', '.join(f'{n}번({freq[n]}회, {(freq[n]/total_draws)*100:.1f}%)' for n in cold)}")
    print("- 1등 당첨 표준 황금 비율: 합계 100~175 | 홀짝 3:3, 4:2 | AC 7 이상")
    print(f"- 역대 1등 중복 배제: 1회~{total_draws}회 100% 전수 검증 필터 적용 (중복 번호 차단)")
    print("=" * 65)

def print_all_rates():
    freq, total_draws, _, _, _ = lotto_data.load_data()
    sorted_by_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)

    print("\n[📊 1번~45번 전체 번호별 출현 횟수 및 비율(%) 순위표]")
    print("-" * 65)
    print(" 순위 | 번호 | 출현 횟수 | 출현 확률(회차 대비 %) ")
    print("-" * 65)
    for rank, (num, count) in enumerate(sorted_by_freq, 1):
        rate = (count / total_draws) * 100
        bar = "■" * int(rate // 2)
        print(f" {rank:2d}위 | [{num:02d}번] | {count:3d}회 | {rate:5.2f}% {bar}")
    print("-" * 65)

def run_generate_slip(fixed=None, excluded=None, top_n_rank=45):
    print(f"\n[◆ 역대 데이터 기반 5게임 추천 번호 생성 (적용 순위: TOP {top_n_rank}위)]")
    print("  * 필터: 역대 1등 당첨번호와 6개 일치 조합 100% 배제 & 5게임 상호 중복 방지")
    if fixed:
        print(f"  * 고정수: {fixed}")
    if excluded:
        print(f"  * 제외수: {excluded}")
    print("-" * 65)

    slip = generator.generate_lotto_slip(fixed_numbers=fixed, excluded_numbers=excluded, top_n_rank=top_n_rank)
    for game in slip:
        num_str = format_lotto_numbers(game["numbers"])
        print(f"[{game['label']}]")
        print(f"  -> 번호: {num_str}")
        print(f"     [검증] {game['overlap_summary']}")
        print(f"     [분석] 합계: {game['sum']:3d} | 홀짝: {game['odd_even']} | 고저: {game['low_high']} | AC값: {game['ac_value']} | 연번: {game['consecutive_pairs']}쌍 | 평균출현: {game['avg_historical_frequency']}회")
        print()
    print("=" * 65)

def handle_check_custom_numbers():
    print("\n[🔍 내 번호 역대 당첨 이력 및 중복 검사]")
    raw = input("확인할 번호 6개를 입력하세요 (공백 또는 쉼표 구분): ").strip()
    try:
        nums = [int(x.strip()) for x in raw.replace(",", " ").split() if x.strip()]
        if len(nums) != 6:
            print("오류: 번호는 정확히 6개여야 합니다.")
            return
        if len(set(nums)) != 6:
            print("오류: 번호에 중복이 있습니다.")
            return
        for n in nums:
            if n < 1 or n > 45:
                print("오류: 번호는 1부터 45 사이여야 합니다.")
                return

        analysis = analyze_combination(nums)
        ov = analysis["overlap_info"]
        print("-" * 60)
        print(f"입력 번호: {format_lotto_numbers(analysis['numbers'])}")
        print(f"검증 결과: {analysis['overlap_summary']}")
        if ov["is_exact_duplicate"]:
            print(f"⚠️ [주의] 제{ov['exact_draw_no']}회 1등 당첨번호와 완전히 동일합니다!")
        else:
            print(f"✅ 역대 1회부터 {lotto_data.TOTAL_DRAWS}회까지 1등으로 나온 적이 없는 미당첨 번호입니다.")

        print(f"- 역대 최대 일치 개수: {ov['max_match_count']}개")
        if ov["max_matches"]:
            print("  최다 일치 회차 목록:")
            for m in ov["max_matches"][:3]:
                print(f"    * 제{m['draw_no']}회 ({m['date']}): {m['matched']} 일치")
        print("-" * 60)
    except Exception as e:
        print(f"조회 중 오류 발생: {e}")

def handle_auto_sync():
    print("\n[⚡ 인터넷 자동 동기화 시도 중...]")
    freq, total_draws, _, _, _ = lotto_data.load_data()
    next_draw = total_draws + 1
    synced = 0

    while True:
        res = lotto_data.fetch_online_draw(next_draw)
        if res:
            nums, bonus, date, amt, cnt = res
            lotto_data.add_custom_draw(next_draw, nums, bonus, date, amt, cnt)
            print(f"  -> 제{next_draw}회차 당첨결과 자동 수집 성공: {sorted(nums)} + 보너스 {bonus} ({date})")
            synced += 1
            next_draw += 1
        else:
            break

    if synced > 0:
        print(f"\n[성공] 총 {synced}개 회차가 자동으로 동기화되었습니다!")
        lotto_data.refresh_data()
    else:
        print("현재 이미 최신 회차이거나, 인터넷 연결을 확인할 수 없습니다. (수동 등록 메뉴 이용 가능)")

def handle_add_draw():
    print("\n[➕ 최신 회차 당첨번호 직접 등록]")
    freq, total_draws, _, _, _ = lotto_data.load_data()
    next_draw = total_draws + 1

    try:
        draw_input = input(f"회차 번호 입력 [기본값: {next_draw}]: ").strip()
        draw_no = int(draw_input) if draw_input else next_draw

        raw_nums = input("당첨 번호 6개 입력 (공백 또는 쉼표 구분): ").strip()
        nums = [int(x.strip()) for x in raw_nums.replace(",", " ").split() if x.strip()]

        if len(nums) != 6:
            print("오류: 번호는 정확히 6개여야 합니다.")
            return

        for n in nums:
            if n < 1 or n > 45:
                print("오류: 번호는 1부터 45 사이여야 합니다.")
                return

        if len(set(nums)) != 6:
            print("오류: 중복된 번호가 있습니다.")
            return

        bonus_input = input("보너스 번호 1개 입력: ").strip()
        bonus = int(bonus_input)
        if bonus in nums or bonus < 1 or bonus > 45:
            print("오류: 보너스 번호가 올바르지 않거나 당첨 번호와 중복됩니다.")
            return

        lotto_data.add_custom_draw(draw_no, nums, bonus)
        print(f"\n[성공] 제{draw_no}회차 데이터가 성공적으로 등록되었습니다!")
        lotto_data.refresh_data()

    except Exception as e:
        print(f"입력 중 오류가 발생했습니다: {e}")

def main():
    print_header()
    print_stats_summary()

    run_generate_slip(top_n_rank=20)
    current_top_n = 20

    while True:
        print("\n[메뉴 선택]")
        print("1. 새 5게임 번호 다시 뽑기 (역대 1등 중복 제외)")
        print(f"2. 최고 확률 순위 기준 변경 (현재: TOP {current_top_n}위)")
        print("3. 고정수/제외수 지정하여 번호 생성")
        print("4. 1~45번 전체 출현율(%) 및 순위표 조회")
        print("5. 🔍 내 번호 역대 당첨 이력 및 중복 검사")
        print("6. ⚡ 최신 회차 인터넷 자동 동기화")
        print("7. ➕ 최신 회차 수동 직접 등록")
        print("8. 종료")
        choice = input("선택하세요 (1-8): ").strip()

        if choice == "1":
            run_generate_slip(top_n_rank=current_top_n)
        elif choice == "2":
            try:
                val = input("조합에 사용할 상위 순위 범위 입력 (10~45): ").strip()
                n = int(val)
                if 10 <= n <= 45:
                    current_top_n = n
                    print(f"적용 완료: 출현 빈도 TOP {current_top_n}위 번호 풀 적용")
                    run_generate_slip(top_n_rank=current_top_n)
                else:
                    print("10부터 45 사이 숫자를 입력해주세요.")
            except Exception as e:
                print(f"오류: {e}")
        elif choice == "3":
            try:
                fixed_raw = input("고정할 번호를 쉼표로 입력 (없으면 엔터): ").strip()
                fixed = [int(x.strip()) for x in fixed_raw.split(",") if x.strip()]

                excluded_raw = input("제외할 번호를 쉼표로 입력 (없으면 엔터): ").strip()
                excluded = [int(x.strip()) for x in excluded_raw.split(",") if x.strip()]

                run_generate_slip(fixed=fixed, excluded=excluded, top_n_rank=current_top_n)
            except Exception as e:
                print(f"입력 오류: {e}")
        elif choice == "4":
            print_all_rates()
        elif choice == "5":
            handle_check_custom_numbers()
        elif choice == "6":
            handle_auto_sync()
            print_stats_summary()
        elif choice == "7":
            handle_add_draw()
            print_stats_summary()
        elif choice == "8":
            print("\n행운을 빕니다! 프로그램을 종료합니다. 🍀")
            break
        else:
            print("올바른 번호를 입력해주세요.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print_header()
        print_stats_summary()
        run_generate_slip(top_n_rank=20)
    else:
        main()
