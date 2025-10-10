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
        self.rate_limits = {}  # Simple in-memory rate limiting
        self.flops_per_sec = 2.5e9  # 2.5 GHz CPU assumption
        self.python_overhead = 1.5
        self.cpu_tdp = 50  # Watts
        self.world_avg_carbon_intensity = 475  # gCO2/kWh
        
    def analyze_code(self, code: str, input_size_n: int = 1000000, 
                    runs_per_year: int = 1000, lat: Optional[float] = None, 
                    lon: Optional[float] = None) -> Dict[str, Any]:
        """Main analysis function."""
        try:
            # Rate limiting check
            if not self._check_rate_limit():
                return {"error": "Rate limit exceeded (10 requests/minute)"}
            
            # Validate input
            if len(code) > 50000:
                return {"error": "Code too large (max 50,000 characters)"}
            
            if not code.strip() or code.strip() == "":
                return {"error": "No code provided - please enter some Python code to analyze"}
            
            # Parse AST
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                return {"error": f"Invalid syntax: {str(e)}"}
            
            # Static analysis
            complexity_analyzer = ComplexityAnalyzer()
            complexity_analyzer.visit(tree)
            
            halstead_analyzer = HalsteadAnalyzer()
            halstead_analyzer.analyze(code)
            
            bytecode_analyzer = BytecodeAnalyzer()
            bytecode_ops = bytecode_analyzer.analyze(code)
            
            smell_detector = CodeSmellDetector()
            smells = smell_detector.detect_smells(tree, code)
            
            # Calculate metrics
            time_complexity = complexity_analyzer.get_time_complexity()
            space_complexity = complexity_analyzer.get_space_complexity()
            cyclomatic_complexity = complexity_analyzer.get_cyclomatic_complexity()
            halstead_volume = halstead_analyzer.get_volume()
            smells_count = len(smells)
            
            # Estimate operations
            total_ops = self._estimate_operations(
                halstead_volume, bytecode_ops, time_complexity, 
                input_size_n, smells_count
            )
            
            # Calculate runtime and energy
            runtime_s = (total_ops / self.flops_per_sec) * self.python_overhead
            energy_kwh = self._calculate_energy(
                code, runtime_s, cyclomatic_complexity, 
                space_complexity, smells
            )
            
            # Get carbon intensity
            carbon_intensity = self._get_carbon_intensity(lat, lon)
            
            # Calculate emissions
            emissions_gco2 = energy_kwh * carbon_intensity
            annual_emissions = emissions_gco2 * runs_per_year
            
            # Calculate eco score
            eco_score = max(0, min(100, 100 * (1 - energy_kwh / 0.01)))
            
            # Generate suggestions
            suggestions = self._generate_suggestions(smells, time_complexity)
            
            # Calculate confidence
            total_nodes = len(list(ast.walk(tree)))
            confidence = max(0, 1 - (smells_count / max(total_nodes, 1) * 0.5))
            
            # Generate warnings
            warnings = self._generate_warnings(smells, time_complexity, confidence)
            
            # Calculate equivalents
            equivalents = self._calculate_equivalents(emissions_gco2)
            
            # Log metrics (anonymized)
            code_hash = hash(code) % 1000000
            logging.info(f"Code hash: {code_hash}, Emissions: {emissions_gco2:.6f}g CO2")
            
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
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _check_rate_limit(self) -> bool:
        """Simple rate limiting: 10 requests per minute per IP."""
        current_time = time.time()
        client_ip = "default"  # In production, get real IP
        
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Remove old requests (older than 1 minute)
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip] 
            if current_time - req_time < 60
        ]
        
        if len(self.rate_limits[client_ip]) >= 10:
            return False
        
        self.rate_limits[client_ip].append(current_time)
        return True
    
    def _estimate_operations(self, halstead_volume: float, bytecode_ops: int, 
                           time_complexity: str, input_size_n: int, 
                           smells_count: int) -> float:
        """Estimate total operations from static metrics."""
        # Base operations from Halstead volume
        base_ops = halstead_volume / 10
        
        # Bytecode operations
        bytecode_ops_weighted = bytecode_ops * 1.2
        
        # Complexity scaling
        complexity_multiplier = self._get_complexity_multiplier(time_complexity, input_size_n)
        
        # Smell penalties
        smell_penalty = smells_count * 100
        
        return base_ops + bytecode_ops_weighted + complexity_multiplier + smell_penalty
    
    def _get_complexity_multiplier(self, time_complexity: str, input_size_n: int) -> float:
        """Convert Big O notation to operation count."""
        if "O(1)" in time_complexity:
            return 1
        elif "O(log N)" in time_complexity:
            return math.log2(input_size_n)
        elif "O(N)" in time_complexity:
            return input_size_n
        elif "O(N log N)" in time_complexity:
            return input_size_n * math.log2(input_size_n)
        elif "O(N^2)" in time_complexity:
            return input_size_n ** 2
        elif "O(N^3)" in time_complexity:
            return input_size_n ** 3
        elif "O(2^N)" in time_complexity:
            return 2 ** min(input_size_n, 20)  # Cap exponential
        else:
            return input_size_n  # Default to linear
    
    def _calculate_energy(self, code: str, runtime_s: float, 
                         cyclomatic_complexity: int, space_complexity: str, 
                         smells: List[str]) -> float:
        """Calculate energy consumption in kWh."""
        lines_of_code = len(code.split('\n'))
        
        # Baseline energy (per line)
        baseline_energy = lines_of_code * 1e-6
        
        # Dynamic energy based on complexity
        power_watts = self.cpu_tdp + (cyclomatic_complexity * 2)
        if space_complexity != "O(1)":
            power_watts += 10  # Memory overhead
        
        dynamic_energy = (power_watts * runtime_s) / 3.6e6  # Convert to kWh
        
        # I/O overhead
        io_overhead = 1.2 if any('io' in smell for smell in smells) else 1.0
        
        return (baseline_energy + dynamic_energy) * io_overhead
    
    def _get_carbon_intensity(self, lat: Optional[float], lon: Optional[float]) -> float:
        """Get carbon intensity from Electricity Maps API or use default."""
        if lat is None or lon is None:
            return self.world_avg_carbon_intensity
        
        try:
            url = f"https://api.electricitymaps.com/free/v3/carbon-intensity/latest?lat={lat}&lon={lon}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data.get('carbonIntensity', self.world_avg_carbon_intensity)
        except:
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
                          confidence: float) -> List[str]:
        """Generate warnings for potential issues."""
        warnings = []
        
        if confidence < 0.5:
            warnings.append("Low confidence analysis; manual review recommended")
        
        if "O(2^N)" in time_complexity:
            warnings.append("Exponential complexity detected; may cause performance issues")
        
        if any('io' in smell for smell in smells):
            warnings.append("I/O operations detected; manual adjustment advised")
        
        if len(smells) > 5:
            warnings.append("Multiple code smells detected; consider refactoring")
        
        return warnings
    
    def _calculate_equivalents(self, emissions_gco2: float) -> Dict[str, float]:
        """Calculate environmental equivalents."""
        return {
            "car_km": emissions_gco2 / 120,
            "trees_offset": emissions_gco2 / 22,
            "emails": emissions_gco2 / 4
        }


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor for complexity analysis."""
    
    def __init__(self):
        self.time_complexity = "O(1)"
        self.space_complexity = "O(1)"
        self.cyclomatic_complexity = 1
        self.loop_depth = 0
        self.max_loop_depth = 0
        self.decision_points = 0
        
    def visit_For(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.decision_points += 1
        
        # Analyze loop complexity
        if self.loop_depth == 1:
            self.time_complexity = "O(N)"
        elif self.loop_depth == 2:
            self.time_complexity = "O(N^2)"
        elif self.loop_depth >= 3:
            self.time_complexity = "O(N^3)"
        
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def visit_While(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.decision_points += 1
        self.generic_visit(node)
        self.loop_depth -= 1
    
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
                self.space_complexity = "O(N)"
        self.generic_visit(node)
    
    def get_time_complexity(self) -> str:
        return self.time_complexity
    
    def get_space_complexity(self) -> str:
        return self.space_complexity
    
    def get_cyclomatic_complexity(self) -> int:
        return self.decision_points + 1


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


class CodeSmellDetector:
    """Code smell detector for energy efficiency."""
    
    def detect_smells(self, tree: ast.AST, code: str) -> List[str]:
        """Detect various code smells."""
        smells = []
        
        # String concatenation in loops
        if re.search(r'\+\s*=', code):
            smells.append('string_concat')
        
        # I/O operations
        if re.search(r'(open|requests\.|urllib\.)', code):
            smells.append('io_operations')
        
        # Global variables
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                smells.append('global_variables')
                break
        
        # Nested loops without early exit
        if self._has_nested_loops_without_break(tree):
            smells.append('nested_loop_no_break')
        
        # Recursive functions
        if self._has_recursion(tree):
            smells.append('recursion')
        
        return list(set(smells))  # Remove duplicates
    
    def _has_nested_loops_without_break(self, tree: ast.AST) -> bool:
        """Check for nested loops without break statements."""
        class NestedLoopChecker(ast.NodeVisitor):
            def __init__(self):
                self.loop_depth = 0
                self.has_nested = False
                self.has_break = False
            
            def visit_For(self, node):
                self.loop_depth += 1
                if self.loop_depth >= 2:
                    self.has_nested = True
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_While(self, node):
                self.loop_depth += 1
                if self.loop_depth >= 2:
                    self.has_nested = True
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_Break(self, node):
                self.has_break = True
        
        checker = NestedLoopChecker()
        checker.visit(tree)
        return checker.has_nested and not checker.has_break
    
    def _has_recursion(self, tree: ast.AST) -> bool:
        """Check for recursive function calls."""
        class RecursionChecker(ast.NodeVisitor):
            def __init__(self):
                self.function_names = set()
                self.has_recursion = False
            
            def visit_FunctionDef(self, node):
                self.function_names.add(node.name)
                self.generic_visit(node)
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and node.func.id in self.function_names:
                    self.has_recursion = True
                self.generic_visit(node)
        
        checker = RecursionChecker()
        checker.visit(tree)
        return checker.has_recursion
