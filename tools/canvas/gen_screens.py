"""Generate the 4 screen .pa.yaml files for 簿記ドリル (CREATE stage, coordinator-built)."""

import sys

OUT = sys.argv[1]

BG = "RGBA(247, 246, 242, 1)"
CARD = "RGBA(255, 255, 255, 1)"
LINE = "RGBA(217, 214, 207, 1)"
INK = "RGBA(31, 35, 40, 1)"
SUB = "RGBA(90, 95, 102, 1)"
PRI = "RGBA(46, 94, 110, 1)"
OK_T, OK_F = "RGBA(30, 107, 58, 1)", "RGBA(230, 242, 234, 1)"
NG_T, NG_F = "RGBA(161, 38, 43, 1)", "RGBA(248, 231, 231, 1)"
WN_T, WN_F = "RGBA(122, 83, 0, 1)", "RGBA(255, 244, 214, 1)"
METHOD_COLOR = 'Switch(varQ.Method, "三分法", RGBA(47, 75, 138, 1), "売上原価対立法", RGBA(122, 74, 30, 1), "分記法", RGBA(47, 107, 69, 1), RGBA(31, 35, 40, 1))'
COLW = "Min(560, Parent.Width)"


def q(v):
    """YAML-safe single-line formula value."""
    s = "=" + v
    if any(c in s for c in [": ", "#", "{", "}"]) or s.endswith(":"):
        return "'" + s.replace("'", "''") + "'"
    return s


def block(v, indent):
    lines = v.strip("\n").split("\n")
    pad = " " * indent
    return "|-\n" + "\n".join(
        pad + ("=" if i == 0 else "") + ln for i, ln in enumerate(lines)
    )


class C:
    def __init__(self, name, control, props, children=None, variant=None):
        self.name, self.control, self.props, self.children, self.variant = (
            name,
            control,
            props,
            children or [],
            variant,
        )

    def render(self, ind):
        p = " " * ind
        out = [f"{p}- {self.name}:", f"{p}    Control: {self.control}"]
        if self.variant:
            out.append(f"{p}    Variant: {self.variant}")
        out.append(f"{p}    Properties:")
        for k, v in self.props.items():
            if "\n" in v:
                out.append(f"{p}      {k}: {block(v, ind + 8)}")
            else:
                out.append(f"{p}      {k}: {q(v)}")
        if self.children:
            out.append(f"{p}    Children:")
            for ch in self.children:
                out.extend(ch.render(ind + 6))
        return out


def child(fill="0", align="AlignInContainer.Stretch", minw="0"):
    return {"FillPortions": fill, "AlignInContainer": align, "LayoutMinWidth": minw}


def box(
    name,
    direction,
    children,
    height=None,
    fill_portions="0",
    fill="RGBA(0, 0, 0, 0)",
    pad=(0, 0, 0, 0),
    gap="0",
    align_items="LayoutAlignItems.Stretch",
    justify=None,
    scroll=False,
    width=None,
    extra=None,
    border=None,
    align="AlignInContainer.Stretch",
):
    props = {
        "LayoutDirection": f"LayoutDirection.{direction}",
        "LayoutAlignItems": align_items,
        "LayoutGap": gap,
        "PaddingTop": str(pad[0]),
        "PaddingRight": str(pad[1]),
        "PaddingBottom": str(pad[2]),
        "PaddingLeft": str(pad[3]),
        "Fill": fill,
        "DropShadow": "DropShadow.None",
        "LayoutMinWidth": "0",
        "LayoutMinHeight": "0",
        "FillPortions": fill_portions,
        "AlignInContainer": align,
        "RadiusTopLeft": "0",
        "RadiusTopRight": "0",
        "RadiusBottomLeft": "0",
        "RadiusBottomRight": "0",
    }
    if justify:
        props["LayoutJustifyContent"] = justify
    if height is not None:
        props["Height"] = str(height)
    if width is not None:
        props["Width"] = width
    if scroll:
        props["LayoutOverflowY"] = "LayoutOverflow.Scroll"
    if border:
        props.update(
            {
                "BorderColor": border,
                "BorderThickness": "1",
                "BorderStyle": "BorderStyle.Solid",
                "RadiusTopLeft": "8",
                "RadiusTopRight": "8",
                "RadiusBottomLeft": "8",
                "RadiusBottomRight": "8",
            }
        )
    if extra:
        props.update(extra)
    return C(name, "GroupContainer", props, children, variant="AutoLayout")


def text(
    name,
    value,
    size=17,
    height=None,
    weight="Normal",
    color=INK,
    wrap=True,
    auto=False,
    fill=None,
    pad=0,
    align_text="Align.Left",
    visible=None,
    fill_portions="0",
    width=None,
    acc=None,
    valign=None,
):
    props = {
        "Text": value,
        "Size": str(size),
        "FontWeight": f"FontWeight.{weight}",
        "Color": color,
        "Wrap": "true" if wrap else "false",
        "PaddingTop": str(pad),
        "PaddingBottom": str(pad),
        "PaddingLeft": str(pad),
        "PaddingRight": str(pad),
        "Align": align_text,
        "LayoutMinWidth": "0",
        "FillPortions": fill_portions,
        "AlignInContainer": "AlignInContainer.Stretch",
    }
    if auto:
        props["AutoHeight"] = "true"
        props["LayoutMinHeight"] = str(height or 24)
        props["Height"] = str(height or 24)
    else:
        props["Height"] = str(height or round(size * 1.5 + 2 * pad))
        props["LayoutMinHeight"] = props["Height"]
    if fill:
        props["Fill"] = fill
    if visible:
        props["Visible"] = visible
    if width:
        props["Width"] = width
        props["AlignInContainer"] = "AlignInContainer.Center"
    if acc:
        props["AccessibleLabel"] = acc
    if valign:
        props["VerticalAlign"] = valign
    return C(name, "ModernText", props)


