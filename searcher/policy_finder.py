#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
policy_finder.py (improved scoring)
Usage:
    python policy_finder.py "<query>" [policy_updates.json] [regulator_notice.json]
"""

from __future__ import annotations
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_DOCNO_RE = re.compile(
    r'(银发|银办发|公告|令|会发|财金|发改|证监|保监|银保监|人民银行令|中国人民银行令)[〔\[\(]?\s*(\d{2,4})\s*[〕\]\)]?\s*(第?\s*\d+\s*号)?',
    re.IGNORECASE
)
_YEAR_RE = re.compile(r'(19|20)\d{2}')

def norm_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize('NFKC', s)
    s = s.replace('（', '(').replace('）', ')').replace('〔','[').replace('〕',']').replace('【','[').replace('】',']')
    s = s.replace('《','"').replace('》','"').replace('“','"').replace('”','"').replace('‘',"'").replace('’',"'")
    s = re.sub(r'\s+', ' ', s).strip()
    return s

STOPWORDS = set(['关于','有关','的','通知','公告','决定','规定','办法','细则','实施','印发','进一步','试行','意见','答复','解读','发布'])

def tokenize_zh(s: str) -> List[str]:
    s = norm_text(s)
    parts = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9]+', s)
    return [p for p in parts if p not in STOPWORDS]

def extract_docno(s: str) -> Optional[str]:
    s = norm_text(s)
    m = _DOCNO_RE.search(s)
    if m:
        head = m.group(1)
        year = m.group(2)
        tail = m.group(3) or ''
        year = year if len(year) == 4 else ('20' + year if len(year)==2 else year)
        docno = f"{head}[{year}]{tail.replace(' ', '') or ''}"
        return docno
    return None

def guess_doctype(s: str) -> Optional[str]:
    s = norm_text(s)
    for kw in ['管理办法','实施细则','暂行规定','规定','细则','办法','通知','决定','公告','意见']:
        if kw in s:
            return kw
    return None

def guess_agency(s: str) -> Optional[str]:
    s = norm_text(s)
    agencies = ['中国人民银行','中国证券监督管理委员会','中国银行保险监督管理委员会','中国银行业监督管理委员会','国家外汇管理局','国务院','中国证监会','中国银保监会','国家统计局']
    hits = [a for a in agencies if a in s]
    if hits:
        return '、'.join(hits[:3])
    return None

def pick_best_path(documents: List[Dict[str, Any]]) -> Optional[str]:
    if not documents:
        return None
    order = {'pdf': 3, 'html': 2, 'word': 1, 'doc': 1, 'docx': 1}
    docs = sorted(documents, key=lambda d: order.get(d.get('type','').lower(), 0), reverse=True)
    for d in docs:
        p = d.get('local_path') or d.get('path') or d.get('localPath')
        if p:
            return p
    return None

@dataclass
class Entry:
    id: int
    title: str
    remark: str
    documents: List[Dict[str, Any]]
    norm_title: str = ""
    doc_no: Optional[str] = None
    year: Optional[str] = None
    doctype: Optional[str] = None
    agency: Optional[str] = None
    best_path: Optional[str] = None
    tokens: List[str] = field(default_factory=list)

    def build(self):
        self.norm_title = norm_text(self.title)
        self.doc_no = extract_docno(self.title) or extract_docno(self.remark or "")
        yfind = re.findall(r'(19|20)\d{2}', self.title + " " + (self.remark or ""))
        self.year = yfind[0] if yfind else None
        self.doctype = guess_doctype(self.title)
        self.agency  = guess_agency(self.title)
        self.best_path = pick_best_path(self.documents)
        self.tokens = tokenize_zh(self.norm_title)

def load_entries(json_path: str) -> List[Entry]:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    es = []
    for i, raw in enumerate(data.get('entries', []), 1):
        e = Entry(
            id=raw.get('serial', i),
            title=raw.get('title', ''),
            remark=raw.get('remark', '') or '',
            documents=raw.get('documents', [])
        )
        e.build()
        es.append(e)
    return es

def jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    uni   = len(sa | sb)
    return inter / uni if uni else 0.0

def fuzzy_score(query: str, e: Entry) -> float:
    qn = norm_text(query)
    score = 0.0

    # 1) Doc number hard match (very strong)
    q_doc = extract_docno(qn)
    if q_doc and e.doc_no:
        if q_doc == e.doc_no:
            score += 120.0
        elif q_doc.replace('[','').replace(']','') in (e.doc_no or '').replace('[','').replace(']',''):
            score += 80.0

    # 2) Year hint: boost match, small penalty mismatch when query has a clear year
    q_years = re.findall(r'(19|20)\d{2}', qn)
    if q_years:
        if e.year and e.year in q_years:
            score += 30.0
        elif e.year:
            score -= 5.0

    # 3) Doctype hint
    q_doctype = guess_doctype(qn)
    if q_doctype and e.doctype == q_doctype:
        score += 15.0

    # 4) Agency hint
    q_agency = guess_agency(qn)
    if q_agency and e.agency and (q_agency in e.agency or e.agency in q_agency):
        score += 10.0

    # 5) Exact phrase presence for CJK words from the query
    phrases = [ph for ph in re.findall(r'[\u4e00-\u9fff]{2,}', qn) if len(ph) >= 2]
    for ph in phrases:
        if ph in e.norm_title:
            score += min(8.0, 2.0 + len(ph) * 0.8)

    # 6) Token overlap (Jaccard)
    q_tokens = tokenize_zh(qn)
    overlap = jaccard(q_tokens, e.tokens)
    score += 40.0 * overlap

    # 7) Exact substring boosts
    if e.doc_no and e.doc_no in qn:
        score += 30.0
    if e.doctype and e.doctype in qn and e.doctype in e.title:
        score += 10.0

    # 8) Prefer PDF path
    if e.best_path and e.best_path.lower().endswith('.pdf'):
        score += 3.0

    return score

class PolicyFinder:
    def __init__(self, json_path_a: str, json_path_b: str):
        self.entries: List[Entry] = []
        self.idx_loaded = False
        self.load(json_path_a, json_path_b)

    def load(self, a: str, b: str):
        ea = load_entries(a)
        eb = load_entries(b)
        self.entries = ea + eb
        self.idx_loaded = True

    def search(self, query: str, topk: int = 1) -> List[Tuple[Entry, float]]:
        assert self.idx_loaded, "Index not loaded"
        scored: List[Tuple[Entry, float]] = []
        for e in self.entries:
            s = fuzzy_score(query, e)
            scored.append((e, s))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:topk]

def main(argv: List[str]):
    if len(argv) < 2:
        print("Usage: python policy_finder.py \"<query>\" [policy_updates.json] [regulator_notice.json]")
        return 1
    query = argv[1]
    script_dir = Path(__file__).resolve().parent
    default_a = script_dir / "policy_updates_state.json"
    default_b = script_dir / "regulator_notice_state.json"

    a = Path(argv[2]) if len(argv) >= 3 else default_a
    b = Path(argv[3]) if len(argv) >= 4 else default_b

    if not a.exists() and (Path('/mnt/data')/a.name).exists():
        a = Path('/mnt/data')/a.name
    if not b.exists() and (Path('/mnt/data')/b.name).exists():
        b = Path('/mnt/data')/b.name

    finder = PolicyFinder(str(a), str(b))
    results = finder.search(query, topk=1)
    if not results or not results[0][0].best_path:
        print("NOT_FOUND")
        return 0
    entry, score = results[0]
    print(entry.best_path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
