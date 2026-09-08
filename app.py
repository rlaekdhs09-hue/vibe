import streamlit as st
import sqlite3, hashlib, secrets
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

DB = Path(__file__).parent / "users.db"

st.set_page_config(page_title="VIBE SPACE DESIGNER", page_icon="🎪", layout="wide")

def conn():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL)""")
    c.commit()
    return c

def hpw(p, salt):
    return hashlib.pbkdf2_hmac("sha256", p.encode(), salt.encode(), 120000).hex()

def signup(u, p):
    u = u.strip()
    if not u or not p: return False, "아이디와 비밀번호를 입력해주세요."
    if len(u) < 3: return False, "아이디는 3자 이상이어야 합니다."
    if len(p) < 6: return False, "비밀번호는 6자 이상이어야 합니다."
    salt = secrets.token_hex(16)
    try:
        c=conn()
        c.execute("INSERT INTO users(username,password_hash,created_at) VALUES(?,?,?)",
                  (u, f"{salt}${hpw(p,salt)}", datetime.now().isoformat(timespec="seconds")))
        c.commit(); c.close()
        return True, "회원가입이 완료되었습니다."
    except sqlite3.IntegrityError:
        return False, "이미 존재하는 아이디입니다."

def login(u,p):
    c=conn(); row=c.execute("SELECT password_hash FROM users WHERE username=?",(u.strip(),)).fetchone(); c.close()
    if not row: return False
    try:
        salt, saved=row[0].split("$",1)
        return secrets.compare_digest(saved,hpw(p,salt))
    except: return False

EVENT = {
"공연":("무대",["객석","음향·조명","출연자 대기실"],"관객의 시야와 무대 집중도를 우선하는 전면 무대형 구조"),
"축제":("메인무대",["체험·부스존","푸드존","휴게존"],"여러 활동을 동시에 수용하는 개방형 구조"),
"전시":("전시존",["전시 A","전시 B","전시 C·체험"],"관람 흐름이 자연스럽게 이어지는 순환형 구조"),
"박람회":("전시·부스존",["상담존","등록·접수","휴게존"],"부스 접근성과 이동 효율을 우선하는 구조"),
"컨퍼런스":("발표무대",["좌석존","등록대","네트워킹존"],"발표 집중도와 네트워킹 동선을 분리한 구조"),
"학교 행사":("메인무대",["학생활동존","객석","운영본부"],"학생 참여와 안전한 이동을 고려한 구조"),
"기타":("메인존",["참여존","휴게존","운영존"],"행사 목적에 따라 기능을 유연하게 배치하는 구조")
}
MOOD={
"활기찬":("참여와 이동이 많은 역동적인 공간","포토존과 체험공간을 주요 동선에 배치합니다."),
"차분한":("여유 있고 소음이 적은 공간","휴게공간과 좌석 사이에 충분한 여유를 둡니다."),
"고급스러운":("넓은 여백과 명확한 시각적 중심","입구부터 메인 공간까지 시각적 흐름을 강조합니다."),
"캐주얼한":("자유롭고 편안한 공간","라운지·휴게공간을 확대합니다."),
"미래지향적":("미디어와 디지털 체험 중심 공간","디지털 체험존을 메인 동선에 연결합니다."),
"자연친화적":("자연광과 개방감을 활용한 공간","창가·외곽의 휴게공간과 그린존을 활용합니다.")
}
AGE={
"10대 이하":"보호자 대기공간, 안전요원, 직관적인 안내를 강화합니다.",
"10~20대":"포토존·체험존·SNS 공유 요소를 주요 동선에 배치합니다.",
"30~40대":"좌석과 휴게공간의 접근성을 높입니다.",
"50대 이상":"좌석·휴식·안내·화장실 접근성을 높입니다.",
"전 연령":"다양한 연령층의 접근성과 안전성을 균형 있게 고려합니다."
}

def design(t,n,h,a,m,fee,place,extra):
    if n<=50: scale,area="소규모",max(80,int(n*2.0))
    elif n<=150: scale,area="중소규모",int(n*1.8)
    elif n<=400: scale,area="중규모",int(n*1.6)
    elif n<=1000: scale,area="대규모",int(n*1.5)
    else: scale,area="초대형",int(n*1.4)
    if h<=2: time="입장→핵심 프로그램→퇴장 흐름을 단순화합니다."
    elif h<=5: time="중간 체류를 고려해 휴게·편의시설을 주요 동선 가까이에 배치합니다."
    else: time="장시간 체류를 고려해 휴게·식음·편의시설을 충분히 확보합니다."
    feeplan=("무료 행사로 입장 절차를 단순화합니다." if fee==0 else
             "일반 유료 행사로 접수·결제·입장 동선을 분리합니다." if fee<=30000 else
             "프리미엄 행사로 체크인과 별도 서비스 공간을 고려합니다.")
    placeplan=("실내의 비상구·소방시설·기둥·냉난방을 고려합니다." if place=="실내" else
               "실외의 기상 변화, 그늘, 전기·음향 보호, 대피공간을 고려합니다.")
    extra_notes=[]
    low=extra.lower()
    for k,v in {
        "포토":"포토존을 주요 동선에 배치합니다.","사진":"포토존을 주요 동선에 배치합니다.",
        "음식":"푸드존을 휴게공간과 가깝게 배치합니다.","푸드":"푸드존을 휴게공간과 가깝게 배치합니다.",
        "푸드트럭":"푸드존을 외곽에 배치해 대기 동선을 확보합니다.","무대":"메인무대의 비중을 확대합니다.",
        "부스":"부스를 주요 이동 동선에 분산합니다.","굿즈":"굿즈존을 출구 방향에 연결합니다.",
        "휴식":"휴게존의 비중을 확대합니다.","휴게":"휴게존의 비중을 확대합니다.",
        "vip":"VIP 공간을 일반 동선과 분리합니다.","체험":"체험존을 중심 동선에 배치합니다."
    }.items():
        if k in low and v not in extra_notes: extra_notes.append(v)
    return dict(scale=scale,area=area,event=t,n=n,h=h,age=a,mood=m,fee=fee,place=place,extra=extra,
                main=EVENT[t][0],secondary=EVENT[t][1],event_desc=EVENT[t][2],
                mood_key=MOOD[m][0],mood_detail=MOOD[m][1],ageplan=AGE[a],
                time=time,feeplan=feeplan,placeplan=placeplan,extra_notes=extra_notes)

def floor(r):
    fig,ax=plt.subplots(figsize=(14,8))
    ax.set_xlim(0,120); ax.set_ylim(0,78); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((3,3),114,70,fill=False,linewidth=2.5))
    ax.text(60,76,f"VIBE SPACE DESIGN — {r['event']}",ha="center",fontsize=16,fontweight="bold")
    boxes=[
      (8,56,104,12,r["main"],"MAIN"),
      (8,34,62,18,"객석 / 주요 참여 공간","AUDIENCE"),
      (74,34,38,18,"체험·부스존","ACTIVITY"),
      (8,20,30,10,"휴게존","REST"),
      (42,20,30,10,"운영본부","STAFF"),
      (76,20,36,10,"안전·응급존","SAFETY"),
      (8,7,30,8,"입구 · 접수","ENTRY"),
      (42,7,30,8,"화장실 / 편의시설","FACILITY"),
      (76,7,36,8,"출구","EXIT")]
    if r["event"]=="공연":
        boxes += [(8,28,62,4,"음향·조명 / FOH","TECH"),(74,56,38,8,"출연자 대기실","BACKSTAGE")]
    elif r["event"]=="축제":
        boxes += [(74,56,38,8,"푸드존","FOOD"),(74,25,38,7,"포토존","PHOTO")]
    elif r["event"]=="전시":
        boxes=[
          (8,56,104,12,"전시 메인존","EXHIBITION"),
          (8,34,30,18,"전시 A","ZONE A"),(42,34,30,18,"전시 B","ZONE B"),
          (76,34,36,18,"전시 C / 체험","ZONE C"),
          (8,20,30,10,"휴게존","REST"),(42,20,30,10,"안내·접수","INFO"),
          (76,20,36,10,"작품 보관 / 운영","STAFF"),
          (8,7,30,8,"입구","ENTRY"),(42,7,30,8,"편의시설","FACILITY"),
          (76,7,36,8,"출구","EXIT")]
    elif r["event"]=="박람회":
        boxes=[
          (8,56,104,10,"발표 / 메인존","MAIN"),
          (8,36,22,16,"부스 A","BOOTH A"),(34,36,22,16,"부스 B","BOOTH B"),
          (60,36,22,16,"부스 C","BOOTH C"),(86,36,26,16,"부스 D","BOOTH D"),
          (8,20,30,10,"등록·접수","REG"),(42,20,30,10,"상담·네트워킹","NETWORK"),
          (76,20,36,10,"휴게존","REST"),(8,7,30,8,"입구","ENTRY"),
          (42,7,30,8,"편의시설","FACILITY"),(76,7,36,8,"출구","EXIT")]
    for x,y,w,h,label,small in boxes:
        ax.add_patch(Rectangle((x,y),w,h,alpha=.18,linewidth=1.5))
        ax.text(x+w/2,y+h/2+1,label,ha="center",va="center",fontsize=10,fontweight="bold")
        ax.text(x+w/2,y+h/2-2.5,small,ha="center",va="center",fontsize=7)
    for s,e in [((22,15),(22,34)),((38,43),(70,43)),((70,43),(92,43)),((98,34),(98,15))]:
        ax.add_patch(FancyArrowPatch(s,e,arrowstyle="<->",mutation_scale=12,linewidth=1.7))
    ax.text(24,25,"입장 동선",fontsize=8,rotation=90,va="center")
    ax.text(54,45.5,"주요 이동 동선",fontsize=8,ha="center")
    ax.text(100,25,"퇴장 동선",fontsize=8,rotation=90,va="center")
    ax.plot([4,116],[18,18],linestyle="--",linewidth=1)
    ax.plot([72,72],[4,72],linestyle="--",linewidth=1)
    ax.text(60,16.2,"외곽 안전통로",ha="center",fontsize=8)
    ax.text(5,1,f"예상 인원 {r['n']:,}명  |  장소: {r['place']}  |  분위기: {r['mood']}",fontsize=9)
    return fig

def explanations(r):
    return [
    f"**전체 배치 전략**  \n{r['n']:,}명 규모의 {r['event']}을 기준으로 약 **{r['area']:,}㎡**를 권장합니다. {r['event_desc']}를 중심으로 메인 공간은 접근성과 시야가 좋은 위치에 두고 운영·안전 공간은 전체를 관리하기 쉬운 위치에 배치했습니다.",
    f"**① 입장·퇴장 동선**  \n입구와 출구를 분리해 방문객이 한곳에서 뒤섞이는 것을 줄였습니다. 입장 후 접수·안내를 거쳐 주요 공간으로 이동하고 행사 종료 후에는 출구로 자연스럽게 빠져나가도록 구성했습니다.",
    f"**② 핵심 공간**  \n메인 공간을 가장 넓고 시야 확보가 쉬운 위치에 배치했습니다. 주변에는 {r['main']}, {', '.join(r['secondary'])} 등을 연결해 주요 프로그램 사이의 이동거리를 줄였습니다.",
    f"**③ 인원수 반영**  \n예상 인원 {r['n']:,}명을 고려해 중앙 이동축과 외곽 안전통로를 확보했습니다. 특히 입구·출구와 메인 공간 사이의 혼잡을 줄이도록 접수 공간을 주요 동선과 적절히 분리했습니다.",
    f"**④ 연령대 반영**  \n주요 방문객은 {r['age']}이며, {r['ageplan']}",
    f"**⑤ 분위기 반영**  \n'{r['mood']}' 분위기를 위해 {r['mood_key']}로 설계했습니다. {r['mood_detail']}",
    f"**⑥ 진행 시간 반영**  \n약 {r['h']:g}시간 행사이므로 {r['time']}",
    f"**⑦ 장소 조건**  \n{r['placeplan']}",
    f"**⑧ 입장료·운영**  \n{r['feeplan']}",
    ("**⑨ 추가 요구사항 반영**  \n" + "  \n".join("- "+x for x in r["extra_notes"])) if r["extra_notes"] else "",
    "**⑩ 안전 설계**  \n비상구와 피난 동선은 장식물·부스로 막지 않는 것을 전제로 합니다. 운영본부와 안전·응급존은 주요 공간을 빠르게 확인하고 접근할 수 있도록 배치했습니다. 실제 행사에서는 현장 구조와 소방·피난·수용인원 기준을 별도로 확인해야 합니다."
    ]

if "logged" not in st.session_state: st.session_state.logged=False
if "user" not in st.session_state: st.session_state.user=""
if "result" not in st.session_state: st.session_state.result=None

if not st.session_state.logged:
    st.markdown("<h1 style='text-align:center'>🎪 VIBE SPACE DESIGNER</h1><p style='text-align:center;font-size:20px'>사용자의 니즈를 분석해 행사장을 설계합니다.</p>",unsafe_allow_html=True)
    a,b=st.tabs(["로그인","회원가입"])
    with a:
        u=st.text_input("아이디",key="li"); p=st.text_input("비밀번호",type="password",key="lp")
        if st.button("로그인",type="primary",use_container_width=True):
            if login(u,p): st.session_state.logged=True; st.session_state.user=u.strip(); st.rerun()
            else: st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
    with b:
        u=st.text_input("새 아이디",key="su"); p=st.text_input("새 비밀번호",type="password",key="sp"); p2=st.text_input("비밀번호 확인",type="password",key="sp2")
        if st.button("회원가입",use_container_width=True):
            if p!=p2: st.error("비밀번호가 일치하지 않습니다.")
            else:
                ok,msg=signup(u,p)
                (st.success if ok else st.error)(msg)
    st.stop()

with st.sidebar:
    st.markdown("## 🎪 VIBE SPACE")
    st.caption(f"사용자: **{st.session_state.user}**")
    if st.button("로그아웃",use_container_width=True):
        st.session_state.logged=False; st.session_state.user=""; st.session_state.result=None; st.rerun()

st.title("🎪 행사장 설계 AI")
st.write("행사 유형·규모·연령대·분위기·장소와 추가 요구사항을 종합해 상세 배치도와 설계 설명을 생성합니다.")
st.markdown("### 1. 행사 정보 입력")

with st.form("form"):
    c1,c2=st.columns(2)
    with c1:
        typ=st.selectbox("행사장의 유형",list(EVENT))
        n=st.number_input("예상 인원수 (명)",1,100000,200,10)
        h=st.number_input("진행 시간 (시간)",.5,24.,4.,.5)
        age=st.selectbox("예상 연령대",list(AGE))
    with c2:
        mood=st.selectbox("원하는 분위기",list(MOOD))
        fee=st.number_input("예상 입장료 (원)",0,10000000,10000,1000)
        place=st.radio("행사 장소",["실내","실외"],horizontal=True)
        extra=st.text_area("추가 요구사항",placeholder="예: 포토존을 크게 만들고 싶어요. 푸드트럭을 많이 넣고 싶어요. 무대를 크게 만들고 싶어요.")
    submit=st.form_submit_button("✨ 상세 행사장 설계하기",use_container_width=True,type="primary")

if submit:
    st.session_state.result=design(typ,n,h,age,mood,fee,place,extra)

r=st.session_state.result
if r:
    st.divider(); st.markdown("## 2. 행사장 설계 결과")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("행사 규모",r["scale"]); c2.metric("예상 인원",f"{r['n']:,}명"); c3.metric("권장 면적",f"{r['area']:,}㎡"); c4.metric("진행 시간",f"{r['h']:g}시간")
    st.markdown("### 🗺️ 상세 행사장 배치도")
    st.caption("입력한 행사 조건을 기준으로 생성한 기획용 배치도입니다.")
    st.pyplot(floor(r),clear_figure=True)
    st.markdown("### 📌 배치도 구성")
    g=st.columns(4)
    g[0].markdown("**① 입구**  \n접수·입장")
    g[1].markdown("**② 메인 공간**  \n핵심 프로그램")
    g[2].markdown("**③ 부대 공간**  \n체험·휴식·운영")
    g[3].markdown("**④ 출구**  \n퇴장 흐름")
    st.divider(); st.markdown("## 3. 배치도 상세 설명")
    for x in explanations(r):
        if x: st.markdown(x); st.write("")
    st.divider(); st.markdown("### 📍 공간별 구성")
    cols=st.columns(3)
    zones=list(dict.fromkeys([r["main"],*r["secondary"],"입구·접수","출구","운영본부","안전·응급존","화장실","안전통로"]))
    for i,z in enumerate(zones): cols[i%3].markdown(f"- **{z}**")
    st.markdown("### 🔄 전체 이동 흐름")
    st.info("입구·접수 → 주요 행사 공간 → 체험·부대시설 → 휴게·편의시설 → 출구 순으로 이동하도록 구성했습니다.")
    st.markdown("### 🛡️ 안전 체크")
    for x in ["입구와 출구의 병목 최소화","비상구·피난 동선을 부스나 장식물로 막지 않기","운영본부에서 주요 공간을 확인할 수 있도록 배치","안전·응급존의 접근성 확보","실외 행사라면 우천·강풍·폭염 등 대체 계획 마련"]:
        st.markdown("- "+x)
else:
    st.markdown("### 🚀 사용 방법\n1. 행사 정보를 입력합니다.\n2. 원하는 분위기와 추가 요구사항을 입력합니다.\n3. **상세 행사장 설계하기**를 누릅니다.\n4. 상세 배치도와 배치 이유를 확인합니다.")
st.divider()
st.caption("VIBE SPACE DESIGNER | 실제 행사에서는 현장 실측 및 소방·피난·전기·수용인원 등 관련 안전기준을 별도로 확인해야 합니다.")
