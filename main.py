import nextcord
import config
import os
import random
import json
from nextcord.ext import commands

intents = nextcord.Intents.all()
intents.members = True

#prefix is !
bot = commands.Bot(command_prefix='!', intents=intents)

#secret santa stuff
data = {}
switch = 0

#open json data file
@bot.event
async def on_ready():
    global data, switch
    print(f"hello it's {bot.user.name} {bot.user.id}")
    print("-----------------------------------------------------------")
    try:
        with open('data.json', 'r') as f:
            saved_data = json.load(f)
            data = saved_data['data']
            switch = saved_data['switch']
    except FileNotFoundError:
        data = {}
        switch = 0

#save json data file
@bot.event
async def on_disconnect():
    with open('data.json', 'w') as f:
        json.dump({'data': data, 'switch': switch}, f)

#commands

@bot.command(name='start')
async def santa(ctx):
    if ctx.message.author.id != 474464957195616258:
        await ctx.send("https://tenor.com/view/damwon-showmaker-gif-22451149")
        return
    await ctx.send("Secret Santa started, join with !me")
    global switch
    switch = 1

@bot.command(name='close')
async def santa(ctx):
    if ctx.message.author.id != 474464957195616258:
        await ctx.send("https://tenor.com/view/damwon-showmaker-gif-22451149")
        return
    await ctx.send("Secret Santa closed, reopen with !start")
    global switch
    switch = 0

@bot.command(name='me')
async def register(ctx):
    global switch
    if switch == 0:
        await ctx.send("Secret Santa has closed or not started")
    else:
        if str(ctx.author.id) in data:
            await ctx.send(f"{ctx.author.name} is already registered")
        else:
            data[str(ctx.author.id)] = {'name': ctx.author.name, 'wishlist': None, 'assigned': None}
            await ctx.send(f"Ok, {ctx.author.name} is now registered, please enter your !wishlist [items/likes/etc] (you can dm this command)")

@bot.command(name='wishlist')
async def wishlist(ctx, *, message):
    if str(ctx.author.id) in data:
        if message == "None":
            await ctx.send("incorrect usage: !wishlist [items/likes/etc] (you can dm this command)")
        else:
            data[str(ctx.author.id)]['wishlist'] = message
            await ctx.send(f"Ok, {ctx.author.name} has updated their wishlist")

        # Check if the user has an assigned Secret Santa
            if 'assigned' in data[str(ctx.author.id)]:
                # Fetch the Secret Santa's user object
                secret_santa = await bot.fetch_user(data[str(ctx.author.id)]['assigned'])
                # Send a DM to the Secret Santa with the updated wishlist
                await secret_santa.send(f"{ctx.author.name} has updated their wishlist to: {message}")
    else:
        await ctx.send(f"{ctx.author.name} is not registered, please register with !me")

@bot.command(name='clear')
async def clear(ctx):
    if ctx.message.author.id != 474464957195616258:
        await ctx.send("https://tenor.com/view/damwon-showmaker-gif-22451149")
        return
    global data
    data = {}
    await ctx.send("Data cleared")

@bot.command(name='unregister')
async def unregister(ctx):
    if ctx.author.id in data:
        del data[ctx.author.id]
        await ctx.send(f"{ctx.author.name} has been unregistered")
    else:
        await ctx.send(f"{ctx.author.name} is not registered")

@bot.command(name='people')
async def people(ctx):
    if data == {}: 
        await ctx.send("No one has registered yet")
    else:
        user_info = [f"{user_data['name']}: {user_data['wishlist']}" for user_data in data.values()]
        await ctx.send('```\n' + '\n'.join(user_info) + '\n```')

@bot.command(name='raffle')
#ask for confirmation
async def raffle(ctx):
    if ctx.message.author.id != 474464957195616258:
        await ctx.send("https://tenor.com/view/damwon-showmaker-gif-22451149")
        return
    global switch
    global data
    if switch == 0:
        await ctx.send("Secret Santa has closed or not started")
    else:
        if data == {}:
            await ctx.send("No one has registered yet")
        elif len(data) < 2:
            await ctx.send("Not enough people have registered")
        else:
            await ctx.send("Are you sure you want to start the raffle? (y/n)")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            msg = await bot.wait_for("message", check=check)
            if msg.content == "y":
                await ctx.send("Raffling... check dms")
                #assign the names to each other
                names = list(data.keys())
                random.shuffle(names)
                for i in range(len(names)):
                    data[names[i]]['assigned'] = names[(i + 1) % len(names)]

                #send the dms
                for user_id, user_data in data.items():
                    user = await bot.fetch_user(user_id)
                    await user.send(f"Your secret santa is {data[user_data['assigned']]['name']}")
                    await user.send(f"Their wishlist is {data[user_data['assigned']]['wishlist']}")
            else:
                await ctx.send("Raffle cancelled")

@bot.command(name='off')
async def off(ctx):
    if ctx.message.author.id == 474464957195616258:
        await ctx.send("good night")
    else:
        ctx.send("https://tenor.com/view/damwon-showmaker-gif-22451149")
    await bot.close()

@bot.command(name='remove')
async def remove(ctx, user_id: int):
    user_id = str(user_id)  # Convert user_id to string
    if ctx.message.author.id != 474464957195616258:
        await ctx.send("https://tenor.com/view/damwon-showmaker-gif-22451149")
        return
    if user_id in data:
        del data[user_id]
        await ctx.send(f"User {user_id} has been removed")
    else:
        await ctx.send(f"User {user_id} is not registered")

bot.run(config.TOKEN)