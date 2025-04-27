import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import random
import asyncio
from datetime import timedelta
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=',', intents=intents)

# Load bot token from Replit secrets
TOKEN = os.getenv("TOKEN")

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Permission Checking Helper
async def check_permissions(ctx, perms):
    missing_perms = [perm for perm in perms if not getattr(ctx.author.permissions_in(ctx.channel), perm)]
    if missing_perms:
        return missing_perms
    return None

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
@bot.command()
@has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Clear messages"""
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

# Banner Command (Get user banner)
@bot.command()
async def banner(ctx, member: discord.Member = None):
    """Show a member's banner"""
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
