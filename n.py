from datetime import datetime
from playwright.sync_api import sync_playwright
import google_sheets
import os

URL = "https://www.business-standard.com/markets/research-report"
SHEET_ID = "1QN5GMlxBKMudeHeWF-Kzt9XsqTt01am7vze1wBjvIdE"
WORKSHEET_NAME = "bis"

def scrape_business_standard():
    print("🚀 Starting the scraping process...")

    # Set headless mode based on environment variable
    headless_mode = os.getenv("HEADLESS_MODE", "True") == "True"

    try:
        with sync_playwright() as p:
            # Launch the browser in headless mode
            browser = p.chromium.launch(headless=headless_mode)  
            context = browser.new_context()
            page = context.new_page()

            page.goto(URL, timeout=60000)
            print("🌐 Page requested. Waiting fixed time for content...")
            page.wait_for_timeout(10_000)  # 10 seconds fixed wait

            # Wait for the table to appear
            page.wait_for_selector("table.cmpnydatatable_cmpnydatatable__Cnf6M tbody tr", timeout=30000)

            trs = page.query_selector_all("table.cmpnydatatable_cmpnydatatable__Cnf6M tbody tr")

            if not trs:
                print("⚠️ No table rows found.")
                return

            headers = ["STOCK", "RECOMMENDATION", "TARGET", "BROKER", "DATE"]
            rows = []

            for tr in trs[:500]:
                tds = tr.query_selector_all("td")
                if len(tds) >= 5:
                    rows.append([td.inner_text().strip() for td in tds[:5]])

            if rows:
                google_sheets.update_google_sheet_by_name(SHEET_ID, WORKSHEET_NAME, headers, rows)
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                google_sheets.append_footer(SHEET_ID, WORKSHEET_NAME, ["Last updated on:", ts])
                print(f"✅ Successfully updated {len(rows)} rows.")
            else:
                print("⚠️ Table found but no rows extracted.")

            browser.close()

    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    scrape_business_standard()
