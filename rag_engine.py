# -*- coding: utf-8 -*-
"""RAG engine for NexRAG system.

Contains the original classes (QueryProfile, QueryCache, SemanticChunker,
ReciprocalRankFusion, EnhancedRAGv3) migrated from the Colab notebook.
"""

from pathlib import Path
import json
import torch
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import re
from html import escape

from datetime import datetime

# Core Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_groq import ChatGroq
from langchain.schema import Document

# Advanced Models
from sentence_transformers import SentenceTransformer, CrossEncoder

# Setup Device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"System ready. Running on: {device.upper()}")


@dataclass
class QueryProfile:
    query_type: str
    intent: str
    needs_multi_docs: bool
    requires_comparison: bool
    answer_style: str
    k: int


class QueryCache:
    """Simple cache for repeated queries"""
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size

    def get(self, query: str) -> Optional[Tuple[str, str, str]]:
        key = hashlib.md5(query.encode("utf-8")).hexdigest()
        return self.cache.get(key)

    def set(self, query: str, response: Tuple[str, str, str]):
        key = hashlib.md5(query.encode("utf-8")).hexdigest()
        if len(self.cache) >= self.max_size:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = response


class SemanticChunker:
    """Advanced semantic chunking using sentence embeddings"""
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name, device=device)

    def chunk_document(self, text: str, max_chunk_size=1000, similarity_threshold=0.5):
        """Split text into semantically coherent chunks"""
        sentences = text.replace('\n', ' ').split('. ')
        sentences = [s.strip() + '.' for s in sentences if s.strip()]

        if not sentences:
            return [text]

        embeddings = self.model.encode(sentences)
        chunks = []
        current_chunk = [sentences[0]]
        current_size = len(sentences[0])

        for i in range(1, len(sentences)):
            previous_norm = float(np.linalg.norm(embeddings[i - 1]))
            current_norm = float(np.linalg.norm(embeddings[i]))
            denominator = previous_norm * current_norm
            if not np.isfinite(denominator) or denominator <= np.finfo(float).eps:
                similarity = 0.0
            else:
                similarity = float(np.dot(embeddings[i - 1], embeddings[i]) / denominator)
                if not np.isfinite(similarity):
                    similarity = 0.0
            sentence_len = len(sentences[i])

            if similarity > similarity_threshold and current_size + sentence_len < max_chunk_size:
                current_chunk.append(sentences[i])
                current_size += sentence_len
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentences[i]]
                current_size = sentence_len

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks


class ReciprocalRankFusion:
    """RRF for combining multiple retrieval results"""
    @staticmethod
    def fuse(retrieval_results: List[List[Document]], k=60) -> List[Document]:
        doc_scores = defaultdict(float)
        doc_map = {}

        for docs in retrieval_results:
            for rank, doc in enumerate(docs):
                doc_id = doc.metadata.get('chunk_id') or f"{doc.metadata.get('pdf_id', 'unknown')}::{hashlib.md5(doc.page_content.encode()).hexdigest()}"
                doc_scores[doc_id] += 1 / (k + rank + 1)
                doc_map[doc_id] = doc

        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc_map[doc_id] for doc_id, _ in sorted_docs]


