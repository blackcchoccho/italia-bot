#!/usr/bin/env python3
"""
이탈리아 여행 회화 텔레그램 알림봇
- 오전 6시: 새 표현 전송
- 낮 1시 / 저녁 8시: 같은 표현 리마인드
- 사용법: python bot.py [morning|afternoon|evening]
"""

import os
import sys
import requests
from datetime import date, datetime
import pytz

from phrases import PHRASES

# ─── 설정 ────────────────────────────────────────────────────────────────────
BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")
GROUP_NAME  = "이탈리아 회화"

# 9월 출발 기준 D-day (연도는 환경변수로 조정 가능, 기본 2026년)
DEPARTURE_YEAR = int(os.environ.get("DEPARTURE_YEAR", "2026"))
DEPARTURE_DATE = date(DEPARTURE_YEAR, 9, 1)

# 표현 순환 시작일 (봇 가동 첫날 = 2026-03-09)
START_DATE = date(2026, 3, 10)

KST = pytz.timezone("Asia/Seoul")

# ─── 유틸 함수 ────────────────────────────────────────────────────────────────

def get_today_phrase() -> dict:
    """오늘 날짜 기준으로 150개 표현 중 해당 표현 반환"""
    today = date.today()
    delta = (today - START_DATE).days
    idx = delta % len(PHRASES)
    return PHRASES[idx]


def get_dday() -> str:
    """9월 출발 기준 D-day 문자열 반환"""
    today = date.today()
    delta = (DEPARTURE_DATE - today).days
    if delta > 0:
        return f"D-{delta}"
    elif delta == 0:
        return "D-Day 🎉 출발!"
    else:
        return f"D+{abs(delta)} ✈️ 여행 중!"


def find_chat_id() -> int | None:
    """
    getUpdates를 통해 그룹 채팅 ID 자동 탐색.
    봇을 그룹에 추가하고 그룹에서 아무 메시지를 보낸 뒤 실행해야 작동합니다.
    """
    # 환경변수로 직접 지정된 경우 우선 사용
    env_chat_id = os.environ.get("CHAT_ID", "").strip()
    if env_chat_id:
        return int(env_chat_id)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        resp = requests.get(url, params={"limit": 100}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] getUpdates 호출 실패: {e}")
        return None

    # 최신 업데이트부터 역순으로 탐색
    for update in reversed(data.get("result", [])):
        for key in ("message", "channel_post", "my_chat_member"):
            msg = update.get(key, {})
            chat = msg.get("chat", {})
            title = chat.get("title", "")
            if GROUP_NAME in title:
                chat_id = chat["id"]
                print(f"[INFO] 그룹 '{title}' 발견 → chat_id: {chat_id}")
                return chat_id

    print(f"[WARN] 그룹 '{GROUP_NAME}'을 찾지 못했습니다.")
    print("  1) 봇을 그룹에 관리자로 추가했는지 확인")
    print("  2) 그룹에서 메시지를 하나 보낸 뒤 재시도")
    print("  3) 또는 GitHub Secret 'CHAT_ID'에 직접 입력")
    return None


