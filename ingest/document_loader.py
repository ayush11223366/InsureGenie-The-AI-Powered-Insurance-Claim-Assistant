import pdfplumber
import docx
import os
from email import policy
from email.parser import BytesParser

class DocumentLoader:
    def __init__(self, docs_folder):
        self.docs_folder = docs_folder

    def load_documents(self):
        docs = []
        for fname in os.listdir(self.docs_folder):
            fpath = os.path.join(self.docs_folder, fname)
            if fname.lower().endswith('.pdf'):
                docs.append(self._load_pdf(fpath))
            elif fname.lower().endswith('.docx'):
                docs.append(self._load_docx(fpath))
            elif fname.lower().endswith('.eml'):
                docs.append(self._load_email(fpath))
        return docs

    def _load_pdf(self, path):
        with pdfplumber.open(path) as pdf:
            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
        return {'type': 'pdf', 'path': path, 'text': text}

    def _load_docx(self, path):
        doc = docx.Document(path)
        text = '\n'.join([p.text for p in doc.paragraphs])
        return {'type': 'docx', 'path': path, 'text': text}

    def _load_email(self, path):
        with open(path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
        text = msg.get_body(preferencelist=('plain')).get_content() if msg.get_body() else ''
        return {'type': 'email', 'path': path, 'text': text}
