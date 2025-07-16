import os
import time
import discord
import undetected_chromedriver as uc
from discord import app_commands
from discord.ext import commands
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# ✅ Set up bot intents and command tree
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

# 🚀 Setup stealth browser with strong anti-bot bypass
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114 Safari/537.36")
    driver = uc.Chrome(options=options)
    return driver

# 🧠 Full bypass logic for link + Cloudflare + ad + result
def bypass_process(original_url):
    start_time = time.time()
    driver = setup_driver()

    try:
        # Step 1: Open original link
        driver.get(original_url)
        time.sleep(5)

        # Step 2: Wait through Cloudflare
        for _ in range(30):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            time.sleep(2)

        # Step 3: Click "continue" if present
        try:
            btn = driver.find_element(By.XPATH, '//button[contains(text(),"continue") and @style="background-color: white;"]')
            btn.click()
            time.sleep(4)
        except:
            pass

        # Step 4: Get redirected URL (lootlabs/vertise)
        redirected_url = driver.current_url

        # Step 5: Open https://bypass.city and input the link
        driver.get("https://bypass.city")
        time.sleep(5)
        for _ in range(20):
            if "Verifying" not in driver.page_source and "cloudflare" not in driver.page_source.lower():
                break
            driver.refresh()
            time.sleep(2)

        input_box = driver.find_element(By.XPATH, '//input[@type="text"]')
        input_box.send_keys(redirected_url)
        time.sleep(1)

        bypass_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Bypass Link")]')
        bypass_btn.click()
        time.sleep(3)

        # Step 6: Close popup ads
        main_window = driver.current_window_handle
        for handle in driver.window_handles:
            if handle != main_window:
                driver.switch_to.window(handle)
                driver.close()
        driver.switch_to.window(main_window)

        # Step 7: Wait for and extract result
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

# 🔁 Clean and sync slash commands when bot starts
@bot.event
async def on_ready():
    print(f"✅ Bot online as {bot.user}")
    try:
        guilds = await bot.fetch_guilds(limit=150).flatten()
        for guild in guilds:
            await tree.clear_commands(guild=guild)
            await tree.sync(guild=guild)
            print(f"🧹 Cleared & synced commands in {guild.name}")
    except Exception as e:
        print(f"❌ Command sync error: {e}")

# 🔧 Slash command to bypass links
@tree.command(name="bypass", description="Bypass a protected link (Cloudflare, ads, etc.)")
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

# 🧪 Simple command to test if bot is alive
@tree.command(name="ping", description="Check if the bot is awake")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Dingdong is alive.", ephemeral=True)

# 🔑 Start bot from environment secret
if __name__ == "__main__":
    bot.run(os.environ["DISCORD_BOT_TOKEN"])
