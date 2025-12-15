# Delta Rare Exe - Free Fire Emote Bot

## Overview
A Free Fire game bot with Telegram integration that sends emotes and manages game interactions. Features include a web-based control panel and shortcut system for easier emote management.

## Project Architecture
- **app.py** - Telegram Bot interface for commands
- **main.py** - Core Free Fire bot logic with TCP connections and web command queue consumer
- **web_server.py** - Flask web server for web-based emote control (Port 5000)
- **emote_shortcuts.py** - Emote shortcut configurations and mappings
- **command_queue.py** - File-based command queue for web-to-bot communication
- **templates/index.html** - Web UI control panel
- **xC4.py** - Utility functions
- **xHeaders.py** - HTTP headers and API functions

## Features
- Telegram bot commands for emotes
- Web-based control panel (Bengali/English)
- Emote shortcuts system (/p, /ak, /scar, etc.)
- Multiple UID support
- Auto-leave squad feature
- Evolution emotes (1-21)
- Dance party feature

## Workflows
1. **Telegram Bot** - `python app.py` - Telegram interface
2. **Web Control Panel** - `python web_server.py` - Web UI on port 5000

## Credits
All development credits: **Delta Rare Exe**

## Recent Changes
- Added web-based emote control panel
- Integrated emote shortcuts system from external repository
- Added command queue for web-to-bot communication
- Updated all credits to "Delta Rare Exe"
- **[Dec 12, 2025]** SIMPLIFIED EMOTE COMMANDS - Now use /lol uid, /hi uid, /rasengan uid directly!
- **[Dec 12, 2025]** Added /emotes command to show all available emote shortcuts
- **[Dec 12, 2025]** Added /emotes2 command for more emotes (page 2)
- **[Dec 12, 2025]** Added /help command with easy-to-understand help text
- **[Dec 12, 2025]** Fixed /s command conflict - now only responds to exact /s or /start
- **[Dec 12, 2025]** Added easy shortcut aliases: /hi, /bye, /clap, /love, /king, /money, /rich, /cry, /laugh, /kick, /punch, /jutsu, /l100, /max, /lambo, /toiletman
- **[Nov 26, 2025]** Added 430 emotes from ff-item.netlify.app (pages 1-6)
- **[Nov 26, 2025]** Updated emote_shortcuts.py with 300+ shortcut commands
- **[Nov 26, 2025]** Added new categories: Naruto, Demon Slayer, Premium, Frostfire, Blue Lock, and more
- **[Nov 26, 2025]** Added Group Invite feature in web control panel (4/5/6 player group invite by UID)
- **[Nov 26, 2025]** Redesigned UI with professional 2-tab interface: "Emote Send" and "Group Invite"
- **[Nov 26, 2025]** Added proper error handling and packet validation for group invites (OpEnSq, cHSq, SEnd_InV)
- **[Nov 27, 2025]** Fixed HWID not match issue in login system - now uses persistent browser-based HWID stored in localStorage
- **[Nov 27, 2025]** Made bot account configurable via secrets (BOT_UID and BOT_PASSWORD) instead of hardcoded values
- **[Nov 27, 2025]** Added separate account support for /spm_inv (SPM_INV_UID, SPM_INV_PASSWORD) and /lag (LAG_UID, LAG_PASSWORD) commands - these now use their own accounts and won't interfere with main bot operations
- **[Nov 27, 2025]** Added connection_pool.py for managing LAG and SPM account connections separately
- **[Nov 27, 2025]** Fixed Telegram Bot 409 Conflict issue - removed hardcoded token, using environment variable only
- **[Nov 27, 2025]** Added fallback mechanism - /lag and /spm_inv use pool accounts but fallback to main bot if unavailable
- **[Nov 27, 2025]** Fixed port 5000 conflict issue for Web Control Panel
- **[Nov 27, 2025]** Complete UI Redesign - Emote category section now more responsive and user-friendly:
  - Added horizontal scrolling category tabs for quick filtering
  - Collapsible accordion-style categories with emote count
  - Improved mobile responsiveness with touch-friendly buttons
  - Better visual hierarchy with gradient backgrounds
  - Sticky search bar for easy emote search
  - Improved emote cards with hover effects and selection states
  - Added "All" tab to show all emotes at once
- **[Nov 27, 2025]** Added Admin Password Login - Direct access without KeyAuth:
  - Admin tab in login form for direct password authentication
  - Bypass KeyAuth using environment variable ADMIN_PASSWORD
  - Default password: "admin123" (should be changed via secrets)
  - Set ADMIN_PASSWORD secret for production use
- **[Nov 27, 2025]** Synced ALL 430 Emotes to Website:
  - Organized into 7 categories by ID range
  - Basic Emotes (1-50): 50 emotes
  - Dance & Action (51-100): 50 emotes
  - Weapon & Combat (101-150): 50 emotes
  - Anime & Collab (151-200): 50 emotes
  - Holiday & Event (201-250): 50 emotes
  - Premium (251-300): 50 emotes
  - Extra Rare (301+): 130 emotes
  - All emote images reference: https://cdn.jsdelivr.net/gh/ShahGCreator/icon@main/PNG/
  - User can search/filter across all 430 emotes on website

## Emote Categories
- **Weapon Emotes**: /ak, /m10, /scar, /mp5, /groza, /thompson, /fist, /p90, /m60
- **Basic Emotes**: /hi, /bye, /lol, /clap, /love, /booyah, /king
- **Naruto Emotes**: /rasengan, /jutsu, /ninjarun, /clonejutsu, /fireballjutsu
- **Demon Slayer**: /thunderbreathing, /waterbreathing, /beastbreathing
- **Premium Emotes**: /l100, /max, /lambo, /prismaticflight, /bossenergy
- **Special Emotes**: /toiletman, /naatunaatu, /moonwalk, /flex, /twerk
