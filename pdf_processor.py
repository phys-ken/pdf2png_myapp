import fitz  # PyMuPDF
import os
import pathlib


class PDFProcessor:
    """PDFファイルをPNG画像に変換するクラス"""
    
    @staticmethod
    def pdf_to_png(pdf_path, output_folder, dpi=150):
        """
        PDFファイルを連番PNG画像に変換
        
        Args:
            pdf_path (str): PDFファイルのパス
            output_folder (str): 出力先フォルダ
            dpi (int): 解像度（デフォルト150）
            
        Returns:
            int: 変換されたページ数
            
        Raises:
            Exception: PDFの読み込みや変換エラー
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # PDFドキュメントを開く
        doc = fitz.open(pdf_path)
        base_name = pathlib.Path(pdf_path).stem
        
        try:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # 解像度を設定してピクスマップを取得
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat)
                
                # 出力ファイル名を生成
                output_path = os.path.join(
                    output_folder, 
                    f"{base_name}_{page_num+1:03d}.png"
                )
                
                # PNG画像として保存
                pix.save(output_path)
                pix = None  # メモリ解放
                
            return len(doc)
            
        finally:
            doc.close()
    
    @staticmethod
    def validate_pdf(pdf_path):
        """
        PDFファイルの有効性をチェック
        
        Args:
            pdf_path (str): PDFファイルのパス
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            if not pdf_path.lower().endswith('.pdf'):
                return False, "PDFファイルではありません"
            
            if not os.path.exists(pdf_path):
                return False, "ファイルが存在しません"
            
            # PDFを開いて確認
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            
            if page_count == 0:
                return False, "ページが含まれていません"
            
            return True, None
            
        except Exception as e:
            return False, f"PDFファイルの読み込みエラー: {str(e)}"
    
    @staticmethod
    def get_pdf_info(pdf_path):
        """
        PDFファイルの情報を取得
        
        Args:
            pdf_path (str): PDFファイルのパス
            
        Returns:
            dict: PDFの情報
        """
        try:
            doc = fitz.open(pdf_path)
            info = {
                'page_count': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'file_size': os.path.getsize(pdf_path)
            }
            doc.close()
            return info
        except Exception as e:
            return {'error': str(e)}
