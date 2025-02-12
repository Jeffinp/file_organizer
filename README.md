# 🚀 FileFlow - Your Smart File Organizer

Hey everyone! I created this project to solve a problem we all face: that messy folder full of jumbled files. **FileFlow** automatically organizes everything, leaving your PC cleaner than Marie Kondo’s closet!

<div align="center">
  <img src="https://github.com/Jeffinp/file_organizer/blob/main/image/Screenshot_1044.png" alt="Modern Interface" width="600">
  <p><i>Clean and modern interface – even your grandpa will know how to use it!</i></p>
</div>

<div align="center">
  <img src="https://github.com/Jeffinp/file_organizer/blob/main/image/Screenshot_1045.png" alt="Dark Mode" width="600">
  <p><i>Dark Mode.</i></p>
</div>

## 💡 Why Use It?

- **Ninja-level organization** into categorized folders (documents, images, music, etc.)
- **Duplicate detector** using SHA-256 hashing (it never duplicates an identical file!)
- **Total security** with permission checks and file locking
- **Modern interface** featuring dark mode, smooth animations, and visual feedback
- **Detailed logs** so you know exactly what happened

## 🛠️ How It Works Under the Hood

### 🔍 Python Core

```python
# Example of the duplicate detection system
def is_duplicate(file1, file2):
    return calculate_hash(file1) == calculate_hash(file2)  # Comparison via SHA-256
```

- **Lock System**: Uses `threading.Lock` to prevent multiple processes from accessing the files simultaneously
- **Permission Verification**: Checks read/write permissions before any operation
- **Advanced Logging**: Generates rotating logs (5MB each) with thread info and timestamps

### 🌐 Web Interface

- **Frontend**: HTML/CSS/JS with a responsive design and over 60 animations
- **Backend**: Flask running locally on port 5000
- **Bridge**: Webview creates an integrated desktop window with Python

## ⚙️ Technologies Used

| Layer        | Tools                                                             |
|--------------|-------------------------------------------------------------------|
| **Backend**  | Python 3.10+, Flask, hashlib, logging                             |
| **Frontend** | HTML5, CSS3 (Custom Properties), JavaScript ES6+                  |
| **Interface**| Webview (for the desktop window), Font Awesome 6                  |
| **Security** | SHA-256, Permission Verification, File Locking                    |

## 🎮 How to Use

1. **Lightning-fast Installation** ⚡
   ```bash
   git clone https://github.com/Jeffinp/file_organizer
   cd file_organizer
   pip install -r requirements.txt
   ```

2. **Running the Program** 🚀
   ```bash
   python app.py
   ```

3. **Step-by-Step Magic** ✨
   - Click **"Browse"** and select the folder
   - Preview the categories
   - Click **"Organize"** and watch the magic happen!

## 🗂️ Categories System

| Folder       | Supported Extensions                                    |
|--------------|---------------------------------------------------------|
| **Images**   | .jpg, .png, .webp, .svg, .gif (and 7 more formats)       |
| **Documents**| .pdf, .docx, .xlsx, .pptx, .txt (and 10 more formats)    |
| **Media**    | .mp3, .mp4, .mkv, .flac, .wav (and 15 more codecs)       |
| **Code**     | .py, .js, .html, .css, .java (and support for 8 more languages) |
| **Others**   | Any extension not listed                                |

## 🚨 And If...?

- **File in use?** → The program detects it and temporarily skips it
- **No permission?** → It clearly alerts you to the issue
- **Unknown error?** → It generates a detailed log with a stack trace

## 💡 Pro Tips

- Use **CTRL+CLICK** on the directory field to paste paths
- **Double-click** recent items for quick selection
- Press **ESC** to close any open dialog

## 📈 Next Steps

- [ ] Drag-and-drop file upload
- [ ] Custom rules system
- [ ] Cloud storage support (Dropbox, Google Drive)

---

Want to see it in action? Check out the code, and if you find any bugs or have a cool idea, open an issue! 🐛💡