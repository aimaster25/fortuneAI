"""

시간/타이밍 관련 유틸리티 함수들

"""

import pytz

from datetime import datetime, timedelta

from typing import Dict, Any

from .state import TarotState

def get_current_context() -> dict:
    """현재 시간 맥락 정보 생성"""
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    return {
        "current_date": now.strftime("%Y년 %m월 %d일"),
        "current_year": now.year,
        "current_month": now.month,
        "current_day": now.day,
        "weekday": now.strftime("%A"),
        "weekday_kr": get_weekday_korean(now.weekday()),
        "season": get_season(now.month),
        "quarter": f"{now.year}년 {(now.month-1)//3 + 1}분기",
        "recent_period": f"최근 {get_recent_timeframe(now)}",
        "timestamp": now.isoformat(),
        "unix_timestamp": int(now.timestamp())
    }
def get_weekday_korean(weekday: int) -> str:
    """요일을 한국어로 변환 (0=월요일, 6=일요일)"""
    weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    return weekdays[weekday]
def get_season(month: int) -> str:
    """계절 정보"""
    if month in [12, 1, 2]:
        return "겨울"
    elif month in [3, 4, 5]:
        return "봄"
    elif month in [6, 7, 8]:
        return "여름"
    else:
        return "가을"
def get_recent_timeframe(now: datetime) -> str:
    """최근 기간 표현"""
    return f"{now.year}년 {now.month}월 기준"
def calculate_days_until_target(target_month: int, target_day: int = 1) -> int:
    """특정 날짜까지 남은 일수 계산"""
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    target_date = datetime(now.year, target_month, target_day, tzinfo=kst)
    if target_date < now:
        target_date = datetime(now.year + 1, target_month, target_day, tzinfo=kst)
    delta = target_date - now
    return delta.days
def get_time_period_description(days: int) -> str:
    """일수를 기간 표현으로 변환"""
    if days <= 7:
        return f"{days}일 이내"
    elif days <= 30:
        weeks = days // 7
        return f"약 {weeks}주 후"
    elif days <= 365:
        months = days // 30
        return f"약 {months}개월 후"
    else:
        years = days // 365
        return f"약 {years}년 후"
def integrate_timing_with_current_date(tarot_timing: dict, current_context: dict) -> dict:
    """타로 시기 분석과 현재 날짜 정보 통합"""
    kst = pytz.timezone('Asia/Seoul')
    current_date = datetime.now(kst)
    concrete_timing = []
    timing_list = tarot_timing.get("timing_predictions", [tarot_timing])
    for timing in timing_list:
        days_min = timing.get("days_min", 1)
        days_max = timing.get("days_max", 7)
        start_date = current_date + timedelta(days=days_min)
        end_date = current_date + timedelta(days=days_max)
        if start_date.year != current_date.year or end_date.year != current_date.year:
            period_str = f"{start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%Y년 %m월 %d일')}"
        elif start_date.month != end_date.month:
            period_str = f"{start_date.strftime('%m월 %d일')} ~ {end_date.strftime('%m월 %d일')}"
        else:
            period_str = f"{start_date.strftime('%m월 %d일')} ~ {end_date.strftime('%d일')}"
        concrete_timing.append({
            "period": period_str,
            "description": timing.get("description", ""),
            "confidence": timing.get("confidence", "보통"),
            "days_from_now": f"{days_min}-{days_max}일 후"
        })
    return {
        "abstract_timing": tarot_timing,
        "concrete_timing": concrete_timing,
        "current_context": current_context
    }
def ensure_temporal_context(state: TarotState) -> TarotState:
    """상태에 시간 맥락 정보가 없으면 추가"""
    if not state.get("temporal_context"):
        state["temporal_context"] = get_current_context()
    return state