def button(
    name,
    label,
    onselect,
    height=52,
    primary=True,
    disabled=None,
    visible=None,
    acc=None,
    width=None,
    size=17,
    color=None,
    border=None,
    fill_portions="0",
):
    props = {
        "Text": label,
        "OnSelect": onselect,
        "Height": str(height),
        "LayoutMinHeight": str(height),
        "LayoutMinWidth": "0",
        "FillPortions": fill_portions,
        "AlignInContainer": "AlignInContainer.Stretch",
        "Size": str(size),
        "Layout": "ButtonLayout.TextOnly",
        "Appearance": "ButtonAppearance.Primary"
        if primary
        else "ButtonAppearance.Outline",
        "BasePaletteColor": PRI,
        "AccessibleLabel": acc or label,
    }
    if disabled:
        props["DisplayMode"] = f"If({disabled}, DisplayMode.Disabled, DisplayMode.Edit)"
    if visible:
        props["Visible"] = visible
    if width:
        props["Width"] = width
    if color:
        props["Color"] = color
    if border:
        props["BorderColor"] = border
    return C(name, "ModernButton", props)


def screen(key, props, root_children):
    root = box(
        f"con{key}Root",
        "Vertical",
        root_children,
        fill=BG,
        align_items="LayoutAlignItems.Center",
        extra={"Width": "Parent.Width", "Height": "Parent.Height", "X": "0", "Y": "0"},
    )
    # root is a direct screen child: drop AutoLayout-child-only props
    for k in ["FillPortions", "AlignInContainer", "LayoutMinWidth", "LayoutMinHeight"]:
        root.props.pop(k, None)
    out = ["Screens:", f"  {key}:", "    Properties:"]
    for k, v in props.items():
        out.append(f"      {k}: {block(v, 8) if chr(10) in v else q(v)}")
    out.append("    Children:")
    out.extend(root.render(6))
    return "\n".join(out) + "\n"


# ---------- shared behavior snippets ----------
POOL = (
    "If(varIsWeakDrill, Filter(nfQuestions, Id in colWeak.Title), "
    'If(varScope = "全問", nfQuestions, Filter(nfQuestions, Method = varScope)))'
)


def start_drill(scope_expr, origin_expr, weak_expr):
    return f"""Set(varScope, {scope_expr});
Set(varIsWeakDrill, {weak_expr});
Set(varOrigin, {origin_expr});
If(varIsWeakDrill, IfError(ClearCollect(colWeak, BokiWeakList), Set(varWeakLoad, "error"), Set(varWeakLoad, "ok")));
ClearCollect(colDrill, ForAll(Shuffle({POOL}) As p, {{Id: p.Id, Seq: 0}}));
Set(varTotal, CountRows(colDrill));
Set(varIdx, 1);
Set(varQ, LookUp(nfQuestions, Id = First(colDrill).Id));
Set(varScore, 0); Set(varCombo, 0); Set(varMaxCombo, 0); Set(varCorrect, 0); Set(varAnswered, 0);
Set(varWeakAdded, 0); Set(varWeakRemoved, 0);
Set(varGraded, false); Set(varQuitConfirm, false); Set(varEmptyError, false);
Set(varWeakMsg, ""); Set(varWeakSaveFailed, false);
Set(varDebRows, 1); Set(varCreRows, 1);
Set(varEndReason, ""); Set(varIsNewBest, false); Set(varBestSaveFailed, false);
Set(varDrillStart, Now()); Set(varNow, Now());
Set(varDrillRunning, varTotal > 0);
If(varTotal > 0, Navigate(scrDrill))"""


END_DRILL = """Set(varDrillRunning, false);
Set(varQuitConfirm, false);
IfError(
    ClearCollect(colBest, Filter(BokiBestScore, Title = "best")),
    Set(varBestSaveFailed, true)
);
Set(varHadBest, !IsEmpty(colBest));
Set(varPrevBest, If(IsEmpty(colBest), 0, First(colBest).Score));
Set(varIsNewBest, !varBestSaveFailed && (IsEmpty(colBest) || varScore > First(colBest).Score));
If(varIsNewBest,
    If(IsError(
        If(IsEmpty(colBest),
            Patch(BokiBestScore, Defaults(BokiBestScore), {Title: "best", Score: varScore, AchievedAt: Now()}),
            Patch(BokiBestScore, First(colBest), {Score: varScore, AchievedAt: Now()})
        )),
        Set(varBestSaveFailed, true)
    )
);
Navigate(scrResult)"""

RESET_INPUTS = ";\n".join(
    f"Reset(inpDrill{s}{f}{i})"
    for s in ("Deb", "Cre")
    for f in ("Acc", "Amt")
    for i in (1, 2, 3)
)

# =====================================================================
# S1 Home (Screen1)
# =====================================================================
SCOPE_N = "(scope) => 0"  # placeholder (not used)


def scope_count(k):
    return f"CountRows({'nfQuestions' if k == '全問' else f'Filter(nfQuestions, Method = "{k}")'})"


home_scope_btns = []
for i, k in enumerate(["全問", "三分法", "売上原価対立法", "分記法"], 1):
    home_scope_btns.append(
        button(
            f"btnHomeScope{i}",
            f'If(varScope = "{k}", "✓ ", "") & "{k}（" & {scope_count(k)} & "問）"',
            f'Set(varScope, "{k}")',
            height=48,
            primary=False,
            size=16,
            acc=f'"出題範囲 {k} " & {scope_count(k)} & "問" & If(varScope = "{k}", " 選択中", "")',
        )
    )
    b = home_scope_btns[-1]
    b.props["Appearance"] = (
        f'If(varScope = "{k}", ButtonAppearance.Primary, ButtonAppearance.Outline)'
    )
    b.props["Text"] = b.props["Text"]

