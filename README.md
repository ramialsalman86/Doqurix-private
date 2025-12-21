# Doqurix - AI Document Intelligence

Professional document Q&A system with advanced RAG (Retrieval-Augmented Generation), hybrid search, and multilingual support.

## Features

- 🤖 **AI-Powered Q&A** - Ask questions about your PDF documents in natural language
- 🌐 **Multilingual** - Supports Arabic, German, Russian, Chinese, and English with automatic language detection
- 🔍 **Hybrid Search** - Combines vector similarity and BM25 ranking for optimal results
- 📊 **Reranking** - Uses cross-encoder to refine search results
- 💻 **Dual Interface** - Desktop GUI (Tkinter) and modern web interface (Bottle)
- 🎨 **Professional UI** - ChatGPT-quality web interface with glassmorphism and smooth animations
- 🔒 **Encrypted PDFs** - Supports password-protected and encrypted documents

## Requirements

- Python 3.9+
- Windows/macOS/Linux
- 8GB+ RAM recommended
- ~4GB disk space for models

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd QA_AI_DOCUMENT
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `.\venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Download models** (not included in repo due to size)
   - Create `models/` directory
   - Download required LLM model (e.g., Qwen or similar GGUF format)
   - Place in `models/` folder

## Usage

### Desktop Application
```bash
python main.py
```

Features:
- Upload multiple PDFs
- Two search modes: Quick and Detailed
- Context highlighting
- Document management

### Web Application
```bash
python main.py
# Then click "Launch Web Version" or navigate to http://localhost:8502
```

Features:
- Modern ChatGPT-style interface
- Drag-and-drop file upload
- Real-time chat interface
- Expandable source citations

## Project Structure

```
QA_AI_DOCUMENT/
├── main.py              # Desktop application (Tkinter)
├── bottle_app.py        # Web application (Bottle framework)
├── web_app.py           # Alternative web implementation
├── requirements.txt     # Python dependencies
├── LICENSE.txt          # License information
├── BUILD_GUIDE.md       # Build instructions for executables
├── build_installer.ps1  # Windows installer builder
├── installer_script.iss # Inno Setup script
└── models/              # AI models (download separately)
```

## Technology Stack

- **AI/ML**: llama-cpp-python, sentence-transformers
- **Vector DB**: ChromaDB
- **Search**: BM25 + Vector similarity + Cross-encoder reranking
- **PDF**: PyPDF2 with PyCryptodome for encryption
- **Desktop**: Tkinter
- **Web**: Bottle framework
- **UI**: Modern CSS with glassmorphism effects

## Language Support

The system automatically detects and preserves the original document language:

| Language | Detection | Status |
|----------|-----------|--------|
| Arabic | Unicode character analysis | ✅ Full support |
| German | Special character detection | ✅ Full support |
| Russian | Cyrillic script detection | ✅ Full support |
| Chinese/Japanese | CJK character detection | ✅ Full support |
| English | Default fallback | ✅ Full support |

## Building Executables

### Windows
```bash
# Build standalone executable
pyinstaller DocumentQA.spec

# Build installer
.\build_installer.ps1
```

### macOS
```bash
chmod +x build_macos.sh
./build_macos.sh
```

## Configuration

Key settings can be adjusted in the code:

- **Chunk size**: Default 600 words with 200-word overlap
- **Search results**: 15 candidates retrieved, top 5 reranked
- **Context window**: Automatically managed to fit LLM limits
- **Temperature**: 0.7 for balanced creativity/accuracy

## Performance

- Desktop: ~2-5 seconds per query (depending on mode)
- Web: Similar performance, optimized for concurrent users
- Context window: Intelligently managed to prevent token overflow

## Known Issues

- Large model files (~4GB) must be downloaded separately
- First query may be slower due to model loading
- Mobile web interface is responsive but optimal on desktop

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See `LICENSE.txt` for details.

## Support

For issues or questions:
- Create an issue in this repository
- Check existing documentation
- Review code comments

## Acknowledgments

- Built with llama-cpp-python for efficient LLM inference
- Uses Sentence Transformers for embeddings
- Powered by ChromaDB for vector storage
- UI inspired by ChatGPT, Claude, and Gemini

---

**Note**: This is a professional document intelligence system. Model files are NOT included due to size constraints. Download separately and place in the `models/` directory.
