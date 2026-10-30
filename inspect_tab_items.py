import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        # Print all tabitems and their visibility
        tabs = await page.locator(".tabitem").all()
        print("Total tabitems:", len(tabs))
        for i, t in enumerate(tabs):
            id_attr = await t.get_attribute("id")
            style = await t.get_attribute("style")
            is_vis = await t.is_visible()
            # Find file input inside this tabitem
            fi_count = await t.locator("input[type='file']").count()
            print(f"Tabitem {i} (id={id_attr}): style={style} visible={is_vis} file_inputs={fi_count}")

        await b.close()

asyncio.run(inspect())
