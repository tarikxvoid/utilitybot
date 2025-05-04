import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import timedelta, datetime
import pytz
import os
import aiohttp
import io
from discord.ext.commands import has_permissions, MissingPermissions
import random
from gtts import gTTS

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix='?', intents=intents)

# Load bot token from Replit secrets
TOKEN = os.getenv("TOKEN")

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Command: ping
@bot.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: discord.Interaction):
    latency = bot.latency * 1000  
    await interaction.response.send_message(f"Pong! Latency: {latency:.2f}ms")


# List of allowed role IDs
ALLOWED_ROLE_IDS = []

# List of allowed user IDs
ALLOWED_USER_IDS = [1116452227851235398]

@bot.tree.command(name="role", description="Give or remove a role from a user")
@app_commands.describe(user="The user to give or remove the role from", role="The role to give or remove")
async def role(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    # Check if user has permission OR is whitelisted
    allowed = False

    if interaction.user.guild_permissions.manage_roles:
        allowed = True
    elif interaction.user.id in ALLOWED_USER_IDS:
        allowed = True
    else:
        for r in interaction.user.roles:
            if r.id in ALLOWED_ROLE_IDS:
                allowed = True
                break

    if not allowed:
        await interaction.response.send_message(
            "You don't have permission to use this command.",
            ephemeral=True
        )
        return

    # Bot permission check
    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "I don't have the `Manage Roles` permission to perform this action.",
            ephemeral=True
        )
        return

    # Role position checks
    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            f"I cannot manage the role `{role.name}` because it is higher than or equal to my top role.",
            ephemeral=True
        )
        return

    if user.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message(
            f"I cannot modify roles for {user.mention} because their top role is higher than or equal to my top role.",
            ephemeral=True
        )
        return

    if role >= interaction.user.top_role and interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message(
            f"You cannot manage the role `{role.name}` because it is higher than or equal to your top role.",
            ephemeral=True
        )
        return

    # Add/remove role
    if role in user.roles:
        await user.remove_roles(role)
        await interaction.response.send_message(f"Removed `{role.name}` from {user.mention}.")
    else:
        await user.add_roles(role)
        await interaction.response.send_message(f"Gave `{role.name}` to {user.mention}.")


# Command: say
@bot.tree.command(name="say", description="Make the Bot say something.")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

# TRIGGERWORDS
hurensohn = ["hrs", "hure", "hxre", "ass", "bitch", "hoe", "idiot", "whore", "arsch", "köter", "wichser", "wixxer", "hund", "nigg", "huso", "lutscher", "bastard", "ausländer", "kanack", "nutt", "basta"]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Automod: Block certain words
    if any(hurensohn in message.content.lower() for hurensohn in hurensohn):
        await message.channel.send(f"{message.author.mention}, You sent a word that was blocked by the bot owner!\nIf this should happen repeatedly you'll be banned from using the bot.")
    
    # Important: Let the bot process the command
    await bot.process_commands(message)  # <-- this line is the key!
    
# Command: vocalremover
@bot.tree.command(name="vocalremover", description="Sends an Link to vocalremover.org")
async def vocalremover(interaction: discord.Interaction):
    await interaction.response.send_message("https://vocalremover.org/")

