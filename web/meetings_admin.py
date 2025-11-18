# web/meetings_admin.py
"""
Flask routes pro administraci schůzek
Poskytuje API a web interface pro správu schůzek a dostupnosti
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from database.meetings_db import MeetingsDB
from services.meeting_scheduler import MeetingScheduler
from datetime import datetime, timedelta

# Blueprint pro meetings
meetings_bp = Blueprint('meetings', __name__, url_prefix='/admin/meetings')

# Inicializace
db = MeetingsDB()
scheduler = MeetingScheduler()


@meetings_bp.route('/')
def dashboard():
    """Dashboard s přehledem schůzek"""
    # Získej statistiky
    stats = db.get_stats()
    
    # Nadcházející schůzky (7 dní)
    now = datetime.now()
    upcoming = db.get_meetings(
        status='scheduled',
        from_date=now.isoformat(),
        to_date=(now + timedelta(days=7)).isoformat()
    )
    
    # Blokované časy
    blocks = db.get_availability_blocks()
    
    return render_template('meetings_dashboard.html',
                         stats=stats,
                         upcoming=upcoming,
                         blocks=blocks)


@meetings_bp.route('/api/meetings', methods=['GET'])
def get_meetings():
    """API pro získání seznamu schůzek"""
    status = request.args.get('status')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    meetings = db.get_meetings(status=status, from_date=from_date, to_date=to_date)
    
    return jsonify({
        'success': True,
        'meetings': meetings
    })


@meetings_bp.route('/api/meetings/<int:meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    """API pro detail schůzky"""
    meeting = db.get_meeting(meeting_id)
    
    if not meeting:
        return jsonify({'success': False, 'error': 'Meeting not found'}), 404
    
    return jsonify({
        'success': True,
        'meeting': meeting
    })


@meetings_bp.route('/api/meetings', methods=['POST'])
def create_meeting():
    """API pro vytvoření nové schůzky"""
    data = request.json
    
    # Validace požadovaných polí
    required = ['contact_name', 'contact_phone', 'meeting_datetime']
    if not all(field in data for field in required):
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
    
    try:
        meeting_id = db.add_meeting(
            contact_name=data['contact_name'],
            contact_phone=data['contact_phone'],
            meeting_datetime=data['meeting_datetime'],
            location_type=data.get('location_type'),
            location_details=data.get('location_details'),
            followup_person=data.get('followup_person', 'Ondřej'),
            notes=data.get('notes'),
            call_sid=data.get('call_sid')
        )
        
        return jsonify({
            'success': True,
            'meeting_id': meeting_id
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meetings_bp.route('/api/meetings/<int:meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    """API pro aktualizaci schůzky"""
    data = request.json
    
    try:
        success = db.update_meeting(meeting_id, **data)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'error': 'Meeting not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meetings_bp.route('/api/meetings/<int:meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    """API pro smazání schůzky"""
    try:
        success = db.delete_meeting(meeting_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'error': 'Meeting not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meetings_bp.route('/api/check-availability', methods=['POST'])
def check_availability():
    """API pro kontrolu dostupnosti"""
    data = request.json
    
    if 'datetime' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing datetime field'
        }), 400
    
    result = scheduler.suggest_meeting_time(data['datetime'])
    
    return jsonify({
        'success': True,
        'result': result
    })


@meetings_bp.route('/api/availability-blocks', methods=['GET'])
def get_blocks():
    """API pro získání blokovaných časů"""
    date = request.args.get('date')
    blocks = db.get_availability_blocks(date=date)
    
    return jsonify({
        'success': True,
        'blocks': blocks
    })


@meetings_bp.route('/api/availability-blocks', methods=['POST'])
def create_block():
    """API pro vytvoření blokovaného času"""
    data = request.json
    
    # Validace požadovaných polí
    required = ['date', 'time_from', 'time_to']
    if not all(field in data for field in required):
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
    
    try:
        block_id = db.add_availability_block(
            date=data['date'],
            time_from=data['time_from'],
            time_to=data['time_to'],
            reason=data.get('reason', '')
        )
        
        return jsonify({
            'success': True,
            'block_id': block_id
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meetings_bp.route('/api/availability-blocks/<int:block_id>', methods=['DELETE'])
def delete_block(block_id):
    """API pro smazání blokovaného času"""
    try:
        success = db.delete_availability_block(block_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'error': 'Block not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@meetings_bp.route('/api/parse-time', methods=['POST'])
def parse_time():
    """API pro parsování času z textu"""
    data = request.json
    
    if 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing text field'
        }), 400
    
    parsed_time = scheduler.parse_time_from_text(data['text'])
    
    if parsed_time:
        formatted = scheduler.format_datetime_czech(parsed_time)
        return jsonify({
            'success': True,
            'datetime': parsed_time,
            'formatted': formatted
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Could not parse time from text'
        })


@meetings_bp.route('/calendar')
def calendar_view():
    """Kalendářní pohled"""
    # Získej schůzky na aktuální měsíc
    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0)
    
    # Konec měsíce
    if now.month == 12:
        end_of_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        end_of_month = now.replace(month=now.month + 1, day=1)
    
    meetings = db.get_meetings(
        from_date=start_of_month.isoformat(),
        to_date=end_of_month.isoformat()
    )
    
    blocks = db.get_availability_blocks()
    
    return render_template('calendar.html',
                         meetings=meetings,
                         blocks=blocks,
                         current_month=now.strftime('%Y-%m'))
