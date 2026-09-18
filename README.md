
# SMART PDF STUDIO — VIP EDITION

Created by **Moinuddin Chishti** • **Chishti Bro Computers and Developers**.

A modern, offline-first Python desktop utility inspired by the requested
**Smart PDF Toolkit + PC Cleaner & File Organizer** concept.

## Included

### Smart PDF Toolkit
- Word → PDF
- PDF → Word
- Images → PDF
- Merge PDFs
- Split PDF by page ranges
- Password protect PDF
- Unlock PDF when the correct password is supplied

### PC Cleaner
- Temporary-file scan
- Preview before deletion
- Disk-space overview
- Duplicate finder using SHA-256

### File Organizer
- Images / Documents / Videos / Audio / Archives / Code / Others
- Collision-safe file moves
- Does not automatically touch hidden files

## UI

The GUI is built with CustomTkinter and uses a dark neon/VIP visual system,
rounded cards, sidebar navigation, status feedback and background worker
threads so long operations do not freeze the interface.

CustomTkinter supports modern customizable widgets and HighDPI scaling:
https://customtkinter.tomschimansky.com/

## Install

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

## Word → PDF

If LibreOffice is installed, the app uses its headless conversion engine for
better DOCX fidelity. If it is not available, a portable ReportLab fallback
creates a readable text-oriented PDF.

## Security

- PDF encryption uses AES-256 through pypdf when its cryptography provider is
  available.
- The cleaner asks for confirmation before deletion.
- The duplicate finder only reports duplicates; it does not delete them.

## YAML

`app.yml` is a feature/configuration contract that can be used as a starting
point for a future Dart/Flutter port. It is **not** a Dart compiler or a
direct Python-to-Dart converter.

## License

MIT for this project's source code. See `THIRD_PARTY_NOTICES.md` for dependency
license considerations.