HOME_N = 'CountRows(If(varScope = "全問", nfQuestions, Filter(nfQuestions, Method = varScope)))'
home = screen(
    "Screen1",
    {
        "Fill": BG,
        "OnVisible": """Set(varDrillRunning, false);
Set(varQuitConfirm, false);
Set(varHomeLoad, "loading");
IfError(
    ClearCollect(colWeak, BokiWeakList), Set(varHomeLoad, "error"),
    ClearCollect(colBest, Filter(BokiBestScore, Title = "best")), Set(varHomeLoad, "error"),
    Set(varHomeLoad, "ok")
)""",
    },
    [
        box(
            "conHomeTop",
            "Vertical",
            [
                text("lblHomeTitle", '"簿記ドリル"', size=20, weight="Bold", height=30),
                text("lblHomeSub", '"全経3級 仕訳"', size=13, color=SUB, height=20),
            ],
            height=74,
            pad=(12, 16, 12, 16),
            gap="0",
            width=COLW,
            align="AlignInContainer.Center",
        ),
        box(
            "conHomeBody",
            "Vertical",
            [
                box(
                    "conHomeSummary",
                    "Vertical",
                    [
                        text(
                            "lblHomeBestLabel",
                            '"自己ベスト"',
                            size=14,
                            weight="Semibold",
                            color=SUB,
                            height=22,
                        ),
                        text(
                            "lblHomeBest",
                            'Switch(varHomeLoad, "loading", "読み込み中…", "error", "—", If(IsEmpty(colBest), "まだ記録がありません", First(colBest).Score & " 点"))',
                            size='If(varHomeLoad = "ok" && !IsEmpty(colBest), 32, 17)',
                            weight="Bold",
                            height=48,
                            acc='"自己ベスト " & Self.Text',
                        ),
                        text(
                            "lblHomeBestAt",
                            'If(varHomeLoad = "ok" && !IsEmpty(colBest), Text(First(colBest).AchievedAt, "yyyy/mm/dd hh:mm") & " 達成", "")',
                            size=13,
                            color=SUB,
                            height=20,
                        ),
                        text(
                            "lblHomeWeak",
                            '"苦手 " & Switch(varHomeLoad, "loading", "読み込み中…", "error", "—", CountRows(colWeak) & "問")',
                            size=17,
                            weight="Semibold",
                            height=28,
                        ),
                        text(
                            "lblHomeErr",
                            '"! 自己ベストと苦手リストを読み込めませんでした。ドリルは始められます。"',
                            size=14,
                            color=WN_T,
                            fill=WN_F,
                            height=48,
                            pad=4,
                            visible='varHomeLoad = "error"',
                        ),
                        text(
                            "lblHomeRule",
                            '"1回 3分・正解1問10点＋コンボボーナス"',
                            size=13,
                            color=SUB,
                            height=20,
                        ),
                    ],
                    height='If(varHomeLoad = "error", 252, 200)',
                    fill=CARD,
                    pad=(16, 16, 16, 16),
                    gap="4",
                    border=LINE,
                ),
                text(
                    "lblHomeScopeLabel",
                    '"出題範囲"',
                    size=14,
                    weight="Semibold",
                    height=22,
                ),
                box(
                    "conHomeScopes",
                    "Vertical",
                    home_scope_btns,
                    height=4 * 48 + 3 * 8,
                    gap="8",
                ),
                button(
                    "btnHomeWeak",
                    '"苦手リストを見る ›"',
                    "Navigate(scrWeak)",
                    height=48,
                    primary=False,
                    size=16,
                ),
            ],
            fill_portions="1",
            pad=(8, 16, 16, 16),
            gap="16",
            scroll=True,
            width=COLW,
            align="AlignInContainer.Center",
        ),
        box(
            "conHomeBottom",
            "Vertical",
            [
                text(
                    "lblHomeScopeInfo",
                    f'If({HOME_N} = 0, "この範囲には問題がありません", varScope & "・" & {HOME_N} & "問")',
                    size=13,
                    color=SUB,
                    height=20,
                ),
                button(
                    "btnHomeStart",
                    '"ドリル開始"',
                    start_drill("varScope", '"Screen1"', "false"),
                    disabled=f"{HOME_N} = 0",
                    acc=f'"ドリル開始 " & varScope & " " & {HOME_N} & "問"',
                ),
            ],
            height=96,
            pad=(8, 16, 12, 16),
            gap="4",
            fill=BG,
            width=COLW,
            align="AlignInContainer.Center",
        ),
    ],
)

# =====================================================================
# S2 Drill
# =====================================================================
REMAIN = "Max(0, 180 - DateDiff(varDrillStart, varNow, TimeUnit.Seconds))"


def ans_row(side_code, side, i):
    rows_var = "varDebRows" if side_code == "Deb" else "varCreRows"
    res = f'LookUp(colAnsR, Side = "{side}" && RowNo = {i})'
    mark = text(
        f"lblDrill{side_code}Mark{i}",
        f'If(IsBlank({res}), "", If({res}.OK, "○", "×"))',
        size=20,
        weight="Bold",
        height=48,
        width="44",
        align_text="Align.Center",
        color=f"If({res}.OK, {OK_T}, {NG_T})",
        visible="varGraded",
        acc=f'"{side} {i}行目 " & If(IsBlank({res}), "未入力", If({res}.OK, "正しい", "誤り"))',
        valign="VerticalAlign.Middle",
    )
    mark.props["LayoutMinWidth"] = "44"
    delete = button(
        f"btnDrill{side_code}Del{i}",
        '"×"',
        (
            f"Reset(inpDrill{side_code}Acc{i}); Reset(inpDrill{side_code}Amt{i})"
            if i == 1
            else f"Reset(inpDrill{side_code}Acc{i}); Reset(inpDrill{side_code}Amt{i}); Set({rows_var}, {rows_var} - 1)"
        ),
        height=48,
        primary=False,
        width="44",
        size=16,
        visible=("!varGraded" if i == 1 else f"!varGraded && {rows_var} = {i}"),
        disabled="varQuitConfirm",
        acc=f'"{side} {i}行目を削除"',
    )
    delete.props["LayoutMinWidth"] = "44"
    delete.props["AlignInContainer"] = "AlignInContainer.Center"
    spacer = text(
        f"lblDrill{side_code}Gap{i}",
        '""',
        size=13,
        height=48,
        width="44",
        visible=f"!varGraded && {i} > 1 && {rows_var} <> {i}",
    )
    spacer.props["LayoutMinWidth"] = "44"

    def inp(field, width=None):
        props = {
            "Default": '""',
            "Placeholder": '""',
            "Height": "48",
            "LayoutMinHeight": "48",
            "LayoutMinWidth": "0",
            "Size": "16",
            "Type": "TextInputType.SingleLine",
            "TriggerOutput": "TriggerOutput.Keypress",
            "AccessibleLabel": f'"{side} {i}行目 {"科目名" if field == "Acc" else "金額"}"',
            "DisplayMode": "If(varGraded || varQuitConfirm, DisplayMode.View, DisplayMode.Edit)",
            "FillPortions": "1" if width is None else "0",
            "AlignInContainer": "AlignInContainer.Stretch",
            "Appearance": "Appearance.Outline",
            "ValidationState": f"If(varGraded && !IsBlank({res}) && !{res}.OK, ValidationState.Error, ValidationState.None)",
        }
        if width:
            props["Width"] = width
            props["Align"] = "Align.Right"
        return C(f"inpDrill{side_code}{field}{i}", "ModernTextInput", props)

    return box(
        f"conDrill{side_code}Row{i}",
        "Horizontal",
        [inp("Acc"), inp("Amt", "104"), delete, spacer, mark],
        height=48,
        gap="8",
        align_items="LayoutAlignItems.Center",
        extra={"Visible": f"{rows_var} >= {i}"},
    )


