from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import xlrd
from validation_rules import ValidationEngine

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'xls'}

def get_excel_data(filepath):
    wb = None
    try:
        # Open the workbook
        wb = xlrd.open_workbook(filepath)
        # Get the first sheet
        sheet = wb.sheet_by_index(0)
        
        # Read all data from the sheet
        data = []
        for row_idx in range(sheet.nrows):
            row_data = []
            for col_idx in range(sheet.ncols):
                # Get cell value
                cell_value = sheet.cell_value(row_idx, col_idx)
                
                # For first column (index 0), convert to integer if possible
                if col_idx == 0 and row_idx > 0:  # Skip header row
                    try:
                        # Try to convert to float first to handle both int and float values
                        num = float(cell_value)
                        # If it's a whole number, convert to int, otherwise keep as is
                        cell_value = int(num) if num.is_integer() else num
                    except (ValueError, TypeError):
                        pass  # Keep original value if conversion fails
                
                # Convert to string for display
                row_data.append(str(cell_value) if cell_value is not None else "")
            data.append(row_data)
            
        return data
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
    finally:
        if wb is not None:
            wb.release_resources()

def validate_excel(filepath):
    data = get_excel_data(filepath)
    if not data or not data[0]:
        return False, [], set(), ["File is empty or could not be read"]
    
    validator = ValidationEngine()
    is_valid, invalid_cells, messages = validator.validate(data)
    
    return is_valid, data, invalid_cells, messages

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = None
    is_valid = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            message = 'No file part'
            return render_template('index.html', message=message, is_valid=is_valid)
            
        file = request.files['file']
        
        if file.filename == '':
            message = 'No selected file'
            return render_template('index.html', message=message, is_valid=is_valid)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            is_valid, excel_data, invalid_cells, messages = validate_excel(filepath)
            
            # Create a set of invalid cell coordinates
            invalid_cells_set = {(row, col) for row, col, _ in invalid_cells}
            
            # Clean up the uploaded file
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error removing file {filepath}: {e}")
            
            return render_template('index.html',
                               messages=messages,
                               is_valid=is_valid,
                               excel_data=excel_data if excel_data and len(excel_data) > 0 else None,
                               invalid_cells=invalid_cells_set,
                               filename=filename)
                
    return render_template('index.html', message=message, is_valid=is_valid)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the Journal application')
    parser.add_argument('--live', metavar='IP', nargs='?', const='0.0.0.0',
                      help='Run in production mode with Waitress')
    
    args = parser.parse_args()
    
    if args.live is not None:
        from waitress import serve
        HOST = args.live
        PORT = 5051
        
        print("Запуск Журнального помічника у продакшн-режимі (Waitress)")
        print(f"Доступ:     http://{HOST if HOST != '0.0.0.0' else 'localhost'}:{PORT}")
        
        serve(
            app,
            host=HOST,
            port=PORT,
            threads=4,
            url_scheme='https'
        )
    else:
        print("Запуск Журнального помічника у режимі розробки (Flask)")
        print("Локальний доступ:    http://127.0.0.1:5000")
        app.run(host='127.0.0.1', port=5000, debug=True)
