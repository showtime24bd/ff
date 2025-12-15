from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from datetime import timedelta
import time
import json
import os
import re
from emote_shortcuts import BASE_EMOTES
from command_queue import command_queue
from simple_auth import SimpleAuth

def normalize_emote_shortcut(shortcut):
    """
    Normalize emote shortcut by removing spaces, special characters, 
    and converting to lowercase to match BASE_EMOTES keys.
    Examples:
    - "boss energy" -> "bossenergy"
    - "p90 surfer" -> "p90surfer"
    - "fire style: fireball jutsu" -> "firestylefireballjutsu"
    - "can't stop laughing" -> "cantstoplaughing"
    """
    normalized = shortcut.lower()
    normalized = re.sub(r'[^a-z0-9]', '', normalized)
    return normalized

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'delta-rare-exe-secret-key-2024')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)  # 1 year session
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
CORS(app, supports_credentials=True)

# Admin Password (Set this as environment variable or secret)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# SimpleAuth Configuration
simple_auth = SimpleAuth(db_file='auth_users.json')

@app.route('/')
def index():
    # Check if user is authenticated
    if not session.get('authenticated'):
        return render_template('login.html')
    return render_template('index.html')

@app.route('/admin')
def admin_panel():
    # Check if user is admin
    if not session.get('authenticated') or session.get('subscription') != 'admin':
        return render_template('login.html')
    return render_template('admin.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/keyauth/login', methods=['POST'])
def keyauth_login():
    """SimpleAuth login endpoint"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        hwid = data.get('hwid', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password required!'
            })
        
        if not hwid:
            return jsonify({
                'success': False,
                'message': 'Device ID required!'
            })
        
        print(f"[SimpleAuth] Login attempt - User: {username}, HWID: {hwid[:20]}...")
        
        success, result = simple_auth.login(username, password, hwid)
        
        if success:
            session.permanent = True  # Make session permanent (persist after browser close)
            session.modified = True  # Force session save
            session['authenticated'] = True
            session['username'] = result['username']
            session['subscription'] = result['subscription']
            session['session_id'] = result.get('session_id')
            session['hwid'] = hwid
            
            print(f"[SimpleAuth] ✅ Login successful - User: {username}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'user': result
            })
        else:
            print(f"[SimpleAuth] ❌ Login failed - User: {username}, Reason: {result}")
            return jsonify({
                'success': False,
                'message': result
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/keyauth/register', methods=['POST'])
def keyauth_register():
    """SimpleAuth register endpoint"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        hwid = data.get('hwid', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password required!'
            })
        
        if not hwid:
            return jsonify({
                'success': False,
                'message': 'Device ID required!'
            })
        
        print(f"[SimpleAuth] Register attempt - User: {username}, HWID: {hwid[:20]}...")
        
        success, result = simple_auth.register(username, password, hwid)
        
        if success:
            print(f"[SimpleAuth] ✅ Registration successful - User: {username}")
            return jsonify({
                'success': True,
                'message': 'Registration successful! You can now login.'
            })
        else:
            print(f"[SimpleAuth] ❌ Registration failed - User: {username}, Reason: {result}")
            return jsonify({
                'success': False,
                'message': result
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })



@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin password login endpoint - bypass KeyAuth"""
    try:
        data = request.json
        password = data.get('password', '').strip()
        
        if not password:
            return jsonify({
                'success': False,
                'message': 'Password required!'
            })
        
        if password == ADMIN_PASSWORD:
            session.permanent = True  # Make session permanent
            session.modified = True  # Force session save
            session['authenticated'] = True
            session['username'] = 'Admin'
            session['subscription'] = 'admin'
            
            print(f"[Admin] Successful admin login")
            
            return jsonify({
                'success': True,
                'message': 'Admin login successful!',
                'user': {'username': 'Admin', 'subscription': 'admin'}
            })
        else:
            print(f"[Admin] Failed admin login attempt")
            return jsonify({
                'success': False,
                'message': 'Invalid admin password!'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    """Admin endpoint to create new users (HWID auto-detected on first login)"""
    if not session.get('authenticated') or session.get('subscription') != 'admin':
        return jsonify({
            'success': False,
            'message': 'Unauthorized! Admin access required.'
        })
    
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password required!'
            })
        
        # Create user without HWID - it will be auto-detected on first login
        success, result = simple_auth.register(username, password, hwid=None)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'User {username} created successfully! Device will be registered on first login.'
            })
        else:
            return jsonify({
                'success': False,
                'message': result
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/admin/list_users', methods=['GET'])
def admin_list_users():
    """Admin endpoint to list all users"""
    if not session.get('authenticated') or session.get('subscription') != 'admin':
        return jsonify({
            'success': False,
            'message': 'Unauthorized! Admin access required.'
        })
    
    try:
        users_list = []
        for username, user_data in simple_auth.users.items():
            device_id = user_data.get('device_id')
            device_display = device_id[:20] + '...' if device_id else None
            
            users_list.append({
                'username': username,
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login'),
                'login_count': user_data.get('login_count', 0),
                'device_id': device_display
            })
        
        return jsonify({
            'success': True,
            'users': users_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/admin/delete_user', methods=['POST'])
def admin_delete_user():
    """Admin endpoint to delete users"""
    if not session.get('authenticated') or session.get('subscription') != 'admin':
        return jsonify({
            'success': False,
            'message': 'Unauthorized! Admin access required.'
        })
    
    try:
        data = request.json
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Username required!'
            })
        
        username = username.lower()
        
        if username not in simple_auth.users:
            return jsonify({
                'success': False,
                'message': 'User not found!'
            })
        
        del simple_auth.users[username]
        simple_auth.save_users()
        
        return jsonify({
            'success': True,
            'message': f'User {username} deleted successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/keyauth/logout', methods=['POST'])
def keyauth_logout():
    """Logout endpoint - clears session and removes from database"""
    session_id = session.get('session_id')
    
    # Delete session from database
    if session_id:
        simple_auth.delete_session(session_id)
        print(f"[SimpleAuth] Session deleted: {session_id[:20]}...")
    
    # Clear Flask session
    session.clear()
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully!'
    })

@app.route('/keyauth/check_session', methods=['GET'])
def check_session():
    """Check if user is authenticated"""
    if session.get('authenticated'):
        return jsonify({
            'success': True,
            'authenticated': True,
            'username': session.get('username'),
            'subscription': session.get('subscription')
        })
    else:
        return jsonify({
            'success': True,
            'authenticated': False
        })

@app.route('/emotes.json', methods=['GET'])
def get_emotes():
    try:
        with open('emotes.json', 'r') as f:
            emotes = json.load(f)
        return jsonify(emotes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send_emote', methods=['POST'])
def send_emote():
    try:
        data = request.json
        print(f"[WEB] Received data: {data}")
        
        teamcode = data.get('teamcode', '').strip()
        uids_raw = data.get('uids', '')
        auto_leave = data.get('auto_leave', True)
        
        # Handle both single emote and multiple emotes
        emotes_raw = data.get('emotes', [])  # New: array of emotes
        single_emote = data.get('emote', '')  # Old: single emote (backward compatibility)
        
        # Build emotes list
        emote_shortcuts = []
        if emotes_raw and isinstance(emotes_raw, list):
            emote_shortcuts = [e.strip() for e in emotes_raw if e.strip()]
        elif single_emote:
            emote_shortcuts = [single_emote.strip()]
        
        # Parse UIDs - can be comma-separated string or array
        uids = []
        if isinstance(uids_raw, str):
            uids = [uid.strip() for uid in uids_raw.split(',') if uid.strip()]
        elif isinstance(uids_raw, list):
            uids = [str(uid).strip() for uid in uids_raw if str(uid).strip()]
        
        print(f"[WEB] Parsed UIDs: {uids}")
        print(f"[WEB] Emotes to send: {emote_shortcuts}")
        
        if not teamcode:
            return jsonify({
                'success': False,
                'message': 'Team code is required!'
            })
        
        if not uids or len(uids) == 0:
            return jsonify({
                'success': False,
                'message': 'At least one UID is required!'
            })
        
        if not emote_shortcuts:
            return jsonify({
                'success': False,
                'message': 'At least one emote is required!'
            })
        
        if not teamcode.isdigit():
            return jsonify({
                'success': False,
                'message': 'Team code must be numeric!'
            })
        
        # Convert UIDs to integers
        uid_ints = []
        for uid in uids:
            try:
                uid_int = int(uid)
                uid_ints.append(uid_int)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid UID: {uid} (must be numeric)'
                })
        
        # Validate and normalize all emotes
        valid_emotes = []
        for emote_shortcut in emote_shortcuts:
            normalized_shortcut = normalize_emote_shortcut(emote_shortcut)
            print(f"[WEB] Original emote: '{emote_shortcut}' -> Normalized: '{normalized_shortcut}'")
            
            if normalized_shortcut not in BASE_EMOTES:
                return jsonify({
                    'success': False,
                    'message': f'Invalid emote shortcut: {emote_shortcut}'
                })
            
            emote_id = BASE_EMOTES[normalized_shortcut]
            valid_emotes.append({
                'shortcut': normalized_shortcut,
                'id': emote_id
            })
        
        # Send all emotes at once
        command_data = {
            'source': 'web',
            'type': 'multi_emote',
            'teamcode': teamcode,
            'uids': uid_ints,
            'emotes': valid_emotes,
            'auto_leave': auto_leave
        }
        
        print(f"[WEB] Sending multi-emote command: {command_data}")
        command_id = command_queue.add_command(command_data)
        
        max_wait = 10  # Increased timeout for multiple emotes
        start_time = time.time()
        response = None
        
        while (time.time() - start_time) < max_wait:
            response = command_queue.get_response(command_id)
            if response:
                break
            time.sleep(0.1)
        
        if response:
            leave_msg = " and left squad" if auto_leave else " (staying in squad)"
            emote_names = ', '.join([e['shortcut'].upper() for e in valid_emotes[:3]])
            if len(valid_emotes) > 3:
                emote_names += f' +{len(valid_emotes) - 3} more'
            return jsonify({
                'success': True,
                'message': f'Successfully sent {len(valid_emotes)} emotes ({emote_names}) to {len(uid_ints)} player(s){leave_msg}!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Request timeout. Please ensure the bot is running (python main.py)'
            })
        
    except Exception as e:
        print(f"[WEB] Error in send_emote: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        })

@app.route('/leave_squad', methods=['POST'])
def leave_squad():
    try:
        command_data = {
            'source': 'web',
            'type': 'leave'
        }
        
        command_id = command_queue.add_command(command_data)
        
        max_wait = 5
        start_time = time.time()
        response = None
        
        while (time.time() - start_time) < max_wait:
            response = command_queue.get_response(command_id)
            if response:
                break
            time.sleep(0.3)
        
        if response:
            return jsonify({
                'success': True,
                'message': 'Successfully left squad!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Request timeout or bot offline'
            })
        
    except Exception as e:
        print(f"[WEB] Error in leave_squad: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/send_group_invite', methods=['POST'])
def send_group_invite():
    """Send group invite to a UID - creates 4, 5, or 6 player group"""
    try:
        data = request.json
        print(f"[WEB] Group Invite - Received data: {data}")
        
        uid_raw = data.get('uid', '')
        uid = str(uid_raw).strip() if uid_raw is not None else ''
        group_size = int(data.get('group_size', 4))
        
        if not uid:
            return jsonify({
                'success': False,
                'message': 'UID is required!'
            })
        
        try:
            uid_int = int(uid)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'UID must be numeric!'
            })
        
        if group_size not in [4, 5, 6]:
            return jsonify({
                'success': False,
                'message': 'Group size must be 4, 5, or 6!'
            })
        
        command_data = {
            'source': 'web',
            'type': 'group_invite',
            'uid': uid_int,
            'group_size': group_size
        }
        
        print(f"[WEB] Sending group invite command: {command_data}")
        command_id = command_queue.add_command(command_data)
        
        max_wait = 10
        start_time = time.time()
        response = None
        
        while (time.time() - start_time) < max_wait:
            response = command_queue.get_response(command_id)
            if response:
                break
            time.sleep(0.5)
        
        if response:
            resp_data = response.get('response', response)
            if resp_data.get('status') == 'success':
                return jsonify({
                    'success': True,
                    'message': resp_data.get('message', f'Successfully sent {group_size}-player group invite to UID: {uid}!')
                })
            else:
                return jsonify({
                    'success': False,
                    'message': resp_data.get('message', 'Failed to send group invite')
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Request timeout. Please ensure the bot is running (python main.py)'
            })
        
    except Exception as e:
        print(f"[WEB] Error in send_group_invite: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        })

@app.route('/bot_status', methods=['GET'])
def bot_status():
    try:
        command_data = {
            'source': 'web',
            'type': 'status'
        }
        
        command_id = command_queue.add_command(command_data)
        
        max_wait = 3
        start_time = time.time()
        response = None
        
        while (time.time() - start_time) < max_wait:
            response = command_queue.get_response(command_id)
            if response:
                break
            time.sleep(0.2)
        
        if response:
            return jsonify({
                'success': True,
                'online': True,
                'message': 'Bot is online and ready'
            })
        else:
            return jsonify({
                'success': False,
                'online': False,
                'message': 'Bot is offline'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'online': False,
            'message': f'Error: {str(e)}'
        })

if __name__ == '__main__':
    print("[WEB] ==========================================")
    print("[WEB] Delta Rare Exe - Web Control Panel")
    print("[WEB] Starting web server on http://0.0.0.0:5000")
    print("[WEB] Make sure main bot is running: python main.py")
    print("[WEB] ==========================================")
    app.run(host='0.0.0.0', port=5000, debug=False)