def side_section(side_code, side):
    rows_var = "varDebRows" if side_code == "Deb" else "varCreRows"
    n_ans = f'CountRows(Filter(colAnsR, Side = "{side}"))'
    n_ok = f'CountRows(Filter(nfLines, QId = varQ.Id && Side = "{side}"))'
    return box(
        f"conDrill{side_code}",
        "Vertical",
        [
            box(
                f"conDrill{side_code}Head",
                "Horizontal",
                [
                    text(
                        f"lblDrill{side_code}Title",
                        f'"{side}"',
                        size=14,
                        weight="Bold",
                        height=24,
                        fill_portions="1",
                    ),
                    text(
                        f"lblDrill{side_code}Count",
                        '"行数が違います"',
                        size=13,
                        color=NG_T,
                        height=24,
                        fill_portions="1",
                        align_text="Align.Right",
                        visible=f"varGraded && {n_ans} <> {n_ok}",
                    ),
                ],
                height=24,
                gap="8",
            ),
            box(
                f"conDrill{side_code}Cols",
                "Horizontal",
                [
                    text(
                        f"lblDrill{side_code}ColAcc",
                        '"科目名"',
                        size=13,
                        color=SUB,
                        height=20,
                        fill_portions="1",
                    ),
                    text(
                        f"lblDrill{side_code}ColAmt",
                        '"金額"',
                        size=13,
                        color=SUB,
                        height=20,
                        width="104",
                        align_text="Align.Right",
                    ),
                    text(
                        f"lblDrill{side_code}ColPad",
                        '""',
                        size=13,
                        height=20,
                        width="44",
                    ),
                ],
                height=20,
                gap="8",
            ),
            ans_row(side_code, side, 1),
            ans_row(side_code, side, 2),
            ans_row(side_code, side, 3),
            button(
                f"btnDrill{side_code}Add",
                f'If({rows_var} >= 3, "{side}は3行まで", "+ {side}の行を追加")',
                f"Set({rows_var}, Min(3, {rows_var} + 1))",
                height=44,
                primary=False,
                size=15,
                disabled=f"{rows_var} >= 3 || varQuitConfirm",
                visible="!varGraded",
            ),
        ],
        height=f"24 + 8 + 20 + 8 + {rows_var} * 56 + If(varGraded, 0, 52)",
        gap="8",
    )


# correct-entry rows (graded detail) as gallery-free text lines
def correct_lines_text(side):
    return (
        f'Concat(SortByColumns(Filter(nfLines, QId = varQ.Id && Side = "{side}"), "LineNo"), '
        f'Account & If(Alt <> "", "（" & Alt & " も可）", "") & "　" & Text(Amount, "#,##0"), Char(10))'
    )


