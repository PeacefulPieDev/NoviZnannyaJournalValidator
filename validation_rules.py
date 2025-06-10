from typing import List, Tuple, Set

class ValidationRule:
    # Base class for all validation rules
    
    @property
    def message(self) -> str:
        # Return the warning message for this rule
        raise NotImplementedError("Subclasses must implement this property")
    
    def validate(self, data: List[List]) -> Set[Tuple[int, int]]:
        # Validate the data against the rule
        # Returns a set of (row, col) tuples representing invalid cells
        raise NotImplementedError("Subclasses must implement this method")


class LastLessonNumberRule(ValidationRule):
    # Rule that checks if the last lesson number is one of the expected values
    
    @property
    def message(self) -> str:
        return f"Невірна кількість занять. Має бути {self.expected_value}"
    
    def __init__(self):
        self.expected_value = None
    
    def _find_closest_expected(self, value: int) -> int:
        # Find the closest expected value (35, 70, 105, 140)
        expected_values = [35, 70, 105, 140]
        return min(expected_values, key=lambda x: abs(x - value))
    
    def validate(self, data: List[List]) -> Set[Tuple[int, int]]:
        if not data or len(data) < 2:
            return set()
            
        last_row = data[-1]
        if not last_row or not last_row[0]:
            return set()
            
        try:
            last_lesson = int(float(last_row[0]))
            self.expected_value = self._find_closest_expected(last_lesson)
            if last_lesson != self.expected_value:
                return {(len(data)-1, 0)}
        except (ValueError, TypeError):
            return {(len(data)-1, 0)}


class HomeTaskPresenceRule(ValidationRule):
    # Rule that checks if home task is present when there's a lesson number and theme
    
    @property
    def message(self) -> str:
        if not self.missing_lessons:
            return ""
        lessons_str = ", ".join(map(str, sorted(self.missing_lessons)))
        return f"Відсутнє домашнє завдання у наступних заняттях: {lessons_str}"
    
    def __init__(self):
        self.missing_lessons = set()
    
    def validate(self, data: List[List]) -> Set[Tuple[int, int]]:
        invalid_cells = set()
        self.missing_lessons = set()
        
        # Skip header row (index 0)
        for row_idx, row in enumerate(data[1:], start=1):
            try:
                # Check if lesson number and theme are present (columns 0 and 2, 0-based)
                has_lesson = bool(str(row[0]).strip()) if len(row) > 0 and row[0] is not None else False
                has_theme = bool(str(row[2]).strip()) if len(row) > 2 and row[2] is not None else False
                has_homework = bool(str(row[3]).strip()) if len(row) > 3 and row[3] is not None else False
                
                if has_lesson and has_theme and not has_homework:
                    lesson_num = int(float(row[0]))
                    self.missing_lessons.add(lesson_num)
                    invalid_cells.add((row_idx, 3))  # Home task column (0-based index 3)
            except (IndexError, ValueError, AttributeError, TypeError):
                continue
                
        return invalid_cells


class HomeTaskLinkRule(ValidationRule):
    # Rule that checks if home task contains internet links
    
    @property
    def message(self) -> str:
        if not self.lessons_with_links:
            return ""
        lessons_str = ", ".join(map(str, sorted(self.lessons_with_links)))
        return f"Домашнє завдання не повинно містити посилань (знайдено у заняттях: {lessons_str})"
    
    def __init__(self):
        self.lessons_with_links = set()
    
    def _contains_link(self, text: str) -> bool:
        # Check for common URL patterns
        import re
        url_pattern = re.compile(
            r'https?://\S+|www\.\S+|'  # http://, https://, or www.
            r'\b[a-zA-Z0-9.-]+\.(?:com|org|net|edu|gov|io|uk|ru|ua)\b'  # Common TLDs
        )
        return bool(url_pattern.search(text))
    
    def validate(self, data: List[List]) -> Set[Tuple[int, int]]:
        invalid_cells = set()
        self.lessons_with_links = set()
        
        # Skip header row (index 0)
        for row_idx, row in enumerate(data[1:], start=1):
            try:
                # Check if home task exists (column index 3, 0-based)
                if len(row) > 3 and row[3] is not None:  # Check if home task column exists
                    home_task = str(row[3]).strip()
                    if home_task and self._contains_link(home_task):
                        lesson_num = int(float(row[0]))
                        self.lessons_with_links.add(lesson_num)
                        invalid_cells.add((row_idx, 3))  # Home task column (0-based index 3)
            except (IndexError, ValueError, AttributeError, TypeError):
                continue
                
        return invalid_cells


