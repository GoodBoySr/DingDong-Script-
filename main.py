import os
import time
import discord
import shutil
import traceback
import openai
import undetected_chromedriver as uc

from discord.ext import commands
from discord import app_commands

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def setup_driver():
    chrome_path = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    options = uc.ChromeOptions()
    if chrome_path:
        options.binary_location = chrome_path

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114 Safari/537.36")

    return uc.Chrome(options=options)

def ai_debug_report(error_text):
    if not AI_KEY:
        return "AI debug unavailable (no API key)"
    try:
        openai.api_key = AI_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a Python and browser automation expert. Help diagnose errors."},
                {"role": "user", "content": f"Here's the traceback:\n{error_text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI failed: {str(e)}"

def bypass_link(original_url):
    start = time.time()
    driver = setup_driver()
    result = "❌ Unknown error"
    try:
        driver.get(original_url)
        time.sleep(6)

        for _ in range(20):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            time.sleep(2)

        try:
            continue_btn = driver.find_element(By.XPATH, '//button[contains(text(),"continue") and @style="background-color: white;"]')
            continue_btn.click()
            time.sleep(4)
        except:
            pass

        redirected = driver.current_url
        if "auth.platorelay" in redirected:
            raise Exception("Still stuck at auth.platorelay")

        driver.get("https://bypass.city")
        time.sleep(4)

        for _ in range(20):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            driver.refresh()
            time.sleep(2)

        input_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
        )
        input_field.send_keys(redirected)
        input_field.send_keys(Keys.RETURN)
        time.sleep(4)

        # Close ad popups
        main_win = driver.current_window_handle
        for win in driver.window_handles:
            if win != main_win:
                driver.switch_to.window(win)
                driver.close()
        driver.switch_to.window(main_win)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(text(),"Copy Results")]'))
        ).click()

        result_url = driver.find_element(By.XPATH, '//input[@type="text"]').get_attribute("value")
        duration = time.time() - start
        return result_url, duration

    except Exception as e:
        error_trace = traceback.format_exc()
        ai_help = ai_debug_report(error_trace)
        return f"❌ Error: {str(e)}\n\n🧠 AI Suggestion:\n{ai_help}", time.time() - start
    finally:
        driver.quit()

@bot.event
async def on_ready():
    print(f"✅ Bot online as {bot.user}")
    try:
        await tree.sync()
        print("📌 Slash commands synced.")
    except Exception as e:
        print(f"❌ Command sync error: {e}")

@tree.command(name="bypass", description="Bypass Cloudflare and ad redirects")
@app_commands.describe(link="The link to bypass (e.g., auth.platorelay.com)")
async def bypass(interaction: discord.Interaction, link: str):
    await interaction.response.send_message("💫May take 10–60 seconds to process...", ephemeral=True)
    try:
        result, seconds = bypass_link(link)
        await interaction.user.send(f"| Results: {result}\nTime: {seconds:.2f} seconds |")
        await interaction.channel.send(f"| Done <@{interaction.user.id}> | Bot: Dingdong |")
    except Exception as e:
        await interaction.user.send(f"❌ Failed: {str(e)}")
        await interaction.channel.send(f"| Failed <@{interaction.user.id}> | Bot: Dingdong |")

@tree.command(name="ping", description="Simple ping command")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! I'm alive.", ephemeral=True)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ DISCORD_BOT_TOKEN not set in environment.")
