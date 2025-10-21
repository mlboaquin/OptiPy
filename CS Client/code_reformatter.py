import ast
from typing import Optional

class EnergyEfficientReformatter(ast.NodeTransformer):
    def __init__(self, keep_comments: bool = True, keep_fstrings: bool = True):
        self.changes_made = []
        self.comments_removed = []
        self.keep_comments = keep_comments
        self.keep_fstrings = keep_fstrings
        
    def visit_Module(self, node):
        """Track comments that will be removed during AST transformation"""
        # Get original source lines if available
        if hasattr(node, 'source_lines'):
            for line in node.source_lines:
                line = line.strip()
                if line.startswith('#'):
                    if not self.keep_comments:
                        self.comments_removed.append(line)
                        self.changes_made.append(f"Removed comment: {line}")
                    else:
                        self.changes_made.append(f"Preserved comment: {line}")
        
        # Continue with normal visit
        self.generic_visit(node)
        return node

    def visit_For(self, node):
        """Convert list.append() in for loops to list comprehension"""
        self.generic_visit(node)  # Continue visiting child nodes
        
        # Check if the loop body is just a single append
        if (len(node.body) == 1 and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Call) and 
            isinstance(node.body[0].value.func, ast.Attribute) and 
            node.body[0].value.func.attr == 'append'):
            
            # Extract the target list and append value
            target_list = node.body[0].value.func.value
            append_value = node.body[0].value.args[0]
            
            # Create list comprehension
            new_node = ast.Assign(
                targets=[target_list],
                value=ast.ListComp(
                    elt=append_value,
                    generators=[ast.comprehension(
                        target=node.target,
                        iter=node.iter,
                        ifs=[],
                        is_async=0
                    )]
                )
            )
            
            self.changes_made.append("Converted for-loop append to list comprehension")
            return new_node
        return node

    def visit_JoinedStr(self, node):
        """Convert f-strings to concatenation with proper type conversion"""
        if self.keep_fstrings:
            # Keep f-strings as they are
            return node
            
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(ast.Constant(value=value.value))
            elif isinstance(value, ast.FormattedValue):
                # Add str() conversion for non-string values
                if (isinstance(value.value, ast.Name) and 
                    value.value.id in ['age', 'count', 'number'] or
                    isinstance(value.value, (ast.Num, ast.BinOp))):
                    parts.append(
                        ast.Call(
                            func=ast.Name(id='str', ctx=ast.Load()),
                            args=[value.value],
                            keywords=[]
                        )
                    )
                else:
                    # Wrap all formatted values with str() for concatenation
                    parts.append(
                        ast.Call(
                            func=ast.Name(id='str', ctx=ast.Load()),
                            args=[value.value],
                            keywords=[]
                        )
                    )
        
        # Build binary operations for string concatenation
        result = parts[0]
        for part in parts[1:]:
            result = ast.BinOp(left=result, op=ast.Add(), right=part)
        
        self.changes_made.append("Converted f-string to string concatenation with type conversion")
        return result

    def visit_Call(self, node):
        """Convert various function calls to more efficient versions"""
        self.generic_visit(node)
        
        # Check for pandas to numpy conversions
        if isinstance(node.func, ast.Attribute):
            # Check if it's a pandas DataFrame/Series method
            if hasattr(node.func.value, 'id') and node.func.value.id in ['df', 'series']:
                # Convert mean() to np.mean() with axis parameter
                if node.func.attr == 'mean':
                    new_node = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='np', ctx=ast.Load()),
                            attr='mean',
                            ctx=ast.Load()
                        ),
                        args=[node.func.value],
                        keywords=[ast.keyword(
                            arg='axis',
                            value=ast.Constant(value=0)
                        )]
                    )
                    self.changes_made.append("Converted pandas mean() to numpy mean() with axis=0")
                    return new_node
                
                # Convert std() to np.std() with axis parameter
                elif node.func.attr == 'std':
                    new_node = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='np', ctx=ast.Load()),
                            attr='std',
                            ctx=ast.Load()
                        ),
                        args=[node.func.value],
                        keywords=[ast.keyword(
                            arg='axis',
                            value=ast.Constant(value=0)
                        )]
                    )
                    self.changes_made.append("Converted pandas std() to numpy std() with axis=0")
                    return new_node
                
                # Convert sort_values() to np.sort() with values conversion
                elif node.func.attr == 'sort_values':
                    new_node = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='np', ctx=ast.Load()),
                            attr='sort',
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.Attribute(
                                value=node.func.value,
                                attr='values',
                                ctx=ast.Load()
                            )
                        ],
                        keywords=[]
                    )
                    self.changes_made.append("Converted pandas sort_values() to numpy sort() with .values")
                    return new_node
                
        return node

def refactor_code(code: str, keep_comments: bool = True, keep_fstrings: bool = True) -> tuple[Optional[str], list[str]]:
    """Refactor code for better energy efficiency.
    
    Args:
        code: The Python code to refactor
        keep_comments: Whether to preserve comments in the output
        keep_fstrings: Whether to preserve f-strings in the output
    """
    try:
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Store original source lines in the AST for comment tracking
        tree.source_lines = code.splitlines()
        
        # Apply our transformations
        reformatter = EnergyEfficientReformatter(keep_comments=keep_comments, keep_fstrings=keep_fstrings)
        modified_tree = reformatter.visit(tree)
        ast.fix_missing_locations(modified_tree)
        
        # Convert back to source code
        refactored = ast.unparse(modified_tree)
        
        # If we need to preserve comments, we need to merge them back
        if keep_comments:
            refactored = _merge_comments_back(code, refactored)
        
        # Validate the refactored code
        try:
            compile(refactored, '<string>', 'exec')
        except Exception as e:
            return None, [f"Refactored code validation failed: {str(e)}"]
        
        return refactored, reformatter.changes_made
        
    except SyntaxError as e:
        return None, [f"Input code has syntax error: {str(e)}"]
    except (ValueError, TypeError) as e:
        return None, [f"Invalid code structure: {str(e)}"]
    except Exception as e:
        return None, [f"Unexpected error during refactoring: {str(e)}"]


def _merge_comments_back(original_code: str, refactored_code: str) -> str:
    """Merge comments from original code back into refactored code."""
    original_lines = original_code.splitlines()
    refactored_lines = refactored_code.splitlines()
    
    # Find comment lines in original code
    comment_lines = []
    for i, line in enumerate(original_lines):
        stripped = line.strip()
        if stripped.startswith('#'):
            comment_lines.append((i, line))
    
    # If no comments, return refactored code as-is
    if not comment_lines:
        return refactored_code
    
    # Insert comments back into refactored code at appropriate positions
    result_lines = refactored_lines.copy()
    
    # For each comment, try to find the best place to insert it
    for line_num, comment_line in comment_lines:
        # Find the closest non-empty line in refactored code
        best_insert_pos = _find_best_insert_position(line_num, result_lines)
        result_lines.insert(best_insert_pos, comment_line)
    
    return '\n'.join(result_lines)


def _find_best_insert_position(original_line_num: int, refactored_lines: list) -> int:
    """Find the best position to insert a comment in the refactored code."""
    # Simple heuristic: try to maintain relative position
    if original_line_num < len(refactored_lines):
        return original_line_num
    else:
        return len(refactored_lines)