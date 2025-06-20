# PDF→PNG変換ツール

シンプルで使いやすいPDFファイルをPNG画像に変換するデスクトップアプリケーションです。

## 概要
このアプリケーションは、複数のPDFファイルを一括でPNG画像に変換するためのツールです。ドラッグ＆ドロップに対応した直感的なインターフェースで、PDFの各ページを高品質なPNG画像として保存できます。

## 主な機能
- 複数PDFファイルの一括処理
- ドラッグ＆ドロップによるファイル選択
- 出力先フォルダの自動設定または手動指定
- 変換処理の進捗表示とキャンセル機能

## 技術仕様
- 言語: Python 3.8+
- GUI: Tkinter/tkinterdnd2
- PDF処理: PyMuPDF (fitz)
- ビルド: PyInstaller

## 動作環境
- Windows 10/11
- macOS 10.14以降
- Linux (GTK+環境)

## ライセンス
このプロジェクトは MIT ライセンスの下で公開されています。ただし、使用している各ライブラリには個別のライセンスが適用されます。詳細は [LICENSES.md](LICENSES.md) を参照してください。

## ドキュメント
詳しい使い方や設定方法については、[ユーザーマニュアル](https://phys-ken.github.io/pdf2png_myapp/docs/user-manual)を参照してください。

## リリース
実行可能ファイルは[GitHubリリースページ](https://github.com/phys-ken/pdf2png_myapp/releases)からダウンロードできます。

## 開発
コードに貢献する場合は、リポジトリをクローンして、必要なパッケージをインストールしてください。
```
pip install -r requirements.txt
```
