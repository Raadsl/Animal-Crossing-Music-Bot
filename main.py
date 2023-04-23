import discord
from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer, opus
from utils import create_embed, handle_error, NoVCError

from datetime import datetime
import os
import pytz
import sys

# opus.load_opus()

ADMINS = [915670836357247006, 658650587679948820, 1015577382826020894]
FFMPEG_OPTIONS = {
    'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
MUSIC_FOLDER = 'music'

timezone = pytz.timezone('Europe/London')


class Bot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="ac!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

    async def on_command_error(self, ctx, error):
        await handle_error(ctx, error, ephemeral=True)


bot = Bot()


@bot.event
async def on_ready():
    print("Ready")
    activity = discord.Activity(type=discord.ActivityType.watching,
                                name="It is 7pm and sunny")
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.hybrid_command(name="restart",
                    with_app_command=True,
                    description="Restart the bot")
async def restart(ctx):
    await ctx.defer(ephemeral=False)
    if not ctx.author.id in ADMINS:
        await ctx.reply(embed=await create_embed())
        return
    await ctx.reply(embed=await create_embed(
        title="Restarting",
        description=f"Restart ordered by {ctx.author.mention}"))

    sys.exit()


@bot.hybrid_command(
    name="ping",
    description="Check bot latency",
    with_app_command=True,
)
async def ping(ctx):
    await ctx.defer(ephemeral=True)
    if round(bot.latency * 1000) <= 50:
        embed = discord.Embed(
            title="PING",
            description=
            f":ping_pong: Pong! Bot's latency  is **{(bot.latency * 1000)}** ms!",
            color=0x44FF44,
        )
    elif round(bot.latency * 1000) <= 100:
        embed = discord.Embed(
            title="PING",
            description=
            f":ping_pong: Pong! Bot's latency  is **{round(bot.latency * 1000)}** ms!",
            color=0xFFD000,
        )
    elif round(bot.latency * 1000) <= 200:
        embed = discord.Embed(
            title="PING",
            description=
            f":ping_pong: Pong! Bot's latency  is **{round(bot.latency * 1000)}** ms!",
            color=0xFF6600,
        )
    else:
        embed = discord.Embed(
            title="PING",
            description=
            f":ping_pong: Pong! Bot's latency  is **{round(bot.latency * 1000)}** ms!",
            color=0x990000,
        )
    await ctx.reply(embed=embed)


@bot.hybrid_command(name="join",
                    description="Join a vc",
                    with_app_command=True)
async def join(ctx, channel: discord.VoiceChannel = None):
    await ctx.defer(ephemeral=False)

    if not channel:
        channel = ctx.author.voice.channel
        if not channel:
            return await ctx.reply(title='Could not join VC',
                                   description='Make sure to specify a voice channel or be in a vc')

    await channel.connect(reconnect=True)
    return await ctx.reply(
        embed=await create_embed(title='Success',
                                 description='Joined voice channel',
                                 color=discord.Color.green()))


@bot.hybrid_command(name='play',
                    description="Start playing music",
                    with_app_command=True)
async def play(ctx):
    await ctx.defer(ephemeral=False)

    voice_channel = ctx.author.voice.channel
    voice_client = ctx.guild.voice_client

    if not voice_client:
        if not voice_channel:
            raise NoVCError()
        voice_client = await voice_channel.connect()

    current_time = datetime.now(timezone) if timezone else datetime.now()
    hour = current_time.hour

    tune = f"{MUSIC_FOLDER}/new-horizons/sunny/{hour}.ogg"

    voice_client.play(FFmpegPCMAudio(tune))

    await ctx.reply(embed=await create_embed(
        title='ACNH 5pm Sunny',
        description=
        "For now, this track is hardcoded. This will be dynamic later and there will be settings for servers and possibly users to change location (for live weather), game and timezone."
    ))


try:
    bot.run(os.environ["BOT_TOKEN"])
except BaseException as e:
    print(f"ERROR WITH LOGGING IN: {e}")
