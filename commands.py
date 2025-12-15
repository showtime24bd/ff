import asyncio
import json
import random
import time
from dataclasses import dataclass
from typing import Any, Optional

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from xC4 import (
    GenJoinSquadsPacket,
    Emote_k,
    ExiT,
    OpEnSq,
    cHSq,
    SEnd_InV,
    CrEaTe_ProTo,
    GeneRaTePk,
)
from command_queue import command_queue
from emote_shortcuts import SHORTCUT_EMOTES, DEFAULT_PLAYER_UIDS, VARIANT_UIDS
from connection_pool import connection_pool


@dataclass
class BotContext:
    online_writer: Any
    whisper_writer: Any
    key: bytes
    iv: bytes
    region: str


EMOTE_MAP = {
    1: 909000063,
    2: 909000081,
    3: 909000075,
    4: 909000085,
    5: 909000134,
    6: 909000098,
    7: 909035007,
    8: 909051012,
    9: 909000141,
    10: 909034008,
    11: 909051015,
    12: 909041002,
    13: 909039004,
    14: 909042008,
    15: 909051014,
    16: 909039012,
    17: 909040010,
    18: 909035010,
    19: 909041005,
    20: 909051003,
    21: 909034001
}


def load_emotes_from_json():
    try:
        with open('emotes.json', 'r') as f:
            emotes_data = json.load(f)
        emotes_map = {}
        for emote in emotes_data:
            if emote['Number'] != 'no':
                emotes_map[emote['Number']] = int(emote['Id'])
        return emotes_map
    except Exception as e:
        print(f"Error loading emotes.json: {e}")
        return {}


GENERAL_EMOTES_MAP = load_emotes_from_json()


async def send_packet(ctx: BotContext, packet_type: str, packet: bytes) -> bool:
    try:
        if packet_type == 'ChaT' and ctx.whisper_writer:
            ctx.whisper_writer.write(packet)
            await ctx.whisper_writer.drain()
            return True
        elif packet_type == 'OnLine' and ctx.online_writer:
            ctx.online_writer.write(packet)
            await ctx.online_writer.drain()
            return True
        return False
    except Exception as e:
        print(f"Error sending packet: {e}")
        return False


def dec_to_hex(decimal):
    hex_str = hex(decimal)[2:]
    return hex_str.upper() if len(hex_str) % 2 == 0 else '0' + hex_str.upper()


async def encrypt_packet(packet_hex: str, key: bytes, iv: bytes) -> str:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    packet_bytes = bytes.fromhex(packet_hex)
    padded_packet = pad(packet_bytes, AES.block_size)
    encrypted = cipher.encrypt(padded_packet)
    return encrypted.hex()


async def nmnmmmmn(packet_hex: str, key: bytes, iv: bytes) -> str:
    return await encrypt_packet(packet_hex, key, iv)


async def ghost_join_packet(player_id, secret_code, key: bytes, iv: bytes):
    try:
        # Ghost Join Packet - Proper structure for invisible join
        fields = {
            1: 3,  # Action type: JOIN (not spectate)
            2: {
                1: int(player_id),
                2: {
                    1: int(player_id),
                    2: int(time.time()),
                    3: "MR3SKR",
                    5: 12,
                    6: 9999999,
                    7: 1,
                    8: {
                        2: 1,
                        3: 1,
                    },
                    9: 3,
                },
                3: secret_code,
                4: 1,  # Join mode
                5: 0,  # Hide from lobby
            }
        }

        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        return await GeneRaTePk(packet_hex, '0515', key, iv)

    except Exception as e:
        print(f"Error creating ghost join packet: {e}")
        return None


async def r_command_operation(ctx: BotContext, team_code: str, target_uid: str, emote_id: int):
    try:
        join_packet = await GenJoinSquadsPacket(team_code, ctx.key, ctx.iv)
        await send_packet(ctx, 'OnLine', join_packet)
        await asyncio.sleep(1.2)

        uid_int = int(target_uid)
        emote_packet = await Emote_k(uid_int, int(emote_id), ctx.key, ctx.iv, ctx.region)
        await send_packet(ctx, 'OnLine', emote_packet)
        await asyncio.sleep(0.5)

        leave_packet = await ExiT(None, ctx.key, ctx.iv)
        await send_packet(ctx, 'OnLine', leave_packet)
        await asyncio.sleep(0.5)

        return True, f"✅ SUCCESS! Joined team {team_code}, sent emote ID {emote_id} to {target_uid}, and left (Total: ~2.2s)"

    except Exception as e:
        return False, f"Error in /r command: {str(e)}"


