#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
local_sqlite_server.py
台灣全國企業統編本地 SQLite 資料庫建置、全量 CSV 批次匯入與本地 API 伺服器 (Zero-AI Rule-Based)

支援三種核心用途：
  1. 初始化本地 SQLite 資料庫並匯入預抓取快取：
     python3 local_sqlite_server.py --init
  2. 匯入政府資料開放平臺 (data.gov.tw / data.gcis.nat.gov.tw) 下載之全國公司／商業登記全量 CSV (支援百萬筆串流批次寫入)：
     python3 local_sqlite_server.py --import-csv /path/to/全國公司登記基本資料.csv
  3. 啟動本地 CORS API 伺服器 (供前端切換至「本地 SQLite 查詢模式」時毫秒級查詢，若本地未命中可自動穿透抓取並寫入 SQLite)：
     python3 local_sqlite_server.py --serve --port 8765
"""

import argparse
import csv
import datetime
import http.server
import json
import os
import re
import socketserver
import sqlite3
import urllib.parse
from typing import Dict, Any, Optional

from sync_gcis_companies import (
    COMPANIES_DB_PATH,
    extract_county,
    map_industry_to_sector,
    convert_roc_date,
    resolve_single_ubn,
    validate_taiwan_ubn,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "companies_local.sqlite")

ALL_22_COUNTIES = [
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
    "基隆市", "新竹市", "新竹縣", "苗栗縣", "彰化縣", "南投縣",
    "雲林縣", "嘉義市", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣",
    "臺東縣", "澎湖縣", "金門縣", "連江縣"
]


def extract_county_22(address: str) -> str:
    """從地址字串精確提取台灣 22 縣市標準名稱"""
    if not address:
        return "臺北市"
    norm = address.replace("台", "臺")
    for c in ALL_22_COUNTIES:
        if c in norm:
            return c
    return "其他縣市"


def init_sqlite_db(db_path: str = SQLITE_DB_PATH) -> int:
    """建立 companies_local.sqlite 資料表與索引，並載入 companies_db.json 初始資料"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            ubn TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            org_type TEXT NOT NULL,
            org_type_label TEXT,
            county TEXT NOT NULL,
            address TEXT,
            paid_in_capital INTEGER DEFAULT 0,
            est_date TEXT,
            industry_code TEXT,
            sector TEXT NOT NULL,
            sector_label TEXT,
            has_factory_reg INTEGER DEFAULT 0,
            default_emp_range TEXT DEFAULT 'under30',
            default_exact_emp INTEGER DEFAULT 15,
            findbiz_url TEXT,
            updated_at TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_companies_county ON companies(county)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector)")

    count = 0
    if os.path.exists(COMPANIES_DB_PATH):
        with open(COMPANIES_DB_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
            companies = payload.get("companies", {})
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rows = []
            for ubn, c in companies.items():
                rows.append((
                    ubn,
                    c.get("name", ""),
                    c.get("orgType", "company"),
                    c.get("orgTypeLabel", "公司法人"),
                    extract_county_22(c.get("address", "") or c.get("county", "")),
                    c.get("address", ""),
                    int(c.get("paidInCapital", 0)),
                    c.get("estDate", ""),
                    c.get("industryCode", ""),
                    c.get("sector", "service"),
                    c.get("sectorLabel", "商業服務業"),
                    1 if c.get("hasFactoryReg") else 0,
                    c.get("defaultEmpRange", "under30"),
                    int(c.get("defaultExactEmp", 15)),
                    c.get("findbizUrl", f"https://findbiz.nat.gov.tw/fts/company/{ubn}"),
                    now_str
                ))
            cur.executemany("""
                INSERT OR REPLACE INTO companies (
                    ubn, name, org_type, org_type_label, county, address,
                    paid_in_capital, est_date, industry_code, sector, sector_label,
                    has_factory_reg, default_emp_range, default_exact_emp, findbiz_url, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            count = len(rows)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM companies")
    total_in_db = cur.fetchone()[0]
    conn.close()
    print(f"[local_sqlite_server] SQLite 資料庫初始化完成 ({db_path})，目前收錄筆數: {total_in_db:,} 筆")
    return total_in_db


def import_gcis_csv_to_sqlite(csv_path: str, db_path: str = SQLITE_DB_PATH) -> int:
    """
    串流讀取政府資料開放平臺《全國公司登記基本資料.csv》或《全國商業登記基本資料.csv》
    以每批 10,000 筆高速寫入 SQLite，支援百萬級全國統編匯入而不佔用記憶體。
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"找不到 CSV 檔案: {csv_path}")

    init_sqlite_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    batch = []
    total_imported = 0
    with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ubn = (
                row.get("統一編號")
                or row.get("Business_Accounting_NO")
                or row.get("商業統一編號")
                or row.get("President_No")
                or ""
            ).strip()
            if not re.match(r"^\d{8}$", ubn):
                continue

            name = (
                row.get("公司名稱")
                or row.get("Company_Name")
                or row.get("商業名稱")
                or row.get("Business_Name")
                or ""
            ).strip()
            if not name:
                continue

            addr = (
                row.get("公司所在地")
                or row.get("Company_Location")
                or row.get("地址")
                or row.get("Business_Address")
                or ""
            ).strip()

            raw_cap = (
                row.get("實收資本額")
                or row.get("Capital_Stock_Amount")
                or row.get("資本額")
                or row.get("Business_Current_Capital")
                or "0"
            )
            cap = int(re.sub(r"[^\d]", "", str(raw_cap)) or "0")

            is_biz = ("商業名稱" in row or "Business_Name" in row) and ("公司名稱" not in row)
            org_type = "business" if is_biz else "company"
            org_label = "獨資／合夥商號（全國開放資料 CSV）" if is_biz else "公司法人（全國開放資料 CSV）"

            ind_code = (
                row.get("所營事業1")
                or row.get("營業項目1")
                or row.get("Main_Industry_Code")
                or ""
            ).strip()
            sector, sector_label = map_industry_to_sector(ind_code, name)
            has_fac = 1 if (sector == "manufacturing" and cap >= 5000000) else 0
            est_date = convert_roc_date(
                row.get("核准設立日期") or row.get("Company_Setup_Date") or ""
            )
            emp_range = "under30" if cap < 10000000 else ("31to199" if cap <= 100000000 else "over200")
            exact_emp = 15 if cap < 10000000 else (50 if cap <= 100000000 else 250)

            batch.append((
                ubn, name, org_type, org_label, extract_county_22(addr), addr,
                cap, est_date, ind_code, sector, sector_label, has_fac,
                emp_range, exact_emp, f"https://findbiz.nat.gov.tw/fts/company/{ubn}", now_str
            ))

            if len(batch) >= 10000:
                cur.executemany("""
                    INSERT OR REPLACE INTO companies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                conn.commit()
                total_imported += len(batch)
                print(f"  ...已匯入 {total_imported:,} 筆統編")
                batch.clear()

    if batch:
        cur.executemany("""
            INSERT OR REPLACE INTO companies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()
        total_imported += len(batch)

    conn.close()
    print(f"[local_sqlite_server] CSV 全量匯入完成！共新增/更新 {total_imported:,} 筆企業統編至 {db_path}")
    return total_imported


def query_company_from_sqlite(ubn: str, db_path: str = SQLITE_DB_PATH, auto_fetch_remote: bool = True) -> Optional[Dict[str, Any]]:
    """從本地 SQLite 查詢統編；若未命中且開啟 auto_fetch_remote，自動從遠端 API 抓回並寫入 SQLite 快取"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies WHERE ubn = ?", (ubn,))
    row = cur.fetchone()
    if row:
        conn.close()
        return {
            "ubn": row["ubn"],
            "name": row["name"],
            "orgType": row["org_type"],
            "orgTypeLabel": row["org_type_label"],
            "county": row["county"],
            "address": row["address"],
            "paidInCapital": int(row["paid_in_capital"]),
            "estDate": row["est_date"],
            "industryCode": row["industry_code"],
            "sector": row["sector"],
            "sectorLabel": row["sector_label"],
            "hasFactoryReg": bool(row["has_factory_reg"]),
            "defaultEmpRange": row["default_emp_range"],
            "defaultExactEmp": int(row["default_exact_emp"]),
            "findbizUrl": row["findbiz_url"],
            "dataSource": "LOCAL_SQLITE_DB"
        }

    conn.close()
    if auto_fetch_remote:
        try:
            rec, trace = resolve_single_ubn(ubn, timeout=3.5)
            rec["county"] = extract_county_22(rec.get("address", "") or rec.get("county", ""))
            conn2 = sqlite3.connect(db_path)
            cur2 = conn2.cursor()
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur2.execute("""
                INSERT OR REPLACE INTO companies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec["ubn"], rec["name"], rec["orgType"], rec["orgTypeLabel"],
                rec["county"], rec["address"], int(rec["paidInCapital"]),
                rec["estDate"], rec.get("industryCode", ""), rec["sector"],
                rec["sectorLabel"], 1 if rec["hasFactoryReg"] else 0,
                rec["defaultEmpRange"], int(rec["defaultExactEmp"]),
                rec["findbizUrl"], now_str
            ))
            conn2.commit()
            conn2.close()
            rec["dataSource"] = f"SQLITE_READ_THROUGH ({trace})"
            return rec
        except Exception:
            return None
    return None