def predict_timing_from_card_metadata(card_info: dict) -> dict:
    """카드 메타데이터로 시기 예측 - 개선된 버전"""
    timing_info = {
        "time_frame": "알 수 없음",
        "days_min": 1,
        "days_max": 365,
        "speed": "보통",
        "description": "시기 정보가 부족합니다.",
        "confidence": "낮음"
    }
    suit = card_info.get("suit", "")
    suit_timing = {
        "Wands": {
            "days_min": 1, "days_max": 7,
            "time_frame": "1-7일",
            "speed": "매우 빠름", 
            "description": "불의 원소 - 즉각적이고 에너지 넘치는 변화"
        },
        "Cups": {
            "days_min": 7, "days_max": 30,
            "time_frame": "1-4주",
            "speed": "보통",
            "description": "물의 원소 - 감정적 변화, 점진적 발전"
        },
        "Swords": {
            "days_min": 3, "days_max": 14,
            "time_frame": "3일-2주", 
            "speed": "빠름",
            "description": "공기의 원소 - 정신적 변화, 빠른 의사결정"
        },
        "Pentacles": {
            "days_min": 30, "days_max": 180,
            "time_frame": "1-6개월",
            "speed": "느림",
            "description": "흙의 원소 - 물질적 변화, 실제적이고 지속적인 결과"
        }
    }
    if suit in suit_timing:
        timing_info.update(suit_timing[suit])
        timing_info["confidence"] = "중간"
    rank = card_info.get("rank", "")
    rank_multipliers = {
        "Ace": 0.5, "Two": 0.7, "Three": 0.8, "Four": 1.0, "Five": 1.3,
        "Six": 1.1, "Seven": 1.4, "Eight": 1.2, "Nine": 1.5, "Ten": 1.6,
        "Page": 0.6, "Knight": 0.4, "Queen": 1.3, "King": 1.5
    }
    if rank in rank_multipliers:
        multiplier = rank_multipliers[rank]
        timing_info["days_min"] = int(timing_info["days_min"] * multiplier)
        timing_info["days_max"] = int(timing_info["days_max"] * multiplier)
        timing_info["time_frame"] = format_time_range(timing_info["days_min"], timing_info["days_max"])
        timing_info["confidence"] = "높음"
    if card_info.get("is_major_arcana"):
        major_timing = {
            "The Fool": (1, 3), "The Magician": (1, 7), "The High Priestess": (30, 90),
            "The Empress": (90, 180), "The Emperor": (30, 90), "The Hierophant": (90, 180),
            "The Lovers": (14, 56), "The Chariot": (7, 14), "Strength": (30, 90),
            "The Hermit": (90, 270), "Wheel of Fortune": (90, 180), "Justice": (30, 180),
            "The Hanged Man": (180, 365), "Death": (90, 365), "Temperance": (90, 180),
            "The Devil": (1, 90), "The Tower": (1, 7), "The Star": (180, 730),
            "The Moon": (30, 180), "The Sun": (30, 90), "Judgement": (90, 365),
            "The World": (180, 730)
        }
        card_name = card_info.get("card_name", "")
        if card_name in major_timing:
            timing_info["days_min"], timing_info["days_max"] = major_timing[card_name]
            timing_info["time_frame"] = format_time_range(timing_info["days_min"], timing_info["days_max"])
            timing_info["description"] = "메이저 아르카나 - 인생의 중요한 변화"
            timing_info["confidence"] = "높음"
    orientation = card_info.get("orientation", "")
    if orientation == "reversed":
        timing_info["days_min"] = int(timing_info["days_min"] * 1.5)
        timing_info["days_max"] = int(timing_info["days_max"] * 1.5)
        timing_info["time_frame"] = format_time_range(timing_info["days_min"], timing_info["days_max"])
        timing_info["description"] += " (역방향 - 지연 또는 내적 변화)"
    return timing_info
def predict_timing_with_current_date(card_info: dict, temporal_context: dict = None) -> dict:
    """현재 날짜를 고려한 개선된 시기 예측"""
    basic_timing = predict_timing_from_card_metadata(card_info)
    if not temporal_context:
        temporal_context = get_current_context()
    enhanced_timing = integrate_timing_with_current_date(
        {"timing_predictions": [basic_timing]}, 
        temporal_context
    )
    result = {
        "basic_timing": basic_timing,
        "current_context": temporal_context,
        "concrete_dates": enhanced_timing["concrete_timing"],
        "recommendations": generate_timing_recommendations(basic_timing, temporal_context)
    }
    return result
def generate_timing_recommendations(timing_info: dict, temporal_context: dict) -> list:
    """시간 맥락을 고려한 타이밍 추천"""
    recommendations = []
    current_season = temporal_context.get("season", "")
    current_month = temporal_context.get("current_month", 1)
    season_advice = {
        "봄": "새로운 시작과 성장의 에너지가 강한 시기입니다.",
        "여름": "활발한 활동과 결실을 맺기 좋은 시기입니다.", 
        "가을": "수확과 정리, 준비의 시기입니다.",
        "겨울": "내적 성찰과 계획 수립에 적합한 시기입니다."
    }
    if current_season in season_advice:
        recommendations.append(f"🌱 현재 {current_season}철: {season_advice[current_season]}")
    speed = timing_info.get("speed", "보통")
    if speed == "매우 빠름":
        recommendations.append("⚡ 즉각적인 행동이 필요한 시기입니다.")
    elif speed == "빠름":
        recommendations.append("🏃 신속한 결정과 실행이 중요합니다.")
    elif speed == "느림":
        recommendations.append("🐌 인내심을 갖고 차근차근 준비하세요.")
    if current_month in [1, 2]:
        recommendations.append("🎊 새해 새로운 계획을 세우기 좋은 시기입니다.")
    elif current_month in [3, 4]:
        recommendations.append("🌸 변화와 새로운 도전을 시작하기 좋습니다.")
    elif current_month in [9, 10]:
        recommendations.append("🍂 성과를 정리하고 다음 단계를 준비하세요.")
    elif current_month == 12:
        recommendations.append("🎄 올해를 마무리하고 내년을 준비하는 시기입니다.")
    return recommendations
def format_time_range(days_min: int, days_max: int) -> str:
    """일수를 사용자 친화적 시간 표현으로 변환"""
    if days_max <= 7:
        return f"{days_min}-{days_max}일"
    elif days_max <= 30:
        weeks_min = max(1, days_min // 7)
        weeks_max = days_max // 7
        if weeks_min == weeks_max:
            return f"{weeks_min}주"
        return f"{weeks_min}-{weeks_max}주"
    elif days_max <= 365:
        months_min = max(1, days_min // 30)
        months_max = days_max // 30
        if months_min == months_max:
            return f"{months_min}개월"
        return f"{months_min}-{months_max}개월"
    else:
        years_min = max(1, days_min // 365)
        years_max = days_max // 365
        if years_min == years_max:
            return f"{years_min}년"
        return f"{years_min}-{years_max}년"
