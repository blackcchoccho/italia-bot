# 🇮🇹 이탈리아 여행 회화 텔레그램 알림봇

매일 3번, 이탈리아 여행 실전 회화 표현을 텔레그램으로 받아보는 봇.
GitHub Actions로 실행되어 **맥북이 꺼져 있어도 자동 동작**합니다.

---

## 📋 기능

| 시간 | 내용 |
|------|------|
| 오전 6시 🌅 | 새 표현 (영어 + 이탈리아어 + 발음 + 팁) |
| 낮 1시 🌞 | 오전 표현 리마인드 |
| 저녁 8시 🌙 | 오전 표현 리마인드 |

- 표현 **150개** (로마→피렌체→베네치아→밀라노→돌로미티→시칠리아→로마)
- **9월 출발** D-day 카운트다운
- 150개 소진 후 **자동 순환** (반복 학습)

---

## 🚀 GitHub Actions 세팅 방법

### 1단계 - 봇을 그룹에 추가

1. 텔레그램에서 **'이탈리아 회화'** 그룹을 열기
2. 그룹 설정 → 멤버 추가 → 봇 아이디(`@봇아이디`) 검색 후 **관리자**로 추가
3. 그룹에서 **아무 메시지**나 하나 전송 (Chat ID 탐색을 위해 필수)

### 2단계 - Chat ID 확인

로컬에서 아래 명령을 실행:

```bash
cd italia-bot
pip install requests pytz
BOT_TOKEN="8570114651:AAHKxyc0jtSZXcHLvsOXaZ0qnYCpiy81P0c" python find_chat_id.py
```

출력 예시:
```
✅ 대상 그룹 '이탈리아 회화' Chat ID: -1001234567890
```

### 3단계 - GitHub 레포지토리 생성 & 코드 업로드

```bash
cd italia-bot
git init
git add .
git commit -m "이탈리아 여행 회화 봇 초기 설정"
# GitHub에서 새 레포 생성 후:
git remote add origin https://github.com/YOUR_USERNAME/italia-bot.git
git push -u origin main
```

### 4단계 - GitHub Secrets 설정

GitHub 레포 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret 이름 | 값 |
|------------|-----|
| `BOT_TOKEN` | `8570114651:AAHKxyc0jtSZXcHLvsOXaZ0qnYCpiy81P0c` |
| `CHAT_ID`   | 2단계에서 확인한 숫자 (예: `-1001234567890`) |

### 5단계 - 첫 테스트

GitHub 레포 → **Actions** 탭 → 워크플로우 선택 → **Run workflow** 버튼 클릭

---

## 📁 파일 구조

```
italia-bot/
├── .github/
│   └── workflows/
│       ├── morning.yml      # 오전 6시 KST (21:00 UTC)
│       ├── afternoon.yml    # 낮 1시 KST  (04:00 UTC)
│       └── evening.yml      # 저녁 8시 KST (11:00 UTC)
├── phrases.py               # 150개 이탈리아 회화 표현
├── bot.py                   # 메인 봇 로직
├── find_chat_id.py          # Chat ID 자동 탐색 (최초 1회 실행)
├── requirements.txt
└── README.md
```

---

## 🛣️ 여행 동선별 표현 구성

| # | 카테고리 | 표현 수 |
|---|---------|--------|
| 1-12 | ✈️ 로마 공항 · 입국 · 숙소 | 12개 |
| 13-22 | 🏛️ 로마 관광 | 10개 |
| 23-32 | 🚗 렌터카 | 10개 |
| 33-42 | 🌸 피렌체 | 10개 |
| 43-52 | 🚢 베네치아 | 10개 |
| 53-62 | 🛍️ 밀라노 | 10개 |
| 63-72 | ⛰️ 돌로미티 | 10개 |
| 73-92 | 🍋 시칠리아 | 20개 |
| 93-112 | 🍝 식당 · 카페 | 20개 |
| 113-127 | 🚨 긴급상황 | 15개 |
| 128-150 | 🛒 쇼핑 · 교통 · 기타 | 23개 |

---

## ⚙️ 로컬 테스트

```bash
pip install -r requirements.txt

# 환경변수 설정
export BOT_TOKEN="8570114651:AAHKxyc0jtSZXcHLvsOXaZ0qnYCpiy81P0c"
export CHAT_ID="여기에_Chat_ID_입력"

# 테스트 실행
python bot.py morning     # 오전 새 표현
python bot.py afternoon   # 점심 리마인드
python bot.py evening     # 저녁 리마인드
```

---

## 🗓️ D-day 설정 변경

`bot.py`의 `DEPARTURE_DATE` 또는 `DEPARTURE_YEAR` 환경변수로 조정:

```python
DEPARTURE_YEAR = int(os.environ.get("DEPARTURE_YEAR", "2026"))
DEPARTURE_DATE = date(DEPARTURE_YEAR, 9, 1)   # 9월 1일 출발
```

GitHub Actions의 `env:` 섹션에서 `DEPARTURE_YEAR: "2026"` 값을 바꾸면 됩니다.

---

## ❓ 자주 묻는 질문

**Q: GitHub Actions가 정확히 6시에 오지 않아요.**
A: GitHub Actions 스케줄은 서버 부하에 따라 최대 15~30분 지연될 수 있어요. 정상입니다.

**Q: 봇 토큰을 코드에 노출해도 되나요?**
A: 반드시 GitHub Secrets에 저장하고 코드에는 넣지 마세요! README의 토큰은 예시입니다.

**Q: 표현이 150개 다 끝나면?**
A: 자동으로 1번부터 다시 순환합니다. 반복 학습 효과!
