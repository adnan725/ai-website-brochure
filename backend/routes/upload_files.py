from flask import request, jsonify, Blueprint

from utils.helpers import process_uploaded_files

upload_files_blueprint = Blueprint("upload_files", __name__)

@upload_files_blueprint.route("/api/upload", methods=["POST"])
def upload_files():
    if "files" not in request.files:
        return jsonify({"error": "No files part in request"}), 400

    files = request.files.getlist("files")
    print(f"Received {len(files)} files for upload.")

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    # process incoming files
    process_uploaded_files(files)

    return jsonify({"message": f"Received {len(files)} files."}), 200

