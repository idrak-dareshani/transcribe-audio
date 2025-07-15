import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import string

# Download required NLTK data (run once)
# nltk.download('punkt')

class UrduTextFormatter:
    def __init__(self):
        # Common Urdu pause indicators and their replacements
        self.pause_patterns = {
            r'\s+(اور|اور پھر|پھر|لیکن|مگر|البتہ|تاہم)\s+': r'. \1 ',
            r'\s+(کیونکہ|چونکہ|کیا|کہ|جب|جہاں|جو|جس)\s+': r'. \1 ',
            r'\s+(اس لیے|اس وجہ سے|لہذا|اسی طرح)\s+': r'. \1 ',
            r'\s+(آخر میں|آخر کار|نتیجہ|خلاصہ)\s+': r'. \1 ',
            r'\s+(پہلے|دوسرے|تیسرے|چوتھے|پانچویں)\s+': r'. \1 ',
            r'\s+(اگر|اگرچہ|حالانکہ|بالفرض)\s+': r'. \1 ',
        }
        
        # Common Arabic religious phrases in Urdu context
        self.religious_phrases = {
            r'اللہ تعالیٰ': 'اللہ تعالیٰ',
            r'صلی اللہ علیہ وسلم': 'صلی اللہ علیہ وسلم',
            r'رضی اللہ عنہ': 'رضی اللہ عنہ',
            r'رضی اللہ عنہا': 'رضی اللہ عنہا',
            r'علیہ السلام': 'علیہ السلام',
            r'سبحان اللہ': 'سبحان اللہ',
            r'الحمد للہ': 'الحمد للہ',
            r'اللہ اکبر': 'اللہ اکبر',
            r'استغفار': 'استغفار',
            r'توبہ': 'توبہ',
        }
        
        # Question markers in Urdu
        self.question_markers = [
            'کیا', 'کیوں', 'کہاں', 'کب', 'کون', 'کس', 'کتنا', 'کتنی',
            'کیسے', 'کیسا', 'کیسی', 'کہ کیا', 'آیا'
        ]
        
        # Sentence ending indicators
        self.sentence_endings = [
            'ہے', 'ہیں', 'تھا', 'تھی', 'تھے', 'گا', 'گی', 'گے',
            'دیا', 'دی', 'دیے', 'کیا', 'کی', 'کیے', 'ہوا', 'ہوی', 'ہوئے',
            'چاہیے', 'ہونا چاہیے', 'کرنا چاہیے', 'آمین', 'انشاء اللہ'
        ]

    def clean_text(self, text):
        """Basic text cleaning"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove repeated characters (common in transcription errors)
        text = re.sub(r'(.)\1{2,}', r'\1', text)
        
        # Clean up common transcription artifacts
        text = re.sub(r'\s*\.\s*\.\s*', ' ', text)  # Remove scattered dots
        text = re.sub(r'\s*,\s*,\s*', ', ', text)  # Fix double commas
        
        return text.strip()

    def add_sentence_breaks(self, text):
        """Add sentence breaks based on Urdu language patterns"""
        # Split into words
        words = text.split()
        formatted_words = []
        
        for i, word in enumerate(words):
            formatted_words.append(word)
            
            # Check if current word indicates sentence ending
            if any(word.endswith(ending) for ending in self.sentence_endings):
                # Look ahead to see if next word starts a new sentence
                if i + 1 < len(words):
                    next_word = words[i + 1]
                    # Add period if next word starts with capital or is a sentence starter
                    if (next_word[0].isupper() or 
                        any(next_word.startswith(marker) for marker in self.question_markers) or
                        next_word in ['اور', 'لیکن', 'مگر', 'پھر', 'اس', 'یہ', 'وہ']):
                        formatted_words.append('.')
        
        return ' '.join(formatted_words)

    def add_question_marks(self, text):
        """Add question marks to interrogative sentences"""
        sentences = text.split('.')
        formatted_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Check if sentence starts with question marker
                words = sentence.split()
                if words and any(words[0].startswith(marker) for marker in self.question_markers):
                    sentence += '?'
                elif sentence.endswith('ہے') or sentence.endswith('ہیں'):
                    # Check if it's a question based on context
                    if any(marker in sentence for marker in self.question_markers):
                        sentence += '?'
                    else:
                        sentence += '.'
                else:
                    sentence += '.'
                
                formatted_sentences.append(sentence)
        
        return ' '.join(formatted_sentences)

    def add_commas(self, text):
        """Add commas for natural pauses"""
        # Add commas before conjunctions
        text = re.sub(r'\s+(اور|لیکن|مگر|یا|تاہم)\s+', r', \1 ', text)
        
        # Add commas after introductory phrases
        text = re.sub(r'^(جی ہاں|جی نہیں|بالکل|اصل میں|دراصل|حقیقت میں)\s+', r'\1, ', text)
        
        # Add commas in lists
        text = re.sub(r'\s+(پہلے|دوسرے|تیسرے|چوتھے|پانچویں)\s+', r', \1 ', text)
        
        return text

    def add_paragraphs(self, text, max_sentence_per_paragraph=3):
        """Add paragraph breaks"""
        sentences = re.split(r'[.!?]', text)
        paragraphs = []
        current_paragraph = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                current_paragraph.append(sentence)
                
                # Create new paragraph after certain number of sentences
                if len(current_paragraph) >= max_sentence_per_paragraph:
                    paragraphs.append('. '.join(current_paragraph) + '.')
                    current_paragraph = []
        
        # Add remaining sentences
        if current_paragraph:
            paragraphs.append('. '.join(current_paragraph) + '.')
        
        return '\n\n'.join(paragraphs)

    def format_religious_content(self, text):
        """Special formatting for religious content"""
        # Ensure proper spacing around religious phrases
        for phrase in self.religious_phrases:
            text = re.sub(f'({phrase})', r' \1 ', text)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text

    def format_transcript(self, text, add_paragraphs=True):
        """Main formatting function"""
        # Step 1: Clean the text
        text = self.clean_text(text)
        
        # Step 2: Format religious content
        text = self.format_religious_content(text)
        
        # Step 3: Add sentence breaks
        text = self.add_sentence_breaks(text)
        
        # Step 4: Add question marks
        text = self.add_question_marks(text)
        
        # Step 5: Add commas
        text = self.add_commas(text)
        
        # Step 6: Add paragraphs
        if add_paragraphs:
            text = self.add_paragraphs(text)
        
        # Step 7: Final cleanup
        text = re.sub(r'\s+([.!?])', r'\1', text)  # Remove spaces before punctuation
        text = re.sub(r'([.!?])\s*([.!?])', r'\1', text)  # Remove duplicate punctuation
        
        return text

# Alternative approach using machine learning
def format_with_ml_approach(text):
    """
    Alternative approach using pre-trained models
    Note: This requires additional libraries
    """
    try:
        from transformers import pipeline
        
        # Use a multilingual punctuation model
        punctuator = pipeline(
            "token-classification",
            model="oliverguhr/fullstop-punctuation-multilang-large",
            tokenizer="oliverguhr/fullstop-punctuation-multilang-large"
        )
        
        # Process text in chunks (models have token limits)
        def chunk_text(text, max_length=500):
            words = text.split()
            chunks = []
            current_chunk = []
            
            for word in words:
                current_chunk.append(word)
                if len(' '.join(current_chunk)) > max_length:
                    chunks.append(' '.join(current_chunk[:-1]))
                    current_chunk = [word]
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
        
        chunks = chunk_text(text)
        formatted_chunks = []
        
        for chunk in chunks:
            result = punctuator(chunk)
            formatted_text = ""
            current_pos = 0
            
            for item in result:
                if item['entity'] != 'O':  # Not 'Other'
                    formatted_text += text[current_pos:item['start']]
                    if item['entity'] == 'B-PERIOD':
                        formatted_text += '.'
                    elif item['entity'] == 'B-COMMA':
                        formatted_text += ','
                    elif item['entity'] == 'B-QUESTION':
                        formatted_text += '?'
                    elif item['entity'] == 'B-EXCLAMATION':
                        formatted_text += '!'
                    current_pos = item['end']
            
            formatted_text += text[current_pos:]
            formatted_chunks.append(formatted_text)
        
        return ' '.join(formatted_chunks)
    
    except ImportError:
        print("Transformers library not installed. Using rule-based approach.")
        return text

# Usage example
def main():
    # Example usage
    formatter = UrduTextFormatter()
    
    # Sample Urdu text (replace with your transcription)
    sample_text = """
    اللہ تعالیٰ نے قرآن مجید میں فرمایا ہے کہ نماز قائم کرو اور زکوۃ دو 
    یہ بہت اہم بات ہے کہ ہم اپنی عبادت میں مخلص ہوں کیا آپ جانتے ہیں 
    کہ نماز کی کیا اہمیت ہے اس کے بارے میں سوچنا چاہیے
    """
    
    # Format the text
    formatted_text = formatter.format_transcript(sample_text)
    print("Original text:")
    print(sample_text)
    print("\nFormatted text:")
    print(formatted_text)

# if __name__ == "__main__":
#     main()