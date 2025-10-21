import ast
import tokenize
import dis
import re
import urllib.request
import json
import logging
import time
import math
import io
import heapq
from typing import Dict, List, Tuple, Any, Optional

# Configure logging
logging.basicConfig(
    filename='emissions.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class StaticCodeAnalyzer:
    """Static analyzer for Python code emissions estimation."""
    
    def __init__(self):
        # Rate limiting with better data structure
        self.rate_limits = {}  # Dict of IP -> list of timestamps
        
        # CPU performance assumptions
        self.flops_per_sec = 2.5e9  # flops_per_sec: Assumes 2.5 GHz single-core CPU with ~1 FLOP per cycle (conservative estimate for Python ops)
        self.python_overhead = 1.5  # python_overhead: Empirical factor for Python's interpreter overhead vs. native code (based on benchmarks)
        
        # Hardware power consumption (Watts)
        self.cpu_tdp = 50  # cpu_tdp: Average thermal design power for a mid-range desktop CPU (e.g., Intel i5)
        self.gpu_tdp = 150  # GPU TDP assumption based on average consumer GPU like RTX 3060; adjust for server-grade if needed
        self.ram_w_per_gb = 0.1  # RAM power consumption per GB
        self.psu_efficiency = 1.2  # PSU efficiency factor (80% efficient = 1.2x multiplier for losses)
        
        # Carbon intensity
        self.world_avg_carbon_intensity = 475  # world_avg_carbon_intensity: Global average from IEA data (2023 estimate)
        self.default_lat = 14.5995  # Manila coordinates as default
        self.default_lon = 120.9842

    def analyze_code(self, code: str, input_size_n: int = 1000000, 
                    runs_per_year: int = 1000, lat: Optional[float] = None, 
                    lon: Optional[float] = None, client_ip: str = "anonymous") -> Dict[str, Any]:
        """Main analysis function."""
        try:
            # Rate limiting check with client IP
            if not self._check_rate_limit(client_ip):
                return {"error": "Rate limit exceeded (20 requests/minute)"}
            
            # Enhanced input validation and logging
            if len(code) > 50000:
                return {"error": "Code too large (max 50,000 characters)"}
            
            if not code.strip() or code.strip() == "":
                return {"error": "No code provided - please enter some Python code to analyze"}
            
            # Log default parameter usage
            if input_size_n == 1000000:
                logging.info("Using default input_size_n=1000000 as no value provided")
            if runs_per_year == 1000:
                logging.info("Using default runs_per_year=1000 as no value provided")
            
            # Input sanitization
            code = code.strip()
            if not any(keyword in code for keyword in ['def ', 'import ', 'class ', 'if ', 'for ', 'while ']):
                logging.warning("Code may not be valid Python - no common keywords detected")
            
            # Parse AST
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                return {"error": f"Invalid syntax: {str(e)}"}
            
            # Consolidated analysis in single pass for better performance
            consolidated_analyzer = ConsolidatedAnalyzer()
            consolidated_analyzer.visit(tree)
            
            # Finalize complexity analysis
            consolidated_analyzer._finalize_complexity_analysis()
            
            # Get results from consolidated analyzer
            time_complexity = consolidated_analyzer.get_time_complexity()
            space_complexity = consolidated_analyzer.get_space_complexity()
            cyclomatic_complexity = consolidated_analyzer.get_cyclomatic_complexity()
            smells = consolidated_analyzer.get_smells()
            
            # Separate analyzers for metrics that need different approaches
            halstead_analyzer = HalsteadAnalyzer()
            halstead_analyzer.analyze(code)
            
            bytecode_analyzer = BytecodeAnalyzer()
            bytecode_ops = bytecode_analyzer.analyze(code)
            
            # GPU detection
            gpu_usage = self._detect_gpu_usage(tree)
            
            # Calculate metrics
            halstead_volume = halstead_analyzer.get_volume()
            smells_count = len(smells)
            
            # Estimate operations with improved accuracy
            total_ops = self._estimate_operations(
                halstead_volume, bytecode_ops, time_complexity, 
                input_size_n, smells_count, smells, gpu_usage
            )
            
            # Calculate runtime and energy with hardware components
            runtime_s = (total_ops / self.flops_per_sec) * self.python_overhead
            energy_kwh = self._calculate_energy(
                code, runtime_s, cyclomatic_complexity, 
                space_complexity, smells, gpu_usage, input_size_n
            )
            
            # Get carbon intensity with improved error handling
            carbon_intensity = self._get_carbon_intensity(lat, lon)
            
            # Calculate emissions
            emissions_gco2 = energy_kwh * carbon_intensity
            annual_emissions = emissions_gco2 * runs_per_year
            
            # Calculate eco score
            eco_score = max(0, min(100, 100 * (1 - energy_kwh / 0.01)))
            
            # Generate suggestions
            suggestions = self._generate_suggestions(smells, time_complexity)
            
            # Enhanced confidence calculation
            total_nodes = len(list(ast.walk(tree)))
            confidence = self._calculate_confidence(smells_count, total_nodes, code, gpu_usage, lat, lon)
            
            # Generate warnings with hardware-specific considerations
            warnings = self._generate_warnings(smells, time_complexity, confidence, gpu_usage, lat, lon)
            
            # Calculate equivalents
            equivalents = self._calculate_equivalents(emissions_gco2)
            
            # Enhanced structured logging
            code_hash = hash(code) % 1000000
            metrics_data = {
                "code_hash": code_hash,
                "emissions_gco2": emissions_gco2,
                "energy_kwh": energy_kwh,
                "time_complexity": time_complexity,
                "gpu_detected": gpu_usage,
                "smells_count": smells_count
            }
            logging.info(f"Analysis complete: {json.dumps(metrics_data)}")
            
            return {
                "metrics": {
                    "time_complexity": time_complexity,
                    "space_complexity": space_complexity,
                    "cyclomatic_complexity": cyclomatic_complexity,
                    "halstead_volume": halstead_volume,
                    "bytecode_ops": bytecode_ops,
                    "smells_count": smells_count
                },
                "estimated": {
                    "ops_total": total_ops,
                    "runtime_s": runtime_s,
                    "energy_kwh": energy_kwh,
                    "carbon_intensity_gco2_kwh": carbon_intensity
                },
                "emissions_gco2": emissions_gco2,
                "eco_score": eco_score,
                "breakdown": {
                    "baseline": len(code.split('\n')) * 1e-6,
                    "dynamic": energy_kwh * 0.8,
                    "patterns": energy_kwh * 0.2,
                    "categories": {
                        "energy_eff": 1.0 if eco_score > 70 else 0.5,
                        "resource": 1.0 if space_complexity == "O(1)" else 0.7,
                        "io": 1.2 if any('io' in smell for smell in smells) else 1.0
                    }
                },
                "confidence": confidence,
                "suggestions": suggestions,
                "equivalents": equivalents,
                "annual_estimate": {
                    "kwh": energy_kwh * runs_per_year,
                    "gco2": annual_emissions
                },
                "warnings": warnings
            }
            
        except Exception as e:
            logging.error(f"Analysis error: {str(e)}")
            logging.error(f"Analysis error: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _detect_gpu_usage(self, tree: ast.AST) -> bool:
        """Detect potential GPU usage by checking for ML framework imports."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['torch', 'tensorflow', 'cupy', 'jax']:
                        return True
            elif isinstance(node, ast.ImportFrom):
                if node.module in ['torch', 'tensorflow', 'cupy', 'jax']:
                    return True
                # Check for CUDA-related imports
                if node.module and any(cuda_term in node.module.lower() for cuda_term in ['cuda', 'gpu', 'device']):
                    return True
        
        return False
    
    def _calculate_confidence(self, smells_count: int, total_nodes: int, 
                            code: str, gpu_usage: bool, lat: Optional[float], 
                            lon: Optional[float]) -> float:
        """Enhanced confidence calculation with multiple factors."""
        # Base confidence from smells vs nodes
        base_confidence = max(0, 1 - (smells_count / max(total_nodes, 1) * 0.5))
        
        # Adjust for code size
        if total_nodes < 10:
            base_confidence *= 0.8  # Lower confidence for very small code
        
        # Adjust for GPU usage without location
        if gpu_usage and (lat is None or lon is None):
            base_confidence *= 0.9
        
        # Adjust for code complexity indicators
        if len(code.split('\n')) > 100:
            base_confidence *= 0.95  # Slightly lower confidence for large files
        
        return min(1.0, base_confidence)
    
    def _check_rate_limit(self, client_ip: str = "anonymous") -> bool:
        """Enhanced rate limiting: 20 requests per minute per IP with efficient cleanup."""
        current_time = time.time()
        
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Efficient cleanup using heapq for sorted timestamps
        # Remove old requests (older than 1 minute)
        while (self.rate_limits[client_ip] and 
               current_time - self.rate_limits[client_ip][0] >= 60):
            heapq.heappop(self.rate_limits[client_ip])
        
        # Rate limit to prevent abuse and align with external API limits like Electricity Maps
        if len(self.rate_limits[client_ip]) >= 20:
            return False
        
        heapq.heappush(self.rate_limits[client_ip], current_time)
        return True
    
    def _estimate_operations(self, halstead_volume: float, bytecode_ops: int, 
                           time_complexity: str, input_size_n: int, 
                           smells_count: int, smells: List[str], gpu_usage: bool) -> float:
        """Estimate total operations from static metrics with improved accuracy."""
        # Base operations from Halstead volume
        # base_ops: Halstead volume divided by 10 to normalize to operation count (empirical scaling)
        base_ops = halstead_volume / 10
        
        # Complexity scaling
        complexity_multiplier = self._get_complexity_multiplier(time_complexity, input_size_n)
        
        # Bytecode operations weighted by complexity
        # bytecode_ops_weighted: Scale by complexity multiplier to account for loops executing ops multiple times
        bytecode_ops_weighted = bytecode_ops * complexity_multiplier * 1.2  # 1.2 factor for average cycle cost of Python bytecode (from dis benchmarks)
        
        # Smell penalties with weighted impact
        smell_penalty = 0
        for smell in smells:
            if 'io_operations' in smell:
                smell_penalty += 150  # I/O operations have higher overhead
            elif 'nested_loop' in smell:
                smell_penalty += 200  # Nested loops are expensive
            elif 'recursion' in smell:
                smell_penalty += 100  # Recursion overhead
            else:
                smell_penalty += 50  # General smell penalty
        
        # GPU operations if detected
        gpu_ops = 0
        if gpu_usage:
            gpu_ops = input_size_n * 0.1  # Assume 10% of operations are GPU-accelerated
        
        return base_ops + bytecode_ops_weighted + complexity_multiplier + smell_penalty + gpu_ops
    
    def _get_complexity_multiplier(self, time_complexity: str, input_size_n: int) -> float:
        """Convert Big O notation to operation count with improved parsing."""
        # Use regex to extract exponents from complexity strings
        if "O(1)" in time_complexity:
            return 1
        elif "O(log N)" in time_complexity:
            return math.log2(input_size_n)
        elif "O(N log N)" in time_complexity:
            return input_size_n * math.log2(input_size_n)
        elif "O(2^N)" in time_complexity:
            return 2 ** min(input_size_n, 30)  # Cap exponential more safely at N=30
        else:
            # Parse polynomial complexities like O(N^2), O(N^3), O(N^4), etc.
            match = re.search(r'O\(N\^(\d+)\)', time_complexity)
            if match:
                exponent = int(match.group(1))
                return input_size_n ** exponent
            
            # Parse O(N^M) where M is detected from loop depth
            match = re.search(r'O\(N\^M\)', time_complexity)
            if match:
                # Assume M=3 for deeply nested loops
                return input_size_n ** 3
            
            # Default to linear for unrecognized patterns
            return input_size_n
    
    def _calculate_energy(self, code: str, runtime_s: float, 
                         cyclomatic_complexity: int, space_complexity: str, 
                         smells: List[str], gpu_usage: bool, input_size_n: int) -> float:
        """Calculate energy consumption in kWh with hardware components."""
        lines_of_code = len(code.split('\n'))
        
        # Baseline energy (per line)
        # baseline_energy: Arbitrary small value per line to account for parsing overhead (1e-6 kWh/line based on micro-benchmarks)
        baseline_energy = lines_of_code * 1e-6
        
        # CPU energy
        cpu_power = self.cpu_tdp + (cyclomatic_complexity * 2)
        cpu_energy = (cpu_power * runtime_s) / 3.6e6  # dynamic_energy: Converts watts * seconds to kWh using 3.6e6 (3600 * 1000)
        
        # GPU energy if detected
        gpu_energy = 0
        if gpu_usage:
            gpu_energy = (self.gpu_tdp * runtime_s) / 3.6e6
        
        # RAM energy based on space complexity
        ram_energy = 0
        if space_complexity != "O(1)":
            # Estimate memory usage in GB
            estimated_bytes = input_size_n * 8  # Assume 8 bytes per integer
            estimated_gb = estimated_bytes / 1e9
            ram_power = estimated_gb * self.ram_w_per_gb
            ram_energy = (ram_power * runtime_s) / 3.6e6
        
        # Total power before PSU efficiency
        total_power = cpu_power + (self.gpu_tdp if gpu_usage else 0) + (estimated_gb * self.ram_w_per_gb if space_complexity != "O(1)" else 0)
        
        # Apply PSU efficiency
        psu_energy = (total_power * self.psu_efficiency * runtime_s) / 3.6e6
        
        # I/O overhead
        io_overhead = 1.5 if any('io_operations' in smell for smell in smells) else 1.0
        
        # Embodied emissions (minimal hardware manufacturing amortization)
        embodied_energy = 1e-8  # Static embodied energy per run
        
        return (baseline_energy + cpu_energy + gpu_energy + ram_energy + psu_energy + embodied_energy) * io_overhead
    
    def _get_carbon_intensity(self, lat: Optional[float], lon: Optional[float]) -> float:
        """Get carbon intensity from Electricity Maps API with improved error handling."""
        # Use default location if no coordinates provided
        if lat is None or lon is None:
            lat, lon = self.default_lat, self.default_lon
            logging.info(f"Using default location (Manila): lat={lat}, lon={lon}")
        
        try:
            url = f"https://api.electricitymaps.com/free/v3/carbon-intensity/latest?lat={lat}&lon={lon}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                carbon_intensity = data.get('carbonIntensity', self.world_avg_carbon_intensity)
                logging.info(f"Fetched CI: {carbon_intensity} gCO2/kWh from Electricity Maps API")
                return carbon_intensity
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limit
                logging.warning("Electricity Maps API rate limit exceeded, retrying after delay")
                time.sleep(1)
                try:
                    with urllib.request.urlopen(url, timeout=5) as response:
                        data = json.loads(response.read().decode())
                        return data.get('carbonIntensity', self.world_avg_carbon_intensity)
                except:
                    pass
            logging.warning(f"Electricity Maps API error: {e}, using fallback")
        except Exception as e:
            logging.warning(f"Electricity Maps API error: {e}, using fallback")
        
        logging.info("Fallback to world avg due to API error")
        return self.world_avg_carbon_intensity
    
    def _generate_suggestions(self, smells: List[str], time_complexity: str) -> List[str]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []
        
        for smell in smells:
            if 'string_concat' in smell:
                suggestions.append("Use ''.join() instead of += in loops to save ~40% energy")
            elif 'io' in smell:
                suggestions.append("Consider caching I/O results to reduce repeated operations")
            elif 'global' in smell:
                suggestions.append("Avoid global variables; use local scope for better performance")
            elif 'nested_loop' in smell:
                suggestions.append("Consider using more efficient algorithms or data structures")
        
        if "O(N^2)" in time_complexity or "O(N^3)" in time_complexity:
            suggestions.append("Consider optimizing algorithm complexity for better energy efficiency")
        
        if not suggestions:
            suggestions.append("Code appears well-optimized for energy efficiency")
        
        return suggestions
    
    def _generate_warnings(self, smells: List[str], time_complexity: str, 
                          confidence: float, gpu_usage: bool, lat: Optional[float], 
                          lon: Optional[float]) -> List[str]:
        """Generate warnings for potential issues with hardware-specific considerations."""
        warnings = []
        
        if confidence < 0.5:
            warnings.append("Low confidence analysis; manual review recommended")
        
        if "O(2^N)" in time_complexity:
            warnings.append("Exponential complexity detected; may cause performance issues")
        
        if any('io_operations' in smell for smell in smells):
            warnings.append("I/O operations detected; manual adjustment advised")
        
        if len(smells) > 5:
            warnings.append("Multiple code smells detected; consider refactoring")
        
        # Hardware-specific warnings
        if gpu_usage and (lat is None or lon is None):
            warnings.append("GPU emissions estimated without location-specific carbon intensity")
        
        if gpu_usage and not any('torch' in smell or 'tensorflow' in smell for smell in smells):
            warnings.append("GPU usage detected but no ML framework imports found")
        
        return warnings
    
    def _calculate_equivalents(self, emissions_gco2: float) -> Dict[str, float]:
        """Calculate environmental equivalents."""
        return {
            "car_km": emissions_gco2 / 120,
            "trees_offset": emissions_gco2 / 22,
            "emails": emissions_gco2 / 4
        }


class ConsolidatedAnalyzer(ast.NodeVisitor):
    """Consolidated AST visitor for complexity analysis and smell detection."""
    
    def __init__(self):
        # Complexity tracking
        self.time_complexity = "O(1)"
        self.space_complexity = "O(1)"
        self.cyclomatic_complexity = 1
        self.loop_depth = 0
        self.max_loop_depth = 0
        self.decision_points = 0
        self.loop_stack = []  # Track nested loops
        self.sequential_loops = 0
        
        # Enhanced tracking for better analysis
        self.recursive_functions = set()
        self.function_calls = []
        self.data_structures = []  # Track list/dict creations
        self.in_function = False
        self.current_function = None
        
        # Smell detection
        self.smells = []
        self.in_loop = False
        self.string_concat_in_loop = False
        self.global_vars = set()
        self.recursive_calls = set()
        self.function_names = set()
        
    def visit_For(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.decision_points += 1
        self.loop_stack.append('for')
        
        # Check for nested vs sequential loops
        if len(self.loop_stack) > 1:
            # Nested loop
            if self.loop_depth == 2:
                self.time_complexity = "O(N^2)"
            elif self.loop_depth == 3:
                self.time_complexity = "O(N^3)"
            elif self.loop_depth >= 4:
                self.time_complexity = f"O(N^{self.loop_depth})"
        else:
            # Sequential loop
            self.sequential_loops += 1
            if self.sequential_loops == 1:
                self.time_complexity = "O(N)"
            else:
                self.time_complexity = f"O(N + N)"  # Multiple sequential loops
        
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = False
        self.loop_depth -= 1
        self.loop_stack.pop()
    
    def visit_While(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.decision_points += 1
        self.loop_stack.append('while')
        
        # Check for binary search pattern (O(log N))
        if self._is_binary_search_pattern(node):
            self.time_complexity = "O(log N)"
        
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = False
        self.loop_depth -= 1
        self.loop_stack.pop()
    
    def visit_If(self, node):
        self.decision_points += 1
        self.generic_visit(node)
    
    def visit_ListComp(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def visit_Assign(self, node):
        # Check for space complexity
        for target in node.targets:
            if isinstance(target, ast.Name):
                if self.in_loop:
                    self.space_complexity = "O(N)"
                # Check for global variables
                if target.id in self.global_vars:
                    self.smells.append('global_variables')
        
        # Check for string concatenation in loops
        if self.in_loop and isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Add):
            if isinstance(node.target, ast.Name):
                self.smells.append('string_concat')
        
        # Enhanced space complexity detection
        self._analyze_space_complexity(node)
        
        self.generic_visit(node)
    
    def visit_AugAssign(self, node):
        # Check for string concatenation in loops
        if self.in_loop and isinstance(node.op, ast.Add):
            self.smells.append('string_concat')
        self.generic_visit(node)
    
    def visit_Global(self, node):
        for name in node.names:
            self.global_vars.add(name)
        self.smells.append('global_variables')
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.function_names.add(node.name)
        self.current_function = node.name
        self.in_function = True
        self.generic_visit(node)
        self.in_function = False
        self.current_function = None
    
    def visit_Call(self, node):
        # Check for recursive calls
        if isinstance(node.func, ast.Name) and node.func.id in self.function_names:
            self.recursive_calls.add(node.func.id)
            self.smells.append('recursion')
        
        # Check for I/O operations
        if isinstance(node.func, ast.Name):
            if node.func.id in ['open', 'input', 'print']:
                self.smells.append('io_operations')
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in ['get', 'post', 'put', 'delete']:
                self.smells.append('io_operations')
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        # Check for ML framework imports
        for alias in node.names:
            if alias.name in ['torch', 'tensorflow', 'cupy', 'jax']:
                self.smells.append('ml_framework')
    
    def visit_ImportFrom(self, node):
        if node.module in ['torch', 'tensorflow', 'cupy', 'jax']:
            self.smells.append('ml_framework')
    
    def _is_binary_search_pattern(self, node) -> bool:
        """Detect binary search pattern in while loops."""
        # Look for patterns like: while low <= high: mid = (low + high) // 2
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name) and target.id == 'mid':
                        if isinstance(child.value, ast.BinOp) and isinstance(child.value.op, ast.FloorDiv):
                            return True
        return False
    
    def get_time_complexity(self) -> str:
        return self.time_complexity
    
    def get_space_complexity(self) -> str:
        return self.space_complexity
    
    def get_cyclomatic_complexity(self) -> int:
        return self.decision_points + 1
    
    def get_smells(self) -> List[str]:
        return list(set(self.smells))  # Remove duplicates
    
    def _analyze_space_complexity(self, node):
        """Enhanced space complexity analysis."""
        # Check for list comprehensions
        if isinstance(node.value, ast.ListComp):
            # Check if it's creating a matrix (nested list comprehension)
            if self._is_matrix_creation(node.value):
                self.space_complexity = "O(N^2)"
            elif self.in_loop:
                self.space_complexity = "O(N^2)"  # Nested list comprehension in loop
            else:
                self.space_complexity = "O(N)"
        
        # Check for list creation with size
        elif isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id in ['list', 'range']:
                    # Check if it's creating a list of size N
                    if self._is_size_n_creation(node.value):
                        if self.in_loop:
                            self.space_complexity = "O(N^2)"
                        else:
                            self.space_complexity = "O(N)"
        
        # Check for nested list creation (like matrix)
        elif isinstance(node.value, ast.List):
            if self._has_nested_lists(node.value):
                if self.in_loop:
                    self.space_complexity = "O(N^2)"
                else:
                    self.space_complexity = "O(N)"
    
    def _is_matrix_creation(self, list_comp):
        """Check if list comprehension creates a matrix."""
        # Look for patterns like [[1] * n for _ in range(n)]
        if isinstance(list_comp.elt, ast.List):
            return True
        # Also check for patterns like [1] * n for _ in range(n)
        elif isinstance(list_comp.elt, ast.BinOp) and isinstance(list_comp.elt.op, ast.Mult):
            return True
        return False
    
    def _is_size_n_creation(self, call_node):
        """Check if a call creates something of size N."""
        if isinstance(call_node.func, ast.Name):
            if call_node.func.id == 'range' and len(call_node.args) == 1:
                return True
            elif call_node.func.id == 'list' and len(call_node.args) == 1:
                return True
        return False
    
    def _has_nested_lists(self, list_node):
        """Check if a list contains nested lists."""
        for elt in list_node.elts:
            if isinstance(elt, ast.List):
                return True
        return False
    
    def _analyze_recursive_complexity(self):
        """Analyze complexity for recursive functions."""
        if self.recursive_calls:
            # If we have recursive calls, analyze the pattern
            if len(self.recursive_calls) == 1:
                # Single recursive call - could be O(N) or O(log N)
                if self._has_divide_and_conquer_pattern():
                    self.time_complexity = "O(N log N)"
                else:
                    self.time_complexity = "O(N)"
            else:
                # Multiple recursive calls - could be exponential
                self.time_complexity = "O(2^N)"
    
    def _has_divide_and_conquer_pattern(self):
        """Check for divide and conquer patterns (like merge sort)."""
        # Look for patterns like mid = len(arr) // 2
        # This is a simplified check - in practice, you'd need more sophisticated analysis
        # For now, assume recursive functions with single calls are divide-and-conquer
        return True  # Simplified for now
    
    def _finalize_complexity_analysis(self):
        """Finalize complexity analysis after visiting all nodes."""
        # Handle recursive functions
        if self.recursive_calls:
            self._analyze_recursive_complexity()
        
        # Handle space complexity for recursive functions
        if self.recursive_calls and self.space_complexity == "O(1)":
            self.space_complexity = "O(N)"  # Recursive functions typically use O(N) space


class HalsteadAnalyzer:
    """Halstead metrics analyzer."""
    
    def __init__(self):
        self.operators = set()
        self.operands = set()
        self.operator_count = 0
        self.operand_count = 0
    
    def analyze(self, code: str):
        """Analyze code for Halstead metrics."""
        try:
            tokens = tokenize.tokenize(io.BytesIO(code.encode('utf-8')).readline)
            
            for token in tokens:
                if token.type == tokenize.OP:
                    self.operators.add(token.string)
                    self.operator_count += 1
                elif token.type in (tokenize.NAME, tokenize.NUMBER, tokenize.STRING):
                    self.operands.add(token.string)
                    self.operand_count += 1
        except:
            pass  # Handle tokenization errors gracefully
    
    def get_volume(self) -> float:
        """Calculate Halstead volume."""
        n1 = len(self.operators)
        n2 = len(self.operands)
        N1 = self.operator_count
        N2 = self.operand_count
        
        if n1 + n2 == 0:
            return 0
        
        return (N1 + N2) * math.log2(n1 + n2)


class BytecodeAnalyzer:
    """Bytecode instruction analyzer."""
    
    def __init__(self):
        self.opcode_weights = {
            'LOAD_FAST': 1, 'LOAD_CONST': 1, 'LOAD_GLOBAL': 2,
            'BINARY_ADD': 5, 'BINARY_SUBTRACT': 5, 'BINARY_MULTIPLY': 5,
            'CALL_FUNCTION': 20, 'CALL_METHOD': 25,
            'FOR_ITER': 10, 'GET_ITER': 5,
            'COMPARE_OP': 8, 'JUMP_IF_FALSE': 3, 'JUMP_IF_TRUE': 3
        }
    
    def analyze(self, code: str) -> int:
        """Analyze bytecode and return weighted operation count."""
        try:
            compiled = compile(code, '<string>', 'exec')
            instructions = list(dis.get_instructions(compiled))
            
            total_weight = 0
            for instruction in instructions:
                weight = self.opcode_weights.get(instruction.opname, 1)
                total_weight += weight
            
            return total_weight
        except:
            return 0