GRADE = """If(varGraded || varQuitConfirm, false,
ClearCollect(colAns,
    {Side: "借方", RowNo: 1, Shown: varDebRows >= 1, RawAcc: inpDrillDebAcc1.Text, RawAmt: inpDrillDebAmt1.Text},
    {Side: "借方", RowNo: 2, Shown: varDebRows >= 2, RawAcc: inpDrillDebAcc2.Text, RawAmt: inpDrillDebAmt2.Text},
    {Side: "借方", RowNo: 3, Shown: varDebRows >= 3, RawAcc: inpDrillDebAcc3.Text, RawAmt: inpDrillDebAmt3.Text},
    {Side: "貸方", RowNo: 1, Shown: varCreRows >= 1, RawAcc: inpDrillCreAcc1.Text, RawAmt: inpDrillCreAmt1.Text},
    {Side: "貸方", RowNo: 2, Shown: varCreRows >= 2, RawAcc: inpDrillCreAcc2.Text, RawAmt: inpDrillCreAmt2.Text},
    {Side: "貸方", RowNo: 3, Shown: varCreRows >= 3, RawAcc: inpDrillCreAcc3.Text, RawAmt: inpDrillCreAmt3.Text}
);
ClearCollect(colAnsR,
    AddColumns(
        AddColumns(
            Filter(colAns, Shown && (!IsBlank(TrimEnds(Substitute(RawAcc, "　", " "))) || !IsBlank(TrimEnds(Substitute(RawAmt, "　", " "))))),
            Acc, NormAcc(RawAcc),
            Amt, NormAmt(RawAmt)
        ) As a,
        OK, !IsEmpty(Filter(nfLines As l, l.QId = varQ.Id && l.Side = a.Side && (l.Account = a.Acc || (l.Alt <> "" && l.Alt = a.Acc)) && l.Amount = a.Amt))
    )
);
If(IsEmpty(colAnsR),
    Set(varEmptyError, true),
    Set(varEmptyError, false);
    Set(varLastCorrect,
        CountRows(Filter(colAnsR, Side = "借方")) = CountRows(Filter(nfLines, QId = varQ.Id && Side = "借方")) &&
        CountRows(Filter(colAnsR, Side = "貸方")) = CountRows(Filter(nfLines, QId = varQ.Id && Side = "貸方")) &&
        IsEmpty(Filter(nfLines As l, l.QId = varQ.Id && IsEmpty(Filter(colAnsR As a, a.Side = l.Side && a.OK && (l.Account = a.Acc || (l.Alt <> "" && l.Alt = a.Acc)) && l.Amount = a.Amt))))
    );
    Set(varAnswered, varAnswered + 1);
    Set(varWeakMsg, "");
    Set(varWeakSaveFailed, false);
    If(varLastCorrect,
        Set(varCombo, varCombo + 1);
        Set(varLastBonus, Min(10, 2 * (varCombo - 1)));
        Set(varLastGain, 10 + varLastBonus);
        Set(varScore, varScore + varLastGain);
        Set(varCorrect, varCorrect + 1);
        Set(varMaxCombo, Max(varMaxCombo, varCombo));
        If(varIsWeakDrill,
            IfError(
                Remove(BokiWeakList, LookUp(BokiWeakList, Title = varQ.Id)),
                Set(varWeakSaveFailed, true);
                Set(varWeakMsg, "! 苦手リストから外せませんでした。この問題はリストに残ります"),
                Set(varWeakRemoved, varWeakRemoved + 1);
                Set(varWeakMsg, "苦手リストから外しました")
            )
        ),
        Set(varCombo, 0);
        Set(varLastBonus, 0);
        Set(varLastGain, 0);
        With({w: LookUp(BokiWeakList, Title = varQ.Id)},
            IfError(
                If(IsBlank(w),
                    Patch(BokiWeakList, Defaults(BokiWeakList), {Title: varQ.Id, MissCount: 1, LastMissedAt: Now()}),
                    Patch(BokiWeakList, w, {MissCount: w.MissCount + 1, LastMissedAt: Now()})
                ),
                Set(varWeakSaveFailed, true);
                Set(varWeakMsg, "! 苦手リストに保存できませんでした"),
                If(IsBlank(w),
                    Set(varWeakAdded, varWeakAdded + 1);
                    Set(varWeakMsg, "苦手リストに追加しました"),
                    Set(varWeakMsg, "苦手リストの誤答回数が " & (w.MissCount + 1) & "回 になりました")
                )
            )
        )
    );
    Set(varGraded, true)
)
)"""

NEXT = f"""If(varIdx >= varTotal,
    Set(varEndReason, "全問終了");
{END_DRILL},
    Set(varIdx, varIdx + 1);
    Set(varQ, LookUp(nfQuestions, Id = Index(colDrill, varIdx).Id));
    Set(varGraded, false);
    Set(varEmptyError, false);
    Set(varWeakMsg, "");
    Set(varWeakSaveFailed, false);
    Set(varDebRows, 1);
    Set(varCreRows, 1);
    Clear(colAnsR);
{RESET_INPUTS}
)"""

TIMER_END = f"""Set(varNow, Now());
If(varDrillRunning && DateDiff(varDrillStart, varNow, TimeUnit.Seconds) >= 180,
    Set(varEndReason, "時間切れ");
{END_DRILL}
)"""

