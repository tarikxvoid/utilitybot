import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from datetime import timedelta
import os
import random
import asyncio
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True  # This intent is needed for tracking reactions

bot = commands.Bot(command_prefix=',', intents=intents)

# Load bot token from Replit secrets
TOKEN = os.getenv("TOKEN")

# Store ongoing giveaways
giveaways = {}

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Giveaway Command
@bot.command()
async def giveaway(ctx, time: str = None, *, prize: str = None):
    """Start a giveaway. time in seconds, prize is the giveaway item."""
    
    # Check if time and prize are provided
    if not time or not prize:
        missing_args = []
        if not time:
            missing_args.append("[time] (in seconds)")
        if not prize:
            missing_args.append("[prize]")
        await ctx.send(f"Missing argument(s): {', '.join(missing_args)}. Usage: `,giveaway [time] [prize]`")
        return

    # Convert time to seconds
    try:
        giveaway_time = int(time)
    except ValueError:
        await ctx.send("Invalid time format. Please enter time in seconds.")
        return

    # Create a giveaway message
    embed = discord.Embed(title="Giveaway!", description=f"React with 🎉 to enter the giveaway for {prize}!\nTime remaining: {time} seconds.", color=0x00ff00)
    giveaway_message = await ctx.send(embed=embed)
    
    # Add reaction for users to react with
    await giveaway_message.add_reaction('🎉')

    # Set the time when the giveaway should end
    end_time = datetime.utcnow() + timedelta(seconds=giveaway_time)

    # Store the giveaway details
    giveaways[giveaway_message.id] = {
        "prize": prize,
        "end_time": end_time,
        "message": giveaway_message,
        "reacted_users": set()
    }

    # Wait for the giveaway to end
    await asyncio.sleep(giveaway_time)

    # Check if the giveaway is still active
    if giveaway_message.id in giveaways:
        winner = await pick_winner(giveaway_message)
        if winner:
            await ctx.send(f"🎉 The giveaway has ended! The winner is {winner.mention} who won **{prize}**!")
        else:
            await ctx.send(f"🎉 The giveaway has ended! Unfortunately, no one reacted to enter the giveaway.")
        
        # Clean up after the giveaway
        del giveaways[giveaway_message.id]

# Helper function to pick a winner from reactions
async def pick_winner(giveaway_message):
    giveaway = giveaways[giveaway_message.id]
    # Fetch all users who reacted with 🎉
    reaction = discord.utils.get(giveaway_message.reactions, emoji='🎉')
    if reaction:
        users = await reaction.users().flatten()
        # Remove bot and the message author from the list of eligible users
        users = [user for user in users if not user.bot and user != giveaway_message.author]
        if users:
            return random.choice(users)  # Randomly pick a winner
    return None

# Reroll Command
@bot.command()
async def reroll(ctx, message_id: int = None):
    """Reroll a giveaway by message ID."""
    if not message_id:
        await ctx.send("Missing argument: [message_id]. Usage: `,reroll [message_id]`")
        return
    
    giveaway = giveaways.get(message_id)
    if giveaway:
        winner = await pick_winner(giveaway["message"])
        if winner:
            await ctx.send(f"🎉 The new winner of the giveaway is {winner.mention} who won **{giveaway['prize']}**!")
        else:
            await ctx.send(f"🎉 The giveaway has no eligible entries. No winner was chosen.")
    else:
        await ctx.send("Giveaway with that ID not found.")

