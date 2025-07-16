import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import string
from difflib import SequenceMatcher
import json
import os

# Download required NLTK data (run once)
# nltk.download('punkt')

class UrduSpellChecker:
    def __init__(self):
        # Common Urdu words dictionary (you can expand this)
        self.urdu_dictionary = {
            # Religious terms
            'اللہ', 'تعالیٰ', 'قرآن', 'حدیث', 'نماز', 'روزہ', 'زکوۃ', 'حج', 'جنت', 'جہنم',
            'مسلمان', 'اسلام', 'ایمان', 'کافر', 'مومن', 'توبہ', 'استغفار', 'دعا', 'ذکر',
            'صلی', 'علیہ', 'وسلم', 'رضی', 'عنہ', 'عنہا', 'السلام', 'سبحان', 'الحمد',
            'للہ', 'اکبر', 'انشاء', 'آمین', 'بسم', 'الرحمن', 'الرحیم', 'ماشاء',
            
            # Common words
            'یہ', 'وہ', 'کیا', 'کیوں', 'کہاں', 'کب', 'کون', 'کس', 'کتنا', 'کتنی',
            'کیسے', 'کیسا', 'کیسی', 'اور', 'یا', 'لیکن', 'مگر', 'پھر', 'تو', 'سے',
            'میں', 'پر', 'کے', 'کی', 'کا', 'کو', 'نے', 'ہے', 'ہیں', 'تھا', 'تھی',
            'تھے', 'گا', 'گی', 'گے', 'ہوا', 'ہوی', 'ہوئے', 'کیا', 'کی', 'کیے',
            'دیا', 'دی', 'دیے', 'لیا', 'لی', 'لیے', 'آیا', 'آئی', 'آئے', 'گیا',
            'گئی', 'گئے', 'چاہیے', 'سکتا', 'سکتی', 'سکتے', 'پڑتا', 'پڑتی', 'پڑتے',
            'ہونا', 'کرنا', 'دینا', 'لینا', 'آنا', 'جانا', 'پڑنا', 'رکھنا', 'دیکھنا',
            'سننا', 'کہنا', 'بولنا', 'لکھنا', 'پڑھنا', 'سیکھنا', 'سکھانا', 'سمجھنا',
            'سمجھانا', 'بتانا', 'پتا', 'معلوم', 'خبر', 'بات', 'کام', 'وقت', 'دن',
            'رات', 'صبح', 'شام', 'دوپہر', 'آج', 'کل', 'پرسوں', 'اب', 'پہلے', 'بعد',
            'اوپر', 'نیچے', 'آگے', 'پیچھے', 'دائیں', 'بائیں', 'اندر', 'باہر', 'یہاں',
            'وہاں', 'کہیں', 'سب', 'کچھ', 'کوئی', 'کسی', 'ہر', 'ہم', 'آپ', 'میں',
            'تم', 'تو', 'وہ', 'یہ', 'اس', 'ان', 'جو', 'جس', 'جن', 'کہ', 'اگر',
            'اگرچہ', 'حالانکہ', 'بالفرض', 'جب', 'جہاں', 'جدھر', 'جتنا', 'جتنی',
            'جیسا', 'جیسی', 'جیسے', 'مثل', 'طرح', 'طور', 'ویسا', 'ویسی', 'ویسے',
            'ایسا', 'ایسی', 'ایسے', 'اتنا', 'اتنی', 'اتنے', 'بہت', 'زیادہ', 'کم',
            'تھوڑا', 'تھوڑی', 'تھوڑے', 'پورا', 'پوری', 'پورے', 'آدھا', 'آدھی', 'آدھے',
            'اچھا', 'اچھی', 'اچھے', 'برا', 'بری', 'برے', 'بڑا', 'بڑی', 'بڑے',
            'چھوٹا', 'چھوٹی', 'چھوٹے', 'لمبا', 'لمبی', 'لمبے', 'چوڑا', 'چوڑی', 'چوڑے',
            'گہرا', 'گہری', 'گہرے', 'اونچا', 'اونچی', 'اونچے', 'نیچا', 'نیچی', 'نیچے',
            'تیز', 'آہستہ', 'جلدی', 'دیر', 'نیا', 'نئی', 'نئے', 'پرانا', 'پرانی', 'پرانے',
            'صاف', 'گندا', 'گندی', 'گندے', 'سفید', 'کالا', 'کالی', 'کالے', 'لال',
            'ہرا', 'ہری', 'ہرے', 'نیلا', 'نیلی', 'نیلے', 'پیلا', 'پیلی', 'پیلے',
            'گلابی', 'بھورا', 'بھوری', 'بھورے', 'سنہری', 'چاندی', 'سونا', 'چاندی',
            'پانی', 'آگ', 'ہوا', 'زمین', 'آسمان', 'سورج', 'چاند', 'ستارہ', 'ستارے',
            'بادل', 'بارش', 'برف', 'موسم', 'گرمی', 'سردی', 'خوشی', 'غم', 'خوف',
            'امید', 'محبت', 'نفرت', 'غصہ', 'حیرت', 'فکر', 'پریشانی', 'آرام', 'راحت',
            'تکلیف', 'درد', 'بیماری', 'صحت', 'طاقت', 'کمزوری', 'زندگی', 'موت',
            'پیدائش', 'مرنا', 'جینا', 'رونا', 'ہنسنا', 'کھیلنا', 'کھانا', 'پینا',
            'سونا', 'بیٹھنا', 'کھڑا', 'چلنا', 'دوڑنا', 'اڑنا', 'گرنا', 'اٹھنا'
        }
        
        # Common misspellings and their corrections
        self.common_corrections = {
            'اللة': 'اللہ',
            'الله': 'اللہ',
            'تعالا': 'تعالیٰ',
            'قران': 'قرآن',
            'نماض': 'نماز',
            'روضہ': 'روزہ',
            'زکات': 'زکوۃ',
            'حج': 'حج',
            'جنة': 'جنت',
            'جہنم': 'جہنم',
            'مسلمان': 'مسلمان',
            'اسلام': 'اسلام',
            'ایمان': 'ایمان',
            'کافر': 'کافر',
            'مومن': 'مومن',
            'توبة': 'توبہ',
            'استغفار': 'استغفار',
            'دعا': 'دعا',
            'ذکر': 'ذکر',
            'صلي': 'صلی',
            'علیة': 'علیہ',
            'وسلم': 'وسلم',
            'رضي': 'رضی',
            'عنة': 'عنہ',
            'عنہا': 'عنہا',
            'السلام': 'السلام',
            'سبحان': 'سبحان',
            'الحمد': 'الحمد',
            'للة': 'للہ',
            'اکبر': 'اکبر',
            'انشا': 'انشاء',
            'آمین': 'آمین',
            'بسم': 'بسم',
            'الرحمن': 'الرحمن',
            'الرحیم': 'الرحیم',
            'ماشا': 'ماشاء',
            'یے': 'یہ',
            'وے': 'وہ',
            'کیا': 'کیا',
            'کیوں': 'کیوں',
            'کہاں': 'کہاں',
            'کب': 'کب',
            'کون': 'کون',
            'کس': 'کس',
            'کتنا': 'کتنا',
            'کتنی': 'کتنی',
            'کیسے': 'کیسے',
            'کیسا': 'کیسا',
            'کیسی': 'کیسی',
            'اور': 'اور',
            'یا': 'یا',
            'لیکن': 'لیکن',
            'مگر': 'مگر',
            'پھر': 'پھر',
            'تو': 'تو',
            'سے': 'سے',
            'میں': 'میں',
            'پر': 'پر',
            'کے': 'کے',
            'کی': 'کی',
            'کا': 'کا',
            'کو': 'کو',
            'نے': 'نے',
            'ہے': 'ہے',
            'ہیں': 'ہیں',
            'تھا': 'تھا',
            'تھی': 'تھی',
            'تھے': 'تھے',
            'گا': 'گا',
            'گی': 'گی',
            'گے': 'گے',
            'ہوا': 'ہوا',
            'ہوی': 'ہوی',
            'ہوئے': 'ہوئے',
            'کیا': 'کیا',
            'کی': 'کی',
            'کیے': 'کیے',
            'دیا': 'دیا',
            'دی': 'دی',
            'دیے': 'دیے',
            'لیا': 'لیا',
            'لی': 'لی',
            'لیے': 'لیے',
            'آیا': 'آیا',
            'آئی': 'آئی',
            'آئے': 'آئے',
            'گیا': 'گیا',
            'گئی': 'گئی',
            'گئے': 'گئے',
            'چاہیے': 'چاہیے',
            'سکتا': 'سکتا',
            'سکتی': 'سکتی',
            'سکتے': 'سکتے',
            'پڑتا': 'پڑتا',
            'پڑتی': 'پڑتی',
            'پڑتے': 'پڑتے',
            'ہونا': 'ہونا',
            'کرنا': 'کرنا',
            'دینا': 'دینا',
            'لینا': 'لینا',
            'آنا': 'آنا',
            'جانا': 'جانا',
            'پڑنا': 'پڑنا',
            'رکھنا': 'رکھنا',
            'دیکھنا': 'دیکھنا',
            'سننا': 'سننا',
            'کہنا': 'کہنا',
            'بولنا': 'بولنا',
            'لکھنا': 'لکھنا',
            'پڑھنا': 'پڑھنا',
            'سیکھنا': 'سیکھنا',
            'سکھانا': 'سکھانا',
            'سمجھنا': 'سمجھنا',
            'سمجھانا': 'سمجھانا',
            'بتانا': 'بتانا',
            'پتا': 'پتا',
            'معلوم': 'معلوم',
            'خبر': 'خبر',
            'بات': 'بات',
            'کام': 'کام',
            'وقت': 'وقت',
            'دن': 'دن',
            'رات': 'رات',
            'صبح': 'صبح',
            'شام': 'شام',
            'دوپہر': 'دوپہر',
            'آج': 'آج',
            'کل': 'کل',
            'پرسوں': 'پرسوں',
            'اب': 'اب',
            'پہلے': 'پہلے',
            'بعد': 'بعد',
            'اوپر': 'اوپر',
            'نیچے': 'نیچے',
            'آگے': 'آگے',
            'پیچھے': 'پیچھے',
            'دائیں': 'دائیں',
            'بائیں': 'بائیں',
            'اندر': 'اندر',
            'باہر': 'باہر',
            'یہاں': 'یہاں',
            'وہاں': 'وہاں',
            'کہیں': 'کہیں',
            'سب': 'سب',
            'کچھ': 'کچھ',
            'کوئی': 'کوئی',
            'کسی': 'کسی',
            'ہر': 'ہر',
            'ہم': 'ہم',
            'آپ': 'آپ',
            'میں': 'میں',
            'تم': 'تم',
            'تو': 'تو',
            'وہ': 'وہ',
            'یہ': 'یہ',
            'اس': 'اس',
            'ان': 'ان',
            'جو': 'جو',
            'جس': 'جس',
            'جن': 'جن',
            'کہ': 'کہ',
            'اگر': 'اگر',
            'اگرچہ': 'اگرچہ',
            'حالانکہ': 'حالانکہ',
            'بالفرض': 'بالفرض',
            'جب': 'جب',
            'جہاں': 'جہاں',
            'جدھر': 'جدھر',
            'جتنا': 'جتنا',
            'جتنی': 'جتنی',
            'جیسا': 'جیسا',
            'جیسی': 'جیسی',
            'جیسے': 'جیسے',
            'مثل': 'مثل',
            'طرح': 'طرح',
            'طور': 'طور',
            'ویسا': 'ویسا',
            'ویسی': 'ویسی',
            'ویسے': 'ویسے',
            'ایسا': 'ایسا',
            'ایسی': 'ایسی',
            'ایسے': 'ایسے',
            'اتنا': 'اتنا',
            'اتنی': 'اتنی',
            'اتنے': 'اتنے',
            'بہت': 'بہت',
            'زیادہ': 'زیادہ',
            'کم': 'کم',
            'تھوڑا': 'تھوڑا',
            'تھوڑی': 'تھوڑی',
            'تھوڑے': 'تھوڑے',
            'پورا': 'پورا',
            'پوری': 'پوری',
            'پورے': 'پورے',
            'آدھا': 'آدھا',
            'آدھی': 'آدھی',
            'آدھے': 'آدھے',
            'اچھا': 'اچھا',
            'اچھی': 'اچھی',
            'اچھے': 'اچھے',
            'برا': 'برا',
            'بری': 'بری',
            'برے': 'برے',
            'بڑا': 'بڑا',
            'بڑی': 'بڑی',
            'بڑے': 'بڑے',
            'چھوٹا': 'چھوٹا',
            'چھوٹی': 'چھوٹی',
            'چھوٹے': 'چھوٹے',
            'لمبا': 'لمبا',
            'لمبی': 'لمبی',
            'لمبے': 'لمبے',
            'چوڑا': 'چوڑا',
            'چوڑی': 'چوڑی',
            'چوڑے': 'چوڑے',
            'گہرا': 'گہرا',
            'گہری': 'گہری',
            'گہرے': 'گہرے',
            'اونچا': 'اونچا',
            'اونچی': 'اونچی',
            'اونچے': 'اونچے',
            'نیچا': 'نیچا',
            'نیچی': 'نیچی',
            'نیچے': 'نیچے',
            'تیز': 'تیز',
            'آہستہ': 'آہستہ',
            'جلدی': 'جلدی',
            'دیر': 'دیر',
            'نیا': 'نیا',
            'نئی': 'نئی',
            'نئے': 'نئے',
            'پرانا': 'پرانا',
            'پرانی': 'پرانی',
            'پرانے': 'پرانے',
            'صاف': 'صاف',
            'گندا': 'گندا',
            'گندی': 'گندی',
            'گندے': 'گندے',
            'سفید': 'سفید',
            'کالا': 'کالا',
            'کالی': 'کالی',
            'کالے': 'کالے',
            'لال': 'لال',
            'ہرا': 'ہرا',
            'ہری': 'ہری',
            'ہرے': 'ہرے',
            'نیلا': 'نیلا',
            'نیلی': 'نیلی',
            'نیلے': 'نیلے',
            'پیلا': 'پیلا',
            'پیلی': 'پیلی',
            'پیلے': 'پیلے',
            'گلابی': 'گلابی',
            'بھورا': 'بھورا',
            'بھوری': 'بھوری',
            'بھورے': 'بھورے',
            'سنہری': 'سنہری',
            'چاندی': 'چاندی',
            'سونا': 'سونا',
            'چاندی': 'چاندی',
            'پانی': 'پانی',
            'آگ': 'آگ',
            'ہوا': 'ہوا',
            'زمین': 'زمین',
            'آسمان': 'آسمان',
            'سورج': 'سورج',
            'چاند': 'چاند',
            'ستارہ': 'ستارہ',
            'ستارے': 'ستارے',
            'بادل': 'بادل',
            'بارش': 'بارش',
            'برف': 'برف',
            'موسم': 'موسم',
            'گرمی': 'گرمی',
            'سردی': 'سردی',
            'خوشی': 'خوشی',
            'غم': 'غم',
            'خوف': 'خوف',
            'امید': 'امید',
            'محبت': 'محبت',
            'نفرت': 'نفرت',
            'غصہ': 'غصہ',
            'حیرت': 'حیرت',
            'فکر': 'فکر',
            'پریشانی': 'پریشانی',
            'آرام': 'آرام',
            'راحت': 'راحت',
            'تکلیف': 'تکلیف',
            'درد': 'درد',
            'بیماری': 'بیماری',
            'صحت': 'صحت',
            'طاقت': 'طاقت',
            'کمزوری': 'کمزوری',
            'زندگی': 'زندگی',
            'موت': 'موت',
            'پیدائش': 'پیدائش',
            'مرنا': 'مرنا',
            'جینا': 'جینا',
            'رونا': 'رونا',
            'ہنسنا': 'ہنسنا',
            'کھیلنا': 'کھیلنا',
            'کھانا': 'کھانا',
            'پینا': 'پینا',
            'سونا': 'سونا',
            'بیٹھنا': 'بیٹھنا',
            'کھڑا': 'کھڑا',
            'چلنا': 'چلنا',
            'دوڑنا': 'دوڑنا',
            'اڑنا': 'اڑنا',
            'گرنا': 'گرنا',
            'اٹھنا': 'اٹھنا'
        }
        
        # Load custom dictionary if available
        self.load_custom_dictionary()
    
    def load_custom_dictionary(self, file_path="urdu_dictionary.json"):
        """Load custom dictionary from JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    custom_dict = json.load(f)
                    if isinstance(custom_dict, dict):
                        self.common_corrections.update(custom_dict)
                    elif isinstance(custom_dict, list):
                        self.urdu_dictionary.update(custom_dict)
        except Exception as e:
            print(f"Could not load custom dictionary: {e}")
    
    def save_custom_dictionary(self, file_path="urdu_dictionary.json"):
        """Save dictionary to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.common_corrections, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Could not save dictionary: {e}")
    
    def similarity(self, a, b):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a, b).ratio()
    
    def get_suggestions(self, word, max_suggestions=3):
        """Get spelling suggestions for a word"""
        suggestions = []
        
        # Check if word is already correct
        if word in self.urdu_dictionary:
            return [word]
        
        # Check common corrections first
        if word in self.common_corrections:
            return [self.common_corrections[word]]
        
        # Find similar words in dictionary
        for correct_word in self.urdu_dictionary:
            similarity_score = self.similarity(word, correct_word)
            if similarity_score > 0.6:  # Threshold for similarity
                suggestions.append((correct_word, similarity_score))
        
        # Sort by similarity and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [word for word, score in suggestions[:max_suggestions]]
    
    def correct_word(self, word):
        """Correct a single word"""
        # Check exact match in corrections
        if word in self.common_corrections:
            return self.common_corrections[word]
        
        # Check if word is already correct
        if word in self.urdu_dictionary:
            return word
        
        # Get best suggestion
        suggestions = self.get_suggestions(word)
        if suggestions:
            return suggestions[0]
        
        return word  # Return original if no suggestions
    
    def spell_check_text(self, text, auto_correct=True):
        """Spell check entire text"""
        words = text.split()
        corrected_words = []
        corrections_made = []
        
        for word in words:
            # Clean word of punctuation for checking
            clean_word = re.sub(r'[^\w\u0600-\u06FF]', '', word)
            
            if clean_word:
                corrected_word = self.correct_word(clean_word)
                
                if corrected_word != clean_word:
                    corrections_made.append({
                        'original': clean_word,
                        'corrected': corrected_word,
                        'suggestions': self.get_suggestions(clean_word)
                    })
                    
                    if auto_correct:
                        # Replace the clean word in original word (preserve punctuation)
                        final_word = word.replace(clean_word, corrected_word)
                        corrected_words.append(final_word)
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        
        return {
            'corrected_text': ' '.join(corrected_words),
            'corrections': corrections_made,
            'original_text': text
        }
    
    def add_word_to_dictionary(self, word):
        """Add a word to the dictionary"""
        self.urdu_dictionary.add(word)
    
    def add_correction(self, wrong_word, correct_word):
        """Add a correction to the corrections dictionary"""
        self.common_corrections[wrong_word] = correct_word

