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

bot = commands.Bot(command_prefix=',', intents=intents)

# Load bot token from Replit secrets
TOKEN = os.getenv("TOKEN")

# Store ongoing giveaways
giveaways = {}

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Mute Command (Timeout)
@bot.command()
@has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, time: str, *, reason=None):
    time_delta = timedelta(seconds=int(time)) if time.isdigit() else None
    if not time_delta:
        await ctx.send("Invalid time format. Please enter time in seconds.")
        return
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
    missing_perms = await check_permissions(ctx, ['ban_members'])
    if missing_perms:
        await ctx.send(f"Missing permissions: {', '.join(missing_perms)}")
        return
    await member.ban(reason=reason)
    embed = discord.Embed(title="Banned", description=f"{member.mention} has been banned.", color=0xff0000)
    await ctx.send(embed=embed)

# Clear Command (Clearing messages)
@bot.command()
@has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    missing_perms = await check_permissions(ctx, ['manage_messages'])
    if missing_perms:
        await ctx.send(f"Missing permissions: {', '.join(missing_perms)}")
        return
    await ctx.channel.purge(limit=amount)
    embed = discord.Embed(title="Messages Cleared", description=f"Cleared {amount} messages.", color=0x00ff00)
    await ctx.send(embed=embed)

# Role Command (Add/Remove Role)
@bot.command()
@has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, role: discord.Role):
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
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=0x00ff00)
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

# Banner Command (Get user banner)
@bot.command()
async def banner(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    banner_url = member.banner.url if member.banner else None
    if banner_url:
        embed = discord.Embed(title=f"{member.name}'s Banner", color=0x00ff00)
        embed.set_image(url=banner_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{member.name} does not have a banner set.")

# Server Info Command
@bot.command()
async def serverinfo(ctx):
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
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f"User Info: {member.name}", color=0x00ff00)
    embed.add_field(name="User ID", value=member.id, inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime('%Y-%m-%d'), inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime('%Y-%m-%d'), inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

# Ping Command
@bot.command()
async def ping(ctx):
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

    await ctx.send(embed=embed)

# Giveaway Command
@bot.command()
async def giveaway(ctx, time: str, *, prize: str):
    """Start a giveaway. time in seconds, prize is the giveaway item."""
    try:
        # Convert time to seconds
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
async def reroll(ctx, message_id: int):
    """Reroll a giveaway by message ID."""
    giveaway = giveaways.get(message_id)
    if giveaway:
        winner = await pick_winner(giveaway["message"])
        if winner:
            await ctx.send(f"🎉 The new winner of the giveaway is {winner.mention} who won **{giveaway['prize']}**!")
        else:
            await ctx.send(f"🎉 The giveaway has no eligible entries. No winner was chosen.")
    else:
        await ctx.send("Giveaway with that ID not found.")

bot.run(TOKEN)