class ThemeLengthRule(ValidationRule):
    # Rule that checks if theme is not longer than 100 symbols
    
    @property
    def message(self) -> str:
        if not self.too_long_themes:
            return ""
        lessons_str = ", ".join(map(str, sorted(self.too_long_themes)))
        return f"Занадто довга тема (макс. 100 символів) у заняттях: {lessons_str}"
    
    def __init__(self):
        self.too_long_themes = set()
    
    def validate(self, data: List[List]) -> Set[Tuple[int, int]]:
        self.too_long_themes = set()
        invalid_cells = set()
        
        for row_idx, row in enumerate(data[1:], 1):  # Skip header row, start from index 1
            try:
                if len(row) > 2 and row[2] is not None:  # Check if theme column (index 2) exists
                    lesson_num = int(float(row[0]))
                    theme = str(row[2]).strip()  # Theme is in column index 2
                    
                    if theme and len(theme) > 100:
                        self.too_long_themes.add(lesson_num)
                        invalid_cells.add((row_idx, 2))  # Theme column is index 2
                        
            except (ValueError, IndexError, AttributeError, TypeError):
                continue
                
        return invalid_cells


class HomeTaskLengthRule(ValidationRule):
    # Rule that checks if home task is not longer than 60 symbols
    
    @property
    def message(self) -> str:
        if not self.too_long_tasks:
            return ""
        lessons_str = ", ".join(map(str, sorted(self.too_long_tasks)))
        return f"Занадто довге домашнє завдання (макс. 60 символів) у заняттях: {lessons_str}"
    
    def __init__(self):
        self.too_long_tasks = set()
    
    def validate(self, data: List[List]) -> Set[Tuple[int, int]]:
        self.too_long_tasks = set()
        invalid_cells = set()
        
        # Skip header row (index 0)
        for row_idx, row in enumerate(data[1:], start=1):
            try:
                # Check home task length (column index 3, 0-based)
                if len(row) > 3 and row[3] is not None:  # Check if home task column exists
                    home_task = str(row[3]).strip()  # Home task is in column index 3
                    if home_task and len(home_task) > 60:
                        lesson_num = int(float(row[0]))
                        self.too_long_tasks.add(lesson_num)
                        invalid_cells.add((row_idx, 3))  # Home task column (0-based index 3)
            except (IndexError, AttributeError, TypeError):
                continue
                
        return invalid_cells


class DateValidationRule(ValidationRule):
    # Rule that checks if dates are valid and within the allowed range
    
    def __init__(self):
        self.invalid_lessons = set()
        from datetime import datetime
        self.min_date = datetime(2025, 1, 1).date()
        self.max_date = datetime(2025, 6, 15).date()
    
    @property
    def message(self) -> str:
        if not self.invalid_lessons:
            return ""
        # Convert lesson numbers to strings and sort them
        sorted_lessons = sorted(self.invalid_lessons)
        lessons_str = ", ".join(map(str, sorted_lessons))
        return f"Знайдено некоректні дати у заняттях: {lessons_str}. Дати мають бути в межах з 2025-01-01 по 2025-06-15"
    
    def _is_valid_date(self, date_str: str) -> bool:
        # Check if the date string is in the format DD.MM.YYYY and within the allowed range
        try:
            day, month, year = map(int, date_str.split('.'))
            from datetime import date
            d = date(year, month, day)
            return self.min_date <= d <= self.max_date
        except (ValueError, AttributeError):
            return False
    
    def validate(self, data: List[List]) -> Set[Tuple[int, int]]:
        self.invalid_lessons = set()
        invalid_cells = set()
        
        if not data or len(data) < 2:  # Skip if no data or only header
            return invalid_cells
            
        for row_idx, row in enumerate(data[1:], 1):  # Skip header row
            try:
                if len(row) > 1 and row[0] is not None:  # Check if lesson number and date columns exist
                    lesson_num = int(float(row[0]))
                    date_str = str(row[1]).strip()
                    # Check for any non-empty cell that's not a valid date
                    if not date_str or not self._is_valid_date(date_str):
                        self.invalid_lessons.add(lesson_num)
                        invalid_cells.add((row_idx, 1))  # Date column (0-based index 1)
            except (IndexError, ValueError, AttributeError):
                continue
                
        return invalid_cells


class ValidationEngine:
    # Applies all validation rules to the data
    
    def __init__(self):
        self.rules = [
            LastLessonNumberRule(),
            HomeTaskPresenceRule(),
            HomeTaskLinkRule(),
            ThemeLengthRule(),
            HomeTaskLengthRule(),
            DateValidationRule()
            # Add more rules here as they are created
        ]
    
    def validate(self, data: List[List]) -> Tuple[bool, Set[Tuple[int, int, str]], List[str]]:
        # Apply all validation rules to the data
        # Returns a tuple of (is_valid, invalid_cells, messages)
        all_invalid_cells = set()
        all_messages = []
        
        for rule in self.rules:
            invalid_cells = rule.validate(data)
            if invalid_cells:
                # Convert to the new format (row, col, rule_id)
                rule_id = rule.__class__.__name__.lower().replace('rule', '')
                updated_cells = {(r, c, rule_id) for r, c in invalid_cells}
                all_invalid_cells.update(updated_cells)
                all_messages.append(rule.message)
        
        is_valid = len(all_invalid_cells) == 0
        return is_valid, all_invalid_cells, all_messages
