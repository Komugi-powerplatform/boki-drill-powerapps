import json, sys
root = sys.argv[1]
qs = json.load(open(f"{root}/data/questions.json"))["questions"]
acc = json.load(open(f"{root}/data/accounts.json"))
def s(x): return '"' + str(x).replace('"','""') + '"'
qrows, lrows = [], []
for q in qs:
    qrows.append("{Id:%s, Category:%s, Method:%s, Text:%s, Explain:%s, Traps:%s}" % (
        s(q["id"]), s(q["category"]), s(q["method"] or ""), s(q["text"]), s(q["explain"]), s("、".join(q["traps"]))))
    for side, key in (("借方","debit"),("貸方","credit")):
        for i,l in enumerate(q[key],1):
            alts = l.get("alts") or []
            assert len(alts) <= 1
            lrows.append("{QId:%s, Side:%s, LineNo:%d, Account:%s, Alt:%s, Amount:%d}" % (
                s(q["id"]), s(side), i, s(l["account"]), s(alts[0] if alts else ""), l["amount"]))
arows = ["{Variant:%s, Account:%s}" % (s(k), s(v)) for k,v in acc["aliases"].items()]
ind = "      "
def tbl(name, rows): return f"{ind}{name} = Table(\n" + ",\n".join(ind+"  "+r for r in rows) + f"\n{ind});"
formulas = "\n".join([tbl("nfQuestions", qrows), tbl("nfLines", lrows), tbl("nfAliases", arows),
  f"{ind}NormAcc(t: Text): Text = With({{u: TrimEnds(Substitute(t, \"　\", \" \"))}}, Coalesce(LookUp(nfAliases, Variant = u).Account, u));",
  f"{ind}NormAmt(t: Text): Number = With({{u: TrimEnds(" + "Substitute(" * 12 + "t" + "".join(f", \"{a}\", \"{b}\")" for a, b in zip("０１２３４５６７８９，　", "0123456789, ")) + ")}, If(IsBlank(u), -1, IfError(Value(Substitute(u, \",\", \"\")), -1)));",
  f"{ind}nfMethods = Table({{Key:\"全問\", Color:RGBA(31,35,40,1)}}, {{Key:\"三分法\", Color:RGBA(47,75,138,1)}}, {{Key:\"売上原価対立法\", Color:RGBA(122,74,30,1)}}, {{Key:\"分記法\", Color:RGBA(47,107,69,1)}});"])
formulas = formulas.replace(ind, "", 1)  # first line gets '=' prefix below
onstart = """=Set(varScope, "全問");
      Set(varOrigin, "Screen1");
      Set(varIsWeakDrill, false);
      ClearCollect(colDrill, {Id: "", Seq: 0});
      Clear(colDrill);
      Set(varIdx, 0);
      Set(varTotal, 0);
      Set(varScore, 0);
      Set(varCombo, 0);
      Set(varMaxCombo, 0);
      Set(varCorrect, 0);
      Set(varAnswered, 0);
      Set(varDrillStart, Now());
      Set(varNow, Now());
      Set(varDrillRunning, false);
      Set(varGraded, false);
      Set(varLastCorrect, false);
      Set(varLastGain, 0);
      Set(varLastBonus, 0);
      Set(varWeakMsg, "");
      Set(varWeakSaveFailed, false);
      Set(varEmptyError, false);
      Set(varQuitConfirm, false);
      Set(varDebRows, 1);
      Set(varCreRows, 1);
      Set(varEndReason, "");
      Set(varIsNewBest, false);
      Set(varBestSaveFailed, false);
      Set(varPrevBest, 0);
      Set(varHadBest, false);
      Set(varQ, First(nfQuestions));
      Set(varWeakAdded, 0);
      Set(varWeakRemoved, 0);
      Set(varHomeLoad, "loading");
      Set(varWeakLoad, "loading")"""
out = f"""App:
  Properties:
    Formulas: |-
      ={formulas}
    OnStart: |-
      {onstart}
    StartScreen: =Screen1
    Theme: =PowerAppsTheme
"""
open(sys.argv[2], "w").write(out)
print(len(out), len(qrows), len(lrows))