async def flash_ghost_emote(ctx: BotContext, team_code: str, target_uids: list, emote_id: int):
    try:
        join_packet = await GenJoinSquadsPacket(team_code, ctx.key, ctx.iv)
        await send_packet(ctx, 'OnLine', join_packet)

        for uid in target_uids:
            try:
                uid_int = int(uid)
                emote_packet = await Emote_k(uid_int, emote_id, ctx.key, ctx.iv, ctx.region)
                await send_packet(ctx, 'OnLine', emote_packet)
            except:
                pass

        await asyncio.sleep(0.1)
        leave_packet = await ExiT(None, ctx.key, ctx.iv)
        await send_packet(ctx, 'OnLine', leave_packet)

        return True, "Flash ghost complete!"
    except Exception as e:
        return False, str(e)


async def lag_team_loop(ctx: BotContext, team_code: str, lag_running_ref: list):
    count = 0
    start_time = asyncio.get_event_loop().time()
    
    lag_bot = connection_pool.get_lag_bot()
    use_main_bot = False
    
    if not lag_bot:
        print(f"[LAG] No LAG account in pool, using MAIN BOT for lag attack!")
        use_main_bot = True
        if not ctx.online_writer:
            print(f"[LAG] Main bot not connected!")
            return
    else:
        print(f"[LAG] Using pooled account {lag_bot.uid}! Starting ULTRA FAST lag attack on team: {team_code}")
    
    if use_main_bot:
        join_packet = await GenJoinSquadsPacket(team_code, ctx.key, ctx.iv)
        leave_packet = await ExiT(None, ctx.key, ctx.iv)
    else:
        join_packet = await GenJoinSquadsPacket(team_code, lag_bot.key, lag_bot.iv)
        leave_packet = await ExiT(None, lag_bot.key, lag_bot.iv)
    
    try:
        while lag_running_ref[0]:
            try:
                elapsed_time = asyncio.get_event_loop().time() - start_time
                if elapsed_time >= 8.0:
                    print(f"[LAG] Attack completed after 8 seconds ({count} cycles)")
                    lag_running_ref[0] = False
                    break

                if use_main_bot:
                    await send_packet(ctx, 'OnLine', join_packet)
                    await asyncio.sleep(0.02)
                    await send_packet(ctx, 'OnLine', leave_packet)
                else:
                    await lag_bot.send_packet(join_packet)
                    await asyncio.sleep(0.02)
                    await lag_bot.send_packet(leave_packet)

                count += 1
                if count % 20 == 0:
                    mode = "MAIN BOT" if use_main_bot else "POOL"
                    print(f"[LAG] ⚡ {mode} #{count} cycles on {team_code}")

                await asyncio.sleep(0.03)

            except Exception as e:
                print(f"[LAG] Error in lag loop: {e}")
                await asyncio.sleep(0.05)
        
        print(f"[LAG] ✅ Completed! {count} ULTRA FAST cycles on team {team_code}")
        
    except Exception as e:
        print(f"[LAG] Error: {e}")


async def general_emote_spam(ctx: BotContext, uids: list, emote_number: str):
    try:
        emote_id = GENERAL_EMOTES_MAP.get(str(emote_number))
        if not emote_id:
            return False, f"Invalid emote number! Use numbers from 1-{len(GENERAL_EMOTES_MAP)}"

        success_count = 0
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, emote_id, ctx.key, ctx.iv, ctx.region)
                await send_packet(ctx, 'OnLine', H)
                success_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error sending general emote to {uid}: {e}")

        return True, f"Sent emote {emote_number} (ID: {emote_id}) to {success_count} player(s)"

    except Exception as e:
        return False, f"Error in general_emote_spam: {str(e)}"


async def random_evo_emote_spam_sender(ctx: BotContext, target_uid: int):
    try:
        emote_ids = list(EMOTE_MAP.values())
        random.shuffle(emote_ids)

        success_count = 0
        total_emotes = len(emote_ids)

        for emote_id in emote_ids:
            try:
                uid_int = int(target_uid)
                H = await Emote_k(uid_int, emote_id, ctx.key, ctx.iv, ctx.region)
                await send_packet(ctx, 'OnLine', H)
                success_count += 1

                emote_number = [k for k, v in EMOTE_MAP.items() if v == emote_id][0]
                print(f"Random: Sent evolution emote {emote_number} (ID: {emote_id}) to command sender {target_uid} - {success_count}/{total_emotes}")

                await asyncio.sleep(2.5)
            except Exception as e:
                print(f"Error sending emote {emote_id} to command sender: {e}")

        return True, f"Successfully sent {success_count}/21 evolution emotes in random order to you! (2.5s delay)"

    except Exception as e:
        return False, f"Error in random_evo_emote_spam_sender: {str(e)}"


