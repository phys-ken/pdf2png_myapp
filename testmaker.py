import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def create_test_pdfs():
    """テスト用PDFファイルを作成する関数"""
    # testpdfフォルダの作成
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testpdf")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"フォルダを作成しました: {test_dir}")
    
    # 作成するPDFファイル名
    file_names = ["a", "b", "c"]
    
    # 各ファイルごとに異なるページ数を設定
    pages_per_file = {
        "a": 3,
        "b": 5,
        "c": 4
    }
    
    for file_name in file_names:
        pdf_path = os.path.join(test_dir, f"{file_name}.pdf")
        
        # PDFキャンバスの作成
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # ページ数
        num_pages = pages_per_file[file_name]
        
        for page in range(1, num_pages + 1):
            # テキスト作成（例: a001, a002, ...）
            text = f"{file_name}{page:03d}"
            
            # 大きなフォントでページの中央にテキストを描画
            c.setFont("Helvetica-Bold", 36)
            c.drawCentredString(width/2, height/2, text)
            
            # ファイル情報を追加
            c.setFont("Helvetica", 12)
            c.drawString(2*cm, height - 2*cm, f"ファイル: {file_name}.pdf")
            c.drawString(2*cm, height - 2.5*cm, f"ページ: {page}/{num_pages}")
            
            # 四隅に識別用のマーカーを追加
            c.setFont("Helvetica", 10)
            c.drawString(1*cm, 1*cm, text + " (左下)")
            c.drawString(width - 4*cm, 1*cm, text + " (右下)")
            c.drawString(1*cm, height - 1*cm, text + " (左上)")
            c.drawString(width - 4*cm, height - 1*cm, text + " (右上)")
            
            # ページを確定して次のページに移る
            c.showPage()
        
        # PDFを保存
        c.save()
        print(f"作成しました: {pdf_path} ({num_pages}ページ)")

if __name__ == "__main__":
    # reportlabがインストールされているか確認
    try:
        import reportlab
        create_test_pdfs()
        print("すべてのテストPDFの作成が完了しました。")
    except ImportError:
        print("reportlabライブラリがインストールされていません。")
        print("以下のコマンドでインストールしてください：")
        print("pip install reportlab")
