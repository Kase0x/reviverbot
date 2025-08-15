# Original work Copyright (c) 2022 Ray Nieport

import discord
# from rcon import rcon
from os import getenv, environ
from dotenv import load_dotenv
from json import load
import paramiko
import ast

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

if __name__ == "__main__":
    # Get environment variables
    load_dotenv()
    TOKEN = getenv('DISCORD_TOKEN')
    USER_ROLE = getenv('DISCORD_USER_ROLE')
    MOD_ROLE = getenv('DISCORD_MOD_ROLE')
    ADMIN_ROLE = getenv('DISCORD_ADMIN_ROLE')
    WOL_SERVER_IP = getenv('UBNT_IP')
    WOL_USERNAME = getenv('UBNT_USR')
    WOL_PASS = getenv('UBNT_PASS')
    UBNT_IP = getenv('UBNT_IP')
    UBNT_USR = getenv('UBNT_USR')
    UBNT_PASS = getenv('UBNT_PASS')
    ADMIN_USER = getenv('ADMIN_USER')
    ADMIN_PASS = getenv('ADMIN_PASS')
    macs = ast.literal_eval(environ["MACS"])
    BOT_LEVEL = getenv('BOT_LEVEL')
    if BOT_LEVEL == None: BOT_LEVEL = 1
    else: BOT_LEVEL = int(BOT_LEVEL) 

    # Get dictionary of commands
    with open('commands.json') as cmd_file:
        cmds = load(cmd_file)

    # Create help message
    Help = discord.Embed(description="A bot to bring life and death - from Discord!")
    Help.add_field(name='\u200b', value='-------------------------' + USER_ROLE + '-------------------------')
    for com in cmds['user_commands']:
        Help.add_field(name=com, value=cmds['user_commands'][com], inline=False)
    Help.add_field(name='\u200b', value='-------------------------' + MOD_ROLE + '-------------------------')
    for com in cmds['mod_commands']:
        Help.add_field(name=com, value=cmds['mod_commands'][com], inline=False)
    Help.add_field(name='\u200b', value='-------------------------' + ADMIN_ROLE + '-------------------------')
    for com in cmds['admin_commands']:
        Help.add_field(name=com, value=cmds['admin_commands'][com], inline=False)
    Help.add_field(name='admin', value='Runs a custom command. DON\'T USE.', inline=False)


async def send_server(cmd, args, message):
    try:   		
        if cmd.lower() == 'startserver':
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(UBNT_IP, username=UBNT_USR, password=UBNT_PASS)
            stdin, stdout, stderr = ssh.exec_command(f'curl -X POST -k -u {ADMIN_USER}:{ADMIN_PASS} https://172.17.17.247/api/atx/power?action=on')
            result = str(stdout.read())
            result = result.replace('b\'','')
            result = result.replace('\\n\'','')
            print(result)
            resp = f'[{message.author}]: Starting gameserver.'
            # print (resp)
        elif cmd.lower() == 'shutdownserver':
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(UBNT_IP, username=UBNT_USR, password=UBNT_PASS)
            stdin, stdout, stderr = ssh.exec_command(f'curl -X POST -k -u {ADMIN_USER}:{ADMIN_PASS} https://172.17.17.247/api/atx/power?action=off')
            result = str(stdout.read())
            result = result.replace('b\'','')
            result = result.replace('\\n\'','')
            print(result)
            resp = f'[{message.author}]: Shutting down gameserver.'
            # print (resp)
        elif args.lower() in macs:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(WOL_SERVER_IP, username=WOL_USERNAME, password=WOL_PASS)
            if args.lower() == 'kaseku':
                cmd_to_execute = f'wakeonlan -i 10.1.1.255 {macs[args.lower()]}'
                stdin, stdout, stderr = ssh.exec_command(cmd_to_execute)
            else:
                cmd_to_execute = f'wakeonlan -i 192.168.20.255 {macs[args.lower()]}'
                stdin, stdout, stderr = ssh.exec_command(cmd_to_execute)
            result = str(stdout.read())
            result = result.replace('b\'','')
            result = result.replace('\\n\'','')
            print (result) 
            resp = f'[{message.author}]: Sending wakeup packets to {args}\'s desktop.'
        elif args == '':
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(WOL_SERVER_IP, username=WOL_USERNAME, password=WOL_PASS)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            resp = str(stdout.read())
            resp = resp.replace('b\'','') 
            resp = resp.replace('\\n\'','')
            resp = f'[{message.author}]: {resp}'
        else:
            resp = f"[{message.author}]: {args} has not been setup for wakeonlan."
    except ValueError as err:
        resp = f'[{message.author}]: Connection from the bot to the server failed.'
        print(err.args)
    if resp:
        await message.channel.send(resp)
        print (f'{resp}')


# Process message when received
@client.event
async def on_message(message):
    
    if not message.content.startswith('>') or message.author == client.user:
        return

    # get command and arguments
    try:
        cmd, args = message.content[+1:].split(None, 1)
    except:
        cmd = message.content[+1:]
        args = ''

    # get author's clearance level
    authLevel = 0
    if message.author.bot == 1:
        authLevel = BOT_LEVEL
    else:
        for role in message.author.roles:
            # print(role.name,ADMIN_ROLE)
            if role.name == USER_ROLE: authLevel+=1
            if role.name == MOD_ROLE: authLevel+=2
            if role.name == ADMIN_ROLE: authLevel+=4
    # print (authLevel)
    # handle command
    if cmd == 'help':
        if authLevel >= 2:
            await message.channel.send(embed=Help)
            print (f'Helped out {message.author}.')
        else:
            await message.channel.send('You require greater authority to be blessed.')
            print (f'Denied help to {message.author}.')
    elif cmd == 'hi':
        await message.channel.send('Hello! I\'m the Revive bot!')
        print (f'Said hi to {message.author}.')
    elif cmd == 'admin':
        if authLevel >= 4:
            cmd = args
            args = ''
            await send_server(cmd, args, message)
        else:
            await message.channel.send('Sorry, you need the ' + ADMIN_ROLE + ' role to use that command.')
    elif cmd in cmds['user_commands']:
        if authLevel >= 1:
            await send_server(cmd, args, message)
        else:
            await message.channel.send('Sorry, you need the ' + USER_ROLE + ' role to use that command.')
    elif cmd in cmds['mod_commands']:
        if authLevel >= 2:
            await send_server(cmd, args, message)
        else:
            await message.channel.send('Sorry, you need the ' + MOD_ROLE + ' role to use that command.')
    elif cmd in cmds['admin_commands']:
        if authLevel >= 4:
            await send_server(cmd, args, message)
        else:
            await message.channel.send('Sorry, you need the ' + ADMIN_ROLE + ' role to use that command.')
    else:
        await message.channel.send('Invalid command.')


@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game(name="Type >help"))
client.run(TOKEN)
