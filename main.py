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

# === Configuration ===
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")

# === Logging setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === Discord Bot Initialization ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# === AI ERROR RECOVERY PLACEHOLDER ===
def ai_auto_fix(error_message):
    if not AI_KEY:
        return "AI auto-fix skipped: AI_KEY not configured."
    # Placeholder for real AI call
    logging.warning("ðŸ§  AI DEBUG: Attempting auto-fix using AI...")
    # Simulate AI debugging response
    return f"AI suggestion: Wait longer or refresh the page if '{error_message}' appears."

# === SUPER STEALTH CHROME SETUP ===
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114 Safari/537.36")
    options.add_argument("--lang=en-US,en;q=0.9")
    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL"}
    return uc.Chrome(options=options, desired_capabilities=caps)

# === Bypass Function ===
def bypass_process(original_url):
    start_time = time.time()
    driver = setup_driver()
    result = "âŒ Unknown error"

    try:
        driver.get(original_url)
        logging.info("ðŸ”— Opened original link.")
        time.sleep(5)

        # Wait for Cloudflare or similar checks
        for _ in range(30):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            logging.info("ðŸ›¡ï¸ Waiting out Cloudflare...")
            time.sleep(2)

        # Click first continue button
        try:
            continue_button = driver.find_element(By.XPATH, '//button[contains(text(),"continue") and @style="background-color: white;"]')
            continue_button.click()
            time.sleep(3)
            logging.info("âœ… Clicked continue.")
        except:
            logging.warning("âš ï¸ Continue button not found. Proceeding.")

        redirected_url = driver.current_url
        logging.info(f"ðŸ” Redirected to: {redirected_url}")

        driver.get("https://bypass.city")
        logging.info("ðŸŒ Opening bypass.city...")
        time.sleep(5)

        # Wait out Cloudflare again
        for _ in range(20):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            driver.refresh()
            time.sleep(2)

        # Enter and bypass URL
        input_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
        )
        input_box.send_keys(redirected_url)
        time.sleep(1)

        bypass_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Bypass Link")]')
        bypass_btn.click()
        logging.info("ðŸš€ Bypass link clicked.")
        time.sleep(4)

        # Close popups
        main_win = driver.current_window_handle
        for win in driver.window_handles:
            if win != main_win:
                driver.switch_to.window(win)
                driver.close()
        driver.switch_to.window(main_win)

        # Get result
        for _ in range(30):
            try:
                result_input = driver.find_element(By.XPATH, '//input[@type="text"]')
                result = result_input.get_attribute("value")
                break
            except:
                time.sleep(2)

        time_taken = time.time() - start_time
        return result, time_taken

    except Exception as e:
        tb = traceback.format_exc()
        logging.error("âŒ Exception occurred:\n" + tb)
        ai_msg = ai_auto_fix(str(e))
        return f"{str(e)} | {ai_msg}", time.time() - start_time

    finally:
        driver.quit()

# === Bot Ready ===
@bot.event
async def on_ready():
    logging.info(f"âœ… Bot online as {bot.user}")
    try:
        await tree.sync()
        logging.info("ðŸ“Œ Synced global slash commands.")
    except Exception as e:
        logging.error("âŒ Sync error: " + str(e))

# === Bypass Command ===
@tree.command(name="bypass", description="ðŸšª Bypass links with heavy protection like Cloudflare & ads")
@app_commands.describe(link="Paste the link to bypass")
async def bypass_cmd(interaction: discord.Interaction, link: str):
    await interaction.response.send_message("ðŸ’«May take 10-60 Seconds to process, because of complexity of site", ephemeral=True)
    try:
        result, duration = bypass_process(link)
        await interaction.user.send(f"| Results: {result} Time: {duration:.2f} seconds |")
        await interaction.channel.send(f"| Done <@{interaction.user.id}> | Bot: Dingdong |")
    except Exception as e:
        await interaction.user.send(f"âŒ Error: {e}")
        await interaction.channel.send(f"| Failed <@{interaction.user.id}> | Bot: Dingdong |")

# === Ping ===
@tree.command(name="ping", description="Check if bot is alive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("ðŸ“ Pong!", ephemeral=True)

# === Run Bot ===
if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("âŒ DISCORD_BOT_TOKEN not set.")
