"""
Assign role to a give users
"""
import decouple
import pandas as pd
import discord

intents = discord.Intents(
    guilds=True,
    members=True,
    bans=True,
    emojis=True,
    voice_states=True,
    messages=True,
    reactions=True,
    message_content=True,
)

client = discord.Client(intents=intents)

ROLE = 'Pathway'  # Change Role Here
TARGET_FILE = 'data.csv'

@client.event
async def on_ready():
    print("Bot Ready!")
    await process_data()


async def process_data():
    print("-> Started processing ...")
    success = []
    failure = []
    data = pd.read_csv(TARGET_FILE)
    ids = data.get('discord_id')
    if ids is None:
        print("-> ERROR : discord_id column not found on csv")
        return
    guild = client.guilds[0]
    if guild is None:
        print("-> ERROR : No guild found")
        return
    role = discord.utils.get(guild.roles, name=ROLE)
    if role is None:
        print(f"-> ERROR : Role '{ROLE}' not found on discord")
        return
    i = 1
    success_count = 0
    total_count = len(ids)
    for discord_id in ids:
        print(f"\t{i})", discord_id, end=', ')
        if member := guild.get_member(discord_id):
            member_role = discord.utils.get(member.roles, name=ROLE)
            print(member.name, end=', ')
            if member_role is not None:
                failure.append(
                    {
                        "id": discord_id,
                        "name": member.name,
                        "reason": "Role already assigned"
                    }
                )
                print("Failure")
            else:
                res = await member.add_roles(role)
                print("Role added", end=", ")
                success.append({
                    "id": discord_id,
                    "name": member.name,
                    "payload": str(res)
                })
                success_count += 1
                print("Success")
        else:
            failure.append({
                "id": discord_id,
                "name": "Unknown",
                "reason": "Member not found"
            })
            print("Unknown, Failure")
        i += 1
    with open("success.csv", "w") as f:
        f.write(pd.DataFrame(success).to_csv())
    with open("failure.csv", "w") as f:
        f.write(pd.DataFrame(failure).to_csv())
    print(f"-> {success_count} / {total_count} Completed Successfully")
    print("DONE !")


client.run(decouple.config("BOT_TOKEN"))
