import os
import time
import discord
import undetected_chromedriver as uc
from discord import app_commands
from discord.ext import commands
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
import logging
import openai

# === ENV ===
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")  # OpenAI API key for debug assistant

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === Discord Bot Init ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# === Real OpenAI Auto-Fix ===
def ai_auto_fix(error_message):
    if not AI_KEY:
        return "🧠 AI auto-fix skipped (no AI_KEY set)."

    openai.api_key = AI_KEY

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a debugging assistant for a Python Discord bot that uses undetected_chromedriver, Selenium, and Cloudflare bypass."},
                {"role": "user", "content": f"An error occurred in the bot:\n{error_message}\nWhat could have caused it and how to fix it?"}
            ],
            temperature=0.5
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"🧠 AI failed to respond: {str(e)}"

# === Selenium Stealth Chrome Setup ===
def setup_driver():
    chrome_path = "/usr/bin/google-chrome"  # Railway's default Chrome path

    options = uc.ChromeOptions()
    options.binary_location = chrome_path
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114 Safari/537.36")

    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL"}

    return uc.Chrome(options=options, desired_capabilities=caps)

# === Bypass Flow ===
def bypass_process(original_url):
    start_time = time.time()
    driver = setup_driver()
    result = "❌ Unknown error"

    try:
        driver.get(original_url)
        time.sleep(5)

        for _ in range(20):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            time.sleep(2)

        try:
            continue_button = driver.find_element(By.XPATH, '//button[contains(text(),"continue") and @style="background-color: white;"]')
            continue_button.click()
            time.sleep(3)
        except:
            pass

        redirected_url = driver.current_url
        if "auth.platorelay" in redirected_url:
            raise Exception("Still stuck on auth.platorelay")

        driver.get("https://bypass.city")
        time.sleep(4)

        for _ in range(20):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            driver.refresh()
            time.sleep(2)

        input_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
        )
        input_box.clear()
        input_box.send_keys(redirected_url)
        time.sleep(1)

        bypass_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Bypass Link")]')
        bypass_btn.click()
        time.sleep(3)

        main_win = driver.current_window_handle
        for win in driver.window_handles:
            if win != main_win:
                driver.switch_to.window(win)
                driver.close()
        driver.switch_to.window(main_win)

        for _ in range(30):
            try:
                result_input = driver.find_element(By.XPATH, '//input[@type="text"]')
                result = result_input.get_attribute("value")
                if result and result.startswith("http"):
                    break
            except:
                pass
            time.sleep(2)

        time_taken = time.time() - start_time
        return result, time_taken

    except Exception as e:
        tb = traceback.format_exc()
        ai_msg = ai_auto_fix(str(e))
        return f"ERROR: {str(e)} | {ai_msg}", time.time() - start_time
    finally:
        driver.quit()

# === On Ready ===
@bot.event
async def on_ready():
    logging.info(f"✅ Bot online as {bot.user}")
    try:
        await tree.sync()
        logging.info("📌 Slash commands synced.")
    except Exception as e:
        logging.error("❌ Slash command sync failed: " + str(e))

# === /bypass ===
@tree.command(name="bypass", description="Bypass Cloudflare & ads to reveal the real URL")
@app_commands.describe(link="The link to bypass (auth.platorelay, lootlabs, etc.)")
async def bypass_cmd(interaction: discord.Interaction, link: str):
    await interaction.response.send_message("💫May take 10–60 seconds to process...", ephemeral=True)
    try:
        result, duration = bypass_process(link)
        await interaction.user.send(f"| Results: {result} Time: {duration:.2f} seconds |")
        await interaction.channel.send(f"| Done <@{interaction.user.id}> | Bot: Dingdong |")
    except Exception as e:
        await interaction.user.send(f"❌ Failed to bypass: {e}")
        await interaction.channel.send(f"| Failed <@{interaction.user.id}> | Bot: Dingdong |")

# === /ping ===
@tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!", ephemeral=True)

# === Main Run ===
if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("❌ DISCORD_BOT_TOKEN not set.")
        
