
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
/**
 * Reads text from the clipboard and pastes it into the CodeMirror editor.
 */
// Robust paste for CodeMirror 5: tries async clipboard; if blocked, uses a hidden catcher.
async function pasteText() {
    const pasteButton = document.querySelector('.paste-btn');
    pasteButton && (pasteButton.style.display = 'none'); // optional UX: hide after first use
  
    // 1) Try async clipboard API first
    try {
      const text = await navigator.clipboard.readText();
      insertIntoInputEditor(text);
      return;
    } catch (err) {
      // fall through to manual capture
      console.warn('readText() blocked or failed, using manual capture:', err);
    }
  
    // 2) Manual fallback: focus off-screen catcher so Ctrl/Cmd+V lands there
    const catcher = document.getElementById('paste-capture');
    if (!catcher) {
      alert('Clipboard access blocked. Click in the editor and press Ctrl+V / Cmd+V.');
      if (window.inputEditor?.focus) window.inputEditor.focus();
      return;
    }
  
    catcher.value = '';
    catcher.focus();
    catcher.select();
  
    // Ask the user once
    alert('Press Ctrl+V (Cmd+V on Mac) now to paste. We will insert it into the editor.');
  
    const onPaste = (evt) => {
      evt.preventDefault();
      const text = evt.clipboardData?.getData('text') ?? catcher.value;
      cleanup();
      insertIntoInputEditor(text);
    };
    const onBlur = () => cleanup();
  
    function cleanup() {
      catcher.removeEventListener('paste', onPaste, { once: true });
      catcher.removeEventListener('blur', onBlur, { once: true });
      catcher.value = '';
    }
  
    catcher.addEventListener('paste', onPaste, { once: true });
    catcher.addEventListener('blur', onBlur, { once: true });
  }
  
  // Insert into CodeMirror at the cursor/selection (not replacing whole doc)
  function insertIntoInputEditor(text) {
    if (!text) {
      window.inputEditor?.focus?.();
      return;
    }
    if (window.inputEditor?.getDoc) {
      const doc = inputEditor.getDoc();
      doc.replaceSelection(text, 'around'); // proper insert at selection/cursor
      inputEditor.focus();
    } else {
      // fallback to raw textarea
      const ta = document.getElementById('input-text');
      if (ta) {
        const start = ta.selectionStart ?? ta.value.length;
        const end   = ta.selectionEnd   ?? ta.value.length;
        ta.setRangeText(text, start, end, 'end');
        ta.focus();
      }
    }
  }
  

  
function handleKeyDown(event) {
    // Only prevent default and submit on Ctrl+Enter (or Cmd+Enter)
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        optimize();
    }
    // For plain Enter, do nothing—let the browser insert a new line
}

const inputArea = document.getElementById('input-text');
if (inputArea) {
    inputArea.addEventListener('keydown', handleKeyDown);
}
  
function hidePasteButtonOnPaste() {
    const inputArea = document.getElementById('input-text');
    const pasteButton = document.querySelector('.paste-btn');
    const uploadButton = document.querySelector('.upload');
  
    if (inputArea && pasteButton && uploadButton) {
      inputArea.addEventListener('paste', () => {
        pasteButton.style.display = 'none';
        uploadButton.style.display = 'none';
      });
    }
}

