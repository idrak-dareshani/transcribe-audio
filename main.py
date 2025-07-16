from post_processor import UrduTextFormatter
import json

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

# Function to integrate with Faster Whisper
def process_whisper_transcription(audio_file, model_size="large-v2"):
    """Complete pipeline: Whisper transcription + formatting + spell checking"""
    from faster_whisper import WhisperModel
    
    # Transcribe audio
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
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