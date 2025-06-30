from datetime import datetime
from playwright.sync_api import sync_playwright

URL = "https://www.business-standard.com/markets/research-report"

def scrape_business_standard():
    print("🚀 Starting the scraping process...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Set to True in CI/GitHub
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )
            page = context.new_page()

            # Manual stealth patch
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.navigator.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """)

            page.goto(URL, timeout=60000)
            print("🌐 Page requested. Waiting fixed time for content...")
            page.wait_for_timeout(10_000)  # 10 seconds fixed wait

            # ✅ Wait for the table to appear
            try:
                page.wait_for_selector("table.cmpnydatatable_cmpnydatatable__Cnf6M tbody tr", timeout=30000)
            except:
                print("❌ Table not found within timeout.")
                page.screenshot(path="debug.png")
                with open("debug.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                browser.close()
                return

            trs = page.query_selector_all("table.cmpnydatatable_cmpnydatatable__Cnf6M tbody tr")

            if not trs:
                print("⚠️ No table rows found. Saving screenshot...")
                page.screenshot(path="final_debug.png")
                print("📸 Saved final_debug.png. Check it.")
                browser.close()
                return

            headers = ["STOCK", "RECOMMENDATION", "TARGET", "BROKER", "DATE"]
            print("📋", "\t".join(headers))

            for tr in trs[:500]:
                tds = tr.query_selector_all("td")
                if len(tds) >= 5:
                    row = [td.inner_text().strip() for td in tds[:5]]
                    print("➡️", "\t".join(row))

            browser.close()

    except Exception as e:
        print(f"❌ Fatal error: {e}")

scrape_business_standard()