async def dance_group_emotes(ctx: BotContext, uids: list):
    try:
        emote_ids = list(EMOTE_MAP.values())
        random.shuffle(emote_ids)

        success_count = 0
        total_emotes = len(emote_ids)

        print(f"Dance: Sending to {len(uids)} players: {uids}")

        for emote_id in emote_ids:
            try:
                emote_sent_count = 0
                for member_uid in uids:
                    try:
                        uid_int = int(member_uid)
                        H = await Emote_k(uid_int, emote_id, ctx.key, ctx.iv, ctx.region)
                        await send_packet(ctx, 'OnLine', H)
                        emote_sent_count += 1
                        print(f"Dance: Sent emote to UID {member_uid}")
                    except Exception as e:
                        print(f"Error sending to UID {member_uid}: {e}")

                success_count += 1

                emote_number = [k for k, v in EMOTE_MAP.items() if v == emote_id][0]
                print(f"Dance: Sent evolution emote {emote_number} (ID: {emote_id}) to {emote_sent_count} players - {success_count}/{total_emotes}")

                await asyncio.sleep(2.5)
            except Exception as e:
                print(f"Error sending dance emote {emote_id} to group: {e}")

        return True, f"🎉 Ultimate dance party! Sent ALL {success_count} evolution emotes (1-21) to {len(uids)} players! (2.5s delay)"

    except Exception as e:
        return False, f"Error in dance_group_emotes: {str(e)}"


