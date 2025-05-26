import js

def count_words(text: str) -> int:
    """Counts the number of words in a given string."""
    if not text:
        return 0
    return len(text.split())

def add_paragraph(text: str):
    """Creates a new paragraph element and appends it to the 'output-area'."""
    output_area = js.document.getElementById("output-area")
    new_paragraph = js.document.createElement("p")
    new_paragraph.textContent = text
    output_area.appendChild(new_paragraph)
