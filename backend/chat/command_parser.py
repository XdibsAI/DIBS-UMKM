"""Smart Command Parser - FIXED"""
import re
from typing import Optional, Dict

class CommandParser:
    """Parse database commands"""
    
    def parse(self, text: str) -> Optional[Dict]:
        """Detect and parse DB commands"""
        text_lower = text.lower().strip()
        
        # Remove DIBS prefix
        text_lower = re.sub(r'^dibs[,\s]+', '', text_lower)
        
        # SAVE: "simpan [anything] ke/di db.TABLE: DATA" or "simpan ke db.TABLE: DATA"
        # Key: DATA is AFTER the colon (:)
        save_pattern = r'(?:simpan|catat|tambahkan?)\s+.*?(?:ke|di)\s+db\.(\w+)\s*:\s*(.+)'
        match = re.search(save_pattern, text_lower)
        if match:
            table = match.group(1)
            data_str = match.group(2)
            
            return {
                'action': 'save',
                'table': table,
                'data': self._parse_data(data_str),
                'original': text,
                'raw_data': data_str
            }
        
        # SAVE variant 2: "simpan ke db.TABLE [space] DATA" (no colon)
        save_pattern2 = r'(?:simpan|catat)\s+(?:ke|di)\s+db\.(\w+)\s+(.+)'
        match = re.search(save_pattern2, text_lower)
        if match:
            table = match.group(1)
            data_str = match.group(2)
            
            return {
                'action': 'save',
                'table': table,
                'data': self._parse_data(data_str),
                'original': text,
                'raw_data': data_str
            }
        
        # QUERY: "tampilkan/lihat db.TABLE"
        query_pattern = r'(?:tampilkan|lihat|cari|ambil)\s+(?:data\s+)?db\.(\w+)'
        match = re.search(query_pattern, text_lower)
        if match:
            return {
                'action': 'query',
                'table': match.group(1),
                'original': text
            }
        
        return None
    
    def _parse_data(self, data_str: str) -> Dict:
        """Parse key:value pairs from string"""
        data = {}
        
        # Clean input
        data_str = data_str.strip()
        
        # Pattern: "key: value, key2: value2" or "key: value key2: value2"
        pairs = re.findall(r'(\w+)\s*:\s*([^,\n]+?)(?:,|$|\s+\w+:)', data_str + ',')
        
        if pairs:
            for key, value in pairs:
                clean_key = key.strip()
                clean_value = value.strip().rstrip(',')
                data[clean_key] = clean_value
        
        # If no pairs found, try split by comma
        if not data and ',' in data_str:
            parts = [p.strip() for p in data_str.split(',')]
            for i, part in enumerate(parts):
                if ':' in part:
                    k, v = part.split(':', 1)
                    data[k.strip()] = v.strip()
                else:
                    data[f'field_{i+1}'] = part
        
        # Fallback: save as content
        if not data:
            data['content'] = data_str
        
        return data

# Singleton
command_parser = CommandParser()
