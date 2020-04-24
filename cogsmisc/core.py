"""
Created on Dec 26, 2016

@author: andrew
"""
import random
import time
from datetime import datetime, timedelta
from math import floor, isnan

import discord
import psutil
from discord.ext import commands

from cogs5e.models import embeds
from cogsmisc.stats import Stats
from utils import checks


class Core(commands.Cog):
    """
    Core utilty and general commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.monotonic()

    @commands.command(hidden=True)
    async def avatar(self, ctx, user: discord.Member = None):
        """Gets a user's avatar.
        Usage: !avatar <USER>"""
        if user is None:
            user = ctx.message.author
        if user.avatar_url != "":
            await ctx.send(user.avatar_url)
        else:
            await ctx.send(user.display_name + " is using the default avatar.")

    @commands.command()
    async def ping(self, ctx):
        """Checks the ping time to the bot."""
        now = datetime.utcnow()
        pong = await ctx.send("Pong.")
        delta = datetime.utcnow() - now
        httping = floor(delta.total_seconds() * 1000)
        wsping = floor(self.bot.latency * 1000) if not isnan(self.bot.latency) else "Unknown"
        await pong.edit(content=f"Pong.\nHTTP Ping = {httping} ms.\nWS Ping = {wsping} ms.")

    @commands.command()
    async def invite(self, ctx):
        """Prints a link to invite Avrae to your server."""
        await ctx.send(
            "You can invite Avrae to your server here:\n"
            "<https://invite.avrae.io>")

    @commands.command()
    async def changelog(self, ctx):
        """Prints a link to the official changelog."""
        await ctx.send("You can check out the latest patch notes at "
                       "https://github.com/avrae/avrae/releases/latest, and a list of all releases at "
                       "<https://github.com/avrae/avrae/releases>!")

    @commands.command(aliases=['stats', 'info'])
    async def about(self, ctx):
        """Information about the bot."""
        stats = {}
        statKeys = ("dice_rolled_life", "spells_looked_up_life", "monsters_looked_up_life", "commands_used_life",
                    "items_looked_up_life", "rounds_init_tracked_life", "turns_init_tracked_life")
        for k in statKeys:
            stats[k] = await Stats.get_statistic(ctx, k)

        embed = discord.Embed(description='Avrae, a bot to streamline D&D 5e online.\n'
                                          'Check out the latest release notes '
                                          '[here](https://github.com/avrae/avrae/releases/latest).')
        embed.title = "Invite Avrae to your server!"
        embed.url = "https://invite.avrae.io"
        embed.colour = 0x7289da
        total_members = sum(1 for _ in self.bot.get_all_members())
        unique_members = len(self.bot.users)
        members = '%s total\n%s unique' % (total_members, unique_members)
        embed.add_field(name='Members (Cluster)', value=members)
        embed.add_field(name='Uptime', value=str(timedelta(seconds=round(time.monotonic() - self.start_time))))
        motd = random.choice(["May the RNG be with you", "May your rolls be high",
                              "Will give higher rolls for cookies", ">:3",
                              "Does anyone even read these?"])
        embed.set_footer(
            text=f'{motd} | Build {await self.bot.rdb.get("build_num")} | Cluster {self.bot.cluster_id}')

        commands_run = "{commands_used_life} total\n{dice_rolled_life} dice rolled\n" \
                       "{spells_looked_up_life} spells looked up\n{monsters_looked_up_life} monsters looked up\n" \
                       "{items_looked_up_life} items looked up\n" \
                       "{rounds_init_tracked_life} rounds of initiative tracked ({turns_init_tracked_life} turns)" \
            .format(**stats)
        embed.add_field(name="Commands Run", value=commands_run)
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)} on this cluster\n"
                                              f"{await Stats.get_guild_count(self.bot)} total")
        memory_usage = psutil.Process().memory_full_info().uss / 1024 ** 2
        embed.add_field(name='Memory Usage', value='{:.2f} MiB'.format(memory_usage))
        embed.add_field(name='About', value='Made with :heart: by zhu.exe#4211 and the D&D Beyond team\n'
                                            'Join the official development server [here](https://discord.gg/pQbd4s6)!',
                        inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @checks.feature_flag("entitlements-enabled", use_ddb_user=True)
    async def ddb(self, ctx):
        """Displays information about your D&D Beyond account."""
        ddb_user = await self.bot.ddb.get_ddb_user(ctx, ctx.author.id)
        embed = embeds.EmbedWithAuthor(ctx)

        if ddb_user is None:
            embed.title = "No D&D Beyond account connected."
            embed.description = \
                "It looks like you don't have your Discord account connected to your D&D Beyond account!\n" \
                "Linking your account means that you'll be able to use everything you own on " \
                "D&D Beyond in Avrae for free - you can link your accounts " \
                "[here](https://www.dndbeyond.com/account)."
            embed.set_footer(text="Already linked your account? It may take up to a minute for Avrae to recognize the "
                                  "link.")
            return await ctx.send(embed=embed)

        embed.title = f"Hello, {ddb_user.username}!"
        embed.url = "https://www.dndbeyond.com/account"
        desc = f"You're all set! Any books or individual purchases made on D&D Beyond should be available for you " \
               f"to use on Avrae."
        embed.description = desc

        if ddb_user.is_staff:
            embed.set_footer(
                text="Official D&D Beyond Staff",
                icon_url="https://media-waterdeep.cursecdn.com/avatars/thumbnails/104/378/32/32/636511944060210307.png")
        elif ddb_user.is_insider:
            embed.set_footer(text="Thanks for being a D&D Beyond Insider.")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Core(bot))
