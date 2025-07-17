import os
import time
import discord
import traceback
import openai
import undetected_chromedriver as uc
from discord.ext import commands
from discord import app_commands
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import asyncio
import logging

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree
openai.api_key = AI_KEY

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--enable-automation")
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--no-first-run")
    options.add_argument("--no-sandbox")
    options.add_argument("--no-zygote")
    options.add_argument("--password-store=basic")
    options.add_argument("--use-gl=swiftshader")
    options.add_argument("--use-file-for-fake-paths")
    options.add_argument("--use-file-for-fake-paths=/tmp")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    return uc.Chrome(options=options)

def switch_to_new_tab(driver):
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

def click_continue_button(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "continue") and @style="background-color: white;"]'))
        ).click()
        time.sleep(3)
        switch_to_new_tab(driver)
    except Exception as e:
        logger.error(f"Error clicking continue button: {e}")

def bypass_city(driver, lootlabs_url):
    driver.get("https://bypass.city")
    time.sleep(3)
    try:
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
        )
        input_box.send_keys(lootlabs_url)
        input_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Wait for final result
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Copy Results/Url")]'))
        ).click()

        result = driver.find_element(By.XPATH, '//input[@type="text"]').get_attribute("value")
        return result
    except Exception as e:
        logger.error(f"Error during bypass.city process: {e}")
        return f"❌ Failed to get result: {str(e)}"

async def send_processing_messages(interaction, duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        await interaction.followup.send("Processing...", ephemeral=True)
        await asyncio.sleep(2)

@tree.command(name="bypass", description="Bypass Cloudflare + Loot/Vertise and get final link.")
@app_commands.describe(link="Enter the protected link.")
async def bypass_command(interaction: discord.Interaction, link: str):
    await interaction.response.send_message("💫May take 10-60 Seconds to process, because of complexity of site", ephemeral=True)
    await interaction.followup.send("DingDong is thinking...", ephemeral=True)

    start_time = time.time()
    try:
        driver = setup_driver()
        driver.get(link)
        time.sleep(4)

        while "cloudflare" in driver.page_source.lower():
            time.sleep(2)
            driver.get(link)

        click_continue_button(driver)
        time.sleep(2)
        switch_to_new_tab(driver)

        loot_url = driver.current_url
        logger.info(f"Loot URL: {loot_url}")
        final_result = bypass_city(driver, loot_url)

        time_taken = time.time() - start_time

        await interaction.user.send(f"| Results: {final_result} Time: {time_taken:.2f} seconds |")
        await interaction.followup.send(f"| Done {interaction.user.mention} | Bot: Dingdong |", ephemeral=False)
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error(error_msg)
        await interaction.user.send(error_msg)
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.error(f"Error quitting driver: {e}")

    # Send processing messages every 2 seconds
    await send_processing_messages(interaction, 60)

@tree.command(name="test", description="AI-analyze a URL to see if it can be bypassed.")
@app_commands.describe(link="The URL you want to test.")
async def test_command(interaction: discord.Interaction, link: str):
    await interaction.response.send_message("🧠 AI analyzing the link...", ephemeral=True)
    try:
        prompt = f"""
You're a web security AI helping a bypass bot. Analyze the following URL:
{link}

Check:
- Is this a common ad/link shortener or cloudflare site?
- Does it likely lead to a lootlabs/vertise-style page?
- Is it worth processing or should it be rejected?

Respond with either:
- ✅ VALID: Bypassable link.
- ❌ INVALID: Not processable.
With a short reason.
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        await interaction.followup.send(f"🔍 AI Result: {result}", ephemeral=True)
    except Exception as e:
        logger.error(f"AI failed to respond: {e}")
        await interaction.followup.send(f"❌ AI failed to respond: {e}", ephemeral=True)

@bot.event
async def on_ready():
    try:
        synced = await tree.sync()
        logger.info(f"✅ Synced {len(synced)} command(s).")
        logger.info(f"🤖 Bot online as {bot.user}")
    except Exception as e:
        logger.error(f"❌ Command sync error: {e}")

bot.run(TOKEN)
