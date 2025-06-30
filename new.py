from playwright.sync_api import sync_playwright
import time
 
def main():
    url = "https://www.business-standard.com/markets/research-report"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to True for GitHub Actions
        page = browser.new_page()
        page.goto(url, timeout=60000)

        # Wait for network to be idle (all JS loaded)
        page.wait_for_load_state("networkidle")

        # Wait for table to appear - try with general selector
        try:
            page.wait_for_selector("table tbody tr", timeout=150000)
        except:
            print("❌ Table not found within timeout.")
            page.screenshot(path="debug.png", full_page=True)
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            browser.close()
            return

        # Extract table data
        rows = page.query_selector_all("table tbody tr")
        print(f"✅ Found {len(rows)} rows")
        for row in rows:
            cells = row.query_selector_all("td")
            data = [cell.inner_text().strip() for cell in cells]
            print(data)

        # Debug snapshot
        page.screenshot(path="final.png", full_page=True)
        with open("final.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        browser.close()

if __name__ == "__main__":
    main()
