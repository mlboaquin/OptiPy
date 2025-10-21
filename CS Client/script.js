var startScreen = document.querySelector("#start-screen"),
    leaf = document.querySelector(".start-leaf"),
    leafTrace = document.querySelector("#leaf-trace"),
    leafLeftTrace = document.querySelector('#leaf-trace__left'),
    leafRightTrace = document.querySelector('#leaf-trace__right'),
    topPanel = document.querySelector(".start-screen__top"),
    bottomPanel = document.querySelector(".start-screen__bottom"),
    renderTrace = function(path) {
    /**
     *  @see http://jakearchibald.com/2013/animated-line-drawing-svg/
     */

        var length = path.getTotalLength();
        // Clear any previous transition
        path.style.transition = path.style.WebkitTransition =
        'none';
        // Set up the starting positions
        path.style.strokeDasharray = length + ' ' + length;
        path.style.strokeDashoffset = length;
        // Trigger a layout so styles are calculated & the browser
        // picks up the starting position before animating
        path.getBoundingClientRect();
        // Define our transition
        path.style.transition = path.style.WebkitTransition =
        'stroke-dashoffset 1.5s ease-in-out';
        // Go!
        path.style.strokeDashoffset = '0';
    };

renderTrace(leafLeftTrace);
renderTrace(leafRightTrace);

// TODO: clean up nesting
setTimeout(function(){
    leafTrace.classList.add("hide");
    leaf.classList.add("show");
    setTimeout(function() {
        leaf.classList.add("scaleDown");
        setTimeout(function() {
            // may possibly need to make panels look seamless
            // document.querySelector("#start-screen").style.background = "none";
            topPanel.classList.add("slideUp");
            bottomPanel.classList.add("slideDown");
            setTimeout(function() {
                // destroy start screen and clear references
                startScreen.parentNode.removeChild(startScreen);
                startScreen = null;
                leaf = null;
                leafTrace = null;
                leafLeftTrace = null;
                leafRightTrace = null;
                topPanel = null;
                bottomPanel = null;
            }, 500);
        }, 600);
    }, 500);
}, 1500);


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
        runOptimize();
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
  
  

hideButtonsOnInput();


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
    const complexityBox = document.getElementById('complexity-metrics');

    if (metrics && metrics.original && metrics.optimized) {
        // Use improvements from the response if available, otherwise compute them
        const emissionsReduction = metrics.improvements?.emissions_reduction || (metrics.original.emissions - metrics.optimized.emissions);
        const energyReduction = metrics.improvements?.energy_reduction || (metrics.original.energy - metrics.optimized.energy);
        const timeReduction = metrics.improvements?.time_reduction || (metrics.original.execution_time - metrics.optimized.execution_time);

        // Update Original Code metrics
        originalBox.innerHTML = `
            <li><i class="ion ion-ios-leaf"></i><b>EMISSION:</b><br> ${toScientificWithSuperscript(metrics.original.emissions)} kg CO2eq </li>
            <li><i class="ion ion-ios-flash"></i><b>ENERGY:</b><br> ${toScientificWithSuperscript(metrics.original.energy)} kWh</li>
            <li><i class="ion ion-md-time"></i><b>EXECUTION TIME:</b><br> ${metrics.original.execution_time.toFixed(6)} s</li>
        `;

        // Update Optimized Code metrics
        optimizedBox.innerHTML = `
            <li><i class="ion ion-ios-leaf"></i><b>EMISSION:</b><br> ${toScientificWithSuperscript(metrics.optimized.emissions)} kg CO2eq</li>
            <li><i class="ion ion-ios-flash"></i><b>ENERGY:</b><br> ${toScientificWithSuperscript(metrics.optimized.energy)} kWh</li>
            <li><i class="ion ion-md-time"></i><b>EXECUTION TIME:</b><br> ${metrics.optimized.execution_time.toFixed(6)} s</li>
        `;

        // Update Results metrics with color-coded arrows
        resultsBox.innerHTML = `
            <li><i class="ion ion-ios-leaf"></i><b>EMISSION REDUCTION:</b><br> ${getResultHTML(emissionsReduction, 'kg CO2eq')}</li>
            <li><i class="ion ion-ios-flash"></i><b>ENERGY REDUCTION:</b><br> ${getResultHTML(energyReduction, 'kWh')}</li>
            <li><i class="ion ion-md-time"></i><b>TIME REDUCTION:</b><br> ${getResultHTML(timeReduction, 's')}</li>
        `;

        // Update Complexity metrics
        if (complexityBox) {
            complexityBox.innerHTML = `
                <li><i class="mdi mdi-timer"></i><b>TIME:</b> ${metrics.optimized.time_complexity}</li>
                <li><i class="mdi mdi-exponent-box" style="color:#edbe25"></i><b>SPACE:</b> ${metrics.optimized.space_complexity}</li>
                <li><i class="mdi mdi-matrix" style="color:#1A79E9"></i><b>CYCLOMATIC:</b> ${metrics.optimized.cyclomatic_complexity}</li>
            `;
        }
    }

    showMetricsToast();
}

