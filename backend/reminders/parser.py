"""Parse reminder commands - IMPROVED"""
import re
from datetime import datetime, timedelta
from typing import Optional, Dict

class ReminderParser:
    """Parse reminder creation commands"""
    
    def parse(self, text: str) -> Optional[Dict]:
        """Extract reminder info from text"""
        text_lower = text.lower().strip()
        
        # Remove DIBS prefix
        text_lower = re.sub(r'^dibs[,\s]+', '', text_lower)
        
        # Pattern 1: "ingatkan saya/aku [waktu] (lagi) untuk [task]"
        # Support: "ingatkan aku 1 menit lagi untuk X"
        #          "ingatkan saya 7 hari untuk X"
        match = re.search(
            r'ingatkan\s+(?:saya|aku|kak)\s+(.+?)\s+(?:lagi\s+)?(?:untuk|tentang|bahwa|:\s*)\s*(.+)',
            text_lower
        )
        if match:
            time_str = match.group(1).replace('lagi', '').strip()
            task = match.group(2).strip()
            
            due_date = self._parse_time(time_str)
            if due_date:
                return {
                    'action': 'create_reminder',
                    'title': task,
                    'due_date': due_date,
                    'time_str': time_str
                }
        
        # Pattern 2: "set/buat reminder [waktu] [task]"
        match = re.search(
            r'(?:set|buat|tambah)\s+(?:reminder|pengingat)\s+(.+)',
            text_lower
        )
        if match:
            content = match.group(1)
            
            # Extract time
            time_match = re.search(r'(\d+)\s+(menit|hari|minggu|bulan|jam)', content)
            if time_match:
                time_str = time_match.group(0)
                task = content.replace(time_str, '').strip()
                task = re.sub(r'^(untuk|tentang)\s+', '', task)
                
                due_date = self._parse_time(time_str)
                if due_date:
                    return {
                        'action': 'create_reminder',
                        'title': task,
                        'due_date': due_date,
                        'time_str': time_str
                    }
        
        # Pattern 3: "reminder [task] [waktu]"
        match = re.search(
            r'reminder\s+(.+?)\s+(\d+\s+(?:menit|hari|minggu|bulan|jam))',
            text_lower
        )
        if match:
            task = match.group(1)
            time_str = match.group(2)
            
            due_date = self._parse_time(time_str)
            if due_date:
                return {
                    'action': 'create_reminder',
                    'title': task,
                    'due_date': due_date,
                    'time_str': time_str
                }
        
        return None
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse relative time into datetime"""
        now = datetime.now()
        
        # "N menit/jam/hari/minggu/bulan"
        match = re.search(r'(\d+)\s+(menit|hari|minggu|bulan|jam)', time_str)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'menit':
                return now + timedelta(minutes=amount)
            elif unit == 'jam':
                return now + timedelta(hours=amount)
            elif unit == 'hari':
                return now + timedelta(days=amount)
            elif unit == 'minggu':
                return now + timedelta(weeks=amount)
            elif unit == 'bulan':
                return now + timedelta(days=amount*30)
        
        # "besok"
        if 'besok' in time_str:
            return now + timedelta(days=1)
        
        # "lusa"
        if 'lusa' in time_str:
            return now + timedelta(days=2)
        
        return None

# Singleton
reminder_parser = ReminderParser()
