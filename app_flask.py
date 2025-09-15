from flask import Flask, render_template, request, jsonify, send_file
import re
import pandas as pd
import io
from werkzeug.utils import secure_filename
import os
from typing import Dict, Optional

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/sagarsinghpricingcalculator'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

class PricingCalculator:
    @staticmethod
    def parse_quantity(quantity_str: str) -> tuple[Optional[float], str]:
        """Parse quantity string and return (total_grams, error_message)."""
        try:
            # Remove spaces and convert to lowercase
            original_str = quantity_str
            quantity_str = quantity_str.replace(" ", "").lower()
            
            # Check if input is just numbers without unit
            if re.match(r'^\d+(?:\.\d+)?$', quantity_str):
                return None, "Please specify the unit of measurement (kg, g, gm, mg, l, ml). Example: 400g, 1.2kg, 500mg, 2l, 250ml"
            
            # Handle multiplication format (e.g., "10x100g", "20*1200g")
            mult_pattern = r'(\d+)[x*](\d+(?:\.\d+)?)([a-z]*)'  
            mult_match = re.match(mult_pattern, quantity_str)
            
            if mult_match:
                count = float(mult_match.group(1))
                weight = float(mult_match.group(2))
                unit = mult_match.group(3)
                
                # Check if unit is missing in multiplication format
                if not unit:
                    return None, "Please specify the unit of measurement. Example: 10x100g, 5x200mg, 3x1.5kg, 2x500ml"
                
                total_weight = count * weight
            else:
                # Handle single quantity format (e.g., "400g", "1.2kg")
                single_pattern = r'(\d+(?:\.\d+)?)([a-z]*)'  
                single_match = re.match(single_pattern, quantity_str)
                
                if single_match:
                    total_weight = float(single_match.group(1))
                    unit = single_match.group(2)
                    
                    # Check if unit is missing
                    if not unit:
                        return None, "Please specify the unit of measurement (kg, g, gm, mg, l, ml). Example: 400g, 1.2kg, 500mg, 2l, 250ml"
                else:
                    return None, "Invalid quantity format. Use formats like '10x100g', '400g', '1.2kg', '500mg'"
            
            # Convert to grams - handle both weight and volume units
            if unit in ["kg", "kilogram", "kilograms"]:
                return total_weight * 1000, ""
            elif unit in ["g", "gm", "gram", "grams"]:
                return total_weight, ""
            elif unit in ["mg", "milligram", "milligrams"]:
                return total_weight / 1000, ""
            elif unit in ["l", "ltr", "litre", "litres", "liter", "liters"]:
                # Convert litres to grams (assuming density of water: 1L = 1000g)
                return total_weight * 1000, ""
            elif unit in ["ml", "millilitre", "millilitres", "milliliter", "milliliters"]:
                # Convert millilitres to grams (assuming density of water: 1ml = 1g)
                return total_weight, ""
            else:
                return None, f"Unsupported unit '{unit}'. Please use kg, g, gm, mg, l, or ml"
                
        except (ValueError, AttributeError):
            return None, "Invalid quantity format. Use formats like '10x100g', '400g', '1.2kg', '500mg'"
    
    @staticmethod
    def calculate_pricing(ingredient_name: str, quantity_input: str, price_input: str) -> Dict:
        """Calculate pricing per different units."""
        result = {
            "success": False,
            "error": "",
            "results": {},
            "ingredient_name": ingredient_name
        }
        
        if not ingredient_name.strip():
            result["error"] = "Please enter an ingredient name."
            return result
        
        if not quantity_input.strip():
            result["error"] = "Please enter a quantity."
            return result
        
        if not price_input.strip():
            result["error"] = "Please enter a price."
            return result
        
        try:
            price = float(price_input)
        except ValueError:
            result["error"] = "Please enter a valid price."
            return result
        
        total_grams, parse_error = PricingCalculator.parse_quantity(quantity_input)
        
        if total_grams is None:
            result["error"] = parse_error
            return result
        
        if total_grams <= 0:
            result["error"] = "Quantity must be greater than zero."
            return result
        
        # Calculate price per gram
        price_per_gram = price / total_grams
        
        # Calculate for different units
        result["results"] = {
            "kg": round(price_per_gram * 1000, 2),
            "g": round(price_per_gram, 4),
            "mg": round(price_per_gram / 1000, 6)
        }
        result["success"] = True
        
        return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    ingredient_name = data.get('ingredient_name', '')
    quantity_input = data.get('quantity_input', '')
    price_input = data.get('price_input', '')
    
    result = PricingCalculator.calculate_pricing(ingredient_name, quantity_input, price_input)
    return jsonify(result)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only Excel (.xlsx, .xls) and CSV files are allowed'}), 400
    
    try:
        # Read the file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Validate that file has exactly 3 columns
        if len(df.columns) != 3:
            return jsonify({
                'error': 'File must contain exactly 3 columns (Ingredient name, Quantity, Pricing)'
            }), 400
        
        # Rename columns to standard names regardless of headers
        df.columns = ['Ingredient name', 'Quantity', 'Pricing']
        
        # Limit to 1000 rows
        if len(df) > 1000:
            return jsonify({
                'error': 'File contains more than 1000 items. Maximum allowed is 1000.'
            }), 400
        
        # Process the data
        results = []
        
        for index, row in df.iterrows():
            ingredient = str(row['Ingredient name']).strip()
            quantity = str(row['Quantity']).strip() if pd.notna(row['Quantity']) else ''
            pricing = row['Pricing'] if pd.notna(row['Pricing']) else 0
            
            if not quantity or quantity.lower() in ['nan', 'none', '']:
                results.append({
                    'ingredient_name': ingredient,
                    'quantity_input': 'Not provided',
                    'price_input': pricing,
                    'results': None,
                    'status': 'Quantity was not provided, so pricing could not be calculated'
                })
            else:
                # Parse the quantity to get grams
                total_grams, parse_error = PricingCalculator.parse_quantity(quantity)
                
                if total_grams is None:
                    results.append({
                        'ingredient_name': ingredient,
                        'quantity_input': quantity,
                        'price_input': pricing,
                        'results': None,
                        'status': f'Error: {parse_error}'
                    })
                else:
                    # Calculate pricing per kg, g, mg
                    price_per_gram = pricing / total_grams if total_grams > 0 else 0
                    price_per_kg = price_per_gram * 1000
                    price_per_mg = price_per_gram / 1000
                    
                    results.append({
                        'ingredient_name': ingredient,
                        'quantity_input': quantity,
                        'price_input': pricing,
                        'results': {
                            'kg': f'₹{price_per_kg:.2f}',
                            'g': f'₹{price_per_gram:.2f}',
                            'mg': f'₹{price_per_mg:.4f}'
                        },
                        'status': 'Calculated successfully'
                    })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_items': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/download', methods=['POST'])
def download_results():
    data = request.get_json()
    results = data.get('results', [])
    file_format = data.get('format', 'excel')  # 'excel' or 'csv'
    
    if not results:
        return jsonify({'error': 'No results to download'}), 400
    
    # Create DataFrame from results
    df = pd.DataFrame(results)
    df.columns = ['Ingredient Name', 'Quantity', 'Unit Price', 'Total Price', 'Status']
    
    # Create file in memory
    output = io.BytesIO()
    
    if file_format == 'csv':
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='pricing_results.csv'
        )
    else:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Pricing Results')
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='pricing_results.xlsx'
        )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)