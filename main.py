import re
from typing import Sequence

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from db import crud
from db.crud import SessionDep
from models.database import Person
from models.request import ModelRequestQuery
from models.response import ModelResponsePersonAggregated

app = FastAPI(
    root_path="/breach",
    title="172.16.1.4",
    version="1.0.0",
    summary="个人信息 “泄漏” 查询接口",
    contact={
        "name": "嘉林数据",
        "url": "https://breach.garinasset.com",
        "email": "contact@garinasset.com",
    },
    license_info={
        "name": "CC BY 4.0",
        "identifier": "CC-BY-4.0",
    }
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("", summary="Hello breach! 🚀 http://172.16.1.4/breach",
         response_class=PlainTextResponse,
         responses={
             200: {
                 "content": {
                     "text/plain": {
                         "example": "Hello breach!\n"
                     }
                 }
             }
         }
         )
async def root():
    return f"Hello breach!\n"


@app.get("/", summary="响应 数据库 记录",
         response_class=PlainTextResponse,
         responses={
             200: {
                 "content": {
                     "text/plain": {
                         "example": "0\n"
                     }
                 }
             }
         }
         )
async def get_counts(session: SessionDep):
    counts = crud.read_counts(session=session)
    return counts


# ---------- 类型识别函数 ----------
def detect_input_type(user_input: str) -> str:
    """
    返回唯一类型：
    - phone
    - qq
    - email
    - id
    - unknown
    """

    phone_pattern = r"^1\d{10}$"
    # 排除手机号的 QQ
    qq_pattern = r"^(?!1\d{10}$)\d{5,11}$"
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    id_pattern = r"^\d{17}[\dXx]$"

    if re.fullmatch(phone_pattern, user_input):
        return "phone"
    elif re.fullmatch(email_pattern, user_input):
        return "email"
    elif re.fullmatch(id_pattern, user_input):
        return "id"
    elif re.fullmatch(qq_pattern, user_input):
        return "qq"
    else:
        return "unknown"

def clean_str_set(values):
    return list({
        v.strip() for v in values
        if isinstance(v, str) and v.strip()
    })


def clean_int_set(values):
    result = set()
    for v in values:
        try:
            if v is not None and str(v).strip():
                result.add(int(v))
        except (ValueError, TypeError):
            continue
    return list(result)

@app.post("/dig", summary="查询 个人信息“泄漏” 记录", response_model=ModelResponsePersonAggregated)
def get_person_by_dig(body: ModelRequestQuery, session: SessionDep):
    # 定义局部变量
    persons: Sequence[Person] = []

    input_type = detect_input_type(body.q)

    match input_type:
        case "phone":
            persons = crud.read_persons_by_dig(session, phone_=body.q)
        case "qq":
            persons = crud.read_persons_by_dig(session, qq_=int(body.q))
        case "email":
            persons = crud.read_persons_by_dig(session, email_=body.q)
        case "id":
            persons = crud.read_persons_by_dig(session, id_=body.q)
        case _:
            raise ValueError(f"未知类型: {body.q}")

    # 聚合并去重
    aggregated = ModelResponsePersonAggregated(
        id=list({p.id for p in persons if p.id is not None}),

        name=clean_str_set(p.name for p in persons),
        receiver=clean_str_set(p.receiver for p in persons),
        nickname=clean_str_set(p.nickname for p in persons),
        phone=clean_str_set(p.phone for p in persons),
        address=clean_str_set(p.address for p in persons),
        car=clean_str_set(p.car for p in persons),
        email=clean_str_set(p.email for p in persons),

        qq=clean_int_set(p.qq for p in persons),
        weibo=clean_int_set(p.weibo for p in persons),

        contact=clean_str_set(p.contact for p in persons),
        company=clean_str_set(p.company for p in persons),

        source=list({
            p.source_obj.source
            for p in persons
            if p.source_obj and p.source_obj.source
        })
    )
    return aggregated
