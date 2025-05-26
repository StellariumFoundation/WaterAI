const pythonCodeTextarea = document.getElementById('python-code');
const runButton = document.getElementById('run-button');
const outputArea = document.getElementById('output-area');

// Elements for actions
const wordCountInput = document.getElementById('text-input-for-word-count');
const wordCountButton = document.getElementById('word-count-button');
const actionResultDisplay = document.getElementById('action-result-display');
const addParagraphInput = document.getElementById('text-input-for-add-paragraph');
const addParagraphButton = document.getElementById('add-paragraph-button');

outputArea.textContent = "Pyodide loading...";

async function main() {
    try {
        let pyodide = await loadPyodide();
        outputArea.textContent = "Pyodide ready. Loading actions.py...";

        // Load actions.py
        const actionsPyContent = await (await fetch('actions.py')).text();
        await pyodide.runPythonAsync(actionsPyContent);
        outputArea.textContent = "Pyodide and actions.py ready.";

        // Get Python functions
        const countWords = pyodide.globals.get('count_words');
        const addParagraph = pyodide.globals.get('add_paragraph');

        runButton.addEventListener('click', async () => {
            const pythonCode = pythonCodeTextarea.value;
            // Clear previous output from python execution, but not from addParagraph
            // outputArea.textContent = ''; 
            try {
                // Redirect Python's stdout to a custom function
                pyodide.setStdout({
                    batched: (str) => {
                        outputArea.textContent += str + '\n';
                    }
                });
                 // Redirect Python's stderr to a custom function
                pyodide.setStderr({
                    batched: (str) => {
                        outputArea.textContent += str + '\n';
                    }
                });
                await pyodide.runPythonAsync(pythonCode);
            } catch (err) {
                outputArea.textContent += err.toString();
            }
        });

        // Word Count Action
        if (wordCountButton) {
            wordCountButton.addEventListener('click', () => {
                const text = wordCountInput.value;
                const count = countWords(text);
                actionResultDisplay.textContent = `Word count: ${count}`;
                wordCountInput.value = ''; // Clear input
            });
        }

        // Add Paragraph Action
        if (addParagraphButton) {
            addParagraphButton.addEventListener('click', () => {
                const text = addParagraphInput.value;
                addParagraph(text);
                addParagraphInput.value = ''; // Clear input after adding
            });
        }

    } catch (err) {
        outputArea.textContent = "Error: " + err.toString();
    }
}

main();
