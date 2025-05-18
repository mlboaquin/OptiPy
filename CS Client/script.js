let typewriterTimeout = null;
let optimizingInterval = null;

function copyText() {

    const outputTextarea = document.querySelector('.output textarea');
    outputTextarea.select();
    outputTextarea.setSelectionRange(0, 99999);
  
    navigator.clipboard.writeText(outputTextarea.value)
        .then(() => {
            // Optional: Add some visual feedback
            const copyIcon = document.querySelector('.output .delete-icon');
            copyIcon.style.opacity = '0.5';
            setTimeout(() => {
                copyIcon.style.opacity = '1';
            }, 200);
        })
        .catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }


function clearText() {
    // Stop the typewriter animation if running
    if (typewriterTimeout) {
        clearTimeout(typewriterTimeout);
        typewriterTimeout = null;
    }

    // Clear the textarea content
    document.getElementById('input-text').value = '';
    document.getElementById('output-text').value = '';

    // Show the paste button and upload image button again
    document.querySelector('.paste-btn').style.display = 'inline-block';
    document.querySelector('.button-group svg').style.display = 'inline-block';

    // Optionally, reset revisions or other UI elements as before
    const revisionsContainer = document.querySelector('.revisions');
    if (revisionsContainer) {
        revisionsContainer.innerHTML = `
            <span class="revisionsp1">
            <b>Your revisions will appear here.</b>
            </span>
            <span class="revisionsp2">
            Start writing to see your corrections.
            </span>
        `;
    }
    
    
}

function pasteText() {
    // Hide the paste button once clicked
    const pasteButton = document.querySelector('.paste-btn');
    pasteButton.style.display = 'none'; // Hide the paste button
    
    // Paste the clipboard content into the textarea
    navigator.clipboard.readText().then(text => {
      document.querySelector('textarea').value = text;
    });
}

  
function handleKeyDown(event) {
    if (event.key === 'Enter') {
      const pasteButton = document.querySelector('.paste-btn');
      if (pasteButton) {
        pasteButton.style.display = 'none';
      }
      
      event.preventDefault(); 
      optimize(); 
    }
  }

  const inputArea = document.getElementById('input-text');
  if (inputArea) {
    inputArea.addEventListener('keydown', handleKeyDown);
  }
  
  function hidePasteButtonOnPaste() {
    const inputArea = document.getElementById('input-text');
    const pasteButton = document.querySelector('.paste-btn');
  
    if (inputArea && pasteButton) {
      inputArea.addEventListener('paste', () => {
        pasteButton.style.display = 'none';
      });
    }
}
  
  
hidePasteButtonOnPaste();
async function optimize() {
    const inputText = document.getElementById('input-text').value;
    const outputText = document.getElementById('output-text');
    const optimizeButton = document.getElementById('optimize-btn');

    // Show loading message with shimmer
    outputText.classList.add('shimmer');
    if (optimizeButton) {
        alert('Please check your code for accuracy before optimizing.');
        optimizeButton.disabled = true;
        optimizeButton.classList.add('shimmer');
      }
      
      outputText.value = 'Please wait while your code is being generated...';


    try {
        const response = await fetch('http://127.0.0.1:5000/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: inputText })
        });

        const text = await response.text();
        console.log("Raw response:", text);
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            outputText.classList.remove('shimmer');
            outputText.value = 'Server returned invalid JSON.';
            return;
        }

        if (response.ok) {
            outputText.classList.remove('shimmer');
            if (data.optimized_code) {
                outputText.value = data.optimized_code;
            } else if (data.error) {
                outputText.value = `Error: ${data.error}`;
            } else {
                outputText.value = 'No optimized code returned.';
            }

            if (data.changes) updateChanges(data.changes);
            if (data.metrics) updateMetrics(data.metrics);
        } else {
            outputText.classList.remove('shimmer');
            outputText.value = `Error: ${data.error || 'Unknown error'}`;
        }
    } catch (error) {
        console.error('Error:', error);
        outputText.classList.remove('shimmer');
        outputText.value = 'Error connecting to the server. Please try again.';
    } finally {
        if (optimizeButton) {
           
            optimizeButton.disabled = false;
            optimizeButton.classList.remove('shimmer');
        }
    }
}


function updateChanges(changes) {
    const revisionsBox1 = document.querySelector('.revisionsp1');
    const revisionsBox2 = document.querySelector('.revisionsp2');

    // Clear existing content
    revisionsBox1.innerHTML = '';
    revisionsBox2.innerHTML = '';

    // Create and append list items with styling
    changes.forEach((change, index) => {
        const li = document.createElement('li');
        li.textContent = change;
        li.style.fontWeight = 'normal';
        li.style.fontSize = '16px';

        if (index % 2 === 0) {
            revisionsBox1.appendChild(li);
        } else {
            revisionsBox2.appendChild(li);
        }
    });

    // Show fallback message if no changes
    if (changes.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'No changes made.';
        li.style.fontWeight = 'normal';
        li.style.fontSize = '16px';
        revisionsBox1.appendChild(li);
    }
    }

