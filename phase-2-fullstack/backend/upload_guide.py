"""
Upload backend code to Hugging Face Spaces
Run this script from the backend directory
"""

import os
from pathlib import Path

def get_file_content(filepath):
    """Read file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def generate_upload_commands():
    """Generate manual upload instructions."""
    src_path = Path('src')
    
    files_to_upload = []
    
    # Walk through src directory
    for root, dirs, files in os.walk(src_path):
        # Skip __pycache__ directories
        if '__pycache__' in root:
            continue
            
        for file in files:
            # Skip .pyc files
            if file.endswith('.pyc'):
                continue
                
            filepath = Path(root) / file
            rel_path = filepath.as_posix()
            files_to_upload.append(rel_path)
    
    print("=" * 80)
    print("HUGGING FACE SPACE - MANUAL UPLOAD GUIDE")
    print("=" * 80)
    print()
    print(f"Total files to upload: {len(files_to_upload)}")
    print()
    print("Go to: https://huggingface.co/spaces/AhmedKHI/todo-api-phase2")
    print()
    print("For each file below:")
    print("1. Click '+ Add file' → 'Create a new file'")
    print("2. Enter the filename exactly as shown")
    print("3. Copy-paste the content from your local file")
    print("4. Click 'Commit new file'")
    print()
    print("=" * 80)
    print()
    
    for i, filepath in enumerate(sorted(files_to_upload), 1):
        local_path = Path(filepath)
        print(f"\n{'=' * 80}")
        print(f"FILE #{i}/{len(files_to_upload)}")
        print(f"{'=' * 80}")
        print(f"Filename: {filepath}")
        print(f"Local path: {local_path.absolute()}")
        print()
        
        try:
            content = get_file_content(filepath)
            lines = len(content.splitlines())
            print(f"Content ({lines} lines):")
            print("-" * 80)
            print(content)
            print("-" * 80)
        except Exception as e:
            print(f"Error reading file: {e}")
    
    print("\n" + "=" * 80)
    print("UPLOAD COMPLETE!")
    print("After uploading all files, your Space will automatically rebuild")
    print("Check the 'Logs' tab to monitor the build progress")
    print("=" * 80)

if __name__ == "__main__":
    if not Path('src').exists():
        print("Error: src/ directory not found")
        print("Please run this script from the backend directory:")
        print("  cd backend")
        print("  python upload_guide.py")
    else:
        generate_upload_commands()
