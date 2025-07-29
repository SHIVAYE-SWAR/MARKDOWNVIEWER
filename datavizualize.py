import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import markdown
from tkinter import scrolledtext
import webbrowser
import tempfile
import shutil
from datetime import datetime

class MarkdownVisualizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 Markdown Visualizer - Upload & Preview")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.uploaded_files = {}  # Store uploaded file contents
        self.current_file = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="📄 Markdown Visualizer", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame, text="Upload and visualize your markdown files", 
                                  font=('Arial', 10), foreground='#666')
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Upload section
        upload_frame = ttk.LabelFrame(main_frame, text="📁 Upload Files", padding="10")
        upload_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Upload buttons
        btn_frame = ttk.Frame(upload_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="📄 Upload Single File", 
                  command=self.upload_single_file).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="📁 Upload Multiple Files", 
                  command=self.upload_multiple_files).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="📂 Upload Folder", 
                  command=self.upload_folder).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="🗑️ Clear All", 
                  command=self.clear_all_files).pack(side=tk.RIGHT)
        
        # File status
        self.status_label = ttk.Label(upload_frame, text="No files uploaded yet", 
                                     foreground='#666')
        self.status_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - File list
        left_panel = ttk.LabelFrame(content_frame, text="📋 Uploaded Files", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # File listbox with scrollbar
        listbox_frame = ttk.Frame(left_panel)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(listbox_frame, width=35, height=20, 
                                      font=('Arial', 10), selectmode=tk.SINGLE)
        file_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, 
                                      command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Right panel - Preview area
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook for different views
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Raw markdown tab
        raw_frame = ttk.Frame(self.notebook)
        self.notebook.add(raw_frame, text="📝 Raw Markdown")
        
        self.raw_text = scrolledtext.ScrolledText(raw_frame, wrap=tk.WORD, 
                                                 font=('Consolas', 11))
        self.raw_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # HTML preview tab
        html_frame = ttk.Frame(self.notebook)
        self.notebook.add(html_frame, text="🔧 HTML Source")
        
        self.html_text = scrolledtext.ScrolledText(html_frame, wrap=tk.WORD, 
                                                  font=('Consolas', 10))
        self.html_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Visual preview info tab
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="👁️ Preview Info")
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, 
                                                     font=('Arial', 11))
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(right_panel)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="🌐 Open in Browser", 
                  command=self.open_in_browser).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(action_frame, text="💾 Save as HTML", 
                  command=self.save_as_html).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(action_frame, text="📤 Export All", 
                  command=self.export_all_files).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(action_frame, text="🔄 Refresh", 
                  command=self.refresh_preview).pack(side=tk.RIGHT)
        
        # Initial welcome message
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """Show welcome message in preview area"""
        welcome_msg = """
        🎉 Welcome to Markdown Visualizer!
        
        📋 How to use:
        1. Click 'Upload Single File' to upload one .md file
        2. Click 'Upload Multiple Files' to select several files at once
        3. Click 'Upload Folder' to upload all .md files from a folder
        4. Select any file from the left panel to preview it
        5. Use 'Open in Browser' to see the beautiful rendered webpage
        
        ✨ Features:
        • Upload multiple files at once
        • Preview raw markdown and HTML source
        • Export as styled HTML files
        • Beautiful webpage rendering
        • Syntax highlighting for code blocks
        • Professional table styling
        
        Start by uploading your markdown files! 🚀
        """
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, welcome_msg)
    
    def upload_single_file(self):
        """Upload a single markdown file"""
        file_path = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Markdown files", "*.markdown"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_file(file_path)
    
    def upload_multiple_files(self):
        """Upload multiple markdown files"""
        file_paths = filedialog.askopenfilenames(
            title="Select Multiple Markdown Files",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Markdown files", "*.markdown"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            for file_path in file_paths:
                self.load_file(file_path)
    
    def upload_folder(self):
        """Upload all markdown files from a folder"""
        folder_path = filedialog.askdirectory(title="Select Folder with Markdown Files")
        
        if folder_path:
            md_files_found = 0
            try:
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(('.md', '.markdown')):
                        file_path = os.path.join(folder_path, filename)
                        self.load_file(file_path)
                        md_files_found += 1
                
                if md_files_found == 0:
                    messagebox.showwarning("No Files", "No markdown files found in the selected folder.")
                else:
                    messagebox.showinfo("Success", f"Loaded {md_files_found} markdown files from folder!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error loading folder: {str(e)}")
    
    def load_file(self, file_path):
        """Load a single file into memory"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            
            # Store file content
            self.uploaded_files[filename] = {
                'content': content,
                'path': file_path,
                'upload_time': datetime.now()
            }
            
            # Update file list
            self.update_file_list()
            
            # Update status
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file {os.path.basename(file_path)}:\n{str(e)}")
    
    def update_file_list(self):
        """Update the file listbox"""
        self.file_listbox.delete(0, tk.END)
        
        for i, filename in enumerate(sorted(self.uploaded_files.keys())):
            display_text = f"📄 {filename}"
            self.file_listbox.insert(tk.END, display_text)
    
    def update_status(self):
        """Update the status label"""
        file_count = len(self.uploaded_files)
        if file_count == 0:
            self.status_label.config(text="No files uploaded yet")
        elif file_count == 1:
            self.status_label.config(text="1 file uploaded")
        else:
            self.status_label.config(text=f"{file_count} files uploaded")
    
    def on_file_select(self, event):
        """Handle file selection from listbox"""
        selection = self.file_listbox.curselection()
        if selection:
            display_text = self.file_listbox.get(selection[0])
            filename = display_text.replace("📄 ", "")
            self.preview_file(filename)
    
    def preview_file(self, filename):
        """Preview the selected file"""
        if filename not in self.uploaded_files:
            return
        
        self.current_file = filename
        file_data = self.uploaded_files[filename]
        content = file_data['content']
        
        try:
            # Show raw markdown
            self.raw_text.delete(1.0, tk.END)
            self.raw_text.insert(1.0, content)
            
            # Convert to HTML
            html_content = markdown.markdown(
                content,
                extensions=[
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.toc',
                    'markdown.extensions.nl2br',
                    'markdown.extensions.codehilite'
                ]
            )
            
            # Show HTML source
            self.html_text.delete(1.0, tk.END)
            self.html_text.insert(1.0, html_content)
            
            # Show preview info
            preview_info = f"""
📄 File: {filename}
📅 Uploaded: {file_data['upload_time'].strftime("%Y-%m-%d %H:%M:%S")}
📍 Original Path: {file_data['path']}
📏 Size: {len(content)} characters
📝 Lines: {len(content.splitlines())} lines

✅ Ready for preview!

🌐 Click "Open in Browser" to see the beautiful rendered webpage
💾 Click "Save as HTML" to export as a styled HTML file

📋 Content Summary:
- Headers: {content.count('#')} found
- Code blocks: {content.count('```')} found
- Tables: {content.count('|')} pipe characters found
- Links: {content.count('[') + content.count('http')} potential links found
            """
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview_info.strip())
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Error previewing file: {str(e)}")
    
    def open_in_browser(self):
        """Open current file in browser"""
        if not self.current_file:
            messagebox.showwarning("No Selection", "Please select a file first.")
            return
        
        try:
            file_data = self.uploaded_files[self.current_file]
            content = file_data['content']
            
            # Convert to HTML
            html_content = markdown.markdown(
                content,
                extensions=[
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.toc',
                    'markdown.extensions.nl2br',
                    'markdown.extensions.codehilite'
                ]
            )
            
            # Create beautiful HTML
            styled_html = self.create_styled_html(html_content, self.current_file)
            
            # Save and open
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(styled_html)
                temp_path = f.name
            
            webbrowser.open(f'file://{temp_path}')
            messagebox.showinfo("✅ Opened", f"{self.current_file} opened in your browser!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error opening in browser: {str(e)}")
    
    def save_as_html(self):
        """Save current file as HTML"""
        if not self.current_file:
            messagebox.showwarning("No Selection", "Please select a file first.")
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('HTML files', '*.html'), ('All files', '*.*')],
            title=f'Save {self.current_file} as HTML',
            initialname=f"{os.path.splitext(self.current_file)}.html"
        )
        
        if save_path:
            try:
                file_data = self.uploaded_files[self.current_file]
                content = file_data['content']
                
                html_content = markdown.markdown(
                    content,
                    extensions=[
                        'markdown.extensions.tables',
                        'markdown.extensions.fenced_code',
                        'markdown.extensions.toc',
                        'markdown.extensions.nl2br',
                        'markdown.extensions.codehilite'
                    ]
                )
                
                styled_html = self.create_styled_html(html_content, self.current_file)
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(styled_html)
                
                messagebox.showinfo("✅ Saved", f"HTML file saved to:\n{save_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
    
    def export_all_files(self):
        """Export all uploaded files as HTML"""
        if not self.uploaded_files:
            messagebox.showwarning("No Files", "No files to export.")
            return
        
        folder_path = filedialog.askdirectory(title="Select folder to save HTML files")
        if not folder_path:
            return
        
        try:
            exported_count = 0
            for filename, file_data in self.uploaded_files.items():
                content = file_data['content']
                
                html_content = markdown.markdown(
                    content,
                    extensions=[
                        'markdown.extensions.tables',
                        'markdown.extensions.fenced_code',
                        'markdown.extensions.toc',
                        'markdown.extensions.nl2br',
                        'markdown.extensions.codehilite'
                    ]
                )
                
                styled_html = self.create_styled_html(html_content, filename)
                
                html_filename = f"{os.path.splitext(filename)}.html"
                html_path = os.path.join(folder_path, html_filename)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(styled_html)
                
                exported_count += 1
            
            messagebox.showinfo("✅ Export Complete", 
                              f"Exported {exported_count} files to:\n{folder_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting files: {str(e)}")
    
    def create_styled_html(self, html_content, filename):
        """Create beautifully styled HTML"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename} - Markdown Preview</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #fff;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px 35px;
            border-radius: 12px;
            margin-bottom: 35px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header p {{
            margin: 8px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .content {{
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 2.5em;
            margin-bottom: 1em;
            font-weight: 600;
            line-height: 1.25;
        }}
        h1 {{
            font-size: 2.5em;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 12px;
        }}
        h2 {{
            font-size: 2em;
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        h3 {{
            font-size: 1.6em;
            color: #34495e;
        }}
        p {{
            margin: 1.2em 0;
            text-align: justify;
        }}
        pre {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            margin: 25px 0;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
            font-size: 14px;
            line-height: 1.5;
        }}
        code {{
            background: #f1f3f4;
            color: #d73a49;
            padding: 3px 8px;
            border-radius: 5px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
            font-size: 90%;
        }}
        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 30px 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            padding: 18px 15px;
            text-align: left;
        }}
        td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e3f2fd;
        }}
        ul, ol {{
            margin: 1.2em 0;
            padding-left: 35px;
        }}
        li {{
            margin: 8px 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 25px 0;
            padding: 18px 28px;
            background: linear-gradient(90deg, #f8f9fa 0%, #ffffff 100%);
            font-style: italic;
            border-radius: 0 10px 10px 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.3s ease;
        }}
        a:hover {{
            border-bottom-color: #3498db;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.12);
            margin: 25px 0;
        }}
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #3498db, transparent);
            margin: 40px 0;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 20px 15px;
            }}
            .content {{
                padding: 25px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📄 {filename}</h1>
        <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")} -  Markdown Visualizer</p>
    </div>
    
    <div class="content">
        {html_content}
    </div>
</body>
</html>"""
    
    def refresh_preview(self):
        """Refresh the current file preview"""
        if self.current_file:
            self.preview_file(self.current_file)
    
    def clear_all_files(self):
        """Clear all uploaded files"""
        if self.uploaded_files:
            result = messagebox.askyesno("Clear All", "Are you sure you want to clear all uploaded files?")
            if result:
                self.uploaded_files.clear()
                self.current_file = None
                self.update_file_list()
                self.update_status()
                
                # Clear all text areas
                self.raw_text.delete(1.0, tk.END)
                self.html_text.delete(1.0, tk.END)
                self.show_welcome_message()
                
                messagebox.showinfo("Cleared", "All files have been cleared.")

def main():
    root = tk.Tk()
    app = MarkdownVisualizerGUI(root)
    
    # Show startup message
    messagebox.showinfo("🚀 Markdown Visualizer", 
                       "Welcome to Markdown Visualizer with Upload!\n\n" +
                       "Features:\n" +
                       "✅ Upload single or multiple files\n" +
                       "✅ Upload entire folders\n" +
                       "✅ Beautiful visual previews\n" +
                       "✅ Export to HTML\n" +
                       "✅ Professional styling\n\n" +
                       "Start by uploading your markdown files!")
    
    root.mainloop()

if __name__ == "__main__":
    main()