class EnhancedRAGv3:
    def __init__(self, api_key: str):
        self.vector_db = None
        self.bm25_retriever = None
        self.documents = []
        self.pdf_metadata = {}  # Track multiple PDFs
        self.pdf_files = {}     # Keep original bytes for PDF tools during this session.
        self.doc_headers = {}   # Store extracted headers (title, authors, abstract) per PDF
        self.cache = QueryCache()
        self.api_key = api_key
        self.is_initialized = False

        # Initialize LLM
        self.llm = ChatGroq(
            temperature=0,
            model_name="openai/gpt-oss-120b",
            groq_api_key=api_key
        )

        # Models (loaded on demand)
        self.embedding_model = None
        self.cross_encoder = None
        self.semantic_chunker = None
        self.query_model = None

    def load_models(self, progress=None):
        if progress is None:
            progress = lambda *a, **kw: None
        """Load all models with progress tracking"""
        if self.is_initialized:
            return "Models already loaded."

        progress(0.1, desc="Loading BGE embeddings...")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en-v1.5",
            model_kwargs={'device': device, 'trust_remote_code': True},
            encode_kwargs={'normalize_embeddings': True}
        )

        progress(0.4, desc="Loading Re-ranker...")
        self.cross_encoder = CrossEncoder('BAAI/bge-reranker-v2-m3', device=device)

        progress(0.6, desc="Loading Semantic Chunker...")
        self.semantic_chunker = SemanticChunker()

        progress(0.8, desc="Loading Query Model...")
        self.query_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)

        progress(1.0, desc="Complete")
        self.is_initialized = True
        return "All models loaded successfully."

    def _extract_document_header(self, pages: List[Document], pdf_name: str, pdf_id: str) -> Dict:
        """Extract title, authors, and abstract from first pages of PDF"""
        # Get text from first 2 pages (where metadata usually is)
        header_text = ""
        for i, page in enumerate(pages[:2]):
            header_text += page.page_content + "\n\n"

        # Use LLM to extract structured metadata
        extraction_prompt = f"""Extract the following information from this academic paper's first pages.
Return ONLY a JSON object with these keys:
- title: The paper's title (string)
- authors: List of author names (array of strings)
- abstract: The paper's abstract if present (string, or null if not found)
- institutions: List of institutions/affiliations if present (array of strings, or empty array)

Text from first pages:
{header_text[:4000]}

JSON:"""

        try:
            response = self.llm.invoke(extraction_prompt)
            # Parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                metadata = json.loads(json_match.group())
                metadata['pdf_name'] = pdf_name
                metadata['pdf_id'] = pdf_id
                metadata['raw_header'] = header_text[:2000]  # Store raw text too
                return metadata
        except Exception as e:
            print(f"Header extraction error: {e}")

        # Fallback: return raw header text
        return {
            'title': None,
            'authors': [],
            'abstract': None,
            'institutions': [],
            'pdf_name': pdf_name,
            'pdf_id': pdf_id,
            'raw_header': header_text[:2000]
        }

    def _is_metadata_query(self, query: str) -> Tuple[bool, str]:
        """Check if query is asking for basic document metadata"""
        query_lower = query.lower()

        # Author queries
        author_patterns = ['who are the authors', 'who wrote', 'author', 'authors', 'written by', 'by whom']
        if any(p in query_lower for p in author_patterns):
            return True, 'authors'

        # Title queries
        title_patterns = ['what is the title', 'title of', 'paper title', 'document title', 'name of the paper']
        if any(p in query_lower for p in title_patterns):
            return True, 'title'

        # Abstract queries
        abstract_patterns = ['what is the abstract', 'abstract of', 'paper abstract', 'summarize the abstract']
        if any(p in query_lower for p in abstract_patterns):
            return True, 'abstract'

        # Institution queries
        institution_patterns = ['which institution', 'which university', 'affiliation', 'where are the authors from']
        if any(p in query_lower for p in institution_patterns):
            return True, 'institutions'

        return False, None

    def _answer_metadata_query(self, query: str, metadata_type: str) -> Tuple[str, str, str]:
        """Answer queries about document metadata directly"""
        if not self.doc_headers:
            return "No document metadata available.", "", ""

        # Build response from stored headers
        responses = []
        citations = []

        for pdf_name, header in self.doc_headers.items():
            if metadata_type == 'authors':
                authors = header.get('authors', [])
                if authors:
                    author_str = ", ".join(authors)
                    responses.append(f"**{pdf_name}**: {author_str}")
                else:
                    # Fallback to raw header
                    responses.append(f"**{pdf_name}**: Authors could not be automatically extracted. See first page.")

            elif metadata_type == 'title':
                title = header.get('title')
                if title:
                    responses.append(f"**{pdf_name}**: {title}")
                else:
                    responses.append(f"**{pdf_name}**: Title could not be automatically extracted.")

            elif metadata_type == 'abstract':
                abstract = header.get('abstract')
                if abstract:
                    responses.append(f"**{pdf_name}**:\n{abstract}")
                else:
                    responses.append(f"**{pdf_name}**: Abstract not found in first pages.")

            elif metadata_type == 'institutions':
                institutions = header.get('institutions', [])
                if institutions:
                    inst_str = ", ".join(institutions)
                    responses.append(f"**{pdf_name}**: {inst_str}")
                else:
                    responses.append(f"**{pdf_name}**: Institutions could not be automatically extracted.")

            # Keep metadata answers consistent with the page excerpt panel.
            raw_header = header.get('raw_header', '')
            header_doc = Document(
                page_content=raw_header,
                metadata={'page': 0, 'pdf_name': pdf_name, 'pdf_id': header.get('pdf_id')},
            )
            citations.append(self._create_citation_card(len(citations) + 1, header_doc, raw_header))

        answer = "\n\n".join(responses)
        citations_html = "\n".join(citations)
        metadata_str = f"**Query Type:** Metadata ({metadata_type}) | **Direct extraction from document headers**"

        return answer, citations_html, metadata_str

    def _classify_query(self, query: str) -> QueryProfile:
        classification_prompt = f"""You route user questions for a RAG system.
Return ONLY compact JSON with keys:
- query_type: one of [factoid, summary, comparison, extraction, reasoning]
- needs_multi_docs: true/false (set true when the query likely spans multiple documents or asks for differences)
- requires_comparison: true/false
- answer_style: one of [direct, bullets, steps]
- k: integer between 5 and 12 indicating how many chunks to retrieve

Question: {query}

JSON:"""

        def heuristic_profile() -> QueryProfile:
            ql = query.lower()
            requires_comparison = any(word in ql for word in ['compare', 'difference', 'versus', 'vs', 'between', 'across'])
            needs_multi = requires_comparison or any(word in ql for word in ['both', 'each document', 'all documents', 'across'])
            if any(pattern in ql for pattern in ['what is', 'who is', 'when ', 'define', 'list ']):
                qt = 'factoid'
                k_val = 6
                style = 'direct'
            elif requires_comparison:
                qt = 'comparison'
                k_val = 12
                style = 'bullets'
            elif any(word in ql for word in ['summarize', 'overview', 'key points', 'conclusion']):
                qt = 'summary'
                k_val = 10
                style = 'bullets'
            elif any(word in ql for word in ['explain', 'how does', 'process', 'steps', 'methodology']):
                qt = 'reasoning'
                k_val = 10
                style = 'steps'
            else:
                qt = 'extraction'
                k_val = 8
                style = 'direct'
            return QueryProfile(
                query_type=qt,
                intent=qt,
                needs_multi_docs=needs_multi,
                requires_comparison=requires_comparison,
                answer_style=style,
                k=k_val
            )

        try:
            response = self.llm.invoke(classification_prompt)
            data = json.loads(response.content)
            qt = str(data.get('query_type', 'extraction')).lower()
            needs_multi = bool(data.get('needs_multi_docs', False))
            requires_comparison = bool(data.get('requires_comparison', False))
            style = str(data.get('answer_style', 'direct')).lower()
            k_val = int(data.get('k', 8))
            k_val = max(5, min(k_val, 12))
            if qt not in ['factoid', 'summary', 'comparison', 'extraction', 'reasoning']:
                qt = 'extraction'
            if style not in ['direct', 'bullets', 'steps']:
                style = 'direct'
            return QueryProfile(
                query_type=qt,
                intent=qt,
                needs_multi_docs=needs_multi or requires_comparison,
                requires_comparison=requires_comparison or qt == 'comparison',
                answer_style=style,
                k=k_val
            )
        except Exception:
            return heuristic_profile()

    def _generate_hyde_document(self, query: str) -> str:
        hyde_prompt = f"""Generate a detailed, factual paragraph that would answer this question:

Question: {query}

Write a comprehensive answer (2-3 sentences) as if from an expert document:"""
        try:
            response = self.llm.invoke(hyde_prompt)
            return response.content
        except:
            return query

    def _expand_query(self, query: str) -> List[str]:
        expansion_prompt = f"""Generate 3 different versions of this question to retrieve relevant documents:

Original Question: {query}

Generate 3 alternative phrasings (one per line):"""
        try:
            response = self.llm.invoke(expansion_prompt)
            queries = response.content.strip().split('\n')
            queries = [q.strip().lstrip('1234567890.-) ') for q in queries if q.strip()]
            return [query] + queries[:3]
        except:
            return [query]

    def ingest_pdf(self, pdf_path: str, use_semantic_chunking=True, progress=None):
        if progress is None:
            progress = lambda *a, **kw: None
        """Ingest PDF with progress tracking - supports multiple PDFs"""
        progress(0.1, desc=f"Loading PDF: {Path(pdf_path).name}...")

        # Check if already loaded
        pdf_name = Path(pdf_path).name
        if pdf_name in self.pdf_metadata:
            self.pdf_files[pdf_name] = Path(pdf_path).read_bytes()
            return f"Notice: Document '{pdf_name}' is already loaded."

        pdf_bytes = Path(pdf_path).read_bytes()
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        # Add unique PDF identifier to metadata
        pdf_id = hashlib.md5(pdf_path.encode()).hexdigest()[:8]

        progress(0.2, desc="Extracting document metadata (title, authors)...")
        # Extract and store document header metadata
        header_info = self._extract_document_header(docs, pdf_name, pdf_id)

        # Log extracted info
        if header_info.get('authors'):
            print(f"Extracted authors: {header_info['authors']}")
        if header_info.get('title'):
            print(f"Extracted title: {header_info['title']}")

        progress(0.3, desc=f"Loaded {len(docs)} pages. Chunking...")

        chunk_counter = len(self.documents)

        if use_semantic_chunking:
            splits = []
            fallback_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=150,
                separators=["\n\n", "\n", ". ", " ", ""],
                length_function=len,
            )
            for i, doc in enumerate(docs):
                progress(0.3 + (0.3 * i / len(docs)), desc=f"Semantic chunking page {i+1}/{len(docs)}...")
                page_text = doc.page_content or ""
                if not page_text.strip():
                    continue
                try:
                    semantic_chunks = self.semantic_chunker.chunk_document(page_text)
                except ZeroDivisionError:
                    # Degenerate sentence embeddings are still indexable with ordinary text chunks.
                    semantic_chunks = fallback_splitter.split_text(page_text)
                for chunk in semantic_chunks:
                    if not chunk or not chunk.strip():
                        continue
                    chunk_counter += 1
                    # Mark first page chunks as header chunks
                    is_header = doc.metadata.get('page', 0) == 0
                    splits.append(Document(
                        page_content=chunk,
                        metadata={
                            'page': doc.metadata.get('page', 0),
                            'source': pdf_path,
                            'pdf_name': pdf_name,
                            'pdf_id': pdf_id,
                            'chunk_id': f"{pdf_id}-{chunk_counter}",
                            'is_header': is_header
                        }
                    ))
        else:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=150,
                separators=["\n\n", "\n", ". ", " ", ""],
                length_function=len
            )
            splits = text_splitter.split_documents(docs)
            splits = [split for split in splits if split.page_content and split.page_content.strip()]
            # Add PDF metadata
            for split in splits:
                chunk_counter += 1
                is_header = split.metadata.get('page', 0) == 0
                split.metadata['pdf_name'] = pdf_name
                split.metadata['pdf_id'] = pdf_id
                split.metadata['chunk_id'] = f"{pdf_id}-{chunk_counter}"
                split.metadata['is_header'] = is_header

        # Build both indexes before changing the live collection. If either build fails,
        # the previous documents and retrievers remain consistent.
        if not splits:
            raise ValueError(f"No readable text was found in {pdf_name}.")
        candidate_documents = [
            doc for doc in self.documents + splits
            if (doc.page_content or "").strip()
        ]
        total_pages = max([doc.metadata.get('page', 0) for doc in docs]) + 1
        pdf_info = {
            'path': pdf_path,
            'pages': total_pages,
            'chunks': len(splits),
            'pdf_id': pdf_id,
            'added': datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        progress(0.7, desc=f"Rebuilding Vector Index ({len(candidate_documents)} total chunks)...")
        try:
            vector_db = Chroma.from_documents(
                documents=candidate_documents,
                embedding=self.embedding_model,
                collection_name="rag_gradio_v3"
            )
        except ZeroDivisionError as exc:
            raise RuntimeError(
                f"Vector embedding failed while indexing {len(splits)} non-empty text chunks. "
                "Try disabling semantic chunking or re-exporting the PDF."
            ) from exc

        progress(0.9, desc="Rebuilding Keyword Index...")
        bm25_retriever = BM25Retriever.from_documents(candidate_documents)

        self.documents = candidate_documents
        self.vector_db = vector_db
        self.bm25_retriever = bm25_retriever
        self.pdf_metadata[pdf_name] = pdf_info
        self.doc_headers[pdf_name] = header_info
        self.pdf_files[pdf_name] = pdf_bytes
        self.cache = QueryCache()

        progress(1.0, desc="Complete")

        # Build return message with extracted metadata
        extracted_info = ""
        if header_info.get('title'):
            extracted_info += f"\n**Title:** {header_info['title']}"
        if header_info.get('authors'):
            extracted_info += f"\n**Authors:** {', '.join(header_info['authors'])}"

        return f"""**Document Added Successfully**

**File:** {pdf_name}
**Pages:** {total_pages}
**Chunks:** {len(splits)}
{extracted_info}

**Total Collection:**
- {len(self.pdf_metadata)} document(s)
- {len(self.documents)} total chunks

Ready to answer questions."""

    def clear_all_documents(self):
        """Clear all loaded documents"""
        self.documents = []
        self.pdf_metadata = {}
        self.pdf_files = {}
        self.doc_headers = {}  # Clear headers too
        self.vector_db = None
        self.bm25_retriever = None
        self.cache = QueryCache()  # Clear cache too
        return "All documents cleared."

    def remove_document(self, pdf_name: str) -> str:
        """Remove one PDF and its passages from both retrieval indexes."""
        info = self.pdf_metadata.get(pdf_name)
        if not info:
            return f"Error: '{pdf_name}' is not in the document library."

        pdf_id = info.get('pdf_id')
        remaining = [
            doc for doc in self.documents
            if doc.metadata.get('pdf_id') != pdf_id and doc.metadata.get('pdf_name') != pdf_name
        ]
        try:
            bm25_retriever = BM25Retriever.from_documents(remaining) if remaining else None
            if self.vector_db is not None and pdf_id:
                self.vector_db.delete(where={"pdf_id": pdf_id})
            self.documents = remaining
            self.pdf_metadata.pop(pdf_name, None)
            self.pdf_files.pop(pdf_name, None)
            self.doc_headers.pop(pdf_name, None)
            self.bm25_retriever = bm25_retriever
            if not remaining:
                self.vector_db = None
            self.cache = QueryCache()
            return f"Removed '{pdf_name}' from the library and retrieval indexes."
        except Exception as exc:
            return f"Error removing '{pdf_name}': {exc}"

    def _ensure_retrieval_indexes(self) -> bool:
        """Repair missing in-memory indexes after an interrupted older ingestion."""
        if not self.documents:
            return False
        if self.vector_db is None:
            self.vector_db = Chroma.from_documents(
                documents=self.documents,
                embedding=self.embedding_model,
                collection_name="rag_gradio_v3",
            )
        if self.bm25_retriever is None:
            self.bm25_retriever = BM25Retriever.from_documents(self.documents)
        return True

    def _retrieve_with_rrf(self, query: str, k: int = 5, fetch_factor: int = 2, prioritize_header: bool = False) -> List[Document]:
        if not self._ensure_retrieval_indexes():
            return []
        fetch_k = max(k * fetch_factor, k)
        vector_docs = self.vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": fetch_k, "fetch_k": fetch_k * 2, "lambda_mult": 0.6}
        ).invoke(query)
        self.bm25_retriever.k = fetch_k
        keyword_docs = self.bm25_retriever.invoke(query)

        # If prioritizing header, add first-page chunks
        if prioritize_header:
            header_docs = [doc for doc in self.documents if doc.metadata.get('is_header', False)]
            fused_docs = ReciprocalRankFusion.fuse([vector_docs, keyword_docs, header_docs])
        else:
            fused_docs = ReciprocalRankFusion.fuse([vector_docs, keyword_docs])

        return fused_docs[:fetch_k]

    def _rerank_documents(self, query: str, documents: List[Document], top_k: int = 5, force_comparison: bool = False, boost_header: bool = False) -> List[Tuple[Document, float]]:
        if not documents:
            return []

        # For comparison queries, boost documents that likely contain comparative info
        is_comparison = force_comparison or any(word in query.lower() for word in ['compare', 'difference', 'differ', 'versus', 'vs'])

        pairs = [[query, doc.page_content] for doc in documents]
        scores = self.cross_encoder.predict(pairs)

        # Boost scores for docs that contain comparison keywords
        if is_comparison:
            comparison_keywords = ['compared to', 'in contrast', 'difference', 'whereas', 'unlike', 'while', 'however']
            for i, doc in enumerate(documents):
                content_lower = doc.page_content.lower()
                keyword_count = sum(1 for kw in comparison_keywords if kw in content_lower)
                if keyword_count > 0:
                    scores[i] *= (1 + 0.1 * keyword_count)  # Boost by 10% per keyword

        # Boost header chunks for metadata-like queries
        if boost_header:
            for i, doc in enumerate(documents):
                if doc.metadata.get('is_header', False) or doc.metadata.get('page', 99) == 0:
                    scores[i] *= 1.5  # 50% boost for first page content

        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:top_k]

    def _dedupe_documents(self, documents: List[Document]) -> List[Document]:
        deduped = []
        seen = set()
        for doc in documents:
            key = doc.metadata.get('chunk_id') or f"{doc.metadata.get('pdf_id', 'unknown')}::{hashlib.md5(doc.page_content.encode()).hexdigest()}"
            if key in seen:
                continue
            seen.add(key)
            deduped.append(doc)
        return deduped

    def _ensure_pdf_diversity(self, query: str, documents: List[Document], target_docs: int = 2, per_pdf: int = 3) -> List[Document]:
        if not documents or not self.pdf_metadata:
            return documents

        seen_ids = set(doc.metadata.get('pdf_id') for doc in documents if doc.metadata.get('pdf_id'))
        if len(seen_ids) >= target_docs:
            return documents

        missing_ids = [info['pdf_id'] for info in self.pdf_metadata.values() if info['pdf_id'] not in seen_ids]
        extra_docs = []
        for pdf_id in missing_ids[:max(0, target_docs - len(seen_ids))]:
            filtered_docs = self.vector_db.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": per_pdf,
                    "fetch_k": per_pdf * 2,
                    "lambda_mult": 0.6,
                    "filter": {"pdf_id": pdf_id}
                }
            ).invoke(query)
            extra_docs.extend(filtered_docs)

        combined = documents + extra_docs
        return self._dedupe_documents(combined)

    def _create_citation_card(self, idx: int, doc: Document, page_text: str) -> str:
        """Show the page label and only the first and last two context words."""
        raw_page = doc.metadata.get('page', 'Unknown')
        try:
            page = int(raw_page) + 1  # PyPDFLoader stores zero-based page indices.
        except (TypeError, ValueError):
            page = raw_page
        text = re.sub(r'\s+', ' ', page_text).strip()
        words = text.split()
        if len(words) > 4:
            excerpt = f"{' '.join(words[:2])} ... {' '.join(words[-2:])}"
        else:
            excerpt = " ".join(words)
        return (
            '<div class="nx-source-row nx-source-row-v2">'
            f'<b>Page {escape(str(page))}:</b> {escape(excerpt)}</div>'
        )

    def chat(self, query: str, use_hyde: bool = False, use_multi_query: bool = True, progress=None):
        if progress is None:
            progress = lambda *a, **kw: None
        """Enhanced chat with better answers and citations"""
        if not self._ensure_retrieval_indexes():
            return "Please upload at least one document first.", "", ""

        cache_key = json.dumps({
            "query": query.strip().casefold(),
            "hyde": bool(use_hyde),
            "multi_query": bool(use_multi_query),
            "documents": sorted(
                (str(name), str(info.get("pdf_id", "")))
                for name, info in self.pdf_metadata.items()
            ),
        }, sort_keys=True, ensure_ascii=False)
        cached_response = self.cache.get(cache_key)
        if cached_response is not None:
            progress(1.0, desc="Answer ready from cache.")
            return cached_response

        # Check if this is a metadata query (authors, title, etc.)
        is_metadata_query, metadata_type = self._is_metadata_query(query)
        if is_metadata_query and self.doc_headers:
            progress(0.5, desc=f"Retrieving {metadata_type} from document metadata...")
            answer, citations, metadata = self._answer_metadata_query(query, metadata_type)
            progress(1.0, desc="Complete")
            result = (answer, citations, metadata)
            self.cache.set(cache_key, result)
            return result

        progress(0.1, desc="Classifying query...")
        profile = self._classify_query(query)
        k = profile.k

        # Check if query might need header info (about the paper itself)
        needs_header_boost = any(word in query.lower() for word in
            ['paper', 'study', 'research', 'introduction', 'propose', 'contribution', 'this work'])

        base_queries = [query]

        if use_multi_query:
            progress(0.22, desc="Expanding query variants...")
            expanded_queries = self._expand_query(query)
            base_queries.extend(expanded_queries[:2])

        if use_hyde:
            progress(0.32, desc="Generating HyDE document...")
            hyde_doc = self._generate_hyde_document(query)
            base_queries.append(hyde_doc)

        progress(0.45, desc="Retrieving candidates (MMR + BM25)...")
        retrieval_results = []
        for bq in base_queries:
            retrieval_results.append(self._retrieve_with_rrf(bq, k=k, fetch_factor=2, prioritize_header=needs_header_boost))

        fused_docs = ReciprocalRankFusion.fuse(retrieval_results)
        fused_docs = self._dedupe_documents(fused_docs)[:max(k * 3, k)]

        if profile.needs_multi_docs and len(self.pdf_metadata) > 1:
            fused_docs = self._ensure_pdf_diversity(
                query,
                fused_docs,
                target_docs=min(3, len(self.pdf_metadata)),
                per_pdf=max(2, k // 3)
            )

        progress(0.7, desc="Re-ranking with CrossEncoder...")
        reranked_docs = self._rerank_documents(query, fused_docs, top_k=max(5, k),
                                                force_comparison=profile.requires_comparison,
                                                boost_header=needs_header_boost)

        progress(0.8, desc="Building context...")

        # Label context passages for the model; the user sees page sources separately.
        context_parts = []
        citation_pages = {}

        for idx, (doc, score) in enumerate(reranked_docs, 1):
            # Add to context
            context_parts.append(f"[Source {idx}]: {doc.page_content}\n")

            page_key = (doc.metadata.get('pdf_id'), doc.metadata.get('page'), doc.metadata.get('pdf_name'))
            citation_pages.setdefault(page_key, doc)

        context_str = "\n".join(context_parts)
        citation_cards = []
        def source_page_order(entry):
            page_key, _ = entry
            try:
                page_number = int(page_key[1])
            except (TypeError, ValueError):
                page_number = 10**9
            return str(page_key[2]).casefold(), page_number

        ordered_citation_pages = sorted(citation_pages.items(), key=source_page_order)
        for idx, (page_key, doc) in enumerate(ordered_citation_pages, 1):
            pdf_id, page_number, _ = page_key
            page_chunks = [
                chunk.page_content for chunk in self.documents
                if chunk.metadata.get('pdf_id') == pdf_id
                and chunk.metadata.get('page') == page_number
            ]
            page_text = "\n".join(page_chunks) or doc.page_content
            citation_cards.append(self._create_citation_card(idx, doc, page_text))

        # Enhanced prompt for better answers
        is_comparison = profile.requires_comparison
        style_hint = ""
        if profile.answer_style == 'bullets':
            style_hint = "Use concise bullet points."
        elif profile.answer_style == 'steps':
            style_hint = "Use numbered steps when explaining processes."

        style_instruction = style_hint or "Keep structure aligned to the question type."

        if is_comparison:
            prompt = f"""You are an expert AI assistant analyzing academic/technical documents. Answer this COMPARISON question with precision and structure.

## COMPARISON QUESTION TYPE

## CRITICAL INSTRUCTIONS:
1. **Start with a direct comparison statement** - Don't give background first
2. **Use a structured format:**
   - Brief 1-2 sentence overview of what's being compared
   - Bullet points listing specific differences
   - Each bullet should be concrete and factual
3. **Be specific with numbers, names, and technical details** from the sources
4. Keep the answer clean; source pages are listed separately, so do not add inline citation markers.
5. **If sources lack comparison info**, explicitly state: "The provided sources do not contain direct comparison information on [aspect]. Based on what's available: [answer what you can]"

## CONTEXT FROM DOCUMENTS:
{context_str}

## COMPARISON QUESTION:
{query}

## STRUCTURED COMPARISON ANSWER:
"""
        else:
            prompt = f"""You are an expert AI assistant analyzing academic/technical documents. Your goal is to provide accurate, well-structured, and comprehensive answers.

## QUERY TYPE: {profile.query_type.upper()}

## INSTRUCTIONS:
1. **Answer the question directly in the first sentence** - Don't start with background
2. **Do not add inline citation markers**; source pages are shown separately below the answer.
3. **Structure your answer clearly:**
   - For factoid queries: Direct answer (2-3 sentences) with supporting details
   - For complex queries: Organized explanation with bullet points or numbered lists
   - For "explain" queries: Start with simple definition, then elaborate
4. **Be comprehensive but concise** - NO repetition or filler words
5. **Use specific facts**: numbers, names, technical terms from sources
6. **If information is insufficient**, state: "The sources provided do not fully address [aspect]. Based on available information: [what you can answer]"
7. {style_instruction}
8. For questions such as "What is this file/document about?", answer in 2-3 clear sentences: state its purpose and main subject, then one key detail. Avoid generic introductions, repeated context, and explanations of your process.

## CONTEXT FROM DOCUMENTS:
{context_str}

## QUESTION:
{query}

## YOUR ANSWER:
"""

        progress(0.9, desc="Generating enhanced answer...")
        try:
            response = self.llm.invoke(prompt)
            answer = response.content

            # Add verification step for complex queries and comparisons
            if profile.query_type in ['summary', 'comparison', 'reasoning'] or is_comparison:
                verify_prompt = f"""Review this answer for a {profile.query_type} query. Check if it:

Question: {query}

Answer: {answer}

**Evaluation Criteria:**
1. **Directness**: Does it answer the question in the first sentence?
2. **Structure**: Is it well-organized with bullet points for complex info?
3. **Specificity**: Does it use concrete facts/numbers from sources?
4. **Completeness**: Does it address all parts of the question?
5. **No fluff**: Is it concise without repetition?
6. Do not add inline source markers. For a question asking what a file/document is about, keep the final answer to 2-3 sentences covering its purpose and main subject.

If the answer has issues, provide an IMPROVED VERSION following this format:
- Start with direct answer
- Use bullet points for lists/comparisons
- Include specific facts supported by the provided sources; do not add inline citation markers
- Be concise

If it's already good, respond with only: "VERIFIED"

Your response:"""

                verify_response = self.llm.invoke(verify_prompt)
                if "VERIFIED" not in verify_response.content.upper():
                    # Extract improved answer (remove any preamble)
                    improved = verify_response.content
                    if "IMPROVED VERSION" in improved or "Here" in improved[:50]:
                        # Find where actual answer starts
                        lines = improved.split('\n')
                        answer_lines = []
                        started = False
                        for line in lines:
                            if started or (line.strip() and not line.strip().startswith(('**', 'If', 'Your', 'The answer'))):
                                started = True
                                answer_lines.append(line)
                        if answer_lines:
                            answer = '\n'.join(answer_lines)
                    else:
                        answer = improved

            # Format citations
            citations_html = "\n".join(citation_cards)

            # Metadata
            metadata = f"""**Query Type:** {profile.query_type.title()} | **Multi-Doc:** {"Yes" if profile.needs_multi_docs else "No"} | **Sources Used:** {len(reranked_docs)} | **Documents Searched:** {len(self.pdf_metadata)}"""

            progress(1.0, desc="Complete")
            result = (answer, citations_html, metadata)
            self.cache.set(cache_key, result)
            return result

        except Exception as e:
            return f"Error: {str(e)}", "", ""

    def summarize_document(self, max_chunks: int = None, progress=None, pdf_name: str = None):
        if progress is None:
            progress = lambda *a, **kw: None
        """Generate document summary"""
        if not self.documents:
            return "No document loaded.", ""

        source_documents = [
            doc for doc in self.documents
            if pdf_name is None or doc.metadata.get('pdf_name') == pdf_name
        ]
        if not source_documents:
            return f"No indexed content found for {pdf_name}.", ""
        chunks_to_process = source_documents[:max_chunks] if max_chunks else source_documents
        total_chunks = len(chunks_to_process)
        documents_included = sorted({doc.metadata.get('pdf_name', 'Unknown') for doc in chunks_to_process})

        progress(0.1, desc=f"Processing {total_chunks} chunks...")

        chunk_summaries = []
        batch_size = 10

        for i in range(0, total_chunks, batch_size):
            batch = chunks_to_process[i:i+batch_size]
            batch_text = "\n\n---\n\n".join([doc.page_content for doc in batch])

            progress(0.1 + (0.6 * i / total_chunks), desc=f"Summarizing chunks {i+1}-{min(i+batch_size, total_chunks)}...")

            map_prompt = f"""Summarize the key points from this document section in 3-5 bullet points:

{batch_text}

Key Points:"""

            try:
                response = self.llm.invoke(map_prompt)
                chunk_summaries.append(response.content)
            except Exception as e:
                continue

        progress(0.8, desc="Synthesizing final summary...")

        combined_summaries = "\n\n".join(chunk_summaries)

        reduce_prompt = f"""You are summarizing documents. Below are summaries of different sections.
The selected file(s) are: {', '.join(documents_included)}.

Create a comprehensive, well-structured summary that includes:

1. **Overview**: What are these documents about? (2-3 sentences)
2. **Main Topics**: Key themes and subjects covered (bullet points)
3. **Important Details**: Critical information, findings, or arguments (3-5 points)
4. **Conclusion**: Overall takeaway or significance

Section Summaries:
{combined_summaries}

## COMPREHENSIVE SUMMARY:"""

        try:
            final_response = self.llm.invoke(reduce_prompt)
            summary = final_response.content

            # Build metadata
            metadata = f"""## Summary Statistics

**Documents Analyzed:** {len(documents_included)}
**Total Chunks:** {total_chunks}
**Total Pages:** {sum(self.pdf_metadata.get(name, {}).get('pages', 0) for name in documents_included)}

### Documents Included:
"""
            for name in documents_included:
                info = self.pdf_metadata.get(name, {})
                metadata += f"- **{name}** ({info['pages']} pages)\n"

            progress(1.0, desc="Complete")
            return summary, metadata

        except Exception as e:
            return f"Error: {str(e)}", ""