drill = screen(
    "scrDrill",
    {
        "Fill": BG,
        "OnVisible": f"""Set(varNow, Now());
Clear(colAnsR);
{RESET_INPUTS}""",
    },
    [
        # status band (fixed)
        box(
            "conDrillStatus",
            "Vertical",
            [
                box(
                    "conDrillStatus1",
                    "Horizontal",
                    [
                        text(
                            "lblDrillRemain",
                            f'"残り " & Int({REMAIN} / 60) & ":" & Text(Mod({REMAIN}, 60), "00")',
                            size=20,
                            weight="Bold",
                            height=44,
                            fill_portions="1",
                            color=f"If({REMAIN} <= 30, {NG_T}, {INK})",
                            valign="VerticalAlign.Middle",
                        ),
                        text(
                            "lblDrillNo",
                            '"第" & varIdx & "問 / " & varTotal',
                            size=14,
                            color=SUB,
                            height=44,
                            width="96",
                            align_text="Align.Right",
                            valign="VerticalAlign.Middle",
                        ),
                        button(
                            "btnDrillQuit",
                            '"中断"',
                            "Set(varQuitConfirm, true)",
                            height=44,
                            primary=False,
                            width="72",
                            size=15,
                            disabled="varQuitConfirm",
                            acc='"ドリルを中断"',
                        ),
                    ],
                    height=44,
                    gap="8",
                    align_items="LayoutAlignItems.Center",
                ),
                box(
                    "conDrillStatus2",
                    "Horizontal",
                    [
                        text(
                            "lblDrillCorrect",
                            '"正解 " & varCorrect',
                            size=15,
                            weight="Semibold",
                            height=26,
                            fill_portions="1",
                        ),
                        text(
                            "lblDrillCombo",
                            '"コンボ " & varCombo',
                            size=15,
                            weight="Semibold",
                            height=26,
                            fill_portions="1",
                        ),
                        text(
                            "lblDrillScore",
                            '"得点 " & varScore',
                            size=15,
                            weight="Semibold",
                            height=26,
                            fill_portions="1",
                            align_text="Align.Right",
                        ),
                    ],
                    height=26,
                    gap="8",
                ),
                C(
                    "tmrDrill",
                    "Timer",
                    {
                        "Duration": "1000",
                        "Repeat": "true",
                        "AutoStart": "false",
                        "AutoPause": "true",
                        "Start": "varDrillRunning",
                        "OnTimerEnd": TIMER_END,
                        "Visible": "false",
                        "Height": "0",
                        "Width": "0",
                        "FillPortions": "0",
                        "LayoutMinHeight": "0",
                        "LayoutMinWidth": "0",
                    },
                ),
            ],
            height=94,
            pad=(8, 16, 8, 16),
            gap="8",
            fill=CARD,
            width=COLW,
            align="AlignInContainer.Center",
        ),
        # body (scroll)
        box(
            "conDrillBody",
            "Vertical",
            [
                box(
                    "conDrillVerdict",
                    "Vertical",
                    [
                        text(
                            "lblDrillVerdict",
                            'If(varLastCorrect, "○ 正解", "× 不正解")',
                            size=20,
                            weight="Bold",
                            height=30,
                            color=f"If(varLastCorrect, {OK_T}, {NG_T})",
                        ),
                        text(
                            "lblDrillGain",
                            'If(varLastCorrect, "+10点" & If(varLastBonus > 0, "（コンボボーナス +" & varLastBonus & "点）", ""), "コンボは0に戻りました")',
                            size=15,
                            height=24,
                        ),
                        text(
                            "lblDrillWeakMsg",
                            "varWeakMsg",
                            size=14,
                            height=44,
                            pad=0,
                            color=f"If(varWeakSaveFailed, {WN_T}, {INK})",
                            fill=f"If(varWeakSaveFailed, {WN_F}, RGBA(0, 0, 0, 0))",
                        ),
                    ],
                    height=130,
                    pad=(12, 12, 12, 12),
                    gap="4",
                    fill=f"If(varLastCorrect, {OK_F}, {NG_F})",
                    border=LINE,
                    extra={"Visible": "varGraded"},
                ),
                text(
                    "lblDrillMethod",
                    '"記帳方式：" & varQ.Method',
                    size=18,
                    weight="Bold",
                    color="RGBA(255, 255, 255, 1)",
                    fill=METHOD_COLOR,
                    height=44,
                    pad=8,
                    visible='varQ.Method <> ""',
                    valign="VerticalAlign.Middle",
                ),
                text(
                    "lblDrillText",
                    "varQ.Text",
                    size=17,
                    auto=True,
                    height=60,
                    fill=CARD,
                    pad=12,
                    acc='If(varQ.Method <> "", "記帳方式 " & varQ.Method & "。", "") & varQ.Text',
                ),
                text(
                    "lblDrillEmpty",
                    '"科目名と金額を入力してください"',
                    size=14,
                    weight="Semibold",
                    color=NG_T,
                    fill=NG_F,
                    height=36,
                    pad=6,
                    visible="varEmptyError && !varGraded",
                ),
                side_section("Deb", "借方"),
                side_section("Cre", "貸方"),
                # graded detail
                box(
                    "conDrillDetail",
                    "Vertical",
                    [
                        text(
                            "lblDrillAnsTitle",
                            '"正解仕訳"',
                            size=14,
                            weight="Bold",
                            height=22,
                        ),
                        text(
                            "lblDrillAnsDeb",
                            f'"借方" & Char(10) & {correct_lines_text("借方")}',
                            size=16,
                            auto=True,
                            height=48,
                        ),
                        text(
                            "lblDrillAnsCre",
                            f'"貸方" & Char(10) & {correct_lines_text("貸方")}',
                            size=16,
                            auto=True,
                            height=48,
                        ),
                        text(
                            "lblDrillTrap",
                            '"注意：ひっかけ科目　" & varQ.Traps',
                            size=15,
                            weight="Semibold",
                            color=WN_T,
                            fill=WN_F,
                            auto=True,
                            height=32,
                            pad=6,
                            visible='!varLastCorrect && varQ.Traps <> ""',
                        ),
                        text(
                            "lblDrillExplainTitle",
                            '"解説"',
                            size=14,
                            weight="Bold",
                            height=22,
                        ),
                        text(
                            "lblDrillExplain",
                            "varQ.Explain",
                            size=17,
                            auto=True,
                            height=48,
                        ),
                    ],
                    height=420,
                    pad=(12, 12, 12, 12),
                    gap="8",
                    fill=CARD,
                    border=LINE,
                    extra={"Visible": "varGraded"},
                ),
            ],
            fill_portions="1",
            pad=(12, 16, 16, 16),
            gap="12",
            scroll=True,
            width=COLW,
            align="AlignInContainer.Center",
        ),
        # action band
        box(
            "conDrillAction",
            "Vertical",
            [
                button(
                    "btnDrillSubmit",
                    '"解答を確定"',
                    GRADE,
                    visible="!varGraded && !varQuitConfirm",
                ),
                button(
                    "btnDrillNext",
                    'If(varIdx >= varTotal, "結果を見る", "次の問題へ")',
                    NEXT,
                    visible="varGraded && !varQuitConfirm",
                ),
                text(
                    "lblDrillQuitMsg",
                    '"ドリルをやめますか？ 得点は自己ベストに記録されません"',
                    size=14,
                    height=40,
                    visible="varQuitConfirm",
                ),
                box(
                    "conDrillQuitBtns",
                    "Horizontal",
                    [
                        button(
                            "btnDrillQuitCancel",
                            '"続ける"',
                            "Set(varQuitConfirm, false)",
                            height=44,
                            primary=False,
                            fill_portions="1",
                        ),
                        button(
                            "btnDrillQuitOk",
                            '"やめる"',
                            'Set(varDrillRunning, false); Set(varQuitConfirm, false); Navigate(If(varOrigin = "scrWeak", scrWeak, Screen1))',
                            height=44,
                            primary=False,
                            fill_portions="1",
                            color=NG_T,
                            border=NG_T,
                        ),
                    ],
                    height=44,
                    gap="8",
                    extra={"Visible": "varQuitConfirm"},
                ),
            ],
            height="If(varQuitConfirm, 104, 76)",
            pad=(8, 16, 16, 16),
            gap="4",
            fill=BG,
            width=COLW,
            align="AlignInContainer.Center",
        ),
    ],
)

