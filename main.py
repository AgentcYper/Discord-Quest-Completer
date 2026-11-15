import os
import sys
import time
import json
import random
import base64
from datetime import datetime, timezone
import requests

try:
    from curl_cffi import requests as c_requests
except ImportError:
    c_requests = None

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

if os.name == "nt":
    import ctypes
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004 | 0x0008)
        kernel32.SetConsoleTitleW("Soar Team - Quest Solver")
    except Exception:
        pass
    os.system("chcp 65001 >nul")

BLUE = "\033[34m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = rf"""{BLUE}{BOLD}
  ███████╗ ██████╗  █████╗ ██████╗     ████████╗███████╗ █████╗ ███╗   ███╗
  ██╔════╝██╔═══██╗██╔══██╗██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
  ███████╗██║   ██║███████║██████╔╝       ██║   █████╗  ███████║██╔████╔██║
  ╚════██║██║   ██║██╔══██║██╔══██╗       ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║
  ███████║╚██████╔╝██║  ██║██║  ██║       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
  ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝{RESET}
"""

SUPPORTED_TASKS = [
    "WATCH_VIDEO",
    "WATCH_VIDEO_ON_MOBILE",
    "PLAY_ON_DESKTOP",
    "STREAM_ON_DESKTOP",
    "PLAY_ACTIVITY"
]

PAGE_SIZE = 5

def create_session():
    s = requests.Session()
    s.trust_env = False
    return s

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def generate_headers(token: str, is_mobile: bool = False) -> dict:
    if is_mobile:
        super_props = {
            "os": "iOS",
            "browser": "Discord iOS",
            "device": "iPhone16,2",
            "system_locale": "en-US",
            "client_version": "270.0",
            "os_version": "18.2",
            "os_arch": "arm64",
            "system_os_arch": "arm64",
            "browser_user_agent": "Discord/270.0 (iPhone; iOS 18.2; Scale/3.00)",
            "browser_version": "270.0",
            "release_channel": "stable",
            "client_build_number": 71520,
            "client_event_source": None
        }
    else:
        super_props = {
            "os": "Windows",
            "browser": "Discord Client",
            "release_channel": "stable",
            "client_version": "1.0.9186",
            "os_version": "10.0.22631",
            "os_arch": "x64",
            "app_arch": "x64",
            "system_locale": "en-US",
            "has_client_mods": False,
            "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9186 Chrome/134.0.6998.89 Electron/34.3.0 Safari/537.36",
            "browser_version": "34.3.0",
            "client_build_number": 518420,
            "native_build_number": 59498,
            "client_event_source": None
        }

    sp_json = json.dumps(super_props, separators=(",", ":"))
    sp_b64 = base64.b64encode(sp_json.encode("utf-8")).decode("utf-8")

    return {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": token,
        "Content-Type": "application/json",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/quest-home",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": super_props["browser_user_agent"],
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "UTC",
        "X-Super-Properties": sp_b64
    }

def get_quest_task(quest: dict):
    if not isinstance(quest, dict):
        return None
    try:
        cfg = quest.get("config") or {}
        task_cfg = (
            cfg.get("task_config_v2")
            or cfg.get("taskConfigV2")
            or cfg.get("task_config")
            or cfg.get("taskConfig")
            or quest.get("task_config_v2")
            or quest.get("task_config")
            or {}
        )
        tasks = task_cfg.get("tasks") if isinstance(task_cfg, dict) else None

        if isinstance(tasks, dict):
            for name in SUPPORTED_TASKS:
                if name in tasks:
                    t = tasks[name]
                    target = 0
                    apps = []
                    if isinstance(t, dict):
                        target = t.get("target") or t.get("target_seconds") or 0
                        apps = t.get("applications") or []
                    elif isinstance(t, (int, float)):
                        target = t
                    return {
                        "type": name,
                        "target": int(target) if target else 900,
                        "applications": apps
                    }
            for k, t in tasks.items():
                target = 0
                apps = []
                if isinstance(t, dict):
                    target = t.get("target") or t.get("target_seconds") or 0
                    apps = t.get("applications") or []
                elif isinstance(t, (int, float)):
                    target = t
                return {
                    "type": str(k),
                    "target": int(target) if target else 900,
                    "applications": apps
                }

        elif isinstance(tasks, list):
            for item in tasks:
                if isinstance(item, dict):
                    t_type = item.get("type") or item.get("name") or "PLAY_ON_DESKTOP"
                    target = item.get("target") or item.get("target_seconds") or 0
                    apps = item.get("applications") or []
                    return {
                        "type": str(t_type),
                        "target": int(target) if target else 900,
                        "applications": apps
                    }

        app = cfg.get("application") or {}
        app_id = app.get("id") or quest.get("application_id")
        return {
            "type": "PLAY_ON_DESKTOP",
            "target": 900,
            "applications": [{"id": app_id}] if app_id else []
        }
    except Exception:
        return {
            "type": "PLAY_ON_DESKTOP",
            "target": 900,
            "applications": []
        }

def get_quest_progress(quest: dict, task_type: str) -> float:
    if not isinstance(quest, dict):
        return 0.0
    u_stat = quest.get("user_status") or {}
    prog_obj = u_stat.get("progress") or {}
    if isinstance(prog_obj, dict) and task_type in prog_obj:
        val = prog_obj[task_type].get("value") if isinstance(prog_obj[task_type], dict) else prog_obj[task_type]
        if isinstance(val, (int, float)):
            return float(val)
    if isinstance(u_stat.get("stream_progress_seconds"), (int, float)):
        return float(u_stat["stream_progress_seconds"])
    return 0.0

def get_quest_name(quest: dict) -> str:
    if not isinstance(quest, dict):
        return "Unknown Quest"
    cfg = quest.get("config") or {}
    msgs = cfg.get("messages") or {}
    app = cfg.get("application") or {}
    name = (
        msgs.get("quest_name")
        or msgs.get("game_title")
        or app.get("name")
        or f"Quest {quest.get('id', 'Unknown')}"
    )
    return str(name)

def get_quest_orbs(quest: dict) -> str:
    if not isinstance(quest, dict):
        return get_quest_name(quest)
    cfg = quest.get("config") or {}
    rew_cfg = cfg.get("rewards_config") or {}
    rewards = rew_cfg.get("rewards") or cfg.get("rewards") or []
    if isinstance(rewards, list):
        for r in rewards:
            if isinstance(r, dict) and r.get("type") in [1, 2, "orb", "ORBS"]:
                msgs = r.get("messages") or {}
                name = msgs.get("name") or msgs.get("reward_name")
                if name:
                    return str(name)
    return get_quest_name(quest)

def is_quest_completed(quest: dict) -> bool:
    if not isinstance(quest, dict):
        return False
    u_stat = quest.get("user_status") or {}
    if u_stat.get("completed_at"):
        return True
    task = get_quest_task(quest)
    if not task:
        return False
    target = task.get("target", 0) if isinstance(task, dict) else 0
    t_type = task.get("type", "PLAY_ON_DESKTOP") if isinstance(task, dict) else "PLAY_ON_DESKTOP"
    current = get_quest_progress(quest, t_type)
    return target > 0 and current >= target

def verify_token(session, token: str):
    headers = generate_headers(token, False)
    try:
        res = session.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json()
        if c_requests:
            c_sess = c_requests.Session(impersonate="chrome124")
            res2 = c_sess.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=15)
            if res2.status_code == 200:
                return res2.json()
        return None
    except Exception:
        return None

def fetch_quests(session, token: str):
    headers = generate_headers(token, False)
    raw_quests = []

    urls = [
        "https://discord.com/api/v9/quests/@me",
        "https://discord.com/api/v10/quests/@me"
    ]

    for url in urls:
        try:
            res = session.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, dict):
                    q_list = data.get("quests") or []
                    ex_list = data.get("excluded_quests") or []
                    if isinstance(q_list, list) and len(q_list) > 0:
                        raw_quests = q_list
                        break
                    elif isinstance(ex_list, list) and len(ex_list) > 0:
                        raw_quests = ex_list
                        break
                    elif isinstance(q_list, list):
                        raw_quests = q_list
                        break
                elif isinstance(data, list):
                    raw_quests = data
                    break
        except Exception:
            pass

    if not raw_quests and c_requests:
        try:
            c_sess = c_requests.Session(impersonate="chrome124")
            for url in urls:
                res = c_sess.get(url, headers=headers, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    if isinstance(data, dict):
                        q_list = data.get("quests") or []
                        ex_list = data.get("excluded_quests") or []
                        if isinstance(q_list, list) and len(q_list) > 0:
                            raw_quests = q_list
                            break
                        elif isinstance(ex_list, list) and len(ex_list) > 0:
                            raw_quests = ex_list
                            break
                        elif isinstance(q_list, list):
                            raw_quests = q_list
                            break
                    elif isinstance(data, list):
                        raw_quests = data
                        break
        except Exception:
            pass

    valid = []
    for q in raw_quests:
        if isinstance(q, dict):
            task = get_quest_task(q)
            if task:
                valid.append(q)

    try:
        valid.sort(key=lambda x: 1 if is_quest_completed(x) else 0)
    except Exception:
        pass
    return valid

def enroll_quest(session, token: str, quest: dict):
    if not isinstance(quest, dict):
        return False
    u_stat = quest.get("user_status") or {}
    if u_stat.get("enrolled_at"):
        return True
    headers = generate_headers(token, False)
    q_id = quest.get("id")
    if not q_id:
        return False
    for url in [
        f"https://discord.com/api/v9/quests/{q_id}/enroll",
        f"https://discord.com/api/v10/quests/{q_id}/enroll"
    ]:
        try:
            res = session.post(
                url,
                json={"location": 11, "is_targeted": False, "metadata_raw": None},
                headers=headers,
                timeout=15
            )
            if res.status_code in [200, 204]:
                if not isinstance(quest.get("user_status"), dict):
                    quest["user_status"] = {}
                quest["user_status"]["enrolled_at"] = datetime.now(timezone.utc).isoformat()
                return True
        except Exception:
            pass
    return False

def print_progress(quest_name: str, pct: int, current: float, target: float, remaining_sec: float):
    bar_size = 20
    filled = int((pct / 100) * bar_size)
    empty = bar_size - filled
    bar = f"[{'█' * filled}{'░' * empty}]"
    mins = int(remaining_sec // 60)
    secs = int(remaining_sec % 60)
    time_str = f"{mins:02d}:{secs:02d}"
    clean_name = quest_name[:24].ljust(24)
    cur_str = f"{int(current):4d}"
    tar_str = f"{int(target):<4d}"

    sys.stdout.write(
        f"\r  {WHITE}{clean_name}{RESET} {BLUE}{bar}{RESET} {WHITE}{pct:3d}%{RESET} [{cur_str}/{tar_str}s] {WHITE}Remaining: {time_str}{RESET}   "
    )
    sys.stdout.flush()

def solve_single_quest(session, token: str, quest: dict) -> bool:
    name = get_quest_name(quest)
    task = get_quest_task(quest)
    if not task:
        print(f"  {BLUE}[-]{RESET} {WHITE}Quest {name} has no supported tasks{RESET}")
        return False

    task_type = task["type"]
    target = task["target"]
    current = get_quest_progress(quest, task_type)

    print(f"\n  {BLUE}[*]{RESET} {WHITE}Solving quest: {name}{RESET}")

    enroll_quest(session, token, quest)

    if task_type in ["WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE"]:
        is_mobile = task_type == "WATCH_VIDEO_ON_MOBILE"
        headers = generate_headers(token, is_mobile)

        while current < target:
            step = random.randint(7, 12) + random.random()
            next_ts = min(target, current + step)

            res = session.post(
                f"https://discord.com/api/v9/quests/{quest['id']}/video-progress",
                json={"timestamp": next_ts},
                headers=headers,
                timeout=15
            )
            data = res.json() if res.status_code == 200 else {}

            current = next_ts
            if not isinstance(quest.get("user_status"), dict):
                quest["user_status"] = {}
            if not isinstance(quest["user_status"].get("progress"), dict):
                quest["user_status"]["progress"] = {}
            quest["user_status"]["progress"][task_type] = {"value": current}

            pct = min(100, int((current / target) * 100)) if target > 0 else 100
            rem = max(0, target - current)
            print_progress(name, pct, current, target, rem)

            if (isinstance(data, dict) and data.get("completed_at")) or current >= target:
                quest["user_status"]["completed_at"] = (data.get("completed_at") if isinstance(data, dict) else None) or datetime.now(timezone.utc).isoformat()
                break

            time.sleep(2.5)

        print()
        print(f"  {BLUE}[+]{RESET} {WHITE}Successfully completed quest: {name}{RESET}")
        return True
    else:
        headers = generate_headers(token, False)
        cfg = quest.get("config") or {}
        app = cfg.get("application") or {}
        app_id = (
            app.get("id")
            or (task["applications"][0].get("id") if (task.get("applications") and isinstance(task["applications"][0], dict)) else None)
            or quest.get("id")
        )

        stream_key = f"call:{quest.get('id', '0')}:{random.randint(100000, 999999)}"

        while current < target:
            res = session.post(
                f"https://discord.com/api/v9/quests/{quest['id']}/heartbeat",
                json={"stream_key": stream_key, "application_id": app_id, "terminal": False},
                headers=headers,
                timeout=15
            )
            data = res.json() if res.status_code == 200 else {}
            if not isinstance(data, dict):
                data = {}

            prog = data.get("progress") or {}
            task_prog = prog.get(task_type) or {}
            server_prog = (
                task_prog.get("value")
                or data.get("stream_progress_seconds")
                or (current + 20)
            )
            current = min(target, max(current + 15, server_prog))

            if not isinstance(quest.get("user_status"), dict):
                quest["user_status"] = {}
            if not isinstance(quest["user_status"].get("progress"), dict):
                quest["user_status"]["progress"] = {}
            quest["user_status"]["progress"][task_type] = {"value": current}

            pct = min(100, int((current / target) * 100)) if target > 0 else 100
            rem = max(0, target - current)
            print_progress(name, pct, current, target, rem)

            if data.get("completed_at") or current >= target:
                quest["user_status"]["completed_at"] = data.get("completed_at") or datetime.now(timezone.utc).isoformat()
                break

            time.sleep(20)

        try:
            session.post(
                f"https://discord.com/api/v9/quests/{quest['id']}/heartbeat",
                json={"stream_key": stream_key, "application_id": app_id, "terminal": True},
                headers=headers,
                timeout=15
            )
        except Exception:
            pass

        print()
        print(f"  {BLUE}[+]{RESET} {WHITE}Successfully completed quest: {name}{RESET}")
        return True

def prompt_token(session):
    saved_token = ""
    bot_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "quest-bot", "config.json")
    local_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    for cfg_p in [local_cfg_path, bot_cfg_path]:
        if os.path.exists(cfg_p):
            try:
                with open(cfg_p, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    tok = cfg.get("token", "").strip()
                    if tok and tok != "توكن البوت":
                        saved_token = tok
                        break
            except Exception:
                pass

    while True:
        token_input = input(f"  {WHITE}{BOLD}Enter account token: {RESET}").strip().strip('"').strip("'")
        if not token_input and saved_token:
            token_input = saved_token

        if not token_input:
            continue

        print(f"  {BLUE}[*]{RESET} {WHITE}Verifying token...{RESET}")
        user_data = verify_token(session, token_input)
        if user_data:
            tag = (
                f"{user_data.get('username', 'User')}#{user_data.get('discriminator', '0')}"
                if user_data.get("discriminator") and str(user_data["discriminator"]) != "0"
                else str(user_data.get("username", "User"))
            )
            print(f"  {BLUE}[+]{RESET} {WHITE}Successfully logged in as: {tag}{RESET}")
            time.sleep(1)
            return token_input, user_data
        else:
            print(f"  {BLUE}[-]{RESET} {WHITE}Invalid or expired token. Please try again.{RESET}")

def main():
    session = create_session()
    clear_screen()
    print(BANNER)

    token, user_data = prompt_token(session)
    page_idx = 0

    while True:
        clear_screen()
        print(BANNER)

        tag = (
            f"{user_data.get('username', 'User')}#{user_data.get('discriminator', '0')}"
            if user_data.get("discriminator") and str(user_data["discriminator"]) != "0"
            else str(user_data.get("username", "User"))
        )

        quests = fetch_quests(session, token)
        total_quests = len(quests)

        if total_quests == 0:
            print(f"\n  {BLUE}[!]{RESET} {WHITE}No available quests found at this time{RESET}")
            print(f"  {BLUE}[*]{RESET} {WHITE}Ensure your account has active quests in Discord User Settings{RESET}")
            print(f"\n  {BLUE}[{WHITE}r{BLUE}]{RESET} {WHITE}Refresh | {BLUE}[{WHITE}t{BLUE}]{RESET} {WHITE}Change Token | {BLUE}[{WHITE}exit{BLUE}]{RESET} {WHITE}Exit{RESET}")
            cmd = input(f"\n  {BLUE}{BOLD}Soar-Team>{RESET} ").strip().lower()
            if cmd in ["exit", "quit", "q"]:
                print(f"  {WHITE}Exiting. Thank you for using Soar Team!{RESET}")
                break
            elif cmd in ["t", "token"]:
                token, user_data = prompt_token(session)
                page_idx = 0
            continue

        total_pages = max(1, (total_quests + PAGE_SIZE - 1) // PAGE_SIZE)
        if page_idx >= total_pages:
            page_idx = total_pages - 1
        if page_idx < 0:
            page_idx = 0

        uncompleted_count = sum(1 for q in quests if not is_quest_completed(q))

        print("  " + f"{BLUE}{'═' * 70}{RESET}")
        print(f"  {WHITE}{BOLD}Account:{RESET} {BLUE}{tag}{RESET} {WHITE}| Total Quests: {total_quests} | Remaining: {uncompleted_count} | Page: {page_idx + 1} of {total_pages}{RESET}")
        print("  " + f"{BLUE}{'═' * 70}{RESET}")

        start_idx = page_idx * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total_quests)
        page_quests = quests[start_idx:end_idx]

        for i, q in enumerate(page_quests):
            local_num = i + 1
            name = get_quest_name(q)[:28].ljust(28)
            orbs = get_quest_orbs(q)[:10].ljust(10)
            task = get_quest_task(q) or {"type": "PLAY_ON_DESKTOP", "target": 900, "applications": []}
            completed = is_quest_completed(q)

            if completed:
                status_badge = f"{BLUE}[COMPLETED]{RESET}"
            else:
                target = task.get("target", 0)
                current = get_quest_progress(q, task.get("type", "PLAY_ON_DESKTOP"))
                pct = min(100, int((current / target) * 100)) if target > 0 else 0
                status_badge = f"{WHITE}[INCOMPLETE {pct}%] [{int(current)}/{target}s]{RESET}"

            print(f"  {BLUE}[{WHITE}{local_num}{BLUE}]{RESET} {WHITE}{name}{RESET} | {BLUE}{orbs}{RESET} | {status_badge}")

        print("  " + f"{BLUE}{'═' * 70}{RESET}")
        print(f"  {WHITE}{BOLD}Available Commands:{RESET}")
        print(f"  {BLUE}[{WHITE}1-{len(page_quests)}{BLUE}]{RESET} {WHITE}Solve quest from current page{RESET}")
        print(f"  {BLUE}[{WHITE}all{BLUE}]{RESET} {WHITE}Solve all remaining quests{RESET}")
        if total_pages > 1:
            print(f"  {BLUE}[{WHITE}next{BLUE}]{RESET} {WHITE}Next page            {BLUE}[{WHITE}prev{BLUE}]{RESET} {WHITE}Previous page{RESET}")
        print(f"  {BLUE}[{WHITE}token{BLUE}]{RESET} {WHITE}Change token         {BLUE}[{WHITE}cls{BLUE}]{RESET} {WHITE}Clear screen{RESET}")
        print(f"  {BLUE}[{WHITE}r{BLUE}]{RESET} {WHITE}Refresh list         {BLUE}[{WHITE}exit{BLUE}]{RESET} {WHITE}Exit tool{RESET}")
        print("  " + f"{BLUE}{'═' * 70}{RESET}")

        raw_cmd = input(f"  {BLUE}{BOLD}Soar-Team>{RESET} ").strip()
        cmd = raw_cmd.lower()

        if cmd in ["exit", "quit", "q"]:
            print(f"\n  {WHITE}Exiting. Thank you for using Soar Team!{RESET}\n")
            break
        elif cmd in ["cls", "clear"]:
            clear_screen()
        elif cmd in ["r", "refresh"]:
            continue
        elif cmd in ["token", "t"]:
            token, user_data = prompt_token(session)
            page_idx = 0
            continue
        elif cmd in ["next", "n"] and total_pages > 1:
            if page_idx < total_pages - 1:
                page_idx += 1
            else:
                page_idx = 0
        elif cmd in ["prev", "p"] and total_pages > 1:
            if page_idx > 0:
                page_idx -= 1
            else:
                page_idx = total_pages - 1
        elif cmd in ["all", "a"]:
            uncompleted = [q for q in quests if not is_quest_completed(q)]
            if not uncompleted:
                print(f"\n  {BLUE}[+]{RESET} {WHITE}All quests are already completed!{RESET}")
                input(f"  {WHITE}Press Enter to return to menu...{RESET}")
                continue

            print(f"\n  {BLUE}[*]{RESET} {WHITE}Starting to solve {len(uncompleted)} quests...{RESET}")
            for idx, quest in enumerate(uncompleted):
                print(f"\n  {BLUE}{'─' * 50}{RESET}")
                print(f"  {WHITE}[{idx + 1}/{len(uncompleted)}] Processing: {get_quest_name(quest)}{RESET}")
                print(f"  {BLUE}{'─' * 50}{RESET}")
                try:
                    solve_single_quest(session, token, quest)
                except Exception as e:
                    print(f"  {BLUE}[-]{RESET} {WHITE}Error solving quest {get_quest_name(quest)}: {e}{RESET}")
                time.sleep(2)

            print(f"\n  {BLUE}[+]{RESET} {WHITE}All remaining quests completed!{RESET}")
            input(f"\n  {WHITE}Press Enter to return to menu...{RESET}")
        elif cmd.isdigit():
            num = int(cmd)
            if 1 <= num <= len(page_quests):
                selected_quest = page_quests[num - 1]
                if is_quest_completed(selected_quest):
                    print(f"\n  {BLUE}[+]{RESET} {WHITE}Quest is already completed!{RESET}")
                    input(f"  {WHITE}Press Enter to return to menu...{RESET}")
                    continue

                try:
                    solve_single_quest(session, token, selected_quest)
                except Exception as e:
                    print(f"  {BLUE}[-]{RESET} {WHITE}Error solving quest: {e}{RESET}")

                input(f"\n  {WHITE}Press Enter to return to menu...{RESET}")
            else:
                print(f"  {BLUE}[!]{RESET} {WHITE}Invalid quest number. Please choose 1-{len(page_quests)}{RESET}")
                time.sleep(1)
        else:
            print(f"  {BLUE}[!]{RESET} {WHITE}Unknown command. Please try again.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print(f"\n  {WHITE}Exiting. Thank you for using Soar Team!{RESET}\n")
    except Exception as e:
        print(f"\n  {BLUE}[-]{RESET} {WHITE}Unexpected error: {e}{RESET}\n")