class UrduTextFormatter:
    def __init__(self):
        self.spell_checker = UrduSpellChecker()
        
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

    def format_transcript(self, text, add_paragraphs=True, spell_check=True, auto_correct=True):
        """Main formatting function with spell checking"""
        spell_check_results = None
        
        # Step 1: Clean the text
        text = self.clean_text(text)
        
        # Step 2: Spell check (if enabled)
        if spell_check:
            spell_check_results = self.spell_checker.spell_check_text(text, auto_correct=auto_correct)
            if auto_correct:
                text = spell_check_results['corrected_text']
        
        # Step 3: Format religious content
        text = self.format_religious_content(text)
        
        # Step 4: Add sentence breaks
        text = self.add_sentence_breaks(text)
        
        # Step 5: Add question marks
        text = self.add_question_marks(text)
        
        # Step 6: Add commas
        text = self.add_commas(text)
        
        # Step 7: Add paragraphs
        if add_paragraphs:
            text = self.add_paragraphs(text)
        
        # Step 8: Final cleanup
        text = re.sub(r'\s+([.!?])', r'\1', text)  # Remove spaces before punctuation
        text = re.sub(r'([.!?])\s*([.!?])', r'\1', text)  # Remove duplicate punctuation
        
        return {
            'formatted_text': text,
            'spell_check_results': spell_check_results
        }

    def get_spell_check_report(self, text):
        """Get detailed spell check report"""
        results = self.spell_checker.spell_check_text(text, auto_correct=False)
        return results
    
    def add_word_to_dictionary(self, word):
        """Add word to spell checker dictionary"""
        self.spell_checker.add_word_to_dictionary(word)
    
    def add_correction(self, wrong_word, correct_word):
        """Add correction to spell checker"""
        self.spell_checker.add_correction(wrong_word, correct_word)
    
    def save_dictionary(self, file_path="urdu_dictionary.json"):
        """Save custom dictionary"""
        self.spell_checker.save_custom_dictionary(file_path)
            
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

