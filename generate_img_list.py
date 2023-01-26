import json
from pathlib import Path

img_path = Path(__file__).parent / 'genshin_img'


img_list = {chara.name: [img.name for img in chara.iterdir()] for chara in img_path.iterdir()}

with open('genshin_img_list.json', 'w', encoding='utf-8') as f:
    json.dump(img_list, f, ensure_ascii=False, indent=2)
