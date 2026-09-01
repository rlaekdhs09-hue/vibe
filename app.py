import streamlit as st
import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

DB_PATH = Path(__file__).parent / "users.db"

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="Vibe Space Designer",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# DB / 회원 기능
# -----------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000
    ).hex()


def create_user(username: str, password: str):
    username = username.strip()
    if not username or not password:
        return False, "아이디와 비밀번호를 입력해주세요."
    if len(username) < 3:
        return False, "아이디는 3자 이상으로 입력해주세요."
    if len(password) < 6:
        return False, "비밀번호는 6자 이상으로 입력해주세요."

    salt = secrets.token_hex(16)
    password_hash = f"{salt}${hash_password(password, salt)}"

    try:
        conn = get_conn()
        conn.execute(
            "INSERT INTO users(username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, password_hash, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
        conn.close()
        return True, "회원가입이 완료되었습니다. 로그인해주세요."
    except sqlite3.IntegrityError:
        return False, "이미 존재하는 아이디입니다."


def verify_user(username: str, password: str) -> bool:
    conn = get_conn()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username.strip(),)
    ).fetchone()
    conn.close()

    if not row:
        return False

    try:
        salt, stored_hash = row[0].split("$", 1)
        return secrets.compare_digest(
            stored_hash,
            hash_password(password, salt)
        )
    except ValueError:
        return False


# -----------------------------
# 행사장 설계 로직
# -----------------------------
def recommend_layout(event_type, people, duration, age_group, mood, fee, place):
    # 규모
    if people <= 50:
        size = "소규모"
        area_per_person = 1.8
    elif people <= 150:
        size = "중규모"
        area_per_person = 1.6
    elif people <= 400:
        size = "대규모"
        area_per_person = 1.45
    else:
        size = "초대형"
        area_per_person = 1.3

    estimated_area = max(80, int(people * area_per_person))

    # 행사 유형
    type_rules = {
        "공연": {
            "zones": ["무대", "객석", "FOH/음향", "대기실", "출입구", "안전통로"],
            "stage_ratio": 0.18,
            "features": ["무대 정면 시야 확보", "음향·조명 장비 구역", "출연자 대기공간"]
        },
        "축제": {
            "zones": ["메인무대", "체험/부스", "푸드존", "휴게존", "출입구", "안전통로"],
            "stage_ratio": 0.12,
            "features": ["동선 분산", "부스 간 간격 확보", "휴게공간 배치"]
        },
        "전시": {
            "zones": ["전시존", "작품 관람 동선", "안내/접수", "휴게존", "출입구", "보관공간"],
            "stage_ratio": 0.06,
            "features": ["순환형 관람 동선", "작품 간 시야 확보", "입·퇴장 동선 분리"]
        },
        "박람회": {
            "zones": ["전시부스", "상담존", "등록/접수", "휴게존", "무대/발표존", "안전통로"],
            "stage_ratio": 0.10,
            "features": ["부스 접근성", "상담 동선 확보", "사람이 몰리는 구역 분산"]
        },
        "컨퍼런스": {
            "zones": ["발표무대", "좌석존", "등록대", "네트워킹존", "대기/휴게존", "안전통로"],
            "stage_ratio": 0.12,
            "features": ["발표자와 청중의 시야 확보", "등록대 전면 배치", "네트워킹 공간 확보"]
        },
        "학교 행사": {
            "zones": ["메인무대", "학생 활동존", "객석", "운영본부", "출입구", "안전통로"],
            "stage_ratio": 0.14,
            "features": ["학생 이동 동선", "운영진 통제구역", "혼잡 구역 분산"]
        },
        "기타": {
            "zones": ["메인존", "참여존", "휴게존", "운영존", "출입구", "안전통로"],
            "stage_ratio": 0.10,
            "features": ["입장·퇴장 동선", "운영구역 분리", "휴게공간 확보"]
        }
    }

    rule = type_rules.get(event_type, type_rules["기타"])

    # 분위기
    mood_rules = {
        "활기찬": ("밝은 조명 + 중앙 집중형 메인존", "참여형 프로그램을 중앙에 배치"),
        "차분한": ("낮은 조도 + 여유 있는 좌석 간격", "소음이 적은 구역을 외곽에 배치"),
        "고급스러운": ("간접조명 + 넓은 여백", "입구와 메인존의 시각적 임팩트 강화"),
        "캐주얼한": ("자유로운 좌석 + 휴게공간 확대", "스탠딩/라운지형 공간 혼합"),
        "미래지향적": ("미디어월 + LED/프로젝션 중심", "디지털 체험존을 메인 동선에 배치"),
        "자연친화적": ("자연광 + 식물/목재 요소", "야외 또는 창가 휴게존 활용")
    }
    mood_plan, mood_detail = mood_rules.get(mood, ("균형 잡힌 조명과 동선", "공간별 기능을 명확히 분리"))

    # 연령대
    age_rules = {
        "10대 이하": "보호자 대기·휴게공간과 안전요원 배치를 강화",
        "10~20대": "포토존·체험존·SNS 공유 포인트를 동선에 포함",
        "30~40대": "접근성이 좋은 좌석과 휴게공간을 충분히 확보",
        "50대 이상": "좌석 중심 구성, 안내 표지와 휴식공간을 강화",
        "전 연령": "유아·청소년·성인 모두 접근하기 쉬운 동선을 구성"
    }
    age_plan = age_rules.get(age_group, age_rules["전 연령"])

    # 시간
    if duration <= 2:
        time_plan = "짧은 행사이므로 입장→메인 프로그램→퇴장 동선을 단순화"
    elif duration <= 5:
        time_plan = "중간 휴식과 이동 시간을 고려해 휴게존을 메인 동선 가까이에 배치"
    else:
        time_plan = "장시간 행사이므로 휴게·식음·화장실 접근성을 특히 강화"

    # 가격
    if fee <= 0:
        fee_plan = "무료 행사: 입장 확인 절차를 단순화하고 대기열을 최소화"
    elif fee <= 30000:
        fee_plan = "일반 유료 행사: 접수·결제·입장 동선을 분리"
    else:
        fee_plan = "프리미엄 행사: 체크인 공간과 VIP/프리미엄 휴게존을 별도 구성"

    # 실내/실외
    if place == "실외":
        place_plan = "실외: 우천 대비 공간, 그늘/휴식, 전기·음향 보호, 비상대피 동선을 함께 고려"
    else:
        place_plan = "실내: 비상구, 소방시설 접근, 냉난방, 기둥·벽면에 의한 시야 방해를 고려"

    safety = [
        f"예상 인원 {people:,}명 기준으로 출입구 병목을 피하도록 입·퇴장 동선을 분리",
        "메인 동선에는 충분한 폭의 안전통로를 확보",
        "행사 운영본부를 출입구와 메인존을 동시에 확인하기 쉬운 위치에 배치",
        "비상구와 대피 동선은 행사 장식물이나 부스로 막지 않도록 설계"
    ]

    if place == "실외":
        safety.append("기상 변화에 대비한 대체 동선과 임시 대피공간을 계획")

    return {
        "size": size,
        "estimated_area": estimated_area,
        "zones": rule["zones"],
        "features": rule["features"],
        "mood_plan": mood_plan,
        "mood_detail": mood_detail,
        "age_plan": age_plan,
        "time_plan": time_plan,
        "fee_plan": fee_plan,
        "place_plan": place_plan,
        "safety": safety,
        "stage_ratio": rule["stage_ratio"],
    }


