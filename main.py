import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import webbrowser
from datetime import datetime
from gui_components import DragDropFrame, ProgressFrame, FileListFrame, ConversionWorker

class PDF2PNGConverter:
    """PDFをPNG画像に変換するメインアプリケーションクラス"""
    
    def __init__(self):
        """アプリケーションの初期化"""
        self.root = TkinterDnD.Tk()
        self.root.title("PDF→PNG変換ツール")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        
        # デフォルトの出力先はデスクトップの"output"フォルダ
        self.output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "output")
        self.worker = None
        
        self.setup_gui()
    
    def setup_gui(self):
        """GUIコンポーネントの初期化"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # タイトルラベル
        title_label = ttk.Label(
            main_frame, 
            text="PDF→PNG変換ツール", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # ドラッグ&ドロップエリア
        self.drag_drop_frame = DragDropFrame(main_frame, callback=self.add_files)
        self.drag_drop_frame.pack(fill="both", expand=True, pady=10)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=5)
        
        # ファイル選択ボタン
        self.file_button = ttk.Button(
            button_frame, 
            text="ファイル選択", 
            command=self.select_files
        )
        self.file_button.pack(side="left", padx=5)
        
        # 出力先選択ボタン
        self.output_button = ttk.Button(
            button_frame, 
            text="出力先選択", 
            command=self.select_output_folder
        )
        self.output_button.pack(side="left", padx=5)
        
        # ファイルリストエリア
        self.file_list_frame = FileListFrame(main_frame)
        self.file_list_frame.pack(fill="both", expand=True, pady=10)
        
        # 出力先ラベル
        self.output_label = ttk.Label(main_frame, text=f"出力先: {self.output_folder}")
        self.output_label.pack(fill="x", pady=5, anchor="w")
        
        # 変換ボタンと進捗フレーム
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=10)
        
        # 変換ボタン
        self.convert_button = tk.Button(
            control_frame, 
            text="変換開始", 
            command=self.start_conversion,
            background="#0078D7",
            foreground="white",
            activebackground="#005fa3",
            activeforeground="white",
            padx=10,
            pady=5,
            relief="flat",
            cursor="hand2"
        )
        self.convert_button.pack(side="left", padx=5)
        
        # キャンセルボタン
        self.cancel_button = ttk.Button(
            control_frame, 
            text="キャンセル", 
            command=self.cancel_conversion,
            state="disabled"
        )
        self.cancel_button.pack(side="left", padx=5)
        
        # 進捗フレーム
        self.progress_frame = ProgressFrame(main_frame)
        self.progress_frame.pack(fill="x", pady=5)
        
        # スタイルの設定
        self.setup_styles()
    
    def setup_styles(self):
        """スタイルの設定"""
        style = ttk.Style()
        
        # アクセントボタンスタイル（変換開始ボタン用）
        style.configure("Accent.TButton", 
                       padding=(10, 5),
                       font=("Arial", 10))
        
        # ボタンの状態に応じたスタイル変更を設定
        style.map("Accent.TButton",
                 background=[('active', '#005fa3'), ('!disabled', '#0078D7')],
                 foreground=[('!disabled', 'white')])
    
    def update_output_folder(self, file_paths):
        """最初のファイルのディレクトリに、タイムスタンプ付きoutputフォルダを作成して設定"""
        if not file_paths:
            return False
        
        try:
            # リストの場合と文字列の場合の両方に対応
            first_file = file_paths[0] if isinstance(file_paths, list) else file_paths
            
            # 文字列をパースする必要がある場合（DnDで渡される場合など）
            if isinstance(first_file, str) and '{' in first_file:
                # DnDからのパスリストをパース
                first_file = first_file.strip('{}').split('} {')[0]
            
            # ファイルの親ディレクトリを取得
            parent_dir = os.path.dirname(os.path.abspath(first_file))
            
            # 現在時刻からフォルダ名を作成
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_folder_name = f"output_{timestamp}"
            
            # 出力先フォルダパスを作成
            new_output_folder = os.path.join(parent_dir, output_folder_name)
            
            # 親ディレクトリに書き込み権限があるか確認
            if not os.access(parent_dir, os.W_OK):
                messagebox.showwarning(
                    "警告", 
                    f"PDFファイルのフォルダ（{parent_dir}）に書き込み権限がありません。\n"
                    "デフォルトの出力先を使用します。"
                )
                return False
            
            # 同名フォルダが既に存在するか確認（念のため）
            if os.path.exists(new_output_folder):
                # 既存のフォルダがある場合はそのまま使用
                pass
            
            # 出力先フォルダを更新
            self.output_folder = new_output_folder
            
            # GUIを更新
            if hasattr(self, 'output_label'):
                self.output_label.config(text=f"出力先: {self.output_folder}")
            
            return True
        
        except Exception as e:
            print(f"出力先フォルダの更新中にエラーが発生しました: {str(e)}")
            # エラーが発生した場合はデフォルトのフォルダを維持
            return False
    
    def add_files(self, file_paths):
        """ファイルをリストに追加"""
        if file_paths:
            # 最初のファイルのディレクトリを出力先として設定
            self.update_output_folder(file_paths)
            
            # ファイルリストに追加
            self.file_list_frame.add_files(file_paths)
    
    def select_files(self):
        """ファイル選択ダイアログを表示"""
        files = filedialog.askopenfilenames(
            title="PDFファイルを選択",
            filetypes=[("PDF files", "*.pdf")]
        )
        if files:
            # 最初のファイルのディレクトリを出力先として設定
            self.update_output_folder(files)
            
            # ファイルリストに追加
            self.add_files(files)
    
    def select_output_folder(self):
        """出力先フォルダ選択ダイアログを表示"""
        folder = filedialog.askdirectory(title="出力先フォルダを選択")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=f"出力先: {self.output_folder}")
    
    def start_conversion(self):
        """変換処理を開始"""
        files = self.file_list_frame.get_files()
        
        if not files:
            messagebox.showwarning("警告", "変換するPDFファイルが選択されていません。")
            return
        
        # 出力先フォルダの存在確認と作成
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder)
                print(f"出力先フォルダを作成しました: {self.output_folder}")
            except Exception as e:
                messagebox.showerror("エラー", f"出力先フォルダの作成に失敗しました。\n{str(e)}")
                return
        
        # 書き込み権限チェック
        if not os.access(self.output_folder, os.W_OK):
            messagebox.showerror("エラー", "出力先フォルダに書き込み権限がありません。")
            return
        
        # UIの状態を変更
        self.convert_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.progress_frame.reset()
        
        # 変換ワーカーを初期化して開始
        self.worker = ConversionWorker(
            self.root,  # rootウィジェットを渡す
            files, 
            self.output_folder,
            progress_callback=self.progress_frame.update_progress,
            completion_callback=self.conversion_complete
        )
        self.worker.start()
    
    def cancel_conversion(self):
        """変換処理をキャンセル"""
        if self.worker:
            self.worker.stop()
            self.convert_button.config(state="normal")
            self.cancel_button.config(state="disabled")
    
    def conversion_complete(self, successful_count, errors):
        """変換完了時の処理"""
        self.convert_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        
        message = f"{successful_count}ファイルの変換が完了しました。"
        
        if errors:
            message += f"\n\n{len(errors)}件のエラーが発生しました。"    
            for error in errors:
                message += f"\n - {error}"
        
        result = messagebox.askquestion("変換完了", f"{message}\n\n出力フォルダを開きますか？")    
        if result == "yes":
            webbrowser.open(self.output_folder)
    
    def run(self):
        """アプリケーションの実行"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PDF2PNGConverter()
    app.run()