# Command: minimumage
@bot.tree.command(name="minimumage", description="Sends the Required Age in different Countries to use Discord.")
async def minimumage(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Minimum Age to Use Discord",
        description="For all countries not listed below, 13 is the minimum age to access Discord.",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Asia",
        value="• South Korea: 14+\n• Vietnam: 15+",
        inline=False
    )

    embed.add_field(
        name="Caribbean",
        value=(
            "• Aruba: 16+\n"
            "• Caribbean Netherlands: 16+\n"
            "• Curaçao: 16+\n"
            "• Sint Maarten: 16+"
        ),
        inline=False
    )

    embed.add_field(
        name="Europe",
        value=(
            "• Austria: 14+\n"
            "• Bulgaria: 14+\n"
            "• Croatia: 16+\n"
            "• Cyprus: 14+\n"
            "• Czech Republic: 15+\n"
            "• France: 15+\n"
            "• Germany: 16+\n"
            "• Greece: 15+\n"
            "• Hungary: 16+\n"
            "• Ireland: 16+\n"
            "• Italy: 14+\n"
            "• Lithuania: 14+\n"
            "• Luxembourg: 16+\n"
            "• Netherlands: 16+\n"
            "• Poland: 16+\n"
            "• Romania: 16+\n"
            "• San Marino: 16+\n"
            "• Serbia: 15+\n"
            "• Slovakia: 16+\n"
            "• Slovenia: 16+\n"
            "• Spain: 14+"
        ),
        inline=False
    )

    embed.add_field(
        name="South America",
        value=(
            "• Chile: 14+\n"
            "• Colombia: 14+\n"
            "• Peru: 14+\n"
            "• Venezuela: 14+"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# Command: appprotocs
@bot.tree.command(name="appprotocs", description="Shows Discord's App Protocols")
async def appprotocs(interaction: discord.Interaction):
    user_id = interaction.user.id  


    if user_id == 1188740550296358912:  
        embed = discord.Embed(
            title="Discord's App Protocols",
            description="Here are the protocols you can use:",
            color=discord.Color.blue()  
        )
        
        embed.add_field(name="Home", value="`/`: `discord://-/`\n"
                                            "friends: `discord://-/channels/@me/`\n"
                                            "nitro: `discord://-/store`\n"
                                            "shop: `discord://-/shop`\n"
                                            "message requests: `discord://-/message-requests`\n"
                                            "family centre: `discord://-/family-center`", inline=False)

        embed.add_field(name="General", value="apps: `discord://-/apps`\n"
                                               "discovery - guilds: `discord://-/guild-discovery`\n"
                                               "gift: `discord://-/gifts/<gift_code>`\n"
                                               "gift (with login screen): `discord://-/gifts/<gift_code>/login`\n"
                                               "new server: `discord://-/guilds/create`\n"
                                               "server invite: `discord://-/invite/<invite_code>`\n"
                                               "server invite (with login screen): `discord://-/invite/<invite_code>/login`\n"
                                               "developer portal: `discord://-/developer`", inline=False)

        embed.add_field(name="Settings", value="user settings: `discord://-/settings/<setting_name>`\n"
                                                "guild settings: `discord://-/guilds/<guild_id>/settings`", inline=False)

        embed.add_field(name="User ", value="user profile: `discord://-/users/<user_id>`", inline=False)

        embed.add_field(name="Guilds and DMs", value="dm channel: `discord://-/channels/@me/<channel_id>`\n"
                                                      "guild: `discord://-/channels/<guild_id>`", inline=False)

        embed.add_field(name="Library", value="library: `discord://-/library/`\n"
                                               "store page: `discord://-/store/skus/<sku_id>`", inline=False)

        embed.add_field(name="Account", value="login: `discord://-/login`\n"
                                               "register: `discord://-/register`", inline=False)

        embed.add_field(name="Events", value="snowsgiving: `discord://-/snowsgiving`\n"
                                              "8th birthday: `discord://-/activities`", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("You are not able to use this Command because it is Restricted to Owner Only")
        
# Command: butter
@bot.tree.command(name="butter", description="shows butter")
async def butter(interaction: discord.Interaction):
    await interaction.response.send_message("https://images.bild.de/66fd40fbd334b272aafaea60/b1a0df1f80eb15228fe2f1bb3a26441d,11b69c98?w=1280")

# Command: torbrowser
@bot.tree.command(name="torbrowser", description="shows downloads for tor browser")
async def torbrowser(interaction: discord.Interaction):
    await interaction.response.send_message("Windows - https://www.torproject.org/dist/torbrowser/14.0.3/tor-browser-windows-x86_64-portable-14.0.3.exe\nMacOS - https://www.torproject.org/dist/torbrowser/14.0.3/tor-browser-macos-14.0.3.dmg\nLinux - https://www.torproject.org/dist/torbrowser/14.0.3/tor-browser-linux-x86_64-14.0.3.tar.xz\nAndroid - https://www.torproject.org/download/#android")

# Command:, excavatorlink
@bot.tree.command(name="excavatorlink", description="shows link to the search engine excavator (Darkweb)")
async def excavatorlink(interaction: discord.Interaction):
    await interaction.response.send_message("https://tor.link/site/excavator/info")

# Command:, ideen
@bot.tree.command(name="ideen", description="Ideen für mein Bot?")
async def ideen(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id == 1116452227851235398:
        await interaction.response.send_message("Habt ihr Ideen für meinen Bot?", ephemeral=True)
    else:
        await interaction.response.send_message("You are not able to use this Command because it is Restricted to Owner only")
    
# Command: revancedmods
@bot.tree.command(name="revancedmods", description="Shows an Link to Modded Clients by ReVanced (Known as Youtube Modded)")
async def revancedmods(interaction: discord.Interaction):
    await interaction.response.send_message("https://revanced.app/")

# Command: vancedmods
@bot.tree.command(name="vancedmods", description="Shows an Link to Modded Clients by Vanced (Known as Youtube Modded)")
async def vancedmods(interaction: discord.Interaction):
    await interaction.response.send_message("https://revanced.net/")

# Cmd: gleggmire
@bot.tree.command(name="gleggmire", description="Shows a picture of the streamer gleggmire.")
async def gleggmire(interaction: discord.Interaction):
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/1366068791749906444/1366138974749327654/1200x630bf-60.png?ex=680fdb91&is=680e8a11&hm=fc0c531da9b8b4a7998d293f4624cf0b4e7f640105fcfcb6f1e15ef8c08d4ef8&")

# Command: gorev2
@bot.tree.command(name="gorev2", description="shows link to gore website (better)")
async def gorev2(interaction: discord.Interaction):
    await interaction.response.send_message("https://goresee.com/")

# Command: gore
@bot.tree.command(name="gore", description="shows link to seegore.com website")
async def gore(interaction: discord.Interaction):
    await interaction.response.send_message("https://seegore.com/")

# Command: mertsucuk
@bot.tree.command(name="mertsucuk", description="Shows the Streamer mertabi in a sucuk industry")
async def mertsucuk(interaction: discord.Interaction):
    await interaction.response.send_message("https://www.dasding.de/newszone/1728566932667%2Cmert-sucuk-100~_v-1x1@2dM_-733e4a95d343c52e922dfd8e3ff26ae78b29e5be.jpg")

# Command: nsfwbbc
@bot.tree.command(name="nsfwbbc", description="Shows an Naked Black Person")
async def nsfwbbc(interaction: discord.Interaction):
    await interaction.response.send_message("https://cdn.thekinkykingdom.com/2018/09/black202.jpg")

# Command: nsfwappollopaok
@bot.tree.command(name="nsfwappollopaok", description="Shows an Leak of apolllopaok_11275 Penis")
async def nsfwappollopaok(interaction: discord.Interaction):
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/1320709733228875827/1320710165040726126/IMG_3513.jpg?ex=676a96b0&is=67694530&hm=9f76b61d988c50870d6189d5eaf128c8be343a94d67d4811eef1934c8fff577e&")

# Command: torlink
@bot.tree.command(name="torlink", description="Shows the Link to the tor.link website search engine for websites.")
async def torlink(interaction: discord.Interaction):
    await interaction.response.send_message("https://tor.link/")


# Command: whitecancer
@bot.tree.command(name="whitecancer", description="Shows an Leak of the Face from prs.stm")
async def whitecancer(interaction: discord.Interaction):
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/1197263175373029416/1320774762477125683/Screenshot_2024-12-23-16-26-49-28_572064f74bd5f9fa804b05334aa4f912.jpg?ex=676ad2da&is=6769815a&hm=34a6a69959d756e35c5d513d02fea290d42ef53450fc04329c775ad3d796a908&")

# Command: blender
@bot.tree.command(name="blender", description="Shows an Leak of the User achmedkilos with his Balls out.")
async def blender(interaction: discord.Interaction):
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/1320775701061828618/1320775715628781588/image.png?ex=676ad3bd&is=6769823d&hm=ffc0f3f1ea1eb6f49839fdd66a540733a0d73d7d3bc091832368c94d09125ecb&")

# Command: blender2
@bot.tree.command(name="blender2", description="Shows an Leak of the User achmedkilos.")
async def blender2(interaction: discord.Interaction):
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/1297469727957848115/1353447104701403247/remix-23c39ee1-e260-4074-9abd-6f87775195af.png?ex=67e1af57&is=67e05dd7&hm=784d6bf53f633fe5d1fafa5f99ba635385a9b79036a3f3a095b98b46d74a84b7&")

# Command: drachenlord
@bot.tree.command(name="drachenlord", description="shows dragonlord streamer aka rainer winkler.")
async def drachenlord(interaction: discord.Interaction):
    await interaction.response.send_message("https://i1.sndcdn.com/artworks-dN9mbk4QTEmEWMCv-JvamaA-t500x500.jpg")
    
# Command: babaeier22
@bot.tree.command(name="babaeier22", description="Shows the Face and Fat Body of the User babaeier22")
async def babaeier22(interaction: discord.Interaction):
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/1320759103458381905/1320759649657684041/IMG_20241223_152709.jpg?ex=676ac4c7&is=67697347&hm=b567736974c8382f61d9a4f979d3bf6584f31fbb1acc891d7ceac3b06104a633&")

# Command: tylermeier
@bot.tree.command(name="tylermeier", description="Shows an Picture of the User tyler_0199 where he was little. His real name is Tyler meier.")
async def tylermeier(interaction: discord.Interaction):
    await interaction.response.send_message("https://cdn.discordapp.com/attachments/1320421030136909878/1320788318853795900/image0.jpg?ex=676adf7a&is=67698dfa&hm=4db57e4612eb5baaa76887c200bd1456504104989c654b9911253d49417b7cc7&\n https://www.tiktok.com/@tyler0199 Is his Tiktok Account.\nHis Real name is Tyler Meier.\n His Account Name on Discord is tyler_0199 and his UserID 1308425665875542017.\n He is 13 Years old and lives in Germany, Eschweiler Nordrhine-Westfalia.\n His Mothers Facebook Profile link is https://www.facebook.com/profile.php?id=100094314540349")

# Whitelisted user IDs allowed to use TTS
ALLOWED_TTS_USERS = {1116452227851235398}  # Replace with real user IDs

@bot.tree.command(name="vcsay", description="Say something in voice channel using TTS")
@app_commands.describe(text="The text you want the bot to say")
async def say(interaction: discord.Interaction, text: str):
    if interaction.user.id not in ALLOWED_TTS_USERS:
        await interaction.response.send_message("You're not authorized to use TTS.", ephemeral=True)
        return

    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You're not in a voice channel!", ephemeral=True)
        return

    vc = await interaction.user.voice.channel.connect()

    # Create TTS audio file
    tts = gTTS(text=text, lang='en')
    tts.save("tts.mp3")

    # Play the audio
    vc.play(discord.FFmpegPCMAudio("tts.mp3"), after=lambda e: print("TTS done"))

    await interaction.response.send_message(f"Saying: {text}", ephemeral=True)

    while vc.is_playing():
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=1))

    await vc.disconnect()
    os.remove("tts.mp3")

# Command: userinfo
@bot.tree.command(name="userinfo", description="Display information about yourself or a user.")
@app_commands.describe(user="The user you want info about.")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    if not user:
        user = interaction.user
    embed = discord.Embed(title=f"User Info for {user.name}", color=discord.Color.blue())
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Username", value=user.name)
    embed.add_field(name="Discriminator", value=user.discriminator)
    embed.add_field(name="Joined at", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

# Command: kick
@bot.tree.command(name="kick", description="Kick a user from the server.")
@app_commands.describe(user="The user to kick.")
async def kick(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.guild_permissions.kick_members:
        await user.kick()
        await interaction.response.send_message(f"{user.name} has been kicked from the server.")
    else:
        await interaction.response.send_message("You do not have permission to kick members.")

# Command: ban
@bot.tree.command(name="ban", description="Ban a user from the server.")
@app_commands.describe(user="The user to ban.")
async def ban(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.guild_permissions.ban_members:
        await user.ban()
        await interaction.response.send_message(f"{user.name} has been banned from the server.")
    else:
        await interaction.response.send_message("You do not have permission to ban members.")

# Command: timeout
@bot.tree.command(name="timeout", description="Timeout a user.")
@app_commands.describe(user="The user to timeout.", duration="Duration in seconds.")
async def timeout(interaction: discord.Interaction, user: discord.Member, duration: int):
    if interaction.user.guild_permissions.moderate_members:
        await user.timeout(duration=timedelta(seconds=duration))
        await interaction.response.send_message(f"{user.name} has been timed out for {duration} seconds.")
    else:
        await interaction.response.send_message("You do not have permission to timeout members.")

# Command: createchannel
@bot.tree.command(name="createchannel", description="Create a new text channel.")
@app_commands.describe(channel_name="The name of the new text channel.")
async def create_channel(interaction: discord.Interaction, channel_name: str):
    if interaction.user.guild_permissions.manage_channels:
        guild = interaction.guild
        await guild.create_text_channel(channel_name)
        await interaction.response.send_message(f"Text channel '{channel_name}' has been created.")
    else:
        await interaction.response.send_message("You do not have permission to create channels.")

# Command: deletechannel
@bot.tree.command(name="deletechannel", description="Delete an existing text channel.")
@app_commands.describe(channel_name="The name of the text channel to delete.")
async def delete_channel(interaction: discord.Interaction, channel_name: str):
    if interaction.user.guild_permissions.manage_channels:
        guild = interaction.guild
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel:
            await channel.delete()
            await interaction.response.send_message(f"Text channel '{channel_name}' has been deleted.")
        else:
            await interaction.response.send_message(f"Text channel '{channel_name}' not found.")
    else:
        await interaction.response.send_message("You do not have permission to delete channels.")


# Whitelisted user and role IDs
ALLOWED_VC_USER_IDS = {1116452227851235398}
ALLOWED_VC_ROLE_IDS = {}

@bot.tree.command(name="join", description="Join the voice channel you're in")
async def join(interaction: discord.Interaction):
    user = interaction.user

    # Check if user is allowed
    if user.id not in ALLOWED_VC_USER_IDS and not any(role.id in ALLOWED_VC_ROLE_IDS for role in user.roles):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    if not user.voice or not user.voice.channel:
        await interaction.response.send_message("You're not in a voice channel!", ephemeral=True)
        return

    channel = user.voice.channel
    await channel.connect()
    await interaction.response.send_message(f"Joined {channel.name}!")



# Command: setfont
@bot.tree.command(name="setfont", description="Set custom font for your messages.")
@app_commands.describe(font="The font type (bold, italic, underline, etc.).")
async def set_font(interaction: discord.Interaction, font: str):
    if font == "bold":
        await interaction.response.send_message(f"**This text is bold**")
    elif font == "italic":
        await interaction.response.send_message(f"*This text is italic*")
    elif font == "underline":
        await interaction.response.send_message(f"__This text is underlined__")
    else:
        await interaction.response.send_message(f"Font '{font}' is not recognized.")

# Command: serverinfo
@bot.tree.command(name="serverinfo", description="Displays server info.")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"Server Info for {guild.name}", color=discord.Color.green())
    embed.add_field(name="Server Name", value=guild.name)
    embed.add_field(name="Server ID", value=guild.id)
    embed.add_field(name="Owner", value=guild.owner)
    embed.add_field(name="Region", value=guild.region)
    embed.add_field(name="Member Count", value=guild.member_count)
    embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

# Command: pipebomb
@bot.tree.command(name='pipebomb', description="Displays an Link for the Tutorial of an Pipebomb.")
async def pipebomb(interaction: discord.Interaction):
    await interaction.response.send_message("https://www.vanderbilt.edu/physicsdemonstration/davesdemos/demonstrations/demo100.htm")
    
# Command: remind
@bot.tree.command(name="remind", description="Set a reminder for yourself.")
@app_commands.describe(time="The time to wait before the reminder in seconds.", reminder="The reminder message.")
async def remind(interaction: discord.Interaction, time: int, reminder: str):
    await interaction.response.send_message(f"Reminder set! I will remind you in {time} seconds.")
    await asyncio.sleep(time)
    await interaction.user.send(f"Reminder: {reminder}")

# Command: countdown
@bot.tree.command(name="countdown", description="Start a countdown timer.")
@app_commands.describe(time="The time to countdown in seconds.")
async def countdown(interaction: discord.Interaction, time: int):
    while time < 10:
        await interaction.response.send_message(f"Countdown: {time} seconds remaining")
        await asyncio.sleep(1)
        time -= 1
    await interaction.response.send_message("Countdown finished!")

# Command: random
@bot.tree.command(name="random", description="Generate a random number.")
@app_commands.describe(min_value="The minimum value for the random number.", max_value="The maximum value for the random number.")
async def random_number(interaction: discord.Interaction, min_value: int, max_value: int):
    import random
    number = random.randint(min_value, max_value)
    await interaction.response.send_message(f"Random number: {number}")

# Command: advice
@bot.tree.command(name="advice", description="Get random advice.")
async def advice(interaction: discord.Interaction):
    import random
    advice_list = ["Believe in yourself.", "Don't give up.", "Stay positive.", "Keep learning."]
    advice = random.choice(advice_list)
    await interaction.response.send_message(f"Here's some advice: {advice}")
    

# Command: randomFact
@bot.tree.command(name="randomfact", description="Get a random fact.")
async def random_fact(interaction: discord.Interaction):
    import random
    facts = ["The Eiffel Tower can grow taller during the summer.", "Honey never spoils.", "Octopuses have three hearts."]
    fact = random.choice(facts)
    await interaction.response.send_message(f"Here's a random fact: {fact}")

# Command: botinfo
@bot.tree.command(name="botinfo", description="Get information about the bot.")
async def bot_info(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Info", description="Information about this bot.", color=discord.Color.orange())
    embed.add_field(name="Name", value=bot.user.name)
    embed.add_field(name="ID", value=bot.user.id)
    embed.add_field(name="Created At", value=bot.user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.set_thumbnail(url=bot.user.avatar.url)
    await interaction.response.send_message(embed=embed)
    
# Command: onlinestatus
ALLOWED_USER_ID = 1116452227851235398  

@bot.tree.command(name="onlinestatus", description="Lets you set the status of the bot.")
@app_commands.choices(
    status=[
        app_commands.Choice(name="Online", value="online"),
        app_commands.Choice(name="Do Not Disturb", value="dnd"),
        app_commands.Choice(name="Idle", value="idle"),
        app_commands.Choice(name="Offline", value="offline"),
    ]
)
async def online_status(interaction: discord.Interaction, status: app_commands.Choice[str]):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message(
            "You don't have permissions to use this command.", ephemeral=True
        )
        return

    status_value = status.value.lower()

    if status_value == "online":
        await bot.change_presence(status=discord.Status.online)
    elif status_value == "dnd":
        await bot.change_presence(status=discord.Status.do_not_disturb)
    elif status_value == "idle":
        await bot.change_presence(status=discord.Status.idle)
    elif status_value == "offline":
        await bot.change_presence(status=discord.Status.invisible)

    await interaction.response.send_message(f"Bot status set to `{status.name}`.")

# Command: setstatus
@bot.tree.command(name="setstatus", description="Set a custom status for the bot.")
@app_commands.describe(status="The custom status message.")
async def set_status(interaction: discord.Interaction, status: str):
    user_id = interaction.user.id
    if user_id == 1116452227851235398:
        await bot.change_presence(activity=discord.Game(status))
        await interaction.response.send_message(f"Status updated to: {status}")
    else:
        await interaction.response.send_message("You do not have permission to change the bot's status.")

# Command: time
@bot.tree.command(name="time", description="Shows the current time.")
async def time(interaction: discord.Interaction):
    tz = pytz.timezone("Europe/Berlin")
    time_now = datetime.now(tz).strftime("%H:%M")
    await interaction.response.send_message(f"Current time in the Timezone Europe/Berlin: {time_now}")

# Command: date
@bot.tree.command(name="date", description="Shows the current date.")
async def date(interaction: discord.Interaction):
    tz = pytz.timezone("Europe/Berlin")
    date_now = datetime.now(tz).strftime("%d.%m.%Y")
    await interaction.response.send_message(f"Current Date in Europe/Berlin: {date_now}")

# Command: deleterole
@bot.tree.command(name="deleterole", description="Delete a specified role.")
@app_commands.describe(role_name="The name of the role to delete.")
async def delete_role(interaction: discord.Interaction, role_name: str):
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name=role_name)

    if interaction.user.guild_permissions.manage_roles:
        if role:  
            await role.delete()
            await interaction.response.send_message(f"Role '{role_name}' has been deleted.")
        else:
            await interaction.response.send_message(f"Role '{role_name}' not found.")
    else:
        await interaction.response.send_message("You do not have permission to delete roles.")


# Command: createrole
@bot.tree.command(name="createrole", description="Create a new role with a custom name and color.")
@app_commands.describe(role_name="The name of the new role.", role_color="The color of the new role (in hex).")
async def create_role(interaction: discord.Interaction, role_name: str, role_color: str):
    guild = interaction.guild
    color = discord.Color(int(role_color.lstrip('#'), 16))  

    if interaction.user.guild_permissions.manage_roles:
        role = await guild.create_role(name=role_name, color=color)
        await interaction.response.send_message(f"Role '{role_name}' created with color {role_color}!")
    else:
        await interaction.response.send_message("You do not have permissions to create roles.")

@bot.tree.command(name="credits", description="Shows Credits of the Bot.")
async def credits(interaction: discord.Interaction):
    embed = discord.Embed(title="Credits", description="Credits for the Bot.", color=discord.Color.blue())
    embed.add_field(name="Owner & Main Developer", value="Username: unkn0wn.sh4d0w\nID: 1116452227851235398")
    await interaction.response.send_message(embed=embed)
        
# Command: renamerole
@bot.tree.command(name="renamerole", description="Rename an existing role.")
@app_commands.describe(old_role_name="The current name of the role.", new_role_name="The new name for the role.")
async def rename_role(interaction: discord.Interaction, old_role_name: str, new_role_name: str):
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name=old_role_name)

    if interaction.user.guild_permissions.manage_roles:
        if role:
            await role.edit(name=new_role_name)
            await interaction.response.send_message(f"Role '{old_role_name}' has been renamed to '{new_role_name}'.")
        else:
            await interaction.response.send_message(f"Role '{old_role_name}' not found.")
    else:
        await interaction.response.send_message("You do not have permission to manage roles.")

# Command: changerolecolor
@bot.tree.command(name="changerolecolor", description="Change the color of an existing role.")
@app_commands.describe(role_name="The name of the role to change.", new_color="The new color in hex for the role.")
async def change_role_color(interaction: discord.Interaction, role_name: str, new_color: str):
    guild = interaction.guild
    color = discord.Color(int(new_color.lstrip('#'), 16))  
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        await interaction.response.send_message(f"Role '{role_name}' not found.")
        return

    if interaction.user.guild_permissions.manage_roles:
        await role.edit(color=color)
        await interaction.response.send_message(f"Role '{role_name}' color has been changed to {new_color}.")
    else:
        await interaction.response.send_message("You do not have permission to change role colors.")

# Command: avatar
@bot.tree.command(name="avatar", description="Get the avatar of a user.")
@app_commands.describe(user="The user whose avatar you want to fetch.")
async def get_avatar(interaction: discord.Interaction, user: discord.Member = None):
    if not user:
        user = interaction.user
    avatar_url = user.avatar.url
    await interaction.response.send_message(f"Here's the avatar of {user.name}: {avatar_url}")

# Command: banner
@bot.tree.command(name="banner", description="Get the banner of a user.")
@app_commands.describe(user="The user whose banner you want to fetch.")
async def get_banner(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    
    # Fetch full user object to get banner
    user = await interaction.client.fetch_user(user.id)
    
    banner_url = user.banner.url if user.banner else None
    if banner_url:
        embed = discord.Embed(
            title=f"Banner of {user.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_image(url=banner_url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"{user.name} does not have a banner set.")


# Command: roles
@bot.tree.command(name="roles", description="Get a list of all roles in the server.")
async def get_roles(interaction: discord.Interaction):
    guild = interaction.guild
    roles = guild.roles
    role_list = [role.name for role in roles]
    await interaction.response.send_message(f"Roles in the server: {', '.join(role_list)}")

# Command: perms
@bot.tree.command(name="perms", description="Shows the permissions a user has in this channel.")
@app_commands.describe(user="The user whose permissions you want to check.")
async def permissions(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    perms = interaction.channel.permissions_for(user)
    permissions_list = [perm for perm, value in perms if value]
    formatted_perms = "\n".join(permissions_list)
    if formatted_perms:
        await interaction.response.send_message(
            f"**Permissions for {user.mention}:**\n```\n{formatted_perms}\n```"
        )
    else:
        await interaction.response.send_message(
            f"{user.mention} has no permissions in this channel."
        )


# Command: channels
@bot.tree.command(name="channels", description="Get a list of all channels in the server.")
async def get_channels(interaction: discord.Interaction):
    guild = interaction.guild
    channels = guild.channels
    channel_list = [channel.name for channel in channels]
    await interaction.response.send_message(f"Channels in the server: {', '.join(channel_list)}")

# Command: channelinfo
@bot.tree.command(name="channelinfo", description="Get information about a specific channel.")
@app_commands.describe(channel="The channel to get information about.")
async def get_channel_info(interaction: discord.Interaction, channel: discord.abc.GuildChannel):
    channel_name = channel.name
    channel_id = channel.id
    channel_type = "Text" if isinstance(channel, discord.TextChannel) else "Voice" if isinstance(channel, discord.VoiceChannel) else "Unknown"
    channel_created_at = channel.created_at.strftime("%Y-%m-%d %H:%M:%S")
    channel_category = channel.category.name if channel.category else "No Category"
    channel_position = channel.position

    if isinstance(channel, discord.TextChannel):
        channel_topic = channel.topic if channel.topic else "No topic set."
        channel_nsfw = "Yes" if channel.is_nsfw() else "No"
        channel_slowmode = f"{channel.slowmode_delay} seconds" if channel.slowmode_delay else "No Slowmode"
    else:
        channel_topic = "N/A"
        channel_nsfw = "N/A"
        channel_slowmode = "N/A"

    if isinstance(channel, discord.VoiceChannel):
        channel_maximum_members = channel.user_limit if channel.user_limit else "Unlimited"
        channel_bitrate = f"{channel.bitrate // 1000} kbps"
        channel_voice_region = channel.rtc_region if channel.rtc_region else "Automatic"
    else:
        channel_maximum_members = "N/A"
        channel_bitrate = "N/A"
        channel_voice_region = "N/A"

    channel_permissions = "Yes" if channel.permissions_synced else "No"
    channel_mention = channel.mention
    channel_members = ", ".join([member.name for member in channel.members]) if channel.members else "No members"

    channel_info = (
        f"**Channel Information:**\n"
        f"Name: {channel_name}\n"
        f"ID: {channel_id}\n"
        f"Type: {channel_type}\n"
        f"Created at: {channel_created_at}\n"
        f"Category: {channel_category}\n"
        f"Position: {channel_position}\n"
        f"Topic: {channel_topic}\n"
        f"NSFW: {channel_nsfw}\n"
        f"Slowmode: {channel_slowmode}\n"
        f"Maximum Members: {channel_maximum_members}\n"
        f"Bitrate: {channel_bitrate}\n"
        f"Voice Region: {channel_voice_region}\n"
        f"Permissions Synced: {channel_permissions}\n"
        f"Mention: {channel_mention}\n"
        f"Members: {channel_members}"
    )
    await interaction.response.send_message(channel_info)
    
#Command: purge
@bot.tree.command(name="purge", description="Delete a specified number of messages.,")
@app_commands.describe(amount="The number of messages to delete.")
async def purge(interaction: discord.Interaction, amount: int):
    if interaction.user.guild_permissions.manage_messages:
        await interaction.response.defer()
        await interaction.channel.purge(limit=amount + 1)
        await interaction.followup.send(f"{amount} messages have been deleted.", ephemeral=True)

    else:
        await interaction.response.send_message("You do not have permission to manage messages.")


@bot.tree.command(name="help", description="Shows a list of available commands.")
async def help_command(interaction: discord.Interaction):
    # Embed 1
    embed1 = discord.Embed(
        title="This is a List of all available Commands for this Bot",
        description="This Bot was made by unkn0wn_sh4d0w!",
        color=discord.Color.blue()
    )
    embed1.add_field(
        name="**Commands List (1/6)**",
        value=(
            "`/ping` - Check the bot's latency.\n"
            "`/say <message>` - Make the bot say something.\n"
            "`/butter` - Shows butter.\n"
            "`/excavatorlink` - Shows a link to the search engine Excavator (Darkweb).\n"
            "`/mertsucuk` - Shows the streamer Mertabi in a sucuk industry.\n"
            "`/nsfwbbc` - Shows an image of a naked black person.\n"
            "`/nsfwappollopaok` - Shows a leaked image of a user.\n"
            "`/userinfo [user]` - Display information about yourself or a user.\n"
            "`/kick <user>` - Kick a user from the server.\n"
            "`/ban <user>` - Ban a user from the server."
        ),
        inline=False
    )

    # Embed 2
    embed2 = discord.Embed(
        title="",
        description=" ",
        color=discord.Color.blue()
    )
    embed2.add_field(
        name="**Commands List (2/6)**",
        value=(
            "`/timeout <user> <duration>` - Timeout a user for a specified duration.\n"
            "`/createchannel <channel_name>` - Create a new text channel.\n"
            "`/deletechannel <channel_name>` - Delete a specified text channel.\n"
            "`/setfont <font>` - Set custom font for your messages (bold, italic, underline).\n"
            "`/serverinfo` - Displays server info.\n"
            "`/pipebomb` - Displays a link for the pipebomb tutorial.\n"
            "`/remind <time> <reminder>` - Set a reminder for yourself.\n"
            "`/countdown <time>` - Start a countdown timer.\n"
            "`/random <min_value> <max_value>` - Generate a random number.\n"
            "`/advice` - Get random advice."
        ),
        inline=False
    )

    # Embed 3
    embed3 = discord.Embed(
        title="",
        description="",
        color=discord.Color.blue()
    )
    embed3.add_field(
        name="**Commands List (3/6)**",
        value=(
            "`/randomfact` - Get a random fact.\n"
            "`/botinfo` - Get information about this bot.\n"
            "`/setstatus <status>` - OWNER ONLY (Set a custom status for the bot.)\n"
            "`/time` - Shows the current time in the Europe/Berlin timezone.\n"
            "`/createrole <role_name> <role_color>` - Create a new role with a custom name and color.\n"
            "`/deleterole <role_name>` - Delete a specified role.\n"
            "`/renamerole <old_role_name> <new_role_name>` - Rename a role.\n"
            "`/changerolecolor <role_name> <new_color>` - Change the color of an existing role.\n"
            "`/avatar [user]` - Get the avatar of a user.\n"
            "`/banner [user]` - Get the banner of a user."
        ),
        inline=False
    )

    # Embed 4
    embed4 = discord.Embed(
        title="",
        description="",
        color=discord.Color.blue()
    )
    embed4.add_field(
        name="**Commands List (4/6)**",
        value=(
            "`/roles` - Get a list of all roles in the server.\n"
            "`/channels` - Get a list of all channels in the server.\n"
            "`/purge <amount>` - Delete a specified number of messages.\n"
            "`/help` - Shows a list of available commands.\n"
            "`/channelinfo <channel>` - Get information about a specific channel.\n"
            "`/whitecancer` - Shows an Image of the Face from prs.stm.\n"
            "`/blender` - Shows a Picture of the user achmedkilos where his balls look out of his pants.\n"
            "`/gore` - Shows a Link to seegore.com\n"
            "`/gorev2` - Shows a Link to goresee.com\n"
            "`/tylermeier` - Shows Information about Tyler Meier\n"
        ),
            inline=False
    )

    # Embed 5
    embed5 = discord.Embed(
        title="",
        description="",
        color=discord.Color.blue()
    )
    embed5.add_field(
        name="**Commands List (5/6)**",
        value=(
            "`/babaeier22` - Shows an Picture of the user babaeier22\n"
            "`/torbrowser` - Shows a Link to Download Tor Browser\n"
            "`/torlink` - Shows a Link to tor.link Website Search Engine for Websites\n"
            "`/ideen` - OWNER ONLY (Shows An Question.)\n"
            "`/revancedmods` - Shows ReVanced Modded Applications for Android (Youtube Modified...)\n"
            "`/approtocs` - OWNER ONLY (Shows Discords App Protocols.)\n"
            "`/date` - Shows current Date in Europe/Berlin\n"
            "`/credits` - Shows Credits of this Bot.\n"
            "`/perms` - Shows Permissions a User got in the Channel the Command were Invoked in.\n"
            "`/role` - Give or Remove Roles from a User.\n"
        ),
    
            inline=False
    )

    # Embed 6
    embed6 = discord.Embed(
        title="",
        description="",
        color=discord.Color.blue()
    )
    embed6.add_field(
        name="**Commands List (6/6)**",
        value=(
            "`/revancedmods` - Shows an link to vanced mods by vanced.\n"
            "`/onlinestatus <status> - OWNER ONLY (Sets the Online Status of the Bot.)\n"
            "`/vocalremover` - Sends an Link to the Website https://vocalremover.org/\n"
            "`/minimumage` - Shows the Minimum Age you must be to use Discord.\n"
            "`/blender2` - Shows a Picture of the User achmedkilos."
        ),
    
            inline=False
    )
    
    await interaction.response.send_message(embed=embed1, ephemeral=True)
    await interaction.followup.send(embed=embed2, ephemeral=True)
    await interaction.followup.send(embed=embed3, ephemeral=True)
    await interaction.followup.send(embed=embed4, ephemeral=True)
    await interaction.followup.send(embed=embed5, ephemeral=True)
    await interaction.followup.send(embed=embed6, ephemeral=True)

# PREFIX CMDS
# Permission Checking Helper
async def check_permissions(ctx, perms):
    missing_perms = []

    user_perms = ctx.author.permissions_in(ctx.channel)  # get the Permissions object once

    for perm in perms:
        if not getattr(user_perms, perm, False):  # safely get the permission
            missing_perms.append(perm)

    return missing_perms if missing_perms else None


# Welcome Message (Embed)
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="news")
    if channel:
        embed = discord.Embed(title=f"Welcome {member.name}!", description=f"Welcome to the server, {member.mention}!", color=0x00ff00)
        await channel.send(embed=embed)

# Mute Command (Timeout)
@bot.command()
@has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, time: str, *, reason=None):
    """Mute a member for a specified duration"""
    time_delta = timedelta(seconds=int(time)) if time.isdigit() else None
    if not time_delta:
        await ctx.send("Invalid time format. Please enter time in seconds.")
        return

    # Check if the bot has permission
    missing_perms = await check_permissions(ctx, ['manage_roles'])
    if missing_perms:
        await ctx.send(f"Missing permissions: {', '.join(missing_perms)}")
        return

    await member.timeout(time_delta, reason=reason)
    embed = discord.Embed(title="Muted", description=f"{member.mention} has been muted for {time} seconds.", color=0xff0000)
    await ctx.send(embed=embed)

# Unmute Command
@bot.command()
@has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """Unmute a member"""
    # Check if the bot has permission
    missing_perms = await check_permissions(ctx, ['manage_roles'])
    if missing_perms:
        await ctx.send(f"Missing permissions: {', '.join(missing_perms)}")
        return

    await member.timeout(None)
    embed = discord.Embed(title="Unmuted", description=f"{member.mention} has been unmuted.", color=0x00ff00)
    await ctx.send(embed=embed)

# Kick Command
@bot.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kick a member"""
    missing_perms = await check_permissions(ctx, ['kick_members'])
    if missing_perms:
        await ctx.send(f"Missing permissions: {', '.join(missing_perms)}")
        return

    await member.kick(reason=reason)
    embed = discord.Embed(title="Kicked", description=f"{member.mention} has been kicked.", color=0xff0000)
    await ctx.send(embed=embed)

# Ban Command
@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """Ban a member"""
    missing_perms = await check_permissions(ctx, ['ban_members'])
    if missing_perms:
        await ctx.send(f"Missing permissions: {', '.join(missing_perms)}")
        return

    await member.ban(reason=reason)
    embed = discord.Embed(title="Banned", description=f"{member.mention} has been banned.", color=0xff0000)
    await ctx.send(embed=embed)

# Clear Command (Clearing messages)
from discord.ext.commands import has_permissions, MissingPermissions

# Clear Command (Clearing messages)
@bot.command(name="purge")
@has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Clear messages in a channel."""

    # Purge the messages
    deleted = await ctx.channel.purge(limit=amount)

    # Send confirmation embed
    embed = discord.Embed(
        title="Messages Cleared",
        description=f"Cleared {len(deleted)} messages.",
        color=0x00ff00
    )
    confirmation = await ctx.send(embed=embed)

    # Auto-delete the confirmation after few seconds (optional)
    await asyncio.sleep(5)
    await confirmation.delete()

# Error handler for missing permissions
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't have permission to manage messages.")
# Role Command (Add/Remove Role)
@bot.command()
@has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, role: discord.Role):
    """Add a role to a member"""
    missing_perms = await check_permissions(ctx, ['manage_roles'])
    if missing_perms:
        await ctx.send(f"Missing permissions: {', '.join(missing_perms)}")
        return

    if ctx.author.top_role > member.top_role:
        await member.add_roles(role)
        embed = discord.Embed(title="Role Added", description=f"{role.name} has been added to {member.mention}.", color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        await ctx.send("You can't assign a role higher than your own top role.")

# Avatar Command (Get user avatar)
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    """Show a member's avatar"""
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=0x00ff00)
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def banner(ctx, member: discord.Member = None):
    """Show a member's banner."""
    if member is None:
        member = ctx.author

    # Fetch the full user profile
    user = await bot.fetch_user(member.id)

    if user.banner:
        banner_url = user.banner.url
        embed = discord.Embed(title=f"{member.name}'s Banner", color=0x00ff00)
        embed.set_image(url=banner_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{member.name} does not have a banner set.")


# Server Info Command
@bot.command()
async def serverinfo(ctx):
    """Get information about the server"""
    guild = ctx.guild
    embed = discord.Embed(title=f"Server Info: {guild.name}", color=0x00ff00)
    embed.add_field(name="Server ID", value=guild.id, inline=False)
    embed.add_field(name="Created At", value=guild.created_at.strftime('%Y-%m-%d'), inline=False)
    embed.add_field(name="Member Count", value=guild.member_count, inline=False)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
    await ctx.send(embed=embed)

# User Info Command
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """Get information about a user"""
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f"User Info: {member.name}", color=0x00ff00)
    embed.add_field(name="User ID", value=member.id, inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime('%Y-%m-%d'), inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime('%Y-%m-%d'), inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    """Ping the bot"""
    await ctx.send(f'Pong! Latency is {round(bot.latency * 1000)}ms')

@bot.command(name="commands")
async def show_commands(ctx):
    """Show bot commands"""
    embed = discord.Embed(
        title="Help Menu",
        description="List of available commands:",
        color=0x00ff00
    )
    embed.add_field(name="?mute", value="Mute a member for a set time (in seconds).", inline=False)
    embed.add_field(name="?unmute", value="Unmute a member.", inline=False)
    embed.add_field(name="?kick", value="Kick a member from the server.", inline=False)
    embed.add_field(name="?ban", value="Ban a member from the server.", inline=False)
    embed.add_field(name="?purge", value="Clear a set number of messages.", inline=False)
    embed.add_field(name="?role", value="Assign a role to a member (if you have permissions).", inline=False)
    embed.add_field(name="?avatar", value="Get a user's avatar.", inline=False)
    embed.add_field(name="?banner", value="Get a user's banner.", inline=False)
    embed.add_field(name="?serverinfo", value="Get server information.", inline=False)
    embed.add_field(name="?userinfo", value="Get user information.", inline=False)
    embed.add_field(name="?ping", value="Check bot latency.", inline=False)

    await ctx.send(embed=embed)
    
bot.run(TOKEN)
