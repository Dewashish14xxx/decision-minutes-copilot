"""Decision-Minutes Copilot - API Routes"""
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
import uuid
import os
import time

from .services.transcription import transcribe_audio
from .services.extraction import extract_action_items

bp = Blueprint('main', __name__)

# In-memory job storage (use Redis/DB in production)
jobs = {}

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'webm', 'ogg', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
def index():
    """Serve the main UI."""
    return render_template('index.html')


@bp.route('/upload', methods=['POST'])
def upload_audio():
    """Upload audio file and start processing."""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save file
    filename = secure_filename(f"{job_id}_{file.filename}")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Initialize job
    jobs[job_id] = {
        'status': 'uploaded',
        'filepath': filepath,
        'filename': file.filename,
        'created_at': time.time(),
        'transcript': None,
        'results': None,
        'confirmed': False,
        'error': None
    }
    
    return jsonify({
        'job_id': job_id,
        'status': 'uploaded',
        'message': 'File uploaded successfully. Call /process to start.'
    })


@bp.route('/process/<job_id>', methods=['POST'])
def process_audio(job_id):
    """Process the uploaded audio file."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job['status'] not in ['uploaded', 'error']:
        return jsonify({'error': f"Cannot process job in status: {job['status']}"}), 400
    
    try:
        # Step 1: Transcribe audio
        job['status'] = 'transcribing'
        transcript = transcribe_audio(job['filepath'])
        job['transcript'] = transcript
        
        # Step 2: Extract action items
        job['status'] = 'extracting'
        results = extract_action_items(transcript)
        job['results'] = results
        
        # Done
        job['status'] = 'completed'
        
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'transcript': transcript,
            'results': results
        })
        
    except Exception as e:
        job['status'] = 'error'
        job['error'] = str(e)
        return jsonify({'error': str(e)}), 500


@bp.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get job status."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'filename': job['filename'],
        'confirmed': job['confirmed'],
        'error': job['error']
    })


@bp.route('/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """Get processing results."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': f"Results not ready. Status: {job['status']}"}), 400
    
    return jsonify({
        'job_id': job_id,
        'transcript': job['transcript'],
        'results': job['results'],
        'confirmed': job['confirmed']
    })


@bp.route('/confirm/<job_id>', methods=['POST'])
def confirm_results(job_id):
    """Confirm and optionally update results."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    # Allow updating results
    data = request.get_json()
    if data and 'results' in data:
        job['results'] = data['results']
    
    job['confirmed'] = True
    
    return jsonify({
        'job_id': job_id,
        'status': 'confirmed',
        'results': job['results']
    })


@bp.route('/export/<job_id>', methods=['GET'])
def export_results(job_id):
    """Export results as markdown."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if not job['results']:
        return jsonify({'error': 'No results to export'}), 400
    
    results = job['results']
    
    # Generate markdown
    md = f"# Meeting Minutes\n\n"
    md += f"**File:** {job['filename']}\n\n"
    
    if results.get('summary'):
        md += f"## Summary\n{results['summary']}\n\n"
    
    if results.get('decisions'):
        md += "## Decisions\n"
        for i, d in enumerate(results['decisions'], 1):
            md += f"{i}. {d['description']}\n"
        md += "\n"
    
    if results.get('action_items'):
        md += "## Action Items\n"
        md += "| # | Action | Owner | Deadline | Confidence |\n"
        md += "|---|--------|-------|----------|------------|\n"
        for i, item in enumerate(results['action_items'], 1):
            owner = item.get('owner', '-') or '-'
            deadline = item.get('deadline', '-') or '-'
            conf = f"{item.get('confidence', 0) * 100:.0f}%"
            md += f"| {i} | {item['description']} | {owner} | {deadline} | {conf} |\n"
    
    return jsonify({'markdown': md, 'filename': job['filename']})
