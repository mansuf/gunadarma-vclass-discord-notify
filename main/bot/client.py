import traceback
import asyncio
import random
import time
from discord import Client, Embed
from discord.interactions import Interaction
from discord.app_commands import CommandTree, Command
from discord.ext.tasks import loop
from typing import List
from django.utils.dateformat import (
    format as dtformat,
    time_format as tformat
)
from django.utils.timezone import now as get_datetime_now
from ..utils import convert_datetime
from ..scrapper.op import (
    iter_courses_url,
    get_materi_courses,
    login,
    logout,
    get_session_time_remaining,
    ServerDown
)
from ..database.assigments_model.models import Activity
from ..database.op import (
    create_matkul, 
    create_materi,
    create_activity,
    get_materi,
    get_activity,
    get_all_activities,
    notice_deadline_activity,
    notice_open_time_activity,
    check_notice_deadline_activity,
    check_notice_open_time_activity
)

login_event = asyncio.Event()

base_dir = Path(__file__).resolve().parent.parent.parent
guild_discord_conf = json.loads((base_dir / "discord-guild.secret.json").read_text())
channel_id = guild_discord_conf["channel_id"]
guild_id = guild_discord_conf["guild_id"]

class IA24Client(Client):
    async def _proc_notice_new_activities(self):
        embeds = []
        async for course_url in iter_courses_url():
            course = await get_materi_courses(course_url)
            matkul = await create_matkul(name=course.matkul)

            for materi in course.materi:
                m = await get_materi(name=materi.name, matkul=matkul)
                if m is None:
                    m = await create_materi(name=materi.name, matkul=matkul)

                for act in materi.activities:
                    embed = Embed()
                    embed.title = f"{act.type.capitalize()} baru"
                    embed.description = act.name
                    embed.description += f"\nLink: {act.url}" # Seriously, fuck you discord
                    embed.url = act.url

                    embed.add_field(name="Nama mata kuliah", value=course.matkul, inline=False)
                    embed.add_field(name="Nama materi", value=materi.name, inline=False)

                    a = await get_activity(id_num=act.id)

                    if a is None:
                        await create_activity(
                            materi=m,
                            id_num=act.id,
                            name=act.name,
                            type=act.type,
                            url=act.url,
                            deadline=act.deadline,
                            open_time=act.open_time
                        )

                        # Add open time
                        if act.open_time is not None:
                            open_time = convert_datetime(act.open_time)
                            embed.add_field(name="Dibuka tanggal", value=open_time, inline=False)

                        # Add deadline
                        if act.deadline is not None:
                            deadline = convert_datetime(act.deadline)
                            embed.add_field(name="Ditutup tanggal (deadline)", value=deadline, inline=False)

                        embeds.append(embed)

        if embeds:
            # await self.channel.send(content="@everyone")

            while True:
                items = embeds[:5]

                if not items:
                    break

                await self.channel.send(embeds=items)
                del embeds[:5]

    @loop(seconds=300)
    async def notice_new_activities(self):
        await login_event.wait()
        try:
            await self._proc_notice_new_activities()
        except Exception as e:
            self.notice_new_activities_error = e

            await logout()
            await asyncio.sleep(3)
            await login()

    @loop(seconds=3)
    async def notice_open_time_activity(self):
        try:
            activities: List[Activity] = await get_all_activities()

            embeds = []
            for act in activities:
                if act.open_time is not None:
                    embed = Embed()
                    embed.title = f"{act.type} '{act.name}' telah dibuka, mari dikerjakan (jangan lupa sharing jawabannya)"
                    embed.description = f"Link {act.type.lower()}: \n{act.url}"
                    embed.add_field(name="Mata kuliah", value=act.materi.matkul.name, inline=False)
                    embed.add_field(name="Materi", value=act.materi.name, inline=False)

                    deadline = convert_datetime(act.deadline)
                    embed.add_field(name="Deadline", value=deadline)

                    is_noticed = await check_notice_open_time_activity(act)
                    now = get_datetime_now()
                    if act.open_time < now and not is_noticed:
                        embeds.append((embed, act))

            if embeds:
                # await self.channel.send(content="@everyone")

                for embed, act in embeds:
                    await self.channel.send(embed=embed)
                    await notice_open_time_activity(act)

        except Exception as e:
            self.notice_open_time_activity_error = e

    @loop(seconds=6)
    async def notice_deadline_activity(self):
        try:
            activities: List[Activity] = await get_all_activities()

            embeds = []
            for act in activities:
                if act.deadline is not None:
                    embed = Embed()
                    embed.title = f"{act.type} '{act.name}' akan berakhir hari ini, mari dikerjakan (jangan lupa sharing jawabannya)"
                    embed.description = f"Link {act.type.lower()}: \n{act.url}"
                    embed.add_field(name="Mata kuliah", value=act.materi.matkul.name, inline=False)
                    embed.add_field(name="Materi", value=act.materi.name, inline=False)

                    deadline = convert_datetime(act.deadline)
                    embed.add_field(name="Deadline", value=deadline)

                    is_noticed = await check_notice_deadline_activity(act)
                    now = get_datetime_now()
                    time_left = act.deadline - now

                    is_open_time_noticed = await check_notice_open_time_activity(act)
                    if act.open_time and act.open_time > now and not is_open_time_noticed:
                        # We don't wanna mentions everyone if the quiz isn't opened up yet
                        continue

                    if time_left.days == 0 and not is_noticed:
                        embeds.append((embed, act))
                        
            
            if embeds:
                # await self.channel.send(content="@everyone")

                for embed, act in embeds:
                    await self.channel.send(embed=embed)
                    await notice_deadline_activity(act)

        except Exception as e:
            self.notice_deadline_activity_error = e

    @loop(seconds=150)
    async def auth_renew(self):
        try:
            time_left = await get_session_time_remaining()

            if time_left <= 600:
                login_event.clear()

                await logout()
                await asyncio.sleep(3)
                await login()

                login_event.set()
        except Exception as e:
            self.auth_renew_error = e
        finally:
            login_event.set()

    async def ping(self, interaction: Interaction):
        is_logged_in = False
        time_remaining = None
        error = None
        try:
            time_remaining = await get_session_time_remaining()
        except Exception as e:
            error = e
        else:
            is_logged_in = True

        embed = Embed()
        embed.title = "Pong, i'm alive !!!"
        embed.add_field(
            name="Status task notice_new_activities",
            value=f"{self.notice_new_activities.is_running()}",
            inline=False
        )
        embed.add_field(
            name="Status task notice_open_time_activity",
            value=f"{self.notice_open_time_activity.is_running()}",
            inline=False,
        )
        embed.add_field(
            name="Status task notice_deadline_activity",
            value=f"{self.notice_deadline_activity.is_running()}",
            inline=False
        )
        embed.add_field(
            name="Status task auth_renew",
            value=f"{self.auth_renew.is_running()}",
            inline=False,
        )
        embed.add_field(
            name="Status task self_healing_tasks",
            value=f"{self.self_healing_tasks.is_running()}",
            inline=False
        )

        if is_logged_in:
            message_auth = f"{time_remaining / 60} minutes remaining\n"
            message_auth += f"{time_remaining} seconds remaining"
        else:
            message_auth = f"Failed to get current auth session, reason: {error}"

        embed.add_field(
            name="Auth session time remaining",
            value=message_auth,
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    async def errors_cmd(self, interaction: Interaction):
        embed = Embed()
        embed.title = "List of last errors for each tasks"

        def show_error(exc):
            if exc is None:
                return "No error"
            
            return f"{exc.__class__}: {exc}"

        embed.add_field(
            name="Task auth_renew",
            value=show_error(self.auth_renew_error),
            inline=False
        )
        embed.add_field(
            name="Task notice_new_activities",
            value=show_error(self.notice_new_activities_error),
            inline=False
        )
        embed.add_field(
            name="Task notice_deadline_activity",
            value=show_error(self.notice_deadline_activity_error),
            inline=False
        )
        embed.add_field(
            name="Task notice_open_time_activity",
            value=show_error(self.notice_open_time_activity_error),
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    async def _proc_relogin(self):
        try:
            await logout()
        except Exception as e:
            pass

        err = None
        try:
            await login()
        except Exception as e:
            err = e

        return err

    async def relogin_cmd(self, interaction: Interaction):
        send_message = interaction.response.send_message
        edit_message = interaction.edit_original_response
        await send_message("Trying relogin to vclass...")
        err = await self._proc_relogin()
        if err:
            await edit_message(content=f"Error when relogin: {err.__class__}: {err}")
        else:
            await edit_message(content="Succesfully relogin")

    async def _proc_heal_tasks(self, force=False):
        tasks = [
            self.auth_renew,
            self.notice_new_activities,
            self.notice_deadline_activity,
            self.notice_open_time_activity,
            self.self_healing_tasks
        ]

        for task in tasks:
            if not task.is_running():

                if task == self.notice_new_activities:
                    # ffs
                    try:
                        await self.notice_new_activities()
                    except Exception:
                        err = await self._proc_relogin()
                        if err:
                            raise err

                task.start()
            elif force:
                # Force restart
                task.restart()

    @loop(seconds=3)
    async def self_healing_tasks(self):
        try:
            await self._proc_heal_tasks()
        except Exception:
            pass

    async def restart_cmd(self, interaction: Interaction):
        send_message = interaction.response.send_message
        edit_message = interaction.edit_original_response
        await send_message("Restarting all tasks...")
        try:
            await self._proc_heal_tasks(force=True)
        except Exception as e:
            await edit_message(content=f"Error restarting tasks\n{e.__class__}: {e}")
            return

        await edit_message(content="All tasks are restarted, use ping command to check it")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cmd_tree = CommandTree(self)
        self.channel = None

        self.auth_renew_error = None
        self.notice_new_activities_error = None
        self.notice_deadline_activity_error = None
        self.notice_open_time_activity_error = None

    async def setup_hook(self) -> None:
        self.channel = await self.fetch_channel(channel_id)
        self.notice_deadline_activity.start()
        self.notice_open_time_activity.start()

        login_failed = False
        try:
            await login()
        except ServerDown:
            login_failed = True

        while login_failed:
            try:
                await login()
            except ServerDown:
                t = random.randrange(300, 500)
                time.sleep(t)
            else:
                login_failed = False

        login_event.set()
        self.auth_renew.start()

        # try:
        #     await self.notice_new_activities()
        # except Exception as e:
        #     # Fuck you
        #     pass

        self.notice_new_activities.start()

        # Ping command
        ping_command = Command(
            name="ping",
            description="Check if the bot is still alive or not",
            callback=self.ping
        )
        errors_command = Command(
            name="errors",
            description="Show last errors of each tasks",
            callback=self.errors_cmd
        )
        restart_command = Command(
            name="restart",
            description="Restart all tasks",
            callback=self.restart_cmd
        )
        relogin_command = Command(
            name="relogin",
            description="Relogin to vclass",
            callback=self.relogin_cmd
        )
        guild = await self.fetch_guild(guild_id)
        self.cmd_tree.add_command(ping_command, guild=guild)
        self.cmd_tree.add_command(errors_command, guild=guild)
        self.cmd_tree.add_command(restart_command, guild=guild)
        self.cmd_tree.add_command(relogin_command, guild=guild)
        self.cmd_tree.copy_global_to(guild=guild)
        await self.cmd_tree.sync(guild=guild)

        # Start self-healing tasks
        # because fuck gundar website ffs
        self.self_healing_tasks.start()

        print("[Bot] Ready")