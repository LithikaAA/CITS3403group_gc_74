from flask import Blueprint, render_template, request, redirect, url_for
from flask import flash

# Create a blueprint for upload routes
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            flash("No file selected. Please choose a file to upload.")
            return redirect(url_for('upload.upload'))

        # Logic to save file goes here

        flash("Upload successful!")  # <- ✅ Do this here
        return redirect(url_for('dashboard.dashboard'))

    return render_template('upload.html')