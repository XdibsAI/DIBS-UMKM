"""Table Formatter for Mobile-Friendly Display"""
import re
from typing import List, Dict, Optional

def detect_table(text: str) -> bool:
    """Detect if text contains a table"""
    # Check for markdown table indicators
    if '|' in text and '-|-' in text:
        return True
    # Check for multiple columns pattern
    lines = text.split('\n')
    pipe_lines = [l for l in lines if l.count('|') >= 3]
    return len(pipe_lines) >= 2

def parse_markdown_table(text: str) -> Optional[Dict]:
    """Parse markdown table into structured data"""
    try:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Find table lines (those with |)
        table_lines = [l for l in lines if '|' in l]
        if len(table_lines) < 3:  # Need header, separator, at least 1 row
            return None
        
        # Parse header
        header_line = table_lines[0]
        headers = [h.strip() for h in header_line.split('|') if h.strip()]
        
        # Skip separator line (the one with ---)
        data_lines = [l for l in table_lines[2:] if not re.match(r'^[\s\|\-:]+$', l)]
        
        # Parse rows
        rows = []
        for line in data_lines:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) == len(headers):
                row = dict(zip(headers, cells))
                rows.append(row)
        
        if not rows:
            return None
        
        return {
            'headers': headers,
            'rows': rows,
            'row_count': len(rows),
            'col_count': len(headers)
        }
    except Exception as e:
        return None

def format_table_as_cards(table_data: Dict) -> str:
    """Convert table to mobile-friendly card format"""
    if not table_data:
        return ""
    
    headers = table_data['headers']
    rows = table_data['rows']
    
    # Build card-based representation
    output = f"\n📊 **Tabel Data** ({len(rows)} item)\n\n"
    
    for idx, row in enumerate(rows, 1):
        output += f"**{idx}. "
        # Use first column as title
        if headers:
            output += f"{row.get(headers[0], 'Item')}"
        output += "**\n"
        
        # List other columns
        for header in headers[1:]:
            value = row.get(header, '-')
            output += f"• {header}: {value}\n"
        
        output += "\n"
    
    return output

def format_table_as_list(table_data: Dict) -> str:
    """Convert table to bulleted list format"""
    if not table_data:
        return ""
    
    headers = table_data['headers']
    rows = table_data['rows']
    
    output = f"\n📋 **Ringkasan** ({len(rows)} item):\n\n"
    
    for row in rows:
        # Combine all columns in one line
        parts = [f"{h}: {row.get(h, '-')}" for h in headers]
        output += f"• {' | '.join(parts)}\n"
    
    return output

def improve_table_formatting(text: str) -> str:
    """Main function to improve table formatting"""
    if not detect_table(text):
        return text
    
    # Try to parse the table
    table_data = parse_markdown_table(text)
    
    if not table_data:
        return text
    
    # Replace table with formatted version
    # Extract non-table content
    lines = text.split('\n')
    table_start = None
    table_end = None
    
    for i, line in enumerate(lines):
        if '|' in line:
            if table_start is None:
                table_start = i
            table_end = i
    
    if table_start is not None and table_end is not None:
        before = '\n'.join(lines[:table_start])
        after = '\n'.join(lines[table_end+1:])
        
        # Choose format based on table size
        if table_data['row_count'] <= 5:
            formatted = format_table_as_cards(table_data)
        else:
            formatted = format_table_as_list(table_data)
        
        return f"{before}\n{formatted}\n{after}".strip()
    
    return text