class GrantPortalSQLiteHandler(http.server.SimpleHTTPRequestHandler):
    """同時提供靜態網頁與 /api/company/<ubn>、/api/health 端點之本地 CORS 伺服器"""

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/health":
            conn = sqlite3.connect(SQLITE_DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM companies")
            cnt = cur.fetchone()[0]
            conn.close()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "engine": "SQLite3",
                "dbPath": "companies_local.sqlite",
                "cachedCompaniesCount": cnt
            }, ensure_ascii=False).encode("utf-8"))
            return

        m = re.match(r"^/api/company/(\d{8})$", parsed.path)
        if m:
            ubn = m.group(1)
            rec = query_company_from_sqlite(ubn, SQLITE_DB_PATH, auto_fetch_remote=True)
            if rec:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "data": rec}, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "查無此統編"}, ensure_ascii=False).encode("utf-8"))
            return

        return super().do_GET()


def run_server(port: int = 8765):
    init_sqlite_db(SQLITE_DB_PATH)
    os.chdir(BASE_DIR)
    with socketserver.TCPServer(("127.0.0.1", port), GrantPortalSQLiteHandler) as httpd:
        print(f"🚀 本地 SQLite 統編查詢伺服器已啟動: http://127.0.0.1:{port}")
        print(f"   - 網頁入口: http://127.0.0.1:{port}/taiwan_grant_matcher.html")
        print(f"   - 統編 API: http://127.0.0.1:{port}/api/company/28458491")
        print(f"   - 狀態檢查: http://127.0.0.1:{port}/api/health")
        httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="本地 SQLite 企業統編資料庫與 API 伺服器")
    parser.add_argument("--init", action="store_true", help="初始化 companies_local.sqlite 並匯入預設快取")
    parser.add_argument("--import-csv", type=str, help="匯入全國公司/商業登記開放資料 CSV 檔案路徑")
    parser.add_argument("--query", type=str, help="從本地 SQLite 測試查詢單一 8 碼統編")
    parser.add_argument("--serve", action="store_true", help="啟動本地 HTTP + SQLite API 伺服器")
    parser.add_argument("--port", type=int, default=8765, help="本地伺服器連接埠 (預設 8765)")
    args = parser.parse_args()

    if args.init:
        init_sqlite_db(SQLITE_DB_PATH)
    if args.import_csv:
        import_gcis_csv_to_sqlite(args.import_csv, SQLITE_DB_PATH)
    if args.query:
        res = query_company_from_sqlite(args.query.strip(), SQLITE_DB_PATH)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    if args.serve:
        run_server(args.port)
    if not (args.init or args.import_csv or args.query or args.serve):
        init_sqlite_db(SQLITE_DB_PATH)


if __name__ == "__main__":
    main()
