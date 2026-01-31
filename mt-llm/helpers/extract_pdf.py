import os
try:
    import pypdf
    print("pypdf available")
    reader = pypdf.PdfReader(os.path.join("knowledge_base", "Predictive Maintenance Knowledge Base.pdf"))
    for page in reader.pages:
        print(page.extract_text())
except ImportError:
    try:
        import PyPDF2
        print("PyPDF2 available")
        reader = PyPDF2.PdfReader("Predictive Maintenance Knowledge Base.pdf")
        for page in reader.pages:
            print(page.extract_text())
    except ImportError:
        print("No compatible PDF library found (pypdf or PyPDF2)")