function toScientificWithSuperscript(num, digits = 6) {
    if (num === 0) return '0';
    const exp = Math.floor(Math.log10(Math.abs(num)));
    const mantissa = (num / Math.pow(10, exp)).toFixed(digits);
    const superscriptDigits = {
        '-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    };
    const expStr = String(exp).split('').map(c => superscriptDigits[c] || c).join('');
    return `${mantissa} × 10${expStr}`;
}

function getResultHTML(value, unit) {
    if (value > 0) {
        return `<span style="color:#27ae60;"><span style='font-size:1.1em;'>▲</span> ${toScientificWithSuperscript(value)} ${unit}</span>`;
    } else if (value < 0) {
        return `<span style="color:#e74c3c; font-size:1.1em;">▼ ${toScientificWithSuperscript(Math.abs(value))} ${unit}</span>`;
    } else {
        return `<span>${toScientificWithSuperscript(value)} ${unit}</span>`;
    }
}

function updateMetrics(metrics) {
    const originalBox = document.getElementById('original-metrics');
    const optimizedBox = document.getElementById('optimized-metrics');
    const resultsBox = document.getElementById('results-metrics');

    if (metrics && metrics.original && metrics.optimized) {
        // Compute reductions
        const emissionsReduction = metrics.original.emissions - metrics.optimized.emissions;
        const energyReduction = metrics.original.energy - metrics.optimized.energy;
        const timeReduction = metrics.original.execution_time - metrics.optimized.execution_time;

        // Update Original Code metrics
        originalBox.innerHTML = `
            <li><i class="icon ion-md-checkmark-circle-outline demo"></i><b>EMISSION:</b><br> ${toScientificWithSuperscript(metrics.original.emissions)} kg CO2eq </li>
            <li><i class="icon ion-md-checkmark-circle-outline demo"></i><b>ENERGY:</b><br> ${toScientificWithSuperscript(metrics.original.energy)} kWh</li>
            <li><i class="icon ion-md-checkmark-circle-outline demo"></i><b>EXECUTION TIME:</b><br> ${metrics.original.execution_time} s</li>
        `;

        // Update Optimized Code metrics
        optimizedBox.innerHTML = `
            <li><i class="icon ion-md-checkmark-circle-outline demo"></i><b>EMISSION:</b><br> ${toScientificWithSuperscript(metrics.optimized.emissions)} kg CO2eq</li>
            <li><i class="icon ion-md-checkmark-circle-outline demo"></i><b>ENERGY:</b><br> ${toScientificWithSuperscript(metrics.optimized.energy)} kWh</li>
            <li><i class="icon ion-md-checkmark-circle-outline demo"></i><b>EXECUTION TIME:</b><br> ${metrics.optimized.execution_time} s</li>
        `;

        // Update Results metrics with color-coded arrows
        resultsBox.innerHTML = `
            <li><i class="icon ion-md-checkmark-circle-outline demo"></i><b>EMISSION REDUCTION:</b><br> ${getResultHTML(emissionsReduction, 'kg CO2eq')}</li>
            <li><i class="icon ion-md-checkmark-circle-outline demo"></i><b>ENERGY REDUCTION:</b><br> ${getResultHTML(energyReduction, 'kWh')}</li>
            <li><i class="icon ion-md-checkmark-circle-outline demo"></i><b>TIME REDUCTION:</b><br> ${getResultHTML(timeReduction, 's')}</li>
        `;
    }
}

function handleImageUpload(event) {
    const uploadedFile = event.target.files?.[0] || null;
    if (!uploadedFile) return;

    const formData = new FormData();
    formData.append('file', uploadedFile);

    fetch('http://127.0.0.1:5000/image-to-code', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            document.getElementById('output-text').value = `Error: ${data.error}`;
        } else {
            const inputTextArea = document.getElementById('input-text');
            typeWriterEffect(inputTextArea, data.code, 10); // Typewriter effect
            document.querySelector('.paste-btn').style.display = 'none';
            document.querySelector('.button-group svg').style.display = 'none';
            alert('Please check your code for accuracy before optimizing.');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        document.getElementById('output-text').value = 'Something went wrong. Please try again.';
    });
}

function typeWriterEffect(element, text, speed = 10) {
    element.value = ""; // Clear the textarea
    let i = 0;
    function type() {
        if (i < text.length) {
            element.value += text.charAt(i);
            i++;
            typewriterTimeout = setTimeout(type, speed);
        }
    }
    type();
}

document.getElementById('input-text').addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        e.preventDefault();
        const textarea = this;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        // Insert 4 spaces (or '\t' for a real tab)
        textarea.value = textarea.value.substring(0, start) + "    " + textarea.value.substring(end);
        textarea.selectionStart = textarea.selectionEnd = start + 4;
    }
});


