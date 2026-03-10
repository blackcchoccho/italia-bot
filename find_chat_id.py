#!/usr/bin/env python3
"""
그룹 Chat ID 자동 탐색 스크립트
─────────────────────────────────
사전 준비:
  1) 봇(@BotFather에서 만든 봇)을 '이탈리아 회화' 그룹에 관리자로 초대
  2) 그룹에서 아무 메시지나 하나 보내기
  3) 아래 명령 실행:
     python find_chat_id.py

출력된 CHAT_ID를 GitHub Secrets에 'CHAT_ID' 이름으로 저장하세요.
"""

import os
import sys
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8570114651:AAHKxyc0jtSZXcHLvsOXaZ0qnYCpiy81P0c")
GROUP_NAME = "이탈리아 회화"


def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN을 환경변수로 설정하거나 스크립트 내 BOT_TOKEN에 입력하세요.")
        sys.exit(1)

    print(f"[*] getUpdates 호출 중 (봇 토큰: ...{BOT_TOKEN[-6:]})")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

    try:
        resp = requests.get(url, params={"limit": 100}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] API 호출 실패: {e}")
        sys.exit(1)

    if not data.get("ok"):
        print(f"[ERROR] Telegram 응답 오류: {data}")
        sys.exit(1)

    results = data.get("result", [])
    print(f"[*] 총 {len(results)}개 업데이트 확인 중...\n")

    found = []
    for update in results:
        for key in ("message", "channel_post", "my_chat_member", "chat_member"):
            msg = update.get(key, {})
            chat = msg.get("chat", {})
            if not chat:
                continue
            title = chat.get("title", "")
            ctype = chat.get("type", "")
            cid   = chat.get("id", "")
            if cid and ctype in ("group", "supergroup", "channel"):
                entry = (cid, title, ctype)
                if entry not in found:
                    found.append(entry)

    if not found:
        print("업데이트에서 그룹/채널을 찾지 못했습니다.")
        print("그룹에서 메시지를 보낸 뒤 다시 시도하거나,")
        print("봇이 그룹에 올바르게 추가되었는지 확인하세요.")
        sys.exit(1)

    print("─────────────────────────────────────")
    print(f"{'CHAT_ID':<20} {'TYPE':<12} TITLE")
    print("─────────────────────────────────────")
    target_id = None
    for cid, title, ctype in found:
        marker = " ← 이 봇 사용 대상!" if GROUP_NAME in title else ""
        print(f"{str(cid):<20} {ctype:<12} {title}{marker}")
        if GROUP_NAME in title:
            target_id = cid
    print("─────────────────────────────────────")

    if target_id:
        print(f"\n✅ 대상 그룹 '{GROUP_NAME}' Chat ID: {target_id}")
        print(f"\nGitHub Secrets에 다음과 같이 저장하세요:")
        print(f"  이름: CHAT_ID")
        print(f"  값:   {target_id}")
    else:
        print(f"\n'{GROUP_NAME}' 그룹을 찾지 못했습니다.")
        print("위 목록에서 원하는 그룹 ID를 확인하고 GitHub Secrets에 저장하세요.")


if __name__ == "__main__":
    main()
