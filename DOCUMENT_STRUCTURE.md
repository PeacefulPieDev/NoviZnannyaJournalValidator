# Document Structure Specification

This document outlines the expected structure of the Excel files that will be validated.

## File Format
- File extension: `.xls`
- First row is always the header

## Column Structure

| Column | Content |
|--------|---------|
| 1      | Index number |
| 2      | Date |
| 3      | Lesson theme |
| 4      | Home task |
| 5      | Replacement teacher |

## Validation Rules

1. **First Cell Validation**
   - The first cell (A1) must contain the text "Hello"

## Future Validation Ideas
- Date format validation in column 2
- Required fields check
- Data type validation for each column
- Duplicate index number check
