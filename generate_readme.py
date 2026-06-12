#!/usr/bin/env python3
"""Regenerate README.md (and README_zh.md) from data/medical_world_models.csv.

Usage:  python generate_readme.py
Edit the CSV to add/update entries, then re-run. Do not hand-edit the READMEs.
"""
import csv, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "medical_world_models.csv")
LAST_VERIFIED = "2026-06-10"

TRACK_ORDER = [
    "T1_definition_review_digital_twin",
    "T2_imaging_representation_world_model",
    "T3_longitudinal_disease_progression",
    "T4_ehr_patient_trajectory",
    "T5_counterfactual_treatment_planning",
    "T6_surgical_robotic_physiology_world_model",
    "T7_background_methods",
]
TRACK = {
    "T1_definition_review_digital_twin":        ("Definitions, Reviews & Digital Twins", "定义、综述与数字孪生", "t1"),
    "T2_imaging_representation_world_model":     ("Medical Imaging World Models",          "医学影像世界模型",     "t2"),
    "T3_longitudinal_disease_progression":       ("Longitudinal Disease Progression",      "纵向疾病进展",         "t3"),
    "T4_ehr_patient_trajectory":                 ("EHR & Patient-Trajectory Models",       "EHR 与患者轨迹模型",   "t4"),
    "T5_counterfactual_treatment_planning":      ("Counterfactuals & Treatment Planning",  "反事实与治疗规划",     "t5"),
    "T6_surgical_robotic_physiology_world_model":("Surgical, Robotic & Physiology Models",  "手术、机器人与生理模型","t6"),
    "T7_background_methods":                      ("Foundational & Background Methods",      "基础与背景方法",       "t7"),
}
LEVELS = ["L0", "L1", "L2", "L3", "L4"]
LEVEL_COLOR = {"L0": "7A7A7A", "L1": "3B6CA8",
               "L2": "4E9A51", "L3": "D98A3D", "L4": "C0504D"}
LEVEL_DESC = {
    "L0": ("static prediction (perception)", "静态预测（感知）"),
    "L1": ("future prediction (Pearl: association)", "未来预测（Pearl：关联）"),
    "L2": ("action-conditioned simulation (intervention)", "动作条件仿真（干预）"),
    "L3": ("counterfactual reasoning", "反事实推理"),
    "L4": ("planning & control", "规划与控制"),
}

