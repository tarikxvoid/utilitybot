import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from datetime import timedelta
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix=',', intents=intents)

# Load bot token from Replit secrets
TOKEN = os.getenv("TOKEN")

# Store for active voice channels
active_vc = {}

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Event: When a user joins a voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:  # User joined a channel
        target_channel_id = 1224024298990342305  # Replace this with the ID of the channel you want users to join
        
        if after.channel.id == target_channel_id:
            if member.id not in active_vc:
                overwrites = {
                    member.guild.default_role: discord.PermissionOverwrite(connect=False),
                    member: discord.PermissionOverwrite(connect=True)
                }
                new_channel = await member.guild.create_voice_channel(f"VC-{member.name}", overwrites=overwrites)
                active_vc[member.id] = new_channel
                await member.move_to(new_channel)

    elif before.channel is not None and before.channel.id in active_vc:
        if len(before.channel.members) == 0:
            await before.channel.delete()
            del active_vc[member.id]

# Voice Ban Command
@bot.command()
@has_permissions(manage_channels=True)
async def voiceban(ctx, member: discord.Member, *, reason=None):
    """Ban a member from a specific voice channel."""
    # Check if the member is already in an active voice channel
    for channel in active_vc.values():
        if member in channel.members:
            await member.move_to(None)
            await channel.set_permissions(member, connect=False)
            embed = discord.Embed(title="Voice Banned", description=f"{member.mention} has been banned from voice channels.", color=0xff0000)
            await ctx.send(embed=embed)
            return
    await ctx.send(f"{member.mention} is not in any voice channels.")

# Voice Kick Command
@bot.command()
@has_permissions(manage_channels=True)
async def voicekick(ctx, member: discord.Member, *, reason=None):
    """Kick a member from a specific voice channel."""
    for channel in active_vc.values():
        if member in channel.members:
            await member.move_to(None)
            embed = discord.Embed(title="Voice Kicked", description=f"{member.mention} has been kicked from the voice channel.", color=0xff0000)
            await ctx.send(embed=embed)
            return
    await ctx.send(f"{member.mention} is not in any voice channels.")

# Voice Limit Command
@bot.command()
@has_permissions(manage_channels=True)
async def voicelimit(ctx, channel: discord.VoiceChannel, limit: int):
    """Set a limit for the number of members allowed in a voice channel."""
    await channel.edit(user_limit=limit)
    embed = discord.Embed(title="Voice Channel Limit Set", description=f"Voice channel {channel.name} now has a limit of {limit} members.", color=0x00ff00)
    await ctx.send(embed=embed)

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
    embed.add_field(name="?voiceban", value="Ban a member from all voice channels.", inline=False)
    embed.add_field(name="?voicekick", value="Kick a member from all voice channels.", inline=False)
    embed.add_field(name="?voicelimit", value="Set the member limit for a voice channel.", inline=False)

    await ctx.send(embed=embed)

bot.run(TOKEN)