def draw_floor_plan(result, place):
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 65)
    ax.axis("off")

    # 전체 공간
    ax.add_patch(Rectangle((2, 2), 96, 61, fill=False, linewidth=2))
    ax.text(50, 60.5, f"VIBE SPACE DESIGN • {place}", ha="center", va="center", fontsize=15, fontweight="bold")

    zones = [
        (5, 45, 90, 13, "메인 프로그램 / 무대·발표"),
        (5, 25, 55, 16, "객석 / 참여존"),
        (63, 25, 30, 16, "체험·부스 / 네트워킹"),
        (5, 7, 28, 12, "휴게존"),
        (37, 7, 25, 12, "운영본부 / 접수"),
        (66, 7, 27, 12, "출입구 / 안내"),
    ]

    for x, y, w, h, label in zones:
        ax.add_patch(Rectangle((x, y), w, h, alpha=0.18, linewidth=1.5))
        ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=10)

    # 안전 통로
    ax.annotate("", xy=(94, 23), xytext=(94, 53),
                arrowprops=dict(arrowstyle="<->", linewidth=2))
    ax.text(96, 38, "안전통로", rotation=90, va="center", fontsize=9)

    ax.annotate("", xy=(67, 5), xytext=(67, 22),
                arrowprops=dict(arrowstyle="<->", linewidth=2))
    ax.text(69, 13.5, "입·퇴장\n동선", va="center", fontsize=9)

    ax.set_title(
        f"권장 규모: {result['size']} / 예상 필요 면적: 약 {result['estimated_area']:,}㎡",
        fontsize=11
    )
    return fig