# Banner Command (Get user banner)
@bot.command()
async def banner(ctx, member: discord.Member = None):
    """Get a user's banner."""
    
    if not member:
        member = ctx.author  # Default to the author if no member is specified
    
    banner_url = member.banner.url if member.banner else None
    if banner_url:
        embed = discord.Embed(title=f"{member.name}'s Banner", color=0x00ff00)
        embed.set_image(url=banner_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{member.name} does not have a banner set.")

@bot.command()
@commands.has_role("Giveaway Host")
async def giveaway(ctx):
    questions = [
        'ðŸ“Œ In welchem Kanal soll das Giveaway stattfinden? (z.â€¯B. #gewinnspiel)',
        'ðŸŽ Was ist der Preis?',
        'â±ï¸ Wie lange soll das Giveaway laufen (in Sekunden)?'
    ]
    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for question in questions:
        await ctx.send(question)
        try:
            message = await client.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('â° Zeit abgelaufen! Bitte versuche es erneut.')
            return
        answers.append(message.content)

    try:
        channel_id = int(answers[0][2:-1])
        channel = client.get_channel(channel_id)
        if channel is None:
            raise Exception()
    except:
        await ctx.send(f'âš ï¸ UngÃ¼ltige KanalerwÃ¤hnung. Bitte nutze z.â€¯B. {ctx.channel.mention}')
        return

    prize = answers[1]
    duration = int(answers[2])

    await ctx.send(f'ðŸŽ‰ Giveaway fÃ¼r **{prize}** startet in {channel.mention} und lÃ¤uft **{duration} Sekunden**!')

    embed = discord.Embed(color=0x2ecc71)
    embed.set_author(name='ðŸŽ‰ GIVEAWAY', icon_url='https://i.imgur.com/VaX0pfM.png')
    embed.add_field(
        name=f'{ctx.author.name} verlost: {prize}',
        value='Reagiere mit ðŸŽ‰ um teilzunehmen!',
        inline=False
    )
    end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
    embed.set_footer(text=f'Ende: {end_time.strftime("%d.%m.%Y um %H:%M:%S")} UTC')
    message = await channel.send(embed=embed)
    await message.add_reaction("ðŸŽ‰")
    await asyncio.sleep(duration)

    message = await channel.fetch_message(message.id)
    users = await message.reactions[0].users().flatten()
    users = [u for u in users if u != client.user]

    if not users:
        await channel.send('âŒ Niemand hat teilgenommen.')
        return

    winner = random.choice(users)
    result = discord.Embed(color=0xff2424)
    result.set_author(name='ðŸŽŠ GIVEAWAY BEENDET!', icon_url='https://i.imgur.com/DDric14.png')
    result.add_field(
        name=f'ðŸŽ Preis: {prize}',
        value=f'ðŸ† Gewinner: {winner.mention}\nðŸ‘¥ Teilnehmer: {len(users)}',
        inline=False
    )
    await channel.send(embed=result)

@bot.command()
@commands.has_role("Giveaway Host")
async def reroll(ctx, channel: discord.TextChannel, message_id: int):
    try:
        message = await channel.fetch_message(message_id)
    except:
        await ctx.send("âŒ Nachricht nicht gefunden.")
        return

    users = await message.reactions[0].users().flatten()
    users = [u for u in users if u != client.user]

    if not users:
        await ctx.send("âŒ Keine Teilnehmer gefunden.")
        return

    winner = random.choice(users)
    embed = discord.Embed(color=0xff2424)
    embed.set_author(name='ðŸ” NEUER GEWINNER', icon_url='https://i.imgur.com/DDric14.png')
    embed.add_field(name='ðŸ† Gewinner:', value=winner.mention, inline=False)
    await channel.send(embed=embed)

# Mute Command (Timeout)
@bot.command()
@has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member = None, time: str = None, *, reason: str = None):
    """Mute a member for a set time."""
    
    # Check if arguments are missing
    if not member:
        await ctx.send("Missing argument: [member]. Usage: `,mute [member] [time] [reason (optional)]`")
        return
    if not time:
        await ctx.send("Missing argument: [time]. Usage: `,mute [member] [time] [reason (optional)]`")
        return
    
    # Validate time format
    try:
        time_delta = timedelta(seconds=int(time))
    except ValueError:
        await ctx.send("Invalid time format. Please enter time in seconds.")
        return

    # Apply the mute
    await member.timeout(time_delta, reason=reason)
    embed = discord.Embed(title="Muted", description=f"{member.mention} has been muted for {time} seconds.", color=0xff0000)
    await ctx.send(embed=embed)

# Unmute Command
@bot.command()
@has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member = None):
    """Unmute a member."""
    
    if not member:
        await ctx.send("Missing argument: [member]. Usage: `,unmute [member]`")
        return
    
    # Unmute the member
    await member.timeout(None)
    embed = discord.Embed(title="Unmuted", description=f"{member.mention} has been unmuted.", color=0x00ff00)
    await ctx.send(embed=embed)