function hideButtonsOnInput() {
    const inputArea = document.getElementById('input-text');
    const pasteButton = document.querySelector('.paste-btn');
    const uploadButton = document.querySelector('.upload');
  
    if (inputArea && pasteButton && uploadButton) {
      inputArea.addEventListener('input', () => {
        pasteButton.style.display = 'none';
        uploadButton.style.display = 'none';
      });
    }
}
  
  
hidePasteButtonOnPaste();
hideButtonsOnInput();
async function optimize() {
    const inputText = inputEditor.getValue(); // Get text from CodeMirror input editor
    const outputText = document.getElementById('output-text');
    const optimizeButton = document.getElementById('optimize-btn');

    // No confirmation dialog here

    // Show loading message with shimmer
    outputEditor.setValue('Please wait while your code is being generated...'); // Set text in CodeMirror output editor
    outputText.classList.add('shimmer');
    if (optimizeButton) {
        optimizeButton.disabled = true;
        optimizeButton.classList.add('shimmer');
    }

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
            outputEditor.setValue('Server returned invalid JSON.'); // Set text in CodeMirror output editor
            return;
        }

        if (response.ok) {
            outputText.classList.remove('shimmer');
            if (data.optimized_code) {
                outputEditor.setValue(data.optimized_code); // Set text in CodeMirror output editor
            } else if (data.error) {
                // Show error and details if available
                let errorMsg = `Error: ${data.error}`;
                if (data.details) {
                    errorMsg += "\n\nDetails:\n" + data.details.join('\n');
                }
                outputEditor.setValue(errorMsg); // Set text in CodeMirror output editor
            } else {
                outputEditor.setValue('No optimized code returned.'); // Set text in CodeMirror output editor
            }

            if (data.changes) updateChanges(data.changes);
            if (data.metrics) updateMetrics(data.metrics);
        } else {
            outputText.classList.remove('shimmer');
            let errorMsg = `Error: ${data.error || 'Unknown error'}`;
            if (data.details) {
                errorMsg += "\n\nDetails:\n" + data.details.join('\n');
            }
            outputEditor.setValue(errorMsg); // Set text in CodeMirror output editor
        }
    } catch (error) {
        console.error('Error:', error);
        outputText.classList.remove('shimmer');
        outputEditor.setValue('Error connecting to the server. Please try again.'); // Set text in CodeMirror output editor
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
        li.style.marginLeft = '2em';
        li.style.fontSize = '16px';

        revisionsBox1.appendChild(li);

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

    showMetricsToast();
}

function showMetricsToast() {
    const toast = document.getElementById('metrics-toast');
    if (toast) {
        toast.style.display = 'block';
        // Hide after 6 seconds if not clicked
        setTimeout(() => {
            toast.style.display = 'none';
        }, 6000);
    }
}

function hideMetricsToast() {
    const toast = document.getElementById('metrics-toast');
    if (toast) {
        toast.style.display = 'none';
    }
}

