import re
import urllib.parse
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from app.analytics import detect_negative_keywords, score_place, build_recommended_angle


def _safe_text(locator, timeout=2000) -> str:
    try:
        return locator.first.inner_text(timeout=timeout).strip()
    except Exception:
        return ""


def _safe_attr(locator, attr: str, timeout=2000) -> str:
    try:
        return locator.first.get_attribute(attr, timeout=timeout) or ""
    except Exception:
        return ""


def scrape_google_maps(query: str, industry: str, max_results: int = 10) -> list:
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="fr-FR",
        )
        page = context.new_page()

        encoded_query = urllib.parse.quote(query)
        page.goto(
            f"https://www.google.com/maps/search/{encoded_query}",
            timeout=30000,
            wait_until="networkidle",
        )
        page.wait_for_timeout(2000)

        # Dismiss cookie consent if present
        for selector in [
            'button[aria-label*="Accept"]',
            'button[aria-label*="Accepter"]',
            'button[jsname="b3VHJd"]',
            'form[action*="consent"] button',
        ]:
            try:
                page.click(selector, timeout=1500)
                page.wait_for_timeout(800)
                break
            except Exception:
                pass

        # Scroll the results feed to load enough items
        scroll_rounds = max(4, max_results // 2 + 2)
        for _ in range(scroll_rounds):
            try:
                feed = page.locator('[role="feed"]')
                feed.evaluate("el => el.scrollBy(0, 600)")
                page.wait_for_timeout(700)
            except Exception:
                break

        items = page.locator(".Nv2PK")
        total = min(items.count(), max_results)

        for i in range(total):
            try:
                item = items.nth(i)
                maps_url = _safe_attr(item.locator("a.hfpxzc"), "href")

                item.click()
                page.wait_for_timeout(2500)

                # Name
                name = _safe_text(page.locator("h1"), timeout=3000)

                # Rating
                rating = None
                rating_raw = _safe_text(
                    page.locator('div.F7nice span[aria-hidden="true"]')
                )
                if rating_raw:
                    try:
                        rating = float(rating_raw.replace(",", "."))
                    except ValueError:
                        pass

                # Review count
                review_count = 0
                for rc_sel in [
                    'button[jsaction*="reviewChart"] span',
                    'button[jsaction*="review"] span',
                ]:
                    rc_raw = _safe_text(page.locator(rc_sel))
                    if rc_raw:
                        nums = re.findall(r"[\d]+", rc_raw.replace(",", "").replace(" ", ""))
                        if nums:
                            review_count = int(nums[0])
                            break

                # Address
                address = ""
                for addr_sel in [
                    '[data-item-id="address"] .fontBodyMedium',
                    'button[data-item-id="address"]',
                ]:
                    address = _safe_text(page.locator(addr_sel))
                    if address:
                        break

                # Phone
                phone = _safe_text(page.locator('button[data-item-id^="phone"]'))

                # Website
                website = _safe_attr(
                    page.locator('a[data-item-id="authority"]'), "href"
                )

                # Price range
                price_range = _safe_text(page.locator("span.mgr77e"), timeout=1000)

                # Page text for keyword detection (reviews section)
                page_text = _safe_text(page.locator(".m6QErb"), timeout=2000)

                neg_keywords = detect_negative_keywords(page_text)

                place = {
                    "name": name,
                    "industry": industry,
                    "address": address,
                    "rating": rating,
                    "review_count": review_count,
                    "phone": phone,
                    "website": website,
                    "price_range": price_range,
                    "maps_url": maps_url,
                    "recent_reviews": [],
                    "negative_keywords": neg_keywords,
                    "recommended_angle": build_recommended_angle(neg_keywords),
                    "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                score_place(place)
                results.append(place)

            except Exception as e:
                print(f"[scraper] item {i} skipped: {e}")
                continue

        browser.close()

    return results