# Enhanced usage example with spell checking
def main():
    # Example usage with spell checking
    formatter = UrduTextFormatter()
    
    # Sample Urdu text with some misspellings (replace with your transcription)
    sample_text = """
    اللة تعالا نے قران مجید میں فرمایا ہے کہ نماض قائم کرو اور زکات دو 
    یے بہت اہم بات ہے کہ ہم اپنی عبادت میں مخلص ہوں کیا آپ جانتے ہیں 
    کہ نماض کی کیا اہمیت ہے اس کے بارے میں سوچنا چاہیے
    """
    
    # Get spell check report first (without auto-correction)
    spell_report = formatter.get_spell_check_report(sample_text)
    print("Spell Check Report:")
    print(f"Original: {spell_report['original_text']}")
    print(f"Corrected: {spell_report['corrected_text']}")
    print("\nCorrections made:")
    for correction in spell_report['corrections']:
        print(f"  {correction['original']} → {correction['corrected']}")
        print(f"    Suggestions: {correction['suggestions']}")
    
    # Format the text with spell checking enabled
    result = formatter.format_transcript(sample_text, spell_check=True, auto_correct=True)
    formatted_text = result['formatted_text']
    
    print("\n" + "="*50)
    print("Original text:")
    print(sample_text)
    print("\nFormatted text with spell checking:")
    print(formatted_text)
    
    # Add custom words to dictionary
    formatter.add_word_to_dictionary("خصوصی")
    formatter.add_correction("غلط", "صحیح")
    
    # Save custom dictionary
    formatter.save_dictionary()

