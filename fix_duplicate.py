import os

base_dir = "d:/GIT/_fork/SpritePro/multiplayer_course"

def process_file(filepath):
    if not filepath.endswith('.py'):
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the duplicate s.multiplayer
    new_content = content.replace('s.multiplayer.s.multiplayer_ctx', 's.multiplayer_ctx')

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

for root, dirs, files in os.walk(base_dir):
    for filename in files:
        if filename.endswith(".py"):
            path = os.path.join(root, filename)
            process_file(path)

print("Fixed s.multiplayer.s.multiplayer_ctx!")