# =====================================================================
# S3 Result
# =====================================================================
REPEAT_N = f"CountRows({POOL})"
result = screen(
    "scrResult",
    {
        "Fill": BG,
        "OnVisible": 'IfError(ClearCollect(colWeak, BokiWeakList), Set(varWeakLoad, "error"), Set(varWeakLoad, "ok"))',
    },
    [
        box(
            "conResTop",
            "Horizontal",
            [
                button(
                    "btnResBack",
                    '"‹ 戻る"',
                    'Navigate(If(varOrigin = "scrWeak", scrWeak, Screen1))',
                    height=44,
                    primary=False,
                    width="88",
                    size=15,
                    acc='"戻る"',
                ),
                text(
                    "lblResTitle",
                    '"結果"',
                    size=20,
                    weight="Bold",
                    height=44,
                    fill_portions="1",
                    align_text="Align.Center",
                    valign="VerticalAlign.Middle",
                ),
                text("lblResTopPad", '""', size=13, height=44, width="88"),
            ],
            height=64,
            pad=(10, 16, 10, 16),
            gap="8",
            align_items="LayoutAlignItems.Center",
            width=COLW,
            align="AlignInContainer.Center",
        ),
        box(
            "conResBody",
            "Vertical",
            [
                box(
                    "conResScore",
                    "Vertical",
                    [
                        text(
                            "lblResReason",
                            "varEndReason",
                            size=13,
                            color=SUB,
                            height=20,
                        ),
                        text(
                            "lblResScore",
                            'varScore & " 点"',
                            size=32,
                            weight="Bold",
                            height=50,
                            acc='varEndReason & "。得点 " & varScore & "点"',
                        ),
                        text(
                            "lblResBest",
                            'If(varIsNewBest, "○ 自己ベスト更新！ " & If(varHadBest, "これまで " & varPrevBest & "点", "初めての記録です"), '
                            'If(varBestSaveFailed, "", "自己ベスト " & varPrevBest & "点（あと " & (varPrevBest - varScore) & "点）"))',
                            size=16,
                            weight="Semibold",
                            height=36,
                            pad=6,
                            color=f"If(varIsNewBest, {OK_T}, {INK})",
                            fill=f"If(varIsNewBest, {OK_F}, RGBA(0, 0, 0, 0))",
                        ),
                        text(
                            "lblResBestErr",
                            '"! 自己ベストを保存できませんでした。次回起動時には反映されません"',
                            size=14,
                            color=WN_T,
                            fill=WN_F,
                            height=48,
                            pad=4,
                            visible="varBestSaveFailed",
                        ),
                    ],
                    height="If(varBestSaveFailed, 200, 148)",
                    pad=(16, 16, 16, 16),
                    gap="4",
                    fill=CARD,
                    border=LINE,
                ),
                box(
                    "conResStats",
                    "Horizontal",
                    [
                        text(
                            "lblResCorrect",
                            '"正解 " & varCorrect & " ／ " & varAnswered & "問"',
                            size=18,
                            weight="Semibold",
                            height=30,
                            fill_portions="1",
                        ),
                        text(
                            "lblResCombo",
                            '"最大コンボ " & varMaxCombo',
                            size=18,
                            weight="Semibold",
                            height=30,
                            fill_portions="1",
                        ),
                    ],
                    height=30,
                    gap="8",
                ),
                text(
                    "lblResWeak",
                    'If(varIsWeakDrill, "苦手リストから外れた " & varWeakRemoved & "問・追加 " & varWeakAdded & "問", "苦手リストに追加 " & varWeakAdded & "問")',
                    size=16,
                    height=26,
                ),
                button(
                    "btnResWeak",
                    '"苦手リストへ"',
                    "Navigate(scrWeak)",
                    height=48,
                    primary=False,
                    size=16,
                ),
                button(
                    "btnResHome",
                    '"ホームへ"',
                    "Navigate(Screen1)",
                    height=48,
                    primary=False,
                    size=16,
                ),
            ],
            fill_portions="1",
            pad=(8, 16, 16, 16),
            gap="16",
            scroll=True,
            width=COLW,
            align="AlignInContainer.Center",
        ),
        box(
            "conResBottom",
            "Vertical",
            [
                text(
                    "lblResScopeInfo",
                    f'If({REPEAT_N} = 0, "この範囲には問題がありません", If(varIsWeakDrill, "苦手のみ", varScope) & "・" & {REPEAT_N} & "問")',
                    size=13,
                    color=SUB,
                    height=20,
                ),
                button(
                    "btnResAgain",
                    '"同じ範囲でもう一度"',
                    start_drill("varScope", "varOrigin", "varIsWeakDrill"),
                    disabled=f"{REPEAT_N} = 0",
                ),
            ],
            height=96,
            pad=(8, 16, 12, 16),
            gap="4",
            fill=BG,
            width=COLW,
            align="AlignInContainer.Center",
        ),
    ],
)

