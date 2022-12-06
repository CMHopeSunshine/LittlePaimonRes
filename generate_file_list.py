import hashlib
import json
from pathlib import Path

font_path = Path(__file__).parent / 'fonts'
res_path = Path(__file__).parent / 'LittlePaimon'
img_path = Path(__file__).parent / 'genshin_img'

exclude_path = ['avatar', 'avatar_side', 'talent', 'weapon', 'splash', 'results', 'material', 'other', 'furniture']
unlock_list = ['general']

emoticons_temp = []

file_list = [{
    'path': f'{file.parent.name}/{file.name}',
    'hash': hashlib.md5(file.read_bytes()).hexdigest(),
    'lock': True
} for file in font_path.iterdir()]

this_path = str(Path().absolute())

for file in res_path.rglob('*'):
    if not file.is_file():
        continue
    if file.parent.name not in exclude_path:
        if file.parent.name.startswith('emoticons'):
            if file.name.split('-')[0] in emoticons_temp:
                continue
            else:
                emoticons_temp.append(file.name.split('-')[0])
        if file.parent.name.startswith('artifact') and file.name.startswith('UI'):
            continue
        file_list.append({
            'path': str(file).replace(this_path, '').replace('\\', '/').lstrip('/'),
            'hash': hashlib.md5(file.read_bytes()).hexdigest(),
            'lock': False if file.parent.name in unlock_list else True
        })

with open('resources_list.json', 'w', encoding='utf-8') as f:
    json.dump(file_list, f, ensure_ascii=False, indent=2)


img_list = {chara.name: [img.name for img in chara.iterdir()] for chara in img_path.iterdir()}

with open('genshin_img_list.json', 'w', encoding='utf-8') as f:
    json.dump(img_list, f, ensure_ascii=False, indent=2)
