import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import threading
from pdf_processor import PDFProcessor


class DragDropFrame(tk.Frame):
    """ドラッグ&ドロップ対応フレーム"""
    
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.setup_ui()
        self.setup_drag_drop()
    
    def setup_ui(self):
        """UI要素の設定"""
        self.configure(relief="ridge", bd=2, bg="#f0f0f0")
        
        # ドロップエリアのラベル
        self.drop_label = tk.Label(
            self, 
            text="PDFファイルをここにドロップ\nまたは「ファイル選択」ボタンを使用",
            bg="#f0f0f0",
            fg="#666666",
            font=("Arial", 12),
            justify="center"
        )
        self.drop_label.pack(expand=True, fill="both", padx=20, pady=20)
    
    def setup_drag_drop(self):
        """ドラッグ&ドロップの設定"""
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<DropEnter>>', self.on_drag_enter)
        self.dnd_bind('<<DropLeave>>', self.on_drag_leave)
        self.dnd_bind('<<Drop>>', self.on_drop)
    
    def on_drag_enter(self, event):
        """ドラッグ開始時の処理"""
        self.configure(bg="#e6f3ff")
        self.drop_label.configure(bg="#e6f3ff", fg="#0066cc")
    
    def on_drag_leave(self, event):
        """ドラッグ終了時の処理"""
        self.configure(bg="#f0f0f0")
        self.drop_label.configure(bg="#f0f0f0", fg="#666666")
    
    def on_drop(self, event):
        """ドロップ時の処理"""
        self.configure(bg="#f0f0f0")
        self.drop_label.configure(bg="#f0f0f0", fg="#666666")
        
        files = self.tk.splitlist(event.data)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        
        if pdf_files and self.callback:
            self.callback(pdf_files)


class ProgressFrame(tk.Frame):
    """進捗表示フレーム"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI要素の設定"""
        # 進捗バー
        self.progress = ttk.Progressbar(self, mode='determinate')
        self.progress.pack(fill="x", padx=5, pady=5)
        
        # 進捗ラベル
        self.progress_label = tk.Label(self, text="待機中...")
        self.progress_label.pack(pady=2)
    
    def update_progress(self, current, total, message=""):
        """進捗の更新"""
        if total > 0:
            progress_value = (current / total) * 100
            self.progress['value'] = progress_value
            
            if message:
                self.progress_label.config(text=f"{message} ({current}/{total}) - {progress_value:.0f}%")
            else:
                self.progress_label.config(text=f"{current}/{total} - {progress_value:.0f}%")
        
        self.update()
    
    def reset(self):
        """進捗のリセット"""
        self.progress['value'] = 0
        self.progress_label.config(text="待機中...")


class FileListFrame(tk.Frame):
    """ファイルリスト表示フレーム"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.files = []
        self.setup_ui()
    
    def setup_ui(self):
        """UI要素の設定"""
        # リストボックスとスクロールバー
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True)
        
        self.listbox = tk.Listbox(list_frame, height=6)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ファイル操作ボタン
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", pady=5)
        
        self.clear_button = ttk.Button(
            button_frame, 
            text="リストクリア", 
            command=self.clear_files
        )
        self.clear_button.pack(side="right", padx=5)
        
        self.remove_button = ttk.Button(
            button_frame, 
            text="選択削除", 
            command=self.remove_selected
        )
        self.remove_button.pack(side="right", padx=5)
    
    def add_files(self, file_paths):
        """ファイルをリストに追加"""
        for file_path in file_paths:
            if file_path not in self.files:
                # PDFファイルの有効性をチェック
                filename = os.path.basename(file_path)  # 先にファイル名を取得
                is_valid, error_msg = PDFProcessor.validate_pdf(file_path)
                if is_valid:
                    self.files.append(file_path)
                    self.listbox.insert(tk.END, filename)
                else:
                    messagebox.showerror("エラー", f"無効なPDFファイル: {filename}\n{error_msg}")
    
    def remove_selected(self):
        """選択されたファイルを削除"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.listbox.delete(index)
            del self.files[index]
    
    def clear_files(self):
        """ファイルリストをクリア"""
        self.listbox.delete(0, tk.END)
        self.files.clear()
    
    def get_files(self):
        """ファイルリストを取得"""
        return self.files.copy()


class ConversionWorker:
    """変換処理を別スレッドで実行するクラス"""
    
    def __init__(self, root, files, output_folder, progress_callback=None, completion_callback=None):
        self.root = root  # rootウィジェットを受け取る
        self.files = files
        self.output_folder = output_folder
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.is_running = False
    
    def start(self):
        """変換処理を開始"""
        if not self.is_running:
            self.is_running = True
            thread = threading.Thread(target=self._convert_files)
            thread.daemon = True
            thread.start()
    
    def _convert_files(self):
        """ファイル変換のメイン処理"""
        total_files = len(self.files)
        successful_conversions = 0
        errors = []
        
        for i, file_path in enumerate(self.files):
            if not self.is_running:
                break
            
            try:
                filename = os.path.basename(file_path)
                # メインスレッドでGUI更新
                if self.progress_callback:
                    self.root.after(0, lambda i=i, total=total_files, fn=filename: 
                                  self.progress_callback(i, total, f"処理中: {fn}"))
                
                page_count = PDFProcessor.pdf_to_png(file_path, self.output_folder)
                successful_conversions += 1
                
            except Exception as e:
                error_msg = f"{os.path.basename(file_path)}: {str(e)}"
                errors.append(error_msg)
        
        # 最終進捗更新（メインスレッドで）
        if self.progress_callback:
            self.root.after(0, lambda: self.progress_callback(total_files, total_files, "完了"))
        
        # 完了コールバック（メインスレッドで）
        if self.completion_callback:
            self.root.after(0, lambda s=successful_conversions, e=errors: 
                         self.completion_callback(s, e))
        
        self.is_running = False
    
    def stop(self):
        """変換処理を停止"""
        self.is_running = False
