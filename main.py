import os
import time
import discord
import undetected_chromedriver as uc
from discord import app_commands
from discord.ext import commands
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

# Fake fingerprint options
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL"}

    driver = uc.Chrome(options=options, desired_capabilities=caps)
    return driver

# ⛩️ AI-assisted logic placeholder (expand if you connect AI_KEY)
def ai_helper(prompt):
    ai_key = os.getenv("AI_KEY")
    if not ai_key:
        return "AI not enabled. Add AI_KEY to environment variables."
    # Placeholder for actual AI interaction
    return "AI Helper: If you're stuck, try waiting or switching IP!"

# Core bypass logic
def bypass_process(original_url):
    start_time = time.time()
    driver = setup_driver()

    try:
        # Step 1: Go to original URL
        driver.get(original_url)
        time.sleep(6)

        # Step 2: Wait for Cloudflare to finish
        for _ in range(20):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            time.sleep(2)

        # Step 3: Click the first "continue" white button
        try:
            button = driver.find_element(By.XPATH, '//button[contains(text(),"continue") and @style="background-color: white;"]')
            button.click()
            time.sleep(4)
        except:
            pass

        # Step 4: Copy the redirected link
        redirected_url = driver.current_url

        # Step 5: Go to bypass.city
        driver.get("https://bypass.city")
        time.sleep(5)

        # Wait for Cloudflare on bypass.city
        for _ in range(15):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            time.sleep(2)
            driver.refresh()

        # Step 6: Enter the URL and click "Bypass Link"
        input_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]')))
        input_box.send_keys(redirected_url)
        time.sleep(1)

        bypass_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Bypass Link")]')
        bypass_btn.click()
        time.sleep(5)

        # Step 7: Close any ad popups
        main = driver.current_window_handle
        for win in driver.window_handles:
            if win != main:
                driver.switch_to.window(win)
                driver.close()
        driver.switch_to.window(main)

        # Step 8: Wait for and get result
        for _ in range(30):
            try:
                result_input = driver.find_element(By.XPATH, '//input[@type="text"]')
                copy_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Copy Results/Url")]')
                copy_btn.click()
                result = result_input.get_attribute("value")
                break
            except:
                time.sleep(2)
        else:
            result = "❌ Failed to get result link. " + ai_helper("Why didn't bypass.city give a result?")

        time_taken = time.time() - start_time
        return result, time_taken

    finally:
        driver.quit()

# Sync new slash commands and remove old ones
@bot.event
async def on_ready():
    print(f"✅ Bot online as {bot.user}")
    try:
        guilds = [g async for g in bot.fetch_guilds(limit=150)]
        for guild in guilds:
            await tree.clear_commands(guild=guild)
            await tree.sync(guild=guild)
            print(f"🧹 Synced & cleared in: {guild.name}")
    except Exception as e:
        print(f"❌ Command sync error: {e}")

# 🔧 Main bypass command
@tree.command(name="bypass", description="Bypass a protected link (Cloudflare, ads, redirect)")
@app_commands.describe(link="Paste the link to bypass")
async def bypass_command(interaction: discord.Interaction, link: str):
    await interaction.response.send_message("💫May take 10-60 Seconds to process, because of complexity of site", ephemeral=True)
    try:
        result, duration = bypass_process(link)
        await interaction.user.send(f"| Results: {result} Time: {duration:.2f} seconds |")
        await interaction.channel.send(f"| Done <@{interaction.user.id}> | Bot: Dingdong |")
    except Exception as e:
        await interaction.user.send(f"❌ Error: {e}")
        await interaction.channel.send(f"| Failed <@{interaction.user.id}> | Bot: Dingdong |")

# 🧪 Ping command
@tree.command(name="ping", description="Check if Dingdong is alive 🟢")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! I'm alive.", ephemeral=True)

# 🚀 Run bot using secret token
if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