T = {  # UI strings: (en, zh)
    "title": ("🏥 Awesome Medical World Models", "🏥 Awesome Medical World Models"),
    "tagline": ("**From static prediction to clinically valid, action-aware simulation.**",
                "**从静态预测，迈向临床有效、可感知动作的仿真。**"),
    "intro": (
        "A curated, **capability-coded** map of medical world models. Every paper is placed on a "
        "**capability ladder** (how far it reaches) and audited with a **SATO-V** rubric (which evidence it actually has), "
        "so that *\"looks like a world model\"* and *\"supports a clinical decision\"* can finally be told apart.",
        "一份**按能力编码**的医学世界模型地图。每篇论文都被放在一条**能力阶梯**上（走到了哪一层），"
        "并用 **SATO-V** 准则审计（到底有哪块证据），从而把*“看起来像 world model”*和*“真的能支持临床决策”*区分开。"),
    "papers": ("papers", "论文"),
    "opensource": ("open-source", "开源"),
    "core": ("core", "核心"),
    "verified": ("verified", "更新于"),
    "stat_papers": ("📚 Total papers", "📚 论文总数"),
    "stat_open": ("💻 With open-source code", "💻 含开源代码"),
    "stat_core": ("🌟 Core (self-identified) world models", "🌟 核心（自我标定）世界模型"),
    "stat_levels": ("🪜 Capability levels", "🪜 能力层级"),
    "stat_tracks": ("🗂️ Tracks", "🗂️ 主题轨道"),
    "stat_verified": ("✅ Last verified", "✅ 最近核对"),
    "lang": ("🌐 Language: **English** | [中文](./README_zh.md)",
             "🌐 语言: [English](./README.md) | **中文**"),
    "legend_h": ("## 🪜 The Capability Ladder", "## 🪜 能力阶梯"),
    "legend_lvl": ("Level", "层级"),
    "legend_mean": ("Meaning", "含义"),
    "satov": ("**SATO-V** = **S**tate · **A**ction · **T**ransition · **O**utcome · **V**alidation — the five components a medical world-model claim should evidence.",
              "**SATO-V** = **S**tate（状态）· **A**ction（动作）· **T**ransition（转移）· **O**utcome（结局）· **V**alidation（验证）—— 一个医学 world model 论断应当具备的五个证据要素。"),
    "markers": ("**Markers:** 🌟 core paper · ![code](https://img.shields.io/badge/code-181717?logo=github&style=flat-square) open-source available · level badges colored by the ladder above.",
                "**标记:** 🌟 核心论文 · ![code](https://img.shields.io/badge/code-181717?logo=github&style=flat-square) 含开源代码 · 层级徽章按上方能力阶梯配色。"),
    "contents": ("## 📑 Contents", "## 📑 目录"),
    "toc_overview": ("Category Overview", "分类总览"),
    "toc_featured": ("Featured: Open-Source Models", "精选：开源模型"),
    "toc_contrib": ("Contributing", "参与贡献"),
    "toc_cite": ("Citation", "引用"),
    "overview_h": ("## 🗂️ Category Overview", "## 🗂️ 分类总览"),
    "ov_track": ("Track", "轨道"),
    "ov_papers": ("Papers", "论文"),
    "ov_open": ("Open-source", "开源"),
    "ov_note": (
        "> A high count at `L4` does **not** mean clinical readiness — most carry planning/control *language* with retrospective or simulated evidence. Counterfactual reasoning (`L3`) is the sparsest level, and prospective validation is rare.",
        "> `L4` 数量高**并不**代表临床可部署——多数只是带有规划/控制*语言*，证据仍是回顾性或仿真的。反事实推理（`L3`）是最稀缺的一层，前瞻性验证非常罕见。"),
    "featured_h": ("## 🚀 Featured: Open-Source Medical World Models", "## 🚀 精选：开源医学世界模型"),
    "featured_sub": ("The subset with publicly available code — the most directly reusable work.",
                     "含公开代码的子集——最可直接复用的工作。"),
    "col_paper": ("Paper", "论文"),
    "col_level": ("Level", "层级"),
    "col_links": ("Links", "链接"),
    "col_code": ("Code", "代码"),
    "col_summary": ("Summary", "简介"),
    "catalog_h": ("## 📚 Catalog", "## 📚 全部条目"),
    "catalog_note": ("Within each track, papers are sorted core-first, then by year (newest first).",
                     "每个轨道内，按核心优先、再按年份（由新到旧）排序。"),
    "contrib_h": ("## 🤝 Contributing", "## 🤝 参与贡献"),
    "contrib_body": (
        "Contributions are very welcome! To add or fix an entry, edit [`data/medical_world_models.csv`](data/medical_world_models.csv) and run `python generate_readme.py` to regenerate both READMEs. Please keep the **conservative public-evidence rule**: mark code/data/validation as *unknown* unless you can link public evidence. See [CONTRIBUTING.md](CONTRIBUTING.md).",
        "非常欢迎贡献！新增或修正条目：编辑 [`data/medical_world_models.csv`](data/medical_world_models.csv)，再运行 `python generate_readme.py` 重新生成两个 README。请遵守**保守的公开证据规则**：除非能给出公开证据链接，否则代码/数据/验证一律标为 *unknown*。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。"),
    "cite_h": ("## 📌 Citation", "## 📌 引用"),
    "cite_body": ("If this resource helps your work, please cite it:", "如果本资源对你有帮助，请引用："),
    "license_h": ("## 📄 License", "## 📄 许可"),
    "license_body": (
        "[![CC0](https://licensebuttons.net/p/zero/1.0/80x15.png)](LICENSE) The curated metadata is released under **CC0 1.0** (public domain). Linked papers and code remain under their own licenses.",
        "[![CC0](https://licensebuttons.net/p/zero/1.0/80x15.png)](LICENSE) 本整理的元数据以 **CC0 1.0**（公有领域）发布。所链接的论文与代码各自遵循其原始许可。"),
}

