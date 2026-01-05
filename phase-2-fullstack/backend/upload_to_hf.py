"""Upload all source files to Hugging Face Space"""

from huggingface_hub import HfApi
import os
from pathlib import Path
import sys

# Get token from user
print("=" * 80)
print("HUGGING FACE SPACE UPLOADER")
print("=" * 80)
print()
print("You need a Hugging Face access token with WRITE permissions.")
print("Get one at: https://huggingface.co/settings/tokens")
print()
token = input("Paste your HF token here (starts with hf_...): ").strip()

if not token or not token.startswith("hf_"):
    print("\nError: Invalid token. Must start with 'hf_'")
    sys.exit(1)

# Initialize API with token
api = HfApi(token=token)

# Space details
repo_id = "AhmedKHI/todo-api-phase2"
repo_type = "space"

print("=" * 80)
print("UPLOADING TO HUGGING FACE SPACE")
print("=" * 80)
print(f"Space: {repo_id}")
print()

# Get all Python files in src/
src_files = []
for root, dirs, files in os.walk('src'):
    # Skip __pycache__
    if '__pycache__' in root:
        continue
    for file in files:
        # Skip .pyc files
        if file.endswith('.pyc'):
            continue
        filepath = os.path.join(root, file)
        src_files.append(filepath)

print(f"Found {len(src_files)} files to upload")
print()

# Upload each file
for i, filepath in enumerate(sorted(src_files), 1):
    rel_path = Path(filepath).as_posix()
    print(f"[{i}/{len(src_files)}] Uploading: {rel_path}")
    
    try:
        api.upload_file(
            path_or_fileobj=filepath,
            path_in_repo=rel_path,
            repo_id=repo_id,
            repo_type=repo_type,
            commit_message=f"Add {rel_path}"
        )
        print(f"  ✓ Success")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print()
print("=" * 80)
print("UPLOAD COMPLETE!")
print("=" * 80)
print()
print("Next steps:")
print("1. Go to: https://huggingface.co/spaces/AhmedKHI/todo-api-phase2")
print("2. Click 'Logs' tab to watch build")
print("3. Wait 3-5 minutes for build to complete")
print("4. Test: https://ahmedkhi-todo-api-phase2.hf.space/health")