# =====================================================================
# S4 Weak list
# =====================================================================
WEAK_ITEMS = (
    "SortByColumns(AddColumns(Filter(nfQuestions, Id in colWeak.Title) As qq, "
    "Miss, LookUp(colWeak, Title = qq.Id).MissCount, Last, LookUp(colWeak, Title = qq.Id).LastMissedAt), "
    '"Miss", SortOrder.Descending, "Last", SortOrder.Descending)'
)
weak = screen(
    "scrWeak",
    {
        "Fill": BG,
        "OnVisible": """Set(varWeakLoad, "loading");
IfError(ClearCollect(colWeak, BokiWeakList), Set(varWeakLoad, "error"), Set(varWeakLoad, "ok"))""",
    },
    [
        box(
            "conWeakTop",
            "Horizontal",
            [
                button(
                    "btnWeakBack",
                    '"‹ 戻る"',
                    "Navigate(Screen1)",
                    height=44,
                    primary=False,
                    width="88",
                    size=15,
                    acc='"戻る"',
                ),
                text(
                    "lblWeakTitle",
                    '"苦手リスト"',
                    size=20,
                    weight="Bold",
                    height=44,
                    fill_portions="1",
                    align_text="Align.Center",
                    valign="VerticalAlign.Middle",
                ),
                text("lblWeakTopPad", '""', size=13, height=44, width="88"),
            ],
            height=64,
            pad=(10, 16, 10, 16),
            gap="8",
            align_items="LayoutAlignItems.Center",
            width=COLW,
            align="AlignInContainer.Center",
        ),
        box(
            "conWeakBody",
            "Vertical",
            [
                text(
                    "lblWeakCount",
                    '"苦手 " & Switch(varWeakLoad, "loading", "—", "error", "—", CountRows(colWeak) & "問")',
                    size=20,
                    weight="Bold",
                    height=30,
                ),
                text(
                    "lblWeakOrder",
                    '"誤答回数の多い順（同数は最後に間違えた日時の新しい順）"',
                    size=13,
                    color=SUB,
                    height=20,
                ),
                text(
                    "lblWeakLoading",
                    '"読み込み中…"',
                    size=17,
                    height=30,
                    visible='varWeakLoad = "loading"',
                ),
                text(
                    "lblWeakErr",
                    '"! 苦手リストを読み込めませんでした"',
                    size=15,
                    color=WN_T,
                    fill=WN_F,
                    height=40,
                    pad=6,
                    visible='varWeakLoad = "error"',
                ),
                button(
                    "btnWeakRetry",
                    '"再読み込み"',
                    'Set(varWeakLoad, "loading"); IfError(ClearCollect(colWeak, BokiWeakList), Set(varWeakLoad, "error"), Set(varWeakLoad, "ok"))',
                    height=44,
                    primary=False,
                    size=15,
                    visible='varWeakLoad = "error"',
                ),
                text(
                    "lblWeakEmpty",
                    '"苦手問題はありません" & Char(10) & "間違えた問題がここに入ります"',
                    size=17,
                    height=60,
                    visible='varWeakLoad = "ok" && IsEmpty(colWeak)',
                ),
                C(
                    "galWeak",
                    "Gallery",
                    {
                        "Items": WEAK_ITEMS,
                        "TemplateSize": "124",
                        "TemplatePadding": "0",
                        "Height": f"CountRows({WEAK_ITEMS}) * 124",
                        "LayoutMinHeight": "0",
                        "LayoutMinWidth": "0",
                        "FillPortions": "0",
                        "AlignInContainer": "AlignInContainer.Stretch",
                        "ShowScrollbar": "false",
                        "Selectable": "false",
                        "TabIndex": "0",
                        "BorderThickness": "0",
                        "AccessibleLabel": '"苦手問題の一覧"',
                        "Visible": 'varWeakLoad = "ok" && !IsEmpty(colWeak)',
                        "DelayItemLoading": "false",
                        "LoadingSpinner": "LoadingSpinner.None",
                    },
                    [
                        C(
                            "conWeakCard",
                            "GroupContainer",
                            {
                                "X": "0",
                                "Y": "0",
                                "Width": "Parent.TemplateWidth",
                                "Height": "Parent.TemplateHeight - 8",
                                "Fill": CARD,
                                "BorderColor": LINE,
                                "BorderThickness": "1",
                                "DropShadow": "DropShadow.None",
                                "LayoutDirection": "LayoutDirection.Vertical",
                                "LayoutAlignItems": "LayoutAlignItems.Stretch",
                                "LayoutGap": "4",
                                "PaddingTop": "10",
                                "PaddingBottom": "10",
                                "PaddingLeft": "12",
                                "PaddingRight": "12",
                            },
                            [
                                box(
                                    "conWeakCardHead",
                                    "Horizontal",
                                    [
                                        text(
                                            "lblWeakCardMethod",
                                            'If(ThisItem.Method = "", ThisItem.Category, ThisItem.Method & "・" & ThisItem.Category)',
                                            size=13,
                                            weight="Semibold",
                                            height=22,
                                            fill_portions="1",
                                            color='Switch(ThisItem.Method, "三分法", RGBA(47, 75, 138, 1), "売上原価対立法", RGBA(122, 74, 30, 1), "分記法", RGBA(47, 107, 69, 1), RGBA(90, 95, 102, 1))',
                                        ),
                                        text(
                                            "lblWeakCardMiss",
                                            '"誤答 " & ThisItem.Miss & "回"',
                                            size=14,
                                            weight="Bold",
                                            height=22,
                                            width="88",
                                            align_text="Align.Right",
                                        ),
                                    ],
                                    height=22,
                                    gap="8",
                                ),
                                text(
                                    "lblWeakCardText",
                                    "ThisItem.Text",
                                    size=15,
                                    height=44,
                                    acc='"誤答 " & ThisItem.Miss & "回。" & ThisItem.Text',
                                ),
                                text(
                                    "lblWeakCardLast",
                                    'If(IsBlank(ThisItem.Last), "", "最後に間違えた日時 " & Text(ThisItem.Last, "yyyy/mm/dd hh:mm"))',
                                    size=13,
                                    color=SUB,
                                    height=20,
                                ),
                            ],
                            variant="AutoLayout",
                        ),
                    ],
                    variant="Vertical",
                ),
            ],
            fill_portions="1",
            pad=(8, 16, 16, 16),
            gap="12",
            scroll=True,
            width=COLW,
            align="AlignInContainer.Center",
        ),
        box(
            "conWeakBottom",
            "Vertical",
            [
                text(
                    "lblWeakStartInfo",
                    'Switch(varWeakLoad, "loading", "読み込み中…", "error", "苦手リストを読み込めないため開始できません", '
                    'If(IsEmpty(colWeak), "苦手問題がないため開始できません", CountRows(Filter(nfQuestions, Id in colWeak.Title)) & "問・3分"))',
                    size=13,
                    color=SUB,
                    height=20,
                ),
                button(
                    "btnWeakStart",
                    '"苦手問題で再挑戦"',
                    start_drill('"苦手"', '"scrWeak"', "true"),
                    disabled='varWeakLoad <> "ok" || IsEmpty(Filter(nfQuestions, Id in colWeak.Title))',
                ),
            ],
            height=96,
            pad=(8, 16, 12, 16),
            gap="4",
            fill=BG,
            width=COLW,
            align="AlignInContainer.Center",
        ),
    ],
)

for name, content in [
    ("Screen1", home),
    ("scrDrill", drill),
    ("scrResult", result),
    ("scrWeak", weak),
]:
    open(f"{OUT}/{name}.pa.yaml", "w").write(content)
    print(name, len(content))
