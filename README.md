# edge-data-validation

## Description
The **edge-data-validation** repository provides Python utilities focused on ensuring data quality and integrity before processing. It includes tools for validating and correcting mailing addresses via the USPS API, as well as detecting duplicate or misspelled names using fuzzy matching techniques. These utilities help to improve data reliability for downstream applications.

## Files
- **usps_address_validator.py**  
  Validates and standardizes mailing addresses using the USPS Address Validation API.
- **duplicate_name_detector.py**  
  Identifies duplicate or misspelled names in datasets by leveraging fuzzy matching on full name combinations.

## Prerequisites
- Python 3.7+
- Required libraries: `requests`, `xml.etree.ElementTree`, `pandas`, `fuzzywuzzy`
  - (Optional) Install `python-Levenshtein` for improved performance with fuzzy matching.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/edge-data-validation.git
   cd edge-data-validation
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
* To validate an address using the USPS API:
  ```bash
  python usps_address_validator.py --street "1600 Amphitheatre Parkway" --city "Mountain View" --state "CA" --zip "94043"
  ```

* To detect duplicate or misspelled names in a CSV file:
  ```bash
  python duplicate_name_detector.py --input names.csv --threshold 90
  ```

* For more details, use the `--help` flag:
  ```bash
  python duplicate_name_detector.py --help
  ```

## License
This project is licensed under the MIT License.