function updateImpactSection(staticAnalysis) {
    // Update the impact section with static analysis data
    const co2Element = document.getElementById('impact-co2');
    const energyElement = document.getElementById('impact-energy');
    const treesElement = document.getElementById('impact-trees');
    const ecoScoreElement = document.getElementById('impact-distance');
    const energyEquivalentList = document.getElementById('energy-equivalent');
    const carbonEquivalentList = document.getElementById('carbon-equivalent');

    if (staticAnalysis && staticAnalysis.optimized) {
        const analysis = staticAnalysis.optimized;
        
        // Update main metrics
        if (co2Element) {
            co2Element.textContent = `${(analysis.emissions_gco2 / 1000).toFixed(3)}kg`;
        }
        
        if (energyElement) {
            energyElement.textContent = `${analysis.estimated.energy_kwh.toFixed(6)}kWh`;
        }
        
        if (treesElement) {
            const trees = analysis.equivalents?.trees_offset || (analysis.emissions_gco2 / 22);
            treesElement.textContent = trees.toFixed(2);
        }
        
        if (ecoScoreElement) {
            ecoScoreElement.textContent = `${analysis.eco_score.toFixed(1)}/100`;
        }

        // Update equivalents
        if (energyEquivalentList) {
            const energy = analysis.estimated.energy_kwh;
            const lightBulbHours = (energy / 0.06).toFixed(1);
            const smartphoneCharges = Math.round(energy * 1000 / 0.005); // Assuming 5Wh per charge
            const laptopHours = (energy / 0.05).toFixed(1); // Assuming 50W laptop
            
            energyEquivalentList.innerHTML = `
                <li>Powers a 60W light bulb for ${lightBulbHours} hours</li>
                <li>Charges a smartphone ${smartphoneCharges} times</li>
                <li>Runs a laptop for ${laptopHours} hours</li>
            `;
        }

        if (carbonEquivalentList) {
            const emissions = analysis.emissions_gco2;
            const emails = Math.round(emissions / 4);
            const trees = (emissions / 22).toFixed(2);
            const impact = emissions < 10 ? 'Low' : emissions < 100 ? 'Moderate' : 'High';
            
            carbonEquivalentList.innerHTML = `
                <li>Same as sending ${emails} emails</li>
                <li>Equal to ${trees} trees absorbing CO₂ for a day</li>
                <li>${impact} environmental impact</li>
            `;
        }
    }
}