# Function to integrate with Whisper
def process_whisper_transcription(audio_file, model_size="large-v2"):
    """Complete pipeline: Whisper transcription + formatting + spell checking"""
    import whisper
    
    # Transcribe audio
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_file, language="ur")
    
    # Format and spell check
    formatter = UrduTextFormatter()
    formatted_result = formatter.format_transcript(
        result["text"], 
        spell_check=True, 
        auto_correct=True
    )
    
    # Save results
    output_data = {
        'original_transcription': result["text"],
        'formatted_text': formatted_result['formatted_text'],
        'spell_corrections': formatted_result['spell_check_results']['corrections'] if formatted_result['spell_check_results'] else [],
        'segments': result.get("segments", [])
    }
    
    # Save to file
    with open("transcription_results.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    with open("formatted_transcript.txt", "w", encoding="utf-8") as f:
        f.write(formatted_result['formatted_text'])
    
    return output_data

# Interactive spell checking function
def interactive_spell_check(text):
    """Interactive spell checking with user input"""
    formatter = UrduTextFormatter()
    spell_report = formatter.get_spell_check_report(text)
    
    corrected_text = text
    
    print("Interactive Spell Check:")
    print("=" * 40)
    
    for correction in spell_report['corrections']:
        print(f"\nFound potential error: '{correction['original']}'")
        print(f"Suggestions: {correction['suggestions']}")
        
        choice = input("Choose correction (number) or 's' to skip, 'a' to add to dictionary: ")
        
        if choice == 's':
            continue
        elif choice == 'a':
            formatter.add_word_to_dictionary(correction['original'])
            print(f"Added '{correction['original']}' to dictionary")
        else:
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(correction['suggestions']):
                    selected_correction = correction['suggestions'][choice_idx]
                    corrected_text = corrected_text.replace(
                        correction['original'], 
                        selected_correction
                    )
                    print(f"Corrected '{correction['original']}' to '{selected_correction}'")
            except (ValueError, IndexError):
                print("Invalid choice, skipping...")
    
    # Save updated dictionary
    formatter.save_dictionary()
    
    # Format the corrected text
    final_result = formatter.format_transcript(corrected_text, spell_check=False)
    return final_result['formatted_text']

if __name__ == "__main__":
    main()