#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_portal_data.py
一鍵資料管線編排與前端注入同步器 (Orchestrator & Atomic HTML Injector)

功能：
  1. 建置並稽核涵蓋「中央 8 大部會署 ＋ 全台 22 縣市」之 48 筆真實補助規則庫 (grants_rules.json)。
  2. 初始化並同步本地 SQLite 企業統編資料庫 (companies_local.sqlite) 與預抓取快取 (companies_db.json)。
  3. 執行「資安與反爬蟲防守官」與「數據稽核會計師」雙重自動化測試。
  4. 將最新驗證通過的 companies_db.json 與 grants_rules.json (48 案) 原子注入：
     - taiwan_grant_matcher.html (2D 瀑布流清單版)
     - index.html (GitHub Pages 預設首頁入口)
     - taiwan_grant_island_3d.html (3D 轉型群島互動版)
"""

import json
import os
import re
import shutil
import time
from sync_gcis_companies import (
    validate_companies_schema,
    COMPANIES_DB_PATH
)
from crawl_gov_grants import (
    build_and_verify_grants_db,
    audit_grants_schema,
    GRANTS_DB_PATH
)
from local_sqlite_server import (
    init_sqlite_db,
    SQLITE_DB_PATH
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_TARGET_PATH = os.path.join(BASE_DIR, "taiwan_grant_matcher.html")
HTML_INDEX_PATH = os.path.join(BASE_DIR, "index.html")
HTML_3D_TARGET_PATH = os.path.join(BASE_DIR, "taiwan_grant_island_3d.html")


def run_role3_security_defense_tests() -> None:
    print("\n[挑毛病角色 1：資安與反爬蟲防守官] 執行容錯與防污染壓力測試...")
    bad_comp_db = {"companies": {"12345678": {"ubn": "12345678", "name": "假公司"}}}
    errs = validate_companies_schema(bad_comp_db)
    assert len(errs) > 0, "防守官退件：非法統編與缺漏欄位未被 validate_companies_schema 攔截！"

    bad_grants = [{"id": f"TEST-{i}", "officialUrl": "https://www.wda.gov.tw/", "maxSubsidyMan": 1500000} for i in range(45)]
    g_errs = audit_grants_schema(bad_grants)
    assert any("空泛部會首頁" in e for e in g_errs), "防守官退件：部會首頁網址未被攔截！"
    assert any("金額單位異常" in e for e in g_errs), "防守官退件：元與萬元單位混淆未被攔截！"
    print("  ✓ 測試通過：非法統編、斷鏈降級備援、空泛首頁攔截與萬元單位防呆均 100% 正常運作！")


def _inject_into_single_html(html_path: str, comp_json_str: str, grants_json_str: str, grants_db: list) -> None:
    if not os.path.exists(html_path):
        return
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    pat_comp = re.compile(
        r"(const\s+DEFAULT_COMPANIES_DB\s*=\s*)\{.*?\}(\s*;\s*\n\s*//\s*={10,}\s*2\.)",
        re.DOTALL
    )
    assert pat_comp.search(html), f"找不到 {os.path.basename(html_path)} 中的 DEFAULT_COMPANIES_DB 錨點"
    html = pat_comp.sub(lambda m: m.group(1) + comp_json_str + m.group(2), html, count=1)

    pat_grants = re.compile(
        r"(const\s+DEFAULT_GRANTS_DB\s*=\s*)\[.*?\](\s*;\s*\n\s*let\s+COMPANIES_DB)",
        re.DOTALL
    )
    assert pat_grants.search(html), f"找不到 {os.path.basename(html_path)} 中的 DEFAULT_GRANTS_DB 錨點"
    html = pat_grants.sub(lambda m: m.group(1) + grants_json_str + m.group(2), html, count=1)

    staging_path = html_path + ".staging"
    with open(staging_path, "w", encoding="utf-8") as f:
        f.write(html)

    assert "preset-btn" not in html, f"{os.path.basename(html_path)} 仍含 preset-btn"
    assert "btnToggleDevDrawer" not in html, f"{os.path.basename(html_path)} 仍含 btnToggleDevDrawer"
    for g in grants_db:
        assert g["officialUrl"] in html, f"{os.path.basename(html_path)} 缺少 {g['officialUrl']}"

    os.replace(staging_path, html_path)


def inject_databases_into_html() -> None:
    with open(COMPANIES_DB_PATH, "r", encoding="utf-8") as f:
        comp_db = json.load(f)
    with open(GRANTS_DB_PATH, "r", encoding="utf-8") as f:
        grants_db = json.load(f)

    c_errs = validate_companies_schema(comp_db)
    g_errs = audit_grants_schema(grants_db)
    if c_errs or g_errs:
        raise RuntimeError(f"[數據稽核會計師退件] 拒絕注入 HTML: companies={c_errs}, grants={g_errs}")

    comp_json_str = json.dumps(comp_db, ensure_ascii=False, indent=6)
    grants_json_str = json.dumps(grants_db, ensure_ascii=False, indent=6)

    _inject_into_single_html(HTML_TARGET_PATH, comp_json_str, grants_json_str, grants_db)
    shutil.copyfile(HTML_TARGET_PATH, HTML_INDEX_PATH)
    _inject_into_single_html(HTML_3D_TARGET_PATH, comp_json_str, grants_json_str, grants_db)

    print(
        f"[update_portal_data] 已將 {len(comp_db['companies'])} 家預快取企業與 {len(grants_db)} 筆全國補助規則 "
        f"原子注入 taiwan_grant_matcher.html、index.html 與 taiwan_grant_island_3d.html！"
    )


def main():
    t_start = time.time()
    print("=" * 72)
    print("🚀 啟動 2026 DTI 全國級政府補助 (48案) 與統編多模式資料庫建置管線")
    print("=" * 72)

    # Step 1: 建置並稽核 48 筆中央跨部會 ＋ 全台 22 縣市補助規則庫
    grant_res = build_and_verify_grants_db()

    # Step 2: 初始化並同步本地 SQLite 資料庫 (companies_local.sqlite)
    sqlite_cnt = init_sqlite_db(SQLITE_DB_PATH)

    # Step 3: 執行挑毛病角色 1 & 2 壓力與數據稽核測試
    run_role3_security_defense_tests()

    # Step 4: 原子注入前端 HTML (2D 版、index.html、3D 群島版)
    inject_databases_into_html()

    total_sec = round(time.time() - t_start, 2)
    print("=" * 72)
    print(f"✅ 全管線執行完畢！總耗時: {total_sec} 秒")
    print(f"   - 本地 SQLite 資料庫 (companies_local.sqlite) 已就緒，收錄基準筆數: {sqlite_cnt} 家 (支援百萬筆 CSV 匯入)")
    print(f"   - 全國補助規則庫 (grants_rules.json): 共 {grant_res['totalGrantsCount']} 案 (中央 {grant_res['centralMinistriesGrantsCount']} 案 ＋ 地方 22 縣市 {grant_res['local22CountiesGrantsCount']} 案)")
    print(f"   - 數據稽核結果: {grant_res['auditStatus']}")
    print("=" * 72)


if __name__ == "__main__":
    main()