def g(key, lang): return T[key][0 if lang == "en" else 1]

def lvl(r):
    m = re.match(r"(L\d)", r.get("capability_level", "") or "")
    return m.group(1) if m else "L?"

def has_code(r):
    c = (r.get("code_available", "") or "").strip().lower()
    u = (r.get("code_url", "") or "").strip()
    return c == "yes" or (u and u.lower() not in ("", "unknown", "n/a", "na", "not_extracted"))

def cell(s, limit=None):
    s = re.sub(r"\s+", " ", (s or "").replace("|", "\\|").replace("\n", " ")).strip()
    if limit and len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0] + "…"
    return s

def safe_title(s):
    return cell((s or "").rstrip(".").replace("[", "(").replace("]", ")"))

def authors_short(a):
    a = (a or "").strip()
    if not a or a.lower() in ("unknown", "n/a", "na"):
        return ""
    parts = [p.strip() for p in a.split(";") if p.strip()]
    return (parts[0] + (" et al." if len(parts) > 1 else "")) if parts else ""

def venue_clean(v):
    v = (v or "").strip()
    if v.lower() in ("unknown", "n/a", "na", "not_reported", ""):
        return ""
    return {"ArXiv.org": "arXiv", "Arxiv.org": "arXiv",
            "arXiv (Cornell University)": "arXiv", "ArXiv (Cornell University)": "arXiv"}.get(v, v)

def level_badge(L):
    return f"![{L}](https://img.shields.io/badge/{L}-{LEVEL_COLOR.get(L,'999')}?style=flat-square)"

def code_badge(r):
    u = (r.get("code_url", "") or "").strip().rstrip(".")
    if u and u.lower() not in ("unknown", "n/a", "na", "not_extracted"):
        return f"[![code](https://img.shields.io/badge/code-181717?logo=github&style=flat-square)]({u})"
    if (r.get("code_available", "") or "").strip().lower() == "yes":
        return "![available](https://img.shields.io/badge/code-available-4E9A51?style=flat-square)"
    return "—"

def links_cell(r):
    out = []
    url = (r.get("url", "") or "").strip()
    arx = (r.get("arxiv_id", "") or "").strip()
    pdf = (r.get("pdf_url", "") or "").strip()
    if url:
        out.append(f"[Paper]({url})")
    if arx and "arxiv" not in url.lower():
        out.append(f"[arXiv](https://arxiv.org/abs/{arx})")
    if pdf and pdf != url and "arxiv" not in pdf.lower():
        out.append(f"[PDF]({pdf})")
    return " · ".join(out) if out else "—"

def row(r):
    core = "🌟 " if (r.get("inclusion_tier", "") or "").strip() == "core" else ""
    title = safe_title(r.get("title", ""))
    sub_bits = [x for x in [authors_short(r.get("authors", "")), venue_clean(r.get("venue", "")),
                            (r.get("year", "") or "").strip()] if x]
    sub = " · ".join(sub_bits)
    paper = f"{core}**{title}**" + (f" <br><sub>{cell(sub)}</sub>" if sub else "")
    summary = cell(r.get("description", ""), 150) or "—"
    return f"| {paper} | {level_badge(lvl(r))} | {links_cell(r)} | {code_badge(r)} | {summary} |"

