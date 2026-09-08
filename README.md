# VIBE SPACE DESIGNER v2
GitHub → Streamlit Cloud용 행사장 설계 앱입니다.

## v2 개선
- 기존 배치도의 이상한 텍스트 문제 제거
- 행사 유형별 상세 배치
- 입구/출구/메인/객석/부스/휴게/운영/안전/편의시설 표시
- 입장·주요 이동·퇴장 동선 표시
- 인원·행사 유형·연령·분위기·실내/실외 반영
- 추가 요구사항 키워드 반영
- 배치도 상세 설명 강화
- 회원가입/로그인 유지

## 배포
GitHub에 `app.py`, `requirements.txt`, `README.md`, `.gitignore`를 올리고 Streamlit Cloud에서 Main file path를 `app.py`로 설정하세요.

회원 데이터는 프로토타입상 SQLite를 사용합니다. 실제 서비스는 Supabase/Firebase/PostgreSQL 등의 외부 DB를 권장합니다.