// When the toast is clicked, scroll to metrics and hide the toast
document.addEventListener('DOMContentLoaded', function() {
    const toast = document.getElementById('metrics-toast');
    if (toast) {
        toast.onclick = function() {
            hideMetricsToast();
            const metricsSection = document.getElementById('results-metrics');
            if (metricsSection) {
                metricsSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        };
    }
});

function handleImageUpload(event) {
    const uploadedFile = event.target.files?.[0] || null;
    if (!uploadedFile) {
        console.log('No file selected');
        return;
    }

    console.log('Uploading file:', uploadedFile.name, 'Size:', uploadedFile.size);
    console.log('Input editor available:', !!window.inputEditor);
    console.log('Output editor available:', !!window.outputEditor);
    
    // Wait for editors to be ready if they're not available yet
    if (!window.inputEditor || !window.outputEditor) {
        console.log('Editors not ready, waiting...');
        setTimeout(() => {
            console.log('Retrying after timeout - Input editor:', !!window.inputEditor, 'Output editor:', !!window.outputEditor);
        }, 1000);
    }
    
    const formData = new FormData();
    formData.append('file', uploadedFile);

    fetch('http://127.0.0.1:5000/image-to-code', {
        method: 'POST',
        body: formData
    })
    .then(res => {
        console.log('Response status:', res.status);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        console.log('Received data:', data);
        if (data.error) {
            console.error('Server error:', data.error);
            // Show error in output editor
            if (window.outputEditor) {
                window.outputEditor.setValue(`Error: ${data.error}`);
            } else {
                document.getElementById('output-text').value = `Error: ${data.error}`;
            }
        } else if (data.code) {
            console.log('Extracted code:', data.code);
            // Set the extracted code in the input editor
            setCodeInInputEditor(data.code);
            
            // Hide paste button and upload button
            document.querySelector('.paste-btn').style.display = 'none';
            document.querySelector('.button-group svg').style.display = 'none';
            alert('Please check your code for accuracy before optimizing.');
        } else {
            console.error('No code extracted from image');
            if (window.outputEditor) {
                window.outputEditor.setValue('No code could be extracted from the image. Please try a clearer image.');
            } else {
                document.getElementById('output-text').value = 'No code could be extracted from the image. Please try a clearer image.';
            }
        }
    })
    .catch(err => {
        console.error('Error:', err);
        // Show error in output editor
        if (window.outputEditor) {
            window.outputEditor.setValue(`Error: ${err.message}`);
        } else {
            document.getElementById('output-text').value = `Error: ${err.message}`;
        }
    });
}

function setCodeInInputEditor(code, retryCount = 0) {
    console.log('Attempting to set code in input editor, retry:', retryCount);
    
    // Try CodeMirror editor first
    if (window.inputEditor && window.inputEditor.setValue) {
        console.log('Setting code in CodeMirror input editor');
        window.inputEditor.setValue(code);
        window.inputEditor.focus();
        return;
    }
    
    // If editors aren't ready and we haven't retried too many times, wait and retry
    if (retryCount < 3) {
        console.log('Editors not ready, retrying in 500ms...');
        setTimeout(() => {
            setCodeInInputEditor(code, retryCount + 1);
        }, 500);
        return;
    }
    
    // Fallback to textarea
    console.log('CodeMirror input editor not available, using textarea fallback');
    const inputTextArea = document.getElementById('input-text');
    if (inputTextArea) {
        typeWriterEffect(inputTextArea, code, 10);
    } else {
        console.error('No input element found');
    }
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


/* =======================
   1) Load external CSS via JS
======================= */
function loadCSS(href) {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      link.onload = resolve;
      link.onerror = () => reject(new Error('Failed to load ' + href));
      document.head.appendChild(link);
    });
  }
  
  async function ensureStyles() {
    const urls = [
      // CodeMirror core + theme
      'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.17/codemirror.min.css',
    //   'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.17/theme/material-darker.min.css',
    //   'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.17/theme/oceanic-next.min.css',
      // YOUR stylesheet (make sure the path/filename matches your project)
      './styles.css'
    ];
    for (const u of urls) await loadCSS(u);
  }
  
  /* =======================
     2) Editors (Python-only)
  ======================= */
  let inputEditor, outputEditor;
  
  function bootEditors() {
    const inputTA  = document.getElementById('input-text');
    const outputTA = document.getElementById('output-text');
  
    inputEditor = CodeMirror.fromTextArea(inputTA, {
      mode: 'python',
      theme: 'default',
      lineNumbers: true,
      styleActiveLine: true,
      matchBrackets: true,
      autoCloseBrackets: true,
      indentUnit: 4,
      tabSize: 4,
      indentWithTabs: false,
      extraKeys: {
        'Ctrl-Enter': runOptimize,
        'Cmd-Enter': runOptimize
      }
    });
  
    outputEditor = CodeMirror.fromTextArea(outputTA, {
      mode: 'python',
      theme: 'default',
      lineNumbers: true,
      readOnly: true,
      
    });
    
    // Make editors globally accessible
    window.inputEditor = inputEditor;
    window.outputEditor = outputEditor;
  }
  
  // Non-blocking Python check
  function looksPythonic(src) {
    const hints = [
      /^\s*(def|class|import|from|if|for|while|try|except|with)\b/m,
      /\b(True|False|None)\b/,
      /^[ \t]*#[^\n]*$/m
    ];
    return hints.some(r => r.test(src));
  }
  
  /* =======================
     3) Optimize flow
  ======================= */
  async function runOptimize() {
    const code = inputEditor.getValue();
  
    if (!looksPythonic(code)) {
      console.warn('Heads up: input doesn’t look like Python. Continuing anyway.');
    }
  
    const btn = document.getElementById('optimizeBtn');
    btn?.classList.add('optimizing');
  
    try {
      const res = await fetch('http://127.0.0.1:5000/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
  
      if (!res.ok) throw new Error((await res.text()) || `HTTP ${res.status}`);
  
      const data = await res.json(); // expect { optimized_code: '...' } (or similar)
      const optimized = data.optimized_code ?? data.code ?? '';
      outputEditor.setValue(optimized);
      outputEditor.scrollTo(0, 0);
    } catch (err) {
      console.error('Optimization failed:', err);
      // plug into your toast if you have one:
      // showToast('Optimization failed: ' + err.message, 'error');
    } finally {
      btn?.classList.remove('optimizing');
    }
  }
  
  /* =======================
     4) Buttons & lifecycle
  ======================= */
  function wireButtons() {
    document.getElementById('pasteBtn')?.addEventListener('click', pasteText);
    document.getElementById('optimizeBtn')?.addEventListener('click', runOptimize);
    document.getElementById('clearLeft')?.addEventListener('click', () => inputEditor.setValue(''));
    document.getElementById('copyRight')?.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(outputEditor.getValue()); }
      catch (e) { console.error('Copy failed:', e); }
    });
  }
  
  (async () => {
    try {
      await ensureStyles();
    } catch (e) {
      console.warn(e.message);
    }
  
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        bootEditors();
        wireButtons();
      });
    } else {
      bootEditors();
      wireButtons();
    }
  })();
  