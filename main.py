import os
from googletrans import Translator
import threading
import time
from datetime import datetime

class TranslationError(Exception):
    pass

def translate_to_bengali(english_sentence):
    translator = Translator()
    try:
        translated = translator.translate(english_sentence, dest='bn')
        bengali_sentence = translated.text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        bengali_sentence = " [Translation Error]"
        raise TranslationError("Translation error occurred")
    return bengali_sentence

# This function will be run in each thread
def translate_line(line, index):
    parts = line.split("+++$+++")

    if len(parts) >= 5:
        english_sentence = parts[-1].strip()
        try:
            bengali_sentence = " " + translate_to_bengali(english_sentence)
            reconstructed_line = '+++$+++'.join(parts[:-1] + [bengali_sentence])
            translated_lines[index] = reconstructed_line + '\n'
            print(reconstructed_line)
        except TranslationError:
            # Handle the translation error by stopping and saving the progress
            print("Translation error occurred. Stopping...")
            save_and_exit(index)

        # Delay to handle rate limit
        time.sleep(1)

def save_and_exit(index):
    # Create a unique output file name with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_output_file = f"translated_movie_lines_{timestamp}.txt"

    # Write the translated lines to the unique output file
    with open(unique_output_file, "w", encoding="utf-8") as outfile:
        outfile.writelines(translated_lines)

    print(f"Translation completed. Translated lines saved to {unique_output_file}")

    # Remove translated lines from the input file
    with open(input_file, "w", encoding="latin-1") as infile:
        remaining_lines = [line for i, line in enumerate(lines) if translated_lines[i] is None]
        infile.writelines(remaining_lines)

    print(f"Translated lines removed from {input_file}")

    # Exit the program
    exit()

input_file = "movie_lines.txt"

if not os.path.exists(input_file):
    print(f"Input file '{input_file}' not found.")
    exit()

with open(input_file, "r", encoding="latin-1") as infile:
    lines = infile.readlines()

translated_lines = [None]*len(lines)
threads = []

for i, line in enumerate(lines):
    thread = threading.Thread(target=translate_line, args=(line, i))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Save the remaining lines and exit
save_and_exit(len(lines))