async def process_web_command(ctx: BotContext, cmd_data: dict):
    try:
        cmd_type = cmd_data.get('type')
        cmd_id = cmd_data.get('id')

        # Check if bot is connected
        if not ctx.online_writer:
            command_queue.add_response(cmd_id, {
                'status': 'connecting',
                'message': 'Bot is still connecting, please wait...'
            })
            return False

        if cmd_type == 'status':
            command_queue.add_response(cmd_id, {
                'status': 'online',
                'message': 'Bot is online and ready'
            })
            return True

        elif cmd_type == 'emote':
            teamcode = cmd_data.get('teamcode')
            uids = cmd_data.get('uids', [])
            emote_id = cmd_data.get('emote_id')
            auto_leave = cmd_data.get('auto_leave', True)

            if not teamcode or not uids or not emote_id:
                command_queue.add_response(cmd_id, {
                    'status': 'error',
                    'message': 'Missing required fields'
                })
                return False

            join_packet = await GenJoinSquadsPacket(teamcode, ctx.key, ctx.iv)
            await send_packet(ctx, 'OnLine', join_packet)
            await asyncio.sleep(1)

            async def send_emote_to_uid(uid, eid):
                try:
                    uid_int = int(uid)
                    emote_packet = await Emote_k(uid_int, int(eid), ctx.key, ctx.iv, ctx.region)
                    await send_packet(ctx, 'OnLine', emote_packet)
                    return True
                except Exception as e:
                    print(f"[WEB] Error sending emote to {uid}: {e}")
                    return False

            results = await asyncio.gather(*[send_emote_to_uid(uid, emote_id) for uid in uids])
            success_count = sum(1 for r in results if r)

            if auto_leave:
                await asyncio.sleep(0.5)
                leave_packet = await ExiT(None, ctx.key, ctx.iv)
                await send_packet(ctx, 'OnLine', leave_packet)

            command_queue.add_response(
                cmd_id, {
                    'status': 'success',
                    'message': f'Emote sent to {success_count} player(s) simultaneously'
                })
            print(f"[WEB] Sent emote {emote_id} to {success_count} players SIMULTANEOUSLY in team {teamcode}")
            return True

        elif cmd_type == 'multi_emote':
            teamcode = cmd_data.get('teamcode')
            uids = cmd_data.get('uids', [])
            emotes = cmd_data.get('emotes', [])
            auto_leave = cmd_data.get('auto_leave', True)

            if not teamcode or not uids or not emotes:
                command_queue.add_response(cmd_id, {
                    'status': 'error',
                    'message': 'Missing required fields'
                })
                return False

            join_packet = await GenJoinSquadsPacket(teamcode, ctx.key, ctx.iv)
            await send_packet(ctx, 'OnLine', join_packet)
            await asyncio.sleep(1)

            total_success = 0
            
            for emote_data in emotes:
                emote_id = emote_data.get('id')
                
                async def send_to_uid(uid, eid):
                    try:
                        uid_int = int(uid)
                        emote_packet = await Emote_k(uid_int, int(eid), ctx.key, ctx.iv, ctx.region)
                        await send_packet(ctx, 'OnLine', emote_packet)
                        return True
                    except Exception as e:
                        print(f"[WEB] Error sending emote to {uid}: {e}")
                        return False
                
                results = await asyncio.gather(*[send_to_uid(uid, emote_id) for uid in uids])
                total_success += sum(1 for r in results if r)
                
                if len(emotes) > 1:
                    await asyncio.sleep(0.3)

            if auto_leave:
                await asyncio.sleep(0.5)
                leave_packet = await ExiT(None, ctx.key, ctx.iv)
                await send_packet(ctx, 'OnLine', leave_packet)

            command_queue.add_response(
                cmd_id, {
                    'status': 'success',
                    'message': f'Sent {len(emotes)} emotes to {len(uids)} player(s) simultaneously'
                })
            print(f"[WEB] Sent {len(emotes)} emotes to {len(uids)} players SIMULTANEOUSLY in team {teamcode}")
            return True

        elif cmd_type == 'leave':
            leave_packet = await ExiT(None, ctx.key, ctx.iv)
            await send_packet(ctx, 'OnLine', leave_packet)
            command_queue.add_response(cmd_id, {
                'status': 'success',
                'message': 'Left squad'
            })
            print("[WEB] Left squad")
            return True

        elif cmd_type == 'group_invite':
            uid = cmd_data.get('uid')
            group_size = cmd_data.get('group_size', 4)

            if uid is None or uid == '':
                command_queue.add_response(cmd_id, {
                    'status': 'error',
                    'message': 'UID is required'
                })
                return False

            if group_size not in [4, 5, 6]:
                command_queue.add_response(
                    cmd_id, {
                        'status': 'error',
                        'message': 'Group size must be 4, 5, or 6'
                    })
                return False

            try:
                uid_int = int(uid)

                PAc = await OpEnSq(ctx.key, ctx.iv, ctx.region)
                if not PAc:
                    command_queue.add_response(
                        cmd_id, {
                            'status': 'error',
                            'message': 'Failed to create squad packet'
                        })
                    return False
                await send_packet(ctx, 'OnLine', PAc)
                await asyncio.sleep(0.3)

                C = await cHSq(group_size, uid_int, ctx.key, ctx.iv, ctx.region)
                if not C:
                    command_queue.add_response(
                        cmd_id, {
                            'status': 'error',
                            'message': 'Failed to create group packet'
                        })
                    return False
                await send_packet(ctx, 'OnLine', C)
                await asyncio.sleep(0.3)

                V = await SEnd_InV(group_size, uid_int, ctx.key, ctx.iv, ctx.region)
                if not V:
                    command_queue.add_response(
                        cmd_id, {
                            'status': 'error',
                            'message': 'Failed to create invite packet'
                        })
                    return False
                await send_packet(ctx, 'OnLine', V)
                await asyncio.sleep(0.3)

                E = await ExiT(None, ctx.key, ctx.iv)
                await asyncio.sleep(2)
                if E:
                    await send_packet(ctx, 'OnLine', E)

                command_queue.add_response(
                    cmd_id, {
                        'status': 'success',
                        'message': f'{group_size}-player group invite sent to UID {uid}'
                    })
                print(f"[WEB] Sent {group_size}-player group invite to UID: {uid}")
                return True

            except ValueError:
                command_queue.add_response(
                    cmd_id, {
                        'status': 'error',
                        'message': 'Invalid UID format - must be numeric'
                    })
                return False
            except Exception as e:
                print(f"[WEB] Error sending group invite: {e}")
                command_queue.add_response(
                    cmd_id, {
                        'status': 'error',
                        'message': 'Failed to send group invite. Please try again.'
                    })
                return False

        return False

    except Exception as e:
        print(f"[WEB] Error processing command: {e}")
        if cmd_data.get('id'):
            command_queue.add_response(cmd_data['id'], {
                'status': 'error',
                'message': str(e)
            })
        return False


async def web_command_consumer(ctx: BotContext):
    print("[WEB] Web command consumer started - Delta Rare Exe")
    while True:
        try:
            cmd = command_queue.get_command()
            if cmd:
                print(f"[WEB] Processing command: {cmd.get('type')}")
                await process_web_command(ctx, cmd)
            command_queue.clear_old_responses()
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"[WEB] Consumer error: {e}")
            await asyncio.sleep(1)
