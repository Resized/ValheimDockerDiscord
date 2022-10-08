import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import docker

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
STATUS_PATH = os.getenv('STATUS_PATH')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
client = docker.from_env()

container_list = client.containers.list(filters={'name': 'valheim-server'}, all=True)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def start(ctx):
    await server(ctx, 'start')


@bot.command()
async def stop(ctx):
    await server(ctx, 'stop')


@bot.command()
async def restart(ctx):
    await server(ctx, 'restart')


@bot.command()
async def status(ctx):
    container_list[0].reload()
    f = open(STATUS_PATH + '\status.json', "r")
    status_json = json.loads(f.read())
    f.close()
    if container_list[0].status == 'exited':
        await ctx.send(f"Server is offline!")
    else:
        if status_json['server_name']:
            await ctx.send(f"Docker container: {container_list[0].status}\nServer \"{status_json['server_name']}\" is online!")
        else:
            await ctx.send(f"Docker container: {container_list[0].status}\nServer is online!")


async def server(ctx, command):
    if command == 'start':
        if container_list[0].status == 'exited':
            container_list[0].start()
            container_list[0].reload()
            await ctx.send("Server Started!")
        else:
            await ctx.send("Server is already running!")
    if command == 'stop':
        if container_list[0].status == 'running':
            container_list[0].stop()
            container_list[0].reload()
            await ctx.send("Server Stopped!")
        else:
            await ctx.send("Server is already stopped!")
    if command == 'restart':
        if container_list[0].status == 'running':
            container_list[0].restart()
            container_list[0].reload()
            await ctx.send("Server Restarted!")
        else:
            await ctx.send("Server is not running!")


bot.run(BOT_TOKEN)
