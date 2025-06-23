# Flashcards collection for the MSc in Computer Science
> This repository contains personal flashcards that i have created in order to review some concepts before exams. 

## How to use 
These flashcards are made for the [Anki](https://apps.ankiweb.net/) application, which is a popular flashcard program that uses spaced repetition to help you learn and remember information more effectively.
In order to use these flashcards, you need to have Anki installed on your compute and then import the `.apkg` files into Anki.

In order to generate the `.apkg` files, you can use the pip package [markdown-anki-decks](https://github.com/lukesmurray/markdown-anki-decks).
```bash
pip install markdown-anki-decks
```
Then you can run the following command to generate the `.apkg` files:
```bash
mdankideck <input_directory> <output_directory>
```
Where `<input_directory>` is the directory containing the markdown files and `<output_directory>` is the directory where you want to save the `.apkg` files.
