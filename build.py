import PyInstaller.__main__
import os
import shutil

# アセットディレクトリの作成
if not os.path.exists('assets'):
    os.makedirs('assets')

# ビルド前のクリーンアップ
for dir_name in ['build', 'dist']:
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

# PyInstallerの実行
PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=PDF2PNG_Converter',
    '--add-data=assets;assets',
    '--hidden-import=tkinterdnd2',
    '--hidden-import=fitz',
    '--hidden-import=PIL',
    '--clean',
])

print("ビルドが完了しました！")
print("実行ファイルは 'dist/PDF2PNG_Converter.exe' にあります。")
