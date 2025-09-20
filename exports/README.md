# Export Files Directory Structure

This directory contains automatically generated validation results organized by type.

## Directory Structure

```
exports/
├── phone_validation/          # Phone number validation results
├── address_validation/        # Address validation results  
├── duplicate_detection/       # Duplicate detection results
└── README.md                 # This file
```

## File Naming Convention

Files are automatically created with timestamps when validation is performed:

- **Phone Validation**: `Phone_Validation_Results_YYYYMMDD_HHMMSS.xlsx`
- **Address Validation**: `Address_Validation_Results_YYYYMMDD_HHMMSS.xlsx`
- **Duplicate Detection**: `Duplicate_Detection_Results_YYYYMMDD_HHMMSS.xlsx`

## File Contents

Each Excel file contains:
- Original validation data
- Validation results and status
- Confidence scores (where applicable)
- Error messages (if any)
- Export timestamp in `Export_Date` column

## Automatic Export

Files are automatically created in the background when you run:
- 📞 Phone Number Validation
- 🏠 Address Validation  
- 🔄 Duplicate Detection

No manual export steps are required - files are saved automatically with timestamps.
