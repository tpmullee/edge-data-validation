# Edge Data Validation

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A robust Python toolkit for data validation and cleaning, focused on address standardization and name deduplication.

## 📋 Overview

**Edge Data Validation** provides powerful utilities to ensure data quality and integrity before processing. The toolkit specializes in:

- **Address validation and standardization** via the USPS API with Smarty as a fallback
- **Duplicate name detection** using advanced fuzzy matching techniques

These tools help improve data reliability for downstream applications, reducing errors and inconsistencies in your datasets.

## 🔧 Core Components

### Address Validation

The `usps_address_validator.py` module validates and standardizes mailing addresses using:
- Primary: USPS Address Validation API
- Fallback: Smarty (formerly SmartyStreets) API

### Duplicate Detection

The `duplicate_name_detector.py` module identifies similar or duplicate entries by:
- Leveraging fuzzy matching algorithms on full name combinations
- Computing similarity scores based on Levenshtein distance
- Generating reports of potential duplicates for review

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Dependencies:
  ```
  requests>=2.28.0
  pandas>=1.3.0
  fuzzywuzzy>=0.18.0
  tqdm>=4.64.0
  ```
- **Performance Enhancement:** Install `python-Levenshtein` for faster fuzzy matching

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/edge-data-validation.git
   cd edge-data-validation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API credentials:**
   ```bash
   # For USPS API access
   export USPS_CONSUMER_KEY="YOUR_USPS_KEY"
   export USPS_CONSUMER_SECRET="YOUR_USPS_SECRET"
   
   # For Smarty API access (fallback service)
   export SMARTY_AUTH_ID="YOUR_SMARTY_ID"
   export SMARTY_AUTH_TOKEN="YOUR_SMARTY_TOKEN"
   ```

## 📝 Usage Examples

### Validating Addresses

```bash
python usps_address_validator.py --street "123 Any St" \
  --city "Anytown" --state "NY" --zip "12345"
```

#### Python API Example

```python
from edge_data_validation import AddressValidator

validator = AddressValidator()
result = validator.validate({
    "street": "123 Any St",
    "city": "Anytown",
    "state": "NY",
    "zip": "12345"
})

print(result.standardized_address)
```

### Detecting Duplicate Names

```bash
python duplicate_name_detector.py --input names.csv --threshold 90
```

#### Python API Example

```python
from edge_data_validation import DuplicateDetector

detector = DuplicateDetector(threshold=90)
duplicates = detector.find_duplicates("names.csv")
detector.generate_report(duplicates, "duplicate_report.csv")
```

## 📊 Sample Output

### Address Validation

```json
{
  "original": {
    "street": "123 Any St",
    "city": "Anytown",
    "state": "NY",
    "zip": "12345"
  },
  "standardized": {
    "street": "123 ANY ST",
    "city": "ANYTOWN",
    "state": "NY",
    "zip": "12345-6789",
    "is_valid": true,
    "validation_source": "USPS"
  }
}
```

### Duplicate Detection

```
Potential Duplicate Groups:
---------------------------
Group 1 (Score: 95):
- John A. Smith
- Jon Smith

Group 2 (Score: 92):
- Sarah Johnson
- Sara Johnson
```

## 🔄 Workflow Integration

Edge Data Validation can be integrated into data pipelines using:

- Direct module imports in Python applications
- Command-line interface for batch processing
- Output to various formats (JSON, CSV, etc.) for downstream tools

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📬 Contact

For questions or feedback, please open an issue on the GitHub repository.