# -----------------------------
# 세션 상태
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# -----------------------------
# 로그인 전 화면
# -----------------------------
if not st.session_state.logged_in:
    st.markdown(
        """
        <div style="text-align:center;padding:35px 0 15px 0;">
            <h1 style="font-size:48px;margin-bottom:4px;">🎪 VIBE SPACE DESIGNER</h1>
            <p style="font-size:20px;color:#666;">사용자의 니즈를 분석해 행사장을 설계해드립니다.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["로그인", "회원가입"])

    with tab1:
        st.subheader("로그인")
        login_id = st.text_input("아이디", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", key="login_pw")

        if st.button("로그인", use_container_width=True, type="primary"):
            if verify_user(login_id, login_pw):
                st.session_state.logged_in = True
                st.session_state.username = login_id.strip()
                st.success("로그인되었습니다.")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

    with tab2:
        st.subheader("회원가입")
        signup_id = st.text_input("새 아이디", key="signup_id")
        signup_pw = st.text_input("새 비밀번호", type="password", key="signup_pw")
        signup_pw2 = st.text_input("비밀번호 확인", type="password", key="signup_pw2")

        if st.button("회원가입", use_container_width=True):
            if signup_pw != signup_pw2:
                st.error("비밀번호가 일치하지 않습니다.")
            else:
                ok, msg = create_user(signup_id, signup_pw)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.info("💡 GitHub + Streamlit Cloud에서 바로 실행할 수 있는 독립형 데모입니다.")
    st.stop()

# -----------------------------
# 메인 앱
# -----------------------------
with st.sidebar:
    st.markdown("## 🎪 VIBE SPACE")
    st.caption(f"로그인 사용자: **{st.session_state.username}**")
    st.divider()

    if st.button("로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.markdown("---")
    st.caption("Vibe Coding Project")
    st.caption("사용자의 니즈 → 행사장 설계안")

st.title("🎪 행사장 설계 AI")
st.write("행사 정보를 입력하면 규모·동선·공간 구성·분위기·안전 요소를 종합해 권장 설계를 만들어드립니다.")

with st.form("event_design_form"):
    st.subheader("1. 행사 기본 정보")

    col1, col2 = st.columns(2)

    with col1:
        event_type = st.selectbox(
            "행사장의 유형",
            ["공연", "축제", "전시", "박람회", "컨퍼런스", "학교 행사", "기타"]
        )
        people = st.number_input(
            "예상 인원수 (명)",
            min_value=1,
            max_value=100000,
            value=200,
            step=10
        )
        duration = st.number_input(
            "진행 시간 (시간)",
            min_value=0.5,
            max_value=24.0,
            value=4.0,
            step=0.5
        )
        age_group = st.selectbox(
            "예상 연령대",
            ["10대 이하", "10~20대", "30~40대", "50대 이상", "전 연령"]
        )

    with col2:
        mood = st.selectbox(
            "원하는 분위기",
            ["활기찬", "차분한", "고급스러운", "캐주얼한", "미래지향적", "자연친화적"]
        )
        fee = st.number_input(
            "예상 입장료 (원)",
            min_value=0,
            max_value=10000000,
            value=10000,
            step=1000
        )
        place = st.radio(
            "행사 장소",
            ["실내", "실외"],
            horizontal=True
        )
        extra = st.text_area(
            "추가 요구사항 (선택)",
            placeholder="예: 포토존이 필요해요 / 음식 부스를 많이 넣고 싶어요 / 무대를 크게 만들고 싶어요"
        )

    submitted = st.form_submit_button(
        "✨ 행사장 설계안 생성하기",
        use_container_width=True,
        type="primary"
    )

if submitted:
    result = recommend_layout(
        event_type, people, duration, age_group, mood, fee, place
    )

    st.success("설계안이 생성되었습니다!")

    st.subheader("2. 설계 결과")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("행사 규모", result["size"])
    c2.metric("예상 인원", f"{people:,}명")
    c3.metric("권장 면적", f"{result['estimated_area']:,}㎡")
    c4.metric("진행 시간", f"{duration:g}시간")

    st.markdown("### 🗺️ 권장 공간 배치")
    st.pyplot(draw_floor_plan(result, place), clear_figure=True)

    left, right = st.columns(2)

    with left:
        st.markdown("### 📍 핵심 공간")
        for zone in result["zones"]:
            st.markdown(f"- **{zone}**")

        st.markdown("### 💡 행사 유형별 설계 포인트")
        for item in result["features"]:
            st.markdown(f"- {item}")

    with right:
        st.markdown("### 🎨 분위기 설계")
        st.write(result["mood_plan"])
        st.write(result["mood_detail"])

        st.markdown("### 👥 대상 연령대")
        st.write(result["age_plan"])

        st.markdown("### ⏱️ 진행 시간")
        st.write(result["time_plan"])

        st.markdown("### 💳 입장료")
        st.write(result["fee_plan"])

    st.markdown("### 🏢 장소 조건")
    st.info(result["place_plan"])

    st.markdown("### 🛡️ 안전·동선 설계")
    for item in result["safety"]:
        st.markdown(f"- {item}")

    if extra.strip():
        st.markdown("### 📝 추가 요구사항 반영")
        st.write(f"입력하신 요구사항: **{extra.strip()}**")
        st.caption("추가 요구사항은 기본 설계안과 함께 검토할 수 있도록 표시했습니다.")

    st.divider()
    st.caption("※ 본 결과는 행사 기획을 위한 설계 제안이며, 실제 행사에서는 행사장 구조·소방·전기·피난·수용인원 등 관련 안전기준을 반드시 별도로 확인해야 합니다.")

else:
    st.markdown(
        """
        ### 🚀 이렇게 사용하세요
        1. 행사 정보를 입력합니다.
        2. **행사장 설계안 생성하기**를 누릅니다.
        3. 예상 규모와 공간 배치, 동선, 분위기, 안전 요소를 확인합니다.

        **핵심 아이디어:**  
        사용자의 요구사항을 입력값으로 받아 행사 목적과 규모에 맞는 공간 구성을 자동으로 제안합니다.
        """
    )
