"""
Calculator tool for mathematical operations and data analysis.
"""

from langchain.tools import tool
import json
import math
import statistics
from typing import Union


@tool
def calculate(expression: str) -> str:
    """
    Perform mathematical calculations and statistical operations.
    
    This tool can evaluate mathematical expressions, perform statistical
    calculations, and handle complex numerical operations. It supports
    basic arithmetic, percentages, growth calculations, and statistical functions.
    
    Args:
        expression (str): Mathematical expression or operation to evaluate
    
    Returns:
        str: Calculation result with explanation
    
    Supported operations:
        - Basic math: +, -, *, /, **, %
        - Functions: sqrt, log, exp, sin, cos, tan
        - Statistics: mean, median, sum, min, max
        - Growth: percentage change, CAGR
    
    Examples:
        >>> calculate("1000 * 1.15")  # Growth calculation
        >>> calculate("sum([10, 20, 30, 40])")  # Sum of values
        >>> calculate("(200 - 150) / 150 * 100")  # Percentage change
    """
    try:
        # Create safe evaluation environment
        safe_dict = {
            # Math functions
            'sqrt': math.sqrt,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'abs': abs,
            'round': round,
            'pow': pow,
            
            # Statistics functions
            'sum': sum,
            'min': min,
            'max': max,
            'mean': statistics.mean,
            'median': statistics.median,
            'stdev': statistics.stdev,
            
            # Constants
            'pi': math.pi,
            'e': math.e,
        }
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        return json.dumps({
            "status": "success",
            "expression": expression,
            "result": result,
            "formatted": f"{result:,.2f}" if isinstance(result, (int, float)) else str(result)
        }, indent=2)
        
    except ZeroDivisionError:
        return json.dumps({
            "status": "error",
            "message": "Division by zero error",
            "expression": expression
        })
    except NameError as e:
        return json.dumps({
            "status": "error",
            "message": f"Unknown function or variable: {str(e)}",
            "expression": expression
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Calculation failed: {str(e)}",
            "expression": expression
        })


@tool
def percentage_change(old_value: float, new_value: float) -> str:
    """
    Calculate percentage change between two values.
    
    Args:
        old_value (float): Original value
        new_value (float): New value
    
    Returns:
        str: Percentage change with direction (increase/decrease)
    
    Example:
        >>> percentage_change(100, 150)  # 50% increase
    """
    try:
        if old_value == 0:
            return "Cannot calculate percentage change from zero"
        
        change = ((new_value - old_value) / old_value) * 100
        direction = "increase" if change > 0 else "decrease"
        
        return json.dumps({
            "status": "success",
            "old_value": old_value,
            "new_value": new_value,
            "percentage_change": round(abs(change), 2),
            "direction": direction,
            "summary": f"{abs(change):.2f}% {direction}"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Calculation failed: {str(e)}"
        })


@tool
def compound_growth_rate(start_value: float, end_value: float, years: float) -> str:
    """
    Calculate Compound Annual Growth Rate (CAGR).
    
    Args:
        start_value (float): Starting value
        end_value (float): Ending value
        years (float): Number of years
    
    Returns:
        str: CAGR percentage
    
    Example:
        >>> compound_growth_rate(11000000000, 188000000000, 6)  # Market growth
    """
    try:
        if start_value <= 0 or years <= 0:
            return "Start value and years must be positive"
        
        cagr = (pow(end_value / start_value, 1 / years) - 1) * 100
        
        return json.dumps({
            "status": "success",
            "start_value": start_value,
            "end_value": end_value,
            "years": years,
            "cagr_percentage": round(cagr, 2),
            "summary": f"CAGR: {cagr:.2f}% over {years} years"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Calculation failed: {str(e)}"
        })
