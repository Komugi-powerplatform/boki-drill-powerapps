"""問題データ data/questions.json の整合性テスト。

採点は「科目の一字一句一致」なので、正解側の科目が公式表記でないと
間違った表記を覚えさせてしまう。ここで機械的に止める。
"""

import json
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ACCOUNTS = json.loads((ROOT / "data/accounts.json").read_text(encoding="utf-8"))
OFFICIAL = set(ACCOUNTS["accounts"]) | set(ACCOUNTS["aliases"])
QUESTIONS = json.loads((ROOT / "data/questions.json").read_text(encoding="utf-8"))[
    "questions"
]
CATEGORIES = {
    "現金預金",
    "債権債務",
    "商品売買",
    "固定資産",
    "給料・税金",
    "決算",
    "株式会社",
}
METHODS = {"三分法", "分記法", "売上原価対立法", None}


def ids(q):
    return q["id"]


def test_official_list_has_no_duplicates():
    assert len(ACCOUNTS["accounts"]) == len(set(ACCOUNTS["accounts"]))


def test_question_count():
    assert len(QUESTIONS) >= 40


def test_ids_unique():
    dup = [k for k, v in Counter(q["id"] for q in QUESTIONS).items() if v > 1]
    assert dup == []


@pytest.mark.parametrize("q", QUESTIONS, ids=ids)
def test_required_fields(q):
    assert q["text"].strip()
    assert q["explain"].strip()
    assert q["category"] in CATEGORIES
    assert q.get("method") in METHODS
    assert q["debit"] and q["credit"]


@pytest.mark.parametrize("q", QUESTIONS, ids=ids)
def test_accounts_are_official(q):
    used = [l["account"] for l in q["debit"] + q["credit"]]
    assert [a for a in used if a not in OFFICIAL] == []


@pytest.mark.parametrize("q", QUESTIONS, ids=ids)
def test_amounts_positive_int(q):
    for l in q["debit"] + q["credit"]:
        assert isinstance(l["amount"], int) and l["amount"] > 0


@pytest.mark.parametrize("q", QUESTIONS, ids=ids)
def test_debit_equals_credit(q):
    assert sum(l["amount"] for l in q["debit"]) == sum(l["amount"] for l in q["credit"])


@pytest.mark.parametrize("q", QUESTIONS, ids=ids)
def test_same_account_not_on_one_side_twice(q):
    for side in ("debit", "credit"):
        names = [l["account"] for l in q[side]]
        assert len(names) == len(set(names))


@pytest.mark.parametrize("q", QUESTIONS, ids=ids)
def test_max_three_lines_per_side(q):
    # スマホ画面で入力欄を各側3行までに固定するため
    assert len(q["debit"]) <= 3 and len(q["credit"]) <= 3


@pytest.mark.parametrize("q", QUESTIONS, ids=ids)
def test_traps_are_not_official(q):
    # 引っかけ表記（よくある誤記）が公式表記と被っていたら採点が壊れる
    for t in q.get("traps", []):
        assert t not in OFFICIAL


def test_merchandise_methods_covered():
    methods = Counter(q.get("method") for q in QUESTIONS if q["category"] == "商品売買")
    for m in ("三分法", "分記法", "売上原価対立法"):
        assert methods[m] >= 3, m


@pytest.mark.parametrize("q", QUESTIONS, ids=ids)
def test_alts_are_official(q):
    for l in q["debit"] + q["credit"]:
        assert [a for a in l.get("alts", []) if a not in OFFICIAL] == []