def table_header(lang):
    return (f"| {g('col_paper',lang)} | {g('col_level',lang)} | {g('col_links',lang)} | "
            f"{g('col_code',lang)} | {g('col_summary',lang)} |\n| --- | :---: | --- | :---: | --- |")

def build(rows, lang):
    n = len(rows)
    tier = collections.Counter((r.get("inclusion_tier", "") or "").strip() for r in rows)
    levels = collections.Counter(lvl(r) for r in rows)
    tracks = collections.Counter((r.get("topic_track", "") or "").strip() for r in rows)
    nopen = sum(1 for r in rows if has_code(r))
    B = []
    A = B.append
    track_name = lambda t: TRACK[t][0 if lang == "en" else 1]

    def sh(s):  # escape text for shields.io badge segments
        return str(s).replace("-", "--").replace("_", "__").replace(" ", "%20")
    A('<a id="top"></a>')
    A('<p align="center"><img src="assets/hero.png" alt="Medical World Models" width="760"></p>')
    A("")
    A(f"<h1 align=\"center\">{g('title',lang)}</h1>")
    A(f"<p align=\"center\"><b>{g('tagline',lang).replace('**','')}</b></p>")
    A('<p align="center">')
    A(f'  <a href="https://awesome.re"><img src="https://awesome.re/badge-flat2.svg" alt="Awesome"></a>')
    A(f'  <img src="https://img.shields.io/badge/{sh(g("papers",lang))}-{n}-3B6CA8?style=flat-square" alt="papers">')
    A(f'  <img src="https://img.shields.io/badge/{sh(g("opensource",lang))}-{nopen}-4E9A51?style=flat-square" alt="open-source">')
    A(f'  <img src="https://img.shields.io/badge/{sh(g("core",lang))}-{tier.get("core",0)}-D98A3D?style=flat-square" alt="core">')
    A(f'  <img src="https://img.shields.io/badge/license-CC0--1.0-lightgrey?style=flat-square" alt="license">')
    A(f'  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs welcome"></a>')
    A(f'  <img src="https://img.shields.io/badge/{sh(g("verified",lang))}-{sh(LAST_VERIFIED)}-2E8B86?style=flat-square" alt="verified">')
    A('</p>')
    A("")
    A(f"> {g('tagline',lang)}  ")
    A(f"> {g('intro',lang)}")
    A("")
    A(f"- {g('stat_papers',lang)}: **{n}**")
    A(f"- {g('stat_open',lang)}: **{nopen}**")
    A(f"- {g('stat_core',lang)}: **{tier.get('core',0)}**")
    A(f"- {g('stat_levels',lang)}: **5** (L0 · L1 · L2 · L3 · L4), anchored to Pearl's ladder of causation")
    A(f"- {g('stat_tracks',lang)}: **7**")
    A(f"- {g('stat_verified',lang)}: **{LAST_VERIFIED}**")
    A(f"- {g('lang',lang)}")
    A("")

    # Contents
    A(g("contents", lang))
    A("")
    A(f"- [{g('toc_overview',lang)}](#overview)")
    A(f"- [{g('toc_featured',lang)}](#featured)")
    A(f"- [{g('catalog_h',lang).lstrip('# ')}](#catalog)")
    for t in TRACK_ORDER:
        if tracks.get(t):
            A(f"  - [{track_name(t)}](#{TRACK[t][2]})")
    A(f"- [{g('toc_contrib',lang)}](#contributing)")
    A(f"- [{g('toc_cite',lang)}](#citation)")
    A("")

    # Capability ladder legend
    A(g("legend_h", lang))
    A("")
    A(f"| {g('legend_lvl',lang)} | {g('legend_mean',lang)} |")
    A("| :---: | --- |")
    for L in LEVELS:
        A(f"| {level_badge(L)} | {LEVEL_DESC[L][0 if lang=='en' else 1]} |")
    A("")
    A(g("satov", lang))
    A("")
    A(g("markers", lang))
    A("")

    # Category overview
    A('<a id="overview"></a>')
    A(g("overview_h", lang))
    A("")
    A(f"| {g('ov_track',lang)} | {g('ov_papers',lang)} | {g('ov_open',lang)} |")
    A("| --- | ---: | ---: |")
    for t in TRACK_ORDER:
        if tracks.get(t):
            o = sum(1 for r in rows if r.get("topic_track") == t and has_code(r))
            A(f"| [{track_name(t)}](#{TRACK[t][2]}) | {tracks[t]} | {o} |")
    A(f"| **Total** | **{n}** | **{nopen}** |")
    A("")
    # capability level mini-table
    A("| " + " | ".join(level_badge(L) for L in LEVELS) + " |")
    A("| " + " | ".join(":---:" for _ in LEVELS) + " |")
    A("| " + " | ".join(str(levels.get(L, 0)) for L in LEVELS) + " |")
    A("")
    A(g("ov_note", lang))
    A("")

    # Featured open-source
    A('<a id="featured"></a>')
    A(g("featured_h", lang))
    A("")
    A(g("featured_sub", lang))
    A("")
    A(table_header(lang))
    osrc = [r for r in rows if has_code(r)]
    osrc.sort(key=lambda r: (TRACK_ORDER.index(r.get("topic_track", "")) if r.get("topic_track", "") in TRACK_ORDER else 9,
                             LEVELS.index(lvl(r)) if lvl(r) in LEVELS else 9))
    for r in osrc:
        A(row(r))
    A("")

    # Catalog per track
    A('<a id="catalog"></a>')
    A(g("catalog_h", lang))
    A("")
    A(f"_{g('catalog_note',lang)}_")
    A("")
    for t in TRACK_ORDER:
        sub = [r for r in rows if (r.get("topic_track", "") or "").strip() == t]
        if not sub:
            continue
        o = sum(1 for r in sub if has_code(r))
        A(f'<a id="{TRACK[t][2]}"></a>')
        A(f"### {track_name(t)}  ·  {len(sub)} {g('ov_papers',lang).lower()}  ·  {o} {g('ov_open',lang).lower()}")
        A("")
        sub.sort(key=lambda r: (0 if r.get("inclusion_tier") == "core" else 1,
                                -(int(r["year"]) if (r.get("year", "") or "").isdigit() else 0),
                                r.get("title", "")))
        A(table_header(lang))
        for r in sub:
            A(row(r))
        A("")
        A(f'<p align="right"><a href="#top">↑ back to top</a></p>')
        A("")

    # Contributing
    A('<a id="contributing"></a>')
    A(g("contrib_h", lang))
    A("")
    A(g("contrib_body", lang))
    A("")

    # Citation
    A('<a id="citation"></a>')
    A(g("cite_h", lang))
    A("")
    A(g("cite_body", lang))
    A("")
    A("```bibtex")
    A("@misc{awesome_medical_world_models,")
    A("  title        = {Awesome Medical World Models},")
    A("  author       = {lanqz7766},")
    A("  year         = {2026},")
    A("  howpublished = {\\url{https://github.com/lanqz7766/awesome-medical-world-models}},")
    A("  note         = {A capability-coded map of medical world models (L0--L4 + SATO-V)}")
    A("}")
    A("```")
    A("")

    # License
    A(g("license_h", lang))
    A("")
    A(g("license_body", lang))
    A("")
    return "\n".join(B) + "\n"

def main():
    rows = list(csv.DictReader(open(CSV, newline="", encoding="utf-8")))
    nopen = sum(1 for r in rows if has_code(r))
    open(os.path.join(HERE, "README.md"), "w", encoding="utf-8").write(build(rows, "en"))
    open(os.path.join(HERE, "README_zh.md"), "w", encoding="utf-8").write(build(rows, "zh"))
    print(f"wrote README.md and README_zh.md ({len(rows)} papers, {nopen} open-source)")

if __name__ == "__main__":
    main()
