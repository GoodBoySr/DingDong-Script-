import os
import time
import discord
from discord.ext import commands
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 Chrome/114 Safari/537.36")
    return uc.Chrome(options=options)

def bypass_process(original_url):
    start_time = time.time()
    driver = setup_driver()

    try:
        driver.get(original_url)
        time.sleep(5)
        for _ in range(30):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            time.sleep(2)

        try:
            btn = driver.find_element(By.XPATH, '//button[contains(text(),"continue") and @style="background-color: white;"]')
            btn.click()
            time.sleep(4)
        except:
            pass

        redirected_url = driver.current_url

        driver.get("https://bypass.city")
        time.sleep(6)
        for _ in range(20):
            if "Verifying" not in driver.page_source:
                break
            time.sleep(2)
            driver.refresh()

        input_box = driver.find_element(By.XPATH, '//input[@type="text"]')
        input_box.send_keys(redirected_url)
        time.sleep(1)

        bypass_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Bypass Link")]')
        bypass_btn.click()
        time.sleep(3)

        main_window = driver.current_window_handle
        for handle in driver.window_handles:
            if handle != main_window:
                driver.switch_to.window(handle)
                driver.close()
        driver.switch_to.window(main_window)

        for _ in range(30):
            try:
                result_input = driver.find_element(By.XPATH, '//input[@type="text"]')
                copy_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Copy Results/Url")]')
                copy_btn.click()
                result = result_input.get_attribute("value")
                break
            except:
                time.sleep(2)

        elapsed = time.time() - start_time
        return result, elapsed

    finally:
        driver.quit()

@bot.event
async def on_ready():
    print(f'✅ Bot online as {bot.user}')

@bot.command()
async def bypass(ctx, link: str):
    await ctx.author.send("💫May take 10-60 Seconds to process, because of complexity of site")

    try:
        result, duration = bypass_process(link)
        await ctx.author.send(f"| Results: {result} Time: {duration:.2f} seconds |")
        await ctx.send(f"| Done {ctx.author.mention} | Bot: Dingdong |")
    except Exception as e:
        await ctx.author.send(f"❌ Error: {e}")
        await ctx.send(f"| Failed {ctx.author.mention} | Bot: Dingdong |")

if __name__ == "__main__":
    bot.run(os.environ["DISCORD_BOT_TOKEN"])
