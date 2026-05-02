
import pandas as pd
import re
from playwright.sync_api import sync_playwright

def extract_part_numbers(text):
    patterns = [
        r"\b\d{5}-\d{5}\b",
        r"\b\d{5}-[A-Z0-9]{5}\b",
        r"\b[A-Z0-9]{10}\b"
    ]
    results = []
    for p in patterns:
        results += re.findall(p, text)
    return list(set(results))

def get_description(page):
    text = ""
    try:
        # iframe内の説明を取得
        frames = page.frames
        for f in frames:
            content = f.content()
            text += " " + content
    except:
        pass
    return text

def main():
    path = input("CSVパス: ")
    df = pd.read_csv(path, encoding="cp932")

    url_col = next((c for c in df.columns if "http" in c or "URL" in c), None)
    title_col = next((c for c in df.columns if "タイトル" in c), None)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for i, row in df.iterrows():
            url = row[url_col]
            print(f"{i+1}/{len(df)} 取得中")

            try:
                page.goto(url, timeout=15000)
                page.wait_for_timeout(3000)

                full_html = page.content()
                desc_html = get_description(page)

                text = str(row[title_col]) + " " + full_html + " " + desc_html

            except:
                text = str(row[title_col])

            parts = extract_part_numbers(text)
            results.append(parts)

        browser.close()

    df["品番"] = results
    df.to_csv("result.csv", index=False, encoding="utf-8-sig")
    print("完了")

if __name__ == "__main__":
    main()