def send_message(chat_id: int, text: str) -> bool:
    """텔레그램 메시지 전송"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        if result.get("ok"):
            print(f"[OK] 메시지 전송 성공 (chat_id: {chat_id})")
            return True
        else:
            print(f"[ERROR] Telegram 응답 오류: {result}")
            return False
    except Exception as e:
        print(f"[ERROR] 메시지 전송 실패: {e}")
        return False


# ─── 메시지 빌더 ──────────────────────────────────────────────────────────────

def build_morning_message(phrase: dict, dday: str) -> str:
    """오전 5시 30분 - 새 표현 메시지"""
    lines = []
    lines.append(f"🇮🇹 <b>이탈리아 여행 회화</b>  |  9월 출발 <b>{dday}</b>")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📖 <b>오늘의 표현 #{phrase['no']}/150</b>")
    lines.append(f"📍 {phrase['category']}")
    lines.append(f"💬 상황: {phrase['situation']}")

    # 심사관/상대방 질문이 있는 경우 표시
    if phrase.get("q"):
        lines.append(f"\n❓ <b>상대방:</b> <i>{phrase['q']}</i>")
        if phrase.get("q_pron"):
            lines.append(f"   🔊 {phrase['q_pron']}")

    lines.append(f"\n⚡ <b>짧게 (실전):</b>")
    lines.append(f"🇬🇧 {phrase['short_en']}")
    lines.append(f"🇮🇹 {phrase['short_it']}")

    lines.append(f"\n📚 <b>풀 문장 (정중하게):</b>")
    lines.append(f"🇬🇧 <i>{phrase['en']}</i>")
    lines.append(f"🇮🇹 <b>{phrase['it']}</b>")
    lines.append(f"🔊 {phrase['pron']}")

    lines.append(f"\n{phrase['tip']}")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"낮 1시·저녁 8시에 다시 복습해요 📚")

    return "\n".join(lines)


def build_reminder_message(phrase: dict, session: str) -> str:
    """낮 1시 / 저녁 8시 - 리마인드 메시지"""
    emoji = "🌞" if session == "afternoon" else "🌙"
    label = "점심 복습" if session == "afternoon" else "저녁 복습"

    lines = []
    lines.append(f"{emoji} <b>{label}</b> | 표현 #{phrase['no']}/150")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📍 {phrase['category']}")
    lines.append(f"💬 {phrase['situation']}")

    if phrase.get("q"):
        lines.append(f"\n❓ <b>상대방:</b> <i>{phrase['q']}</i>")
        if phrase.get("q_pron"):
            lines.append(f"   🔊 {phrase['q_pron']}")

    lines.append(f"\n⚡ <b>짧게:</b> {phrase['short_en']}  /  {phrase['short_it']}")
    lines.append(f"\n🇬🇧 <i>{phrase['en']}</i>")
    lines.append(f"🇮🇹 <b>{phrase['it']}</b>")
    lines.append(f"🔊 {phrase['pron']}")
    lines.append(f"\n{phrase['tip']}")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"오늘 이 표현, 꼭 외워서 이탈리아에서 써먹어요! 💪")

    return "\n".join(lines)


# ─── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        print("[ERROR] BOT_TOKEN 환경변수가 설정되지 않았습니다.")
        print("  GitHub Secret 'BOT_TOKEN'을 확인하세요.")
        sys.exit(1)

    # 실행 모드 결정
    if len(sys.argv) < 2:
        # 현재 한국 시간 기준 자동 판단 (로컬 테스트용)
        now_kst = datetime.now(KST)
        hour = now_kst.hour
        if 5 <= hour < 10:
            mode = "morning"
        elif 12 <= hour < 15:
            mode = "afternoon"
        else:
            mode = "evening"
        print(f"[INFO] 모드 자동 판단: {mode} (현재 KST {now_kst.strftime('%H:%M')})")
    else:
        mode = sys.argv[1].lower()

    if mode not in ("morning", "afternoon", "evening"):
        print(f"[ERROR] 알 수 없는 모드: {mode}")
        print("  사용법: python bot.py [morning|afternoon|evening]")
        sys.exit(1)

    # 오늘의 표현 & D-day
    phrase = get_today_phrase()
    dday   = get_dday()

    print(f"[INFO] 모드={mode} | 표현#{phrase['no']} | {dday}")
    print(f"[INFO] 표현: {phrase['it']}")

    # 채팅 ID 탐색
    chat_id = find_chat_id()
    if chat_id is None:
        sys.exit(1)

    # 메시지 생성 & 전송
    if mode == "morning":
        text = build_morning_message(phrase, dday)
    else:
        text = build_reminder_message(phrase, mode)

    success = send_message(chat_id, text)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