function updateSummarySections(staticAnalysis) {
    // Update summary-left (Annual Impact)
    const summaryLeft = document.getElementById('summary-left');
    if (summaryLeft && staticAnalysis && staticAnalysis.optimized) {
        const analysis = staticAnalysis.optimized;
        const annualEmissions = analysis.annual_estimate?.gco2 || (analysis.emissions_gco2 * 1000);
        const annualEnergy = analysis.annual_estimate?.kwh || (analysis.estimated.energy_kwh * 1000);
        
        summaryLeft.innerHTML = `
            <h6> <i class="mdi mdi-calendar" style="color:#1A79E9"></i> Annual Impact</h6>
            <div class="divider-light"></div>
            <ul>
                <li><b>Annual CO₂:</b> ${(annualEmissions / 1000).toFixed(3)} kg</li>
                <li><b>Annual Energy:</b> ${annualEnergy.toFixed(6)} kWh</li>
                <li><b>Eco Score:</b> ${analysis.eco_score.toFixed(1)}/100</li>
                <li><b>Confidence:</b> ${(analysis.confidence * 100).toFixed(1)}%</li>
            </ul>
        `;
    }

    // Update summary-right (Optimization Suggestions)
    const summaryRight = document.getElementById('summary-right');
    if (summaryRight && staticAnalysis && staticAnalysis.optimized) {
        const analysis = staticAnalysis.optimized;
        const suggestions = analysis.suggestions || [];
        const warnings = analysis.warnings || [];
        
        let suggestionsHTML = '';
        if (suggestions.length > 0) {
            suggestionsHTML = suggestions.map(suggestion => `<li>${suggestion}</li>`).join('');
        } else {
            suggestionsHTML = '<li>Code appears well-optimized</li>';
        }

        let warningsHTML = '';
        if (warnings.length > 0) {
            warningsHTML = warnings.map(warning => `<li style="color: #ff6b6b;">⚠️ ${warning}</li>`).join('');
        }

        summaryRight.innerHTML = `
            <h6> <i class="mdi mdi-lightbulb-on" style="color:#edbe25;"></i> Optimization Suggestions</h6>
            <div class="divider-light"></div>
            <ul>
                ${suggestionsHTML}
                ${warningsHTML}
            </ul>
        `;
    }
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

function setupHidePasteOnEdit() {
    const pasteBtn = document.getElementById('pasteBtn') || document.querySelector('.paste-btn');
  
    if (!window.inputEditor || !pasteBtn) return;
  
    const updateVisibility = () => {
      const content = inputEditor.getValue().trim();
      pasteBtn.style.display = content.length === 0 ? 'inline-block' : 'none';
    };
  
    // Update on any change triggered by the user
    inputEditor.on('change', (cm, change) => {
      // Ignore programmatic changes (like .setValue on load)
      if (change?.origin !== 'setValue') {
        updateVisibility();
      }
    });
  
    // Also monitor paste and typing directly
    inputEditor.on('paste', updateVisibility);
    inputEditor.on('keydown', updateVisibility);
    inputEditor.on('inputRead', updateVisibility);
  
    // Run once on startup to ensure correct state
    updateVisibility();
  }
  


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

    setupHidePasteOnEdit();  
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
    const btn  = document.getElementById('optimizeBtn');
  
    // Get input parameters from the form
    const inputSizeInput = document.getElementById('input-size');
    const runsPerYearInput = document.getElementById('runs-per-year');
    const keepCommentsCheckbox = document.getElementById('keep-comments');
    const keepFstringsCheckbox = document.getElementById('keep-fstrings');
    
    const inputSizeN = inputSizeInput ? parseInt(inputSizeInput.value) || 1000000 : 1000000;
    const runsPerYear = runsPerYearInput ? parseInt(runsPerYearInput.value) || 1000 : 1000;
    const keepComments = keepCommentsCheckbox ? keepCommentsCheckbox.checked : true;
    const keepFstrings = keepFstringsCheckbox ? keepFstringsCheckbox.checked : true;
  
    btn.classList.add('optimizing');
  
    try {
      const res = await fetch('http://127.0.0.1:5000/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          code,
          input_size_n: inputSizeN,
          runs_per_year: runsPerYear,
          keep_comments: keepComments,
          keep_fstrings: keepFstrings
        })
      });
      if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`);
  
      const data = await res.json();
      const optimized = data.optimized_code ?? data.code ?? '';
      outputEditor.setValue(optimized);
      outputEditor.scrollTo(0, 0);
      
      // Update changes and metrics if available
      if (data.changes) updateChanges(data.changes);
      if (data.metrics) updateMetrics(data.metrics);
      if (data.static_analysis) {
        updateImpactSection(data.static_analysis);
        updateSummarySections(data.static_analysis);
      }
    } catch (err) {
      console.error('Optimization failed:', err);
      outputEditor.setValue(`Error: ${err.message}`);
    } finally {
      btn.classList.remove('optimizing'); // SVG + "Optimize" come back
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
  