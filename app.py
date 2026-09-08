import streamlit as st
import sqlite3, hashlib, secrets
from pathlib import Path
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

st.set_page_config(page_title="VIBE SPACE DESIGNER", page_icon="🎪", layout="wide")
DB = Path(__file__).parent / "users.db"

def db():
    c=sqlite3.connect(DB,check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE,
    password_hash TEXT, created_at TEXT)""")
    c.commit(); return c

def h(p,s): return hashlib.pbkdf2_hmac("sha256",p.encode(),s.encode(),120000).hex()

def signup(u,p):
    u=u.strip()
    if len(u)<3 or len(p)<6: return False,"아이디 3자 이상, 비밀번호 6자 이상이 필요합니다."
    s=secrets.token_hex(16)
    try:
        c=db(); c.execute("INSERT INTO users(username,password_hash,created_at) VALUES(?,?,?)",
                          (u,f"{s}${h(p,s)}",datetime.now().isoformat())); c.commit(); c.close()
        return True,"회원가입이 완료되었습니다."
    except sqlite3.IntegrityError: return False,"이미 존재하는 아이디입니다."

def login(u,p):
    c=db(); r=c.execute("SELECT password_hash FROM users WHERE username=?",(u.strip(),)).fetchone(); c.close()
    if not r:return False
    try:
        s,x=r[0].split("$",1); return secrets.compare_digest(x,h(p,s))
    except:return False

for k,v in {"logged":False,"user":"","info":None,"spaces":[],"chat":[]}.items():
    if k not in st.session_state: st.session_state[k]=v

if not st.session_state.logged:
    st.markdown("<div style='text-align:center;padding:50px'><h1>🎪 VIBE SPACE DESIGNER</h1><p>AI와 대화하며 나만의 행사장을 설계하세요.</p></div>",unsafe_allow_html=True)
    a,b=st.tabs(["로그인","회원가입"])
    with a:
        u=st.text_input("아이디"); p=st.text_input("비밀번호",type="password")
        if st.button("로그인",type="primary",use_container_width=True):
            if login(u,p): st.session_state.logged=True; st.session_state.user=u.strip(); st.rerun()
            else: st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
    with b:
        u=st.text_input("새 아이디",key="su"); p=st.text_input("새 비밀번호",type="password",key="sp"); q=st.text_input("비밀번호 확인",type="password")
        if st.button("회원가입",use_container_width=True):
            if p!=q: st.error("비밀번호가 일치하지 않습니다.")
            else:
                ok,msg=signup(u,p); (st.success if ok else st.error)(msg)
    st.stop()

if st.session_state.info is None:
    st.markdown("<h1 style='text-align:center'>🎪 VIBE SPACE DESIGNER</h1><p style='text-align:center'>처음에는 5가지만 입력하고, 나머지는 채팅으로 함께 발전시킵니다.</p>",unsafe_allow_html=True)
    with st.form("start"):
        name=st.text_input("이벤트 이름",placeholder="예: 아산 청소년 음악 페스티벌")
        purpose=st.text_area("이벤트 목적",placeholder="예: 청소년들이 음악을 즐기고 교류하는 축제")
        c1,c2,c3=st.columns(3)
        visitors=c1.number_input("예상 방문객 수",1,100000,300,10)
        budget=c2.number_input("예산 (원)",0,10000000000,10000000,100000)
        location=c3.text_input("장소",placeholder="예: 학교 운동장 / 체육관 / 공원")
        ok=st.form_submit_button("✨ 행사장 설계 시작하기",type="primary",use_container_width=True)
    if ok:
        if not name.strip() or not purpose.strip() or not location.strip(): st.error("5개 기본 정보 중 빠진 항목을 입력해주세요.")
        else:
            st.session_state.info={"name":name.strip(),"purpose":purpose.strip(),"visitors":int(visitors),"budget":int(budget),"location":location.strip()}
            st.session_state.chat=[{"role":"assistant","content":f"좋아요! **{name}** 행사를 함께 설계해볼게요. 현재 보드는 비어 있습니다. 원하는 공간을 자연스럽게 말해주세요. 예: `큰 무대를 만들어줘`, `입구 옆에 포토존을 추가해줘`"}]
            st.rerun()
    st.stop()

def add_spaces(text):
    rules=[
        (["무대","stage"],"무대","stage"),(["객석","좌석","관객석"],"객석","audience"),
        (["부스"],"부스존","booth"),(["푸드","푸드트럭","음식"],"푸드존","food"),
        (["포토","사진"],"포토존","photo"),(["휴게","휴식","라운지"],"휴게존","rest"),
        (["화장실","편의시설"],"편의시설","facility"),(["입구","입장"],"입구","entry"),
        (["출구","퇴장"],"출구","exit"),(["운영본부","운영실","스태프"],"운영본부","staff"),
        (["응급","의무실","안전"],"안전·응급존","safety"),(["체험"],"체험존","activity")]
    made=[]
    for keys,label,kind in rules:
        if any(x in text.lower() for x in keys) and not any(s["label"]==label for s in st.session_state.spaces):
            i=len(st.session_state.spaces)+len(made)
            positions={
                "stage":(32,62,56,10),"audience":(25,35,70,20),"booth":(78,22,30,12),
                "food":(78,22,30,12),"photo":(10,22,28,12),"rest":(42,20,30,12),
                "entry":(8,5,28,10),"exit":(84,5,28,10)}
            x,y,w,h=positions.get(kind,(8+(i%4)*25,7,20,10))
            made.append({"label":label,"kind":kind,"x":x,"y":y,"w":w,"h":h})
    st.session_state.spaces.extend(made); return made

def modify(text):
    low=text.lower()
    for s in st.session_state.spaces:
        if s["label"] not in text: continue
        if "크게" in low or "넓게" in low: s["w"]=min(95,s["w"]*1.25); s["h"]=min(32,s["h"]*1.2)
        if "작게" in low: s["w"]=max(10,s["w"]*.75); s["h"]=max(6,s["h"]*.8)
        e=next((x for x in st.session_state.spaces if x["kind"]=="entry"),None)
        q=next((x for x in st.session_state.spaces if x["kind"]=="exit"),None)
        if e and "입구" in low: s["x"]=e["x"]+30; s["y"]=e["y"]+8
        if q and "출구" in low: s["x"]=q["x"]-25; s["y"]=q["y"]+8

def board(spaces,flow=False,heat=0):
    fig,ax=plt.subplots(figsize=(12,7)); ax.set_xlim(0,120); ax.set_ylim(0,80); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((2,2),116,74,fill=False,linewidth=2)); ax.text(60,78,"EVENT SPACE BOARD",ha="center",fontsize=16,fontweight="bold")
    if not spaces:
        ax.text(60,40,"EMPTY BOARD",ha="center",fontsize=22,alpha=.35); ax.text(60,35,"채팅으로 원하는 공간을 말해보세요.",ha="center",fontsize=11,alpha=.6); return fig
    if heat:
        for s in spaces:
            if s["kind"] in ("entry","audience","food","photo","activity","stage"):
                cx,cy=s["x"]+s["w"]/2,s["y"]+s["h"]/2
                for j in range(3): ax.add_patch(Circle((cx,cy),10+heat*3-j*2,alpha=.05*heat))
    for s in spaces:
        ax.add_patch(Rectangle((s["x"],s["y"]),s["w"],s["h"],alpha=.2,linewidth=1.8))
        ax.text(s["x"]+s["w"]/2,s["y"]+s["h"]/2,s["label"],ha="center",va="center",fontsize=10,fontweight="bold")
    if flow:
        e=next((s for s in spaces if s["kind"]=="entry"),None); a=next((s for s in spaces if s["kind"]=="audience"),None); q=next((s for s in spaces if s["kind"]=="exit"),None)
        if e and a: ax.add_patch(FancyArrowPatch((e["x"]+e["w"]/2,e["y"]+e["h"]),(a["x"]+a["w"]/2,a["y"]),arrowstyle="->",mutation_scale=15,linewidth=2))
        if a:
            for t in [s for s in spaces if s["kind"] in ("food","photo","activity","rest")]:
                ax.add_patch(FancyArrowPatch((a["x"]+a["w"]/2,a["y"]+a["h"]/2),(t["x"]+t["w"]/2,t["y"]+t["h"]/2),arrowstyle="->",mutation_scale=12,linewidth=1.5))
        if q and a: ax.add_patch(FancyArrowPatch((a["x"]+a["w"],a["y"]+a["h"]/2),(q["x"]+q["w"]/2,q["y"]+q["h"]),arrowstyle="->",mutation_scale=15,linewidth=2))
    return fig

def heatmap(spaces,t,visitors):
    fig,ax=plt.subplots(figsize=(12,7)); x=np.linspace(0,120,180); y=np.linspace(0,80,120); X,Y=np.meshgrid(x,y); D=np.zeros_like(X)
    phase={11:.45,12:.6,13:.75,14:.95,15:1,16:.85,17:.7,18:.55,19:.35,20:.2}.get(t,.65)
    for s in spaces:
        if s["kind"] not in ("entry","audience","food","photo","activity","stage","exit"): continue
        cx,cy=s["x"]+s["w"]/2,s["y"]+s["h"]/2; sx=max(5,s["w"]/2); sy=max(4,s["h"]/2); strength=phase
        if s["kind"] in ("stage","audience"): strength*=1.35
        if t in (11,12) and s["kind"]=="entry": strength*=1.6
        if t in (18,19,20) and s["kind"]=="exit": strength*=1.7
        D+=strength*np.exp(-(((X-cx)**2)/(2*sx**2)+((Y-cy)**2)/(2*sy**2)))
    if D.max(): D/=D.max()
    D*=min(1,.35+visitors/1000)
    ax.imshow(D,extent=[0,120,0,80],origin="lower",interpolation="bilinear",alpha=.7,aspect="auto")
    for s in spaces:
        ax.add_patch(Rectangle((s["x"],s["y"]),s["w"],s["h"],fill=False,linewidth=1.2)); ax.text(s["x"]+s["w"]/2,s["y"]+s["h"]/2,s["label"],ha="center",va="center",fontsize=8,fontweight="bold")
    ax.set_title(f"예상 방문객 혼잡도 Heatmap · {t}:00",fontsize=15,fontweight="bold"); ax.set_xlabel("공간 가로 위치"); ax.set_ylabel("공간 세로 위치")
    return fig

with st.sidebar:
    st.markdown("## 🎪 VIBE SPACE")
    st.caption(f"사용자: **{st.session_state.user}**")
    if st.button("새 행사"): st.session_state.info=None; st.session_state.spaces=[]; st.session_state.chat=[]; st.rerun()
    if st.button("로그아웃"): st.session_state.logged=False; st.rerun()

info=st.session_state.info
st.title(info["name"])
st.caption(f"방문객 {info['visitors']:,}명 · 예산 {info['budget']:,}원 · {info['location']}")

left,right=st.columns([.38,.62],gap="large")
with left:
    st.markdown("### 💬 AI DESIGNER")
    chatbox=st.container(height=480)
    with chatbox:
        for m in st.session_state.chat:
            with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt=st.chat_input("예: 무대를 크게 만들고 입구 반대편에 배치해줘")
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        modify(prompt); made=add_spaces(prompt)
        if made:
            names=", ".join(x["label"] for x in made)
            ans=f"좋아요. **{names}**을(를) 보드에 추가했습니다. 계속해서 위치, 크기, 동선 등을 채팅으로 수정할 수 있습니다."
        elif "혼잡" in prompt or "동선" in prompt:
            ans="오른쪽의 **방문객 이동 동선**과 **시간대별 혼잡도** 탭에서 시각화할 수 있습니다."
        else:
            ans="요구사항을 설계 조건으로 반영했습니다. 원하는 공간이나 배치 변경을 자연스럽게 말해주세요."
        st.session_state.chat.append({"role":"assistant","content":ans}); st.rerun()

with right:
    st.markdown("### 🗺️ DESIGN BOARD")
    t1,t2,t3=st.tabs(["설계 보드","방문객 이동 동선","시간대별 혼잡도"])
    with t1:
        st.caption("처음에는 빈 보드입니다. 채팅할수록 도형이 하나씩 추가됩니다.")
        st.pyplot(board(st.session_state.spaces),clear_figure=True)
    with t2:
        if st.session_state.spaces: st.pyplot(board(st.session_state.spaces,flow=True),clear_figure=True)
        else: st.warning("먼저 공간을 추가해주세요.")
    with t3:
        if st.session_state.spaces:
            t=st.slider("시간 선택",11,20,15,format="%d:00")
            st.pyplot(heatmap(st.session_state.spaces,t,info["visitors"]),clear_figure=True)
            level="높음" if t in (14,15,16) else "보통~높음" if t in (12,13,17) else "낮음~보통"
            st.markdown(f"**{t}:00 예상 혼잡도: {level}**")
            st.caption("※ 실제 센서 데이터가 없는 기획 단계의 예상 시각화입니다.")
        else: st.warning("먼저 공간을 추가해주세요.")

st.divider()
st.markdown("### 📋 현재 설계")
if st.session_state.spaces:
    st.write(" · ".join(s["label"] for s in st.session_state.spaces))
else:
    st.info("아직 공간이 없습니다. 왼쪽 AI와 대화하면서 하나씩 추가해보세요.")
st.caption("VIBE SPACE DESIGNER v3 · 실제 행사에서는 현장 실측 및 관련 안전기준을 별도로 확인해야 합니다.")
