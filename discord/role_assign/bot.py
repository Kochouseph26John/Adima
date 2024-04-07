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

BOT_TOKEN = decouple.config("BOT_TOKEN")
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
    discord_errors = 0
    unknown_error = 0
    already_assigned = 0
    unknown_member = 0

    for discord_id in ids:
        try:
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
                    already_assigned += 1
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
                unknown_member += 1
                print("Unknown, Failure")
            i += 1
        except discord.DiscordServerError as e:
            print(" EXCEPTION: Discord Server Error")
            failure.append({
                "id": discord_id,
                "name": "Unknown",
                "reason": "Discord Server Error"
            })
            discord_errors += 1
            continue
        except Exception as e:
            print(" EXCEPTION : Unknown")
            print("EXCEPTION:", e)
            failure.append({
                "id": discord_id,
                "name": "Unknown",
                "reason": "Unknown Exception"
            })
            unknown_error += 1
            continue

    with open("success.csv", "w") as f:
        f.write(pd.DataFrame(success).to_csv())
    with open("failure.csv", "w") as f:
        f.write(pd.DataFrame(failure).to_csv())

    print()
    print(f"-> {discord_errors} Discord Errors")
    print(f"-> {unknown_error} Unknown Errors")
    print(f"-> {already_assigned} Already Assigned")
    print(f"-> {unknown_member} Unknown Member")
    print(f"-> {success_count}/{total_count} Completed Successfully")
    print("DONE !")


client.run(BOT_TOKEN)
