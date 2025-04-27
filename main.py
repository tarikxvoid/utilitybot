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
async def giveaway(ctx, time: int = None, *, prize: str = None):
    """Start a giveaway. Users react to join."""
    if time is None or prize is None:
        return await ctx.send("Usage: `,giveaway [time in seconds] [prize]`")

    embed = discord.Embed(
        title="🎉 Giveaway Started!",
        description=f"Prize: **{prize}**\nReact with 🎉 to join!\nTime: {time} seconds",
        color=discord.Color.random()
    )
    message = await ctx.send(embed=embed)
    await message.add_reaction('🎉')

    giveaways[message.id] = {
        'prize': prize,
        'message': message,
        'channel': ctx.channel
    }

    await asyncio.sleep(time)

    # After waiting, pick a winner
    new_message = await ctx.channel.fetch_message(message.id)
    reaction = discord.utils.get(new_message.reactions, emoji='🎉')

    if reaction:
        users = await reaction.users().flatten()
        users = [user for user in users if not user.bot]

        if users:
            winner = random.choice(users)
            await ctx.send(f"🎉 Congratulations {winner.mention}! You won **{prize}**!")
        else:
            await ctx.send("No valid entries. No winner could be determined.")

    giveaways.pop(message.id, None)

@bot.command()
async def reroll(ctx, message_id: int = None):
    """Reroll a giveaway by message ID."""
    if message_id is None:
        return await ctx.send("Usage: `,reroll [message_id]`")

    giveaway = giveaways.get(message_id)

    if not giveaway:
        try:
            # Fetch old message
            channel = ctx.channel
            message = await channel.fetch_message(message_id)
        except:
            return await ctx.send("Couldn't find that giveaway message.")

        reaction = discord.utils.get(message.reactions, emoji='🎉')
        if reaction:
            users = await reaction.users().flatten()
            users = [user for user in users if not user.bot]

            if users:
                winner = random.choice(users)
                await ctx.send(f"🔄 Rerolled! New winner is {winner.mention}!")
            else:
                await ctx.send("No valid entries to reroll.")
        else:
            await ctx.send("No reactions found on the giveaway message.")
    else:
        await ctx.send("This giveaway is still running, wait until it ends to reroll!")
        
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
