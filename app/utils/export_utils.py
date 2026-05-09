# app/utils/export_utils.py
import pandas as pd
import io
from flask import send_file
from datetime import datetime

def export_model_to_csv(model_data, filename_prefix):
    """
    Export SQLAlchemy model data to CSV file
    
    Args:
        model_data: Query results from SQLAlchemy model
        filename_prefix: Prefix for the generated filename
    
    Returns:
        Flask response with CSV file attachment
    """
    # Convert to DataFrame
    if not model_data:
        df = pd.DataFrame()
    else:
        # Convert SQLAlchemy model objects to dictionaries
        records = []
        for item in model_data:
            record = {column.name: getattr(item, column.name) 
                     for column in item.__table__.columns}
            # Add any computed properties that aren't in the table
            if hasattr(item, 'full_name'):
                record['full_name'] = item.full_name
            records.append(record)
        
        df = pd.DataFrame(records)
    
    # Generate output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        download_name=filename,
        as_attachment=True
    )

def export_model_to_excel(model_data, filename_prefix):
    """
    Export SQLAlchemy model data to Excel file
    
    Args:
        model_data: Query results from SQLAlchemy model
        filename_prefix: Prefix for the generated filename
    
    Returns:
        Flask response with Excel file attachment
    """
    # Convert to DataFrame
    if not model_data:
        df = pd.DataFrame()
    else:
        # Convert SQLAlchemy model objects to dictionaries
        records = []
        for item in model_data:
            record = {column.name: getattr(item, column.name) 
                     for column in item.__table__.columns}
            # Add any computed properties that aren't in the table
            if hasattr(item, 'full_name'):
                record['full_name'] = item.full_name
            records.append(record)
        
        df = pd.DataFrame(records)
    
    # Generate output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.xlsx"
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
        
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Data']
        
        # Add a header format
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Write the column headers with the defined format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Set column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name=filename,
        as_attachment=True
    )