# Kick Command
@bot.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason: str = None):
    """Kick a member."""
    
    if not member:
        await ctx.send("Missing argument: [member]. Usage: `,kick [member] [reason (optional)]`")
        return

    # Kick the member
    await member.kick(reason=reason)
    embed = discord.Embed(title="Kicked", description=f"{member.mention} has been kicked.", color=0xff0000)
    await ctx.send(embed=embed)

# Ban Command
@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason: str = None):
    """Ban a member."""
    
    if not member:
        await ctx.send("Missing argument: [member]. Usage: `,ban [member] [reason (optional)]`")
        return

    # Ban the member
    await member.ban(reason=reason)
    embed = discord.Embed(title="Banned", description=f"{member.mention} has been banned.", color=0xff0000)
    await ctx.send(embed=embed)

# Clear Command (Clearing messages)
@bot.command()
@has_permissions(manage_messages=True)
async def clear(ctx, amount: int = None):
    """Clear messages."""
    
    if not amount:
        await ctx.send("Missing argument: [amount]. Usage: `,clear [amount]`")
        return

    # Clear the messages
    await ctx.channel.purge(limit=amount)
    embed = discord.Embed(title="Messages Cleared", description=f"Cleared {amount} messages.", color=0x00ff00)
    await ctx.send(embed=embed)

# Role Command (Add/Remove Role)
@bot.command()
@has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member = None, role: discord.Role = None):
    """Assign a role to a member."""
    
    if not member:
        await ctx.send("Missing argument: [member]. Usage: `,role [member] [role]`")
        return
    if not role:
        await ctx.send("Missing argument: [role]. Usage: `,role [member] [role]`")
        return

    # Add the role
    await member.add_roles(role)
    embed = discord.Embed(title="Role Added", description=f"{role.name} has been added to {member.mention}.", color=0x00ff00)
    await ctx.send(embed=embed)

# Avatar Command (Get user avatar)
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    """Get a user's avatar."""
    
    if not member:
        await ctx.send("Missing argument: [member]. Usage: `,avatar [member]`")
        return
    
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=0x00ff00)
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

# Server Info Command
@bot.command()
async def serverinfo(ctx):
    """Get server information."""
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
    """Get user information."""
    
    if not member:
        await ctx.send("Missing argument: [member]. Usage: `,userinfo [member]`")
        return
    
    embed = discord.Embed(title=f"User Info: {member.name}", color=0x00ff00)
    embed.add_field(name="User ID", value=member.id, inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime('%Y-%m-%d'), inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime('%Y-%m-%d'), inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

# Ping Command
@bot.command()
async def ping(ctx):
    """Check bot latency."""
    await ctx.send(f'Pong! Latency is {round(bot.latency * 1000)}ms')

# Show Commands
@bot.command(name="commands")
async def show_commands(ctx):
    embed = discord.Embed(
        title="Help Menu",
        description="List of available commands:",
        color=0x00ff00
    )
    embed.add_field(name="?mute", value="Mute a member for a set time (in seconds).", inline=False)
    embed.add_field(name="?unmute", value="Unmute a member.", inline=False)
    embed.add_field(name="?kick", value="Kick a member from the server.", inline=False)
    embed.add_field(name="?ban", value="Ban a member from the server.", inline=False)
    embed.add_field(name="?clear", value="Clear a set number of messages.", inline=False)
    embed.add_field(name="?role", value="Assign a role to a member (if you have permissions).", inline=False)
    embed.add_field(name="?avatar", value="Get a user's avatar.", inline=False)
    embed.add_field(name="?banner", value="Get a user's banner.", inline=False)
    embed.add_field(name="?serverinfo", value="Get server information.", inline=False)
    embed.add_field(name="?userinfo", value="Get user information.", inline=False)
    embed.add_field(name="?ping", value="Check bot latency.", inline=False)
    embed.add_field(name="?giveaway", value="Start a giveaway. Usage: `,giveaway [time] [prize]`", inline=False)
    embed.add_field(name="?reroll", value="Reroll a giveaway. Usage: `,reroll [message_id]`", inline=False)
    
    await ctx.send(embed=embed)

bot.run(TOKEN)
