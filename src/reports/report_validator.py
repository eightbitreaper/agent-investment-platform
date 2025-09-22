"""
Report Validation System for Agent Investment Platform

This module provides validation and quality checks for generated investment reports
to ensure they meet standards for completeness, accuracy, and professional presentation.
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required. Install with: pip install PyYAML")


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationCategory(Enum):
    """Categories of validation checks."""
    STRUCTURE = "structure"
    CONTENT = "content"
    FORMAT = "format"
    DATA = "data"
    COMPLIANCE = "compliance"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a report."""
    level: ValidationLevel
    category: ValidationCategory
    message: str
    line_number: Optional[int] = None
    section: Optional[str] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Results of report validation."""
    is_valid: bool
    score: float  # 0-100
    issues: List[ValidationIssue] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    validation_time: float = 0.0

    def get_issues_by_level(self, level: ValidationLevel) -> List[ValidationIssue]:
        """Get issues filtered by severity level."""
        return [issue for issue in self.issues if issue.level == level]

    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationIssue]:
        """Get issues filtered by category."""
        return [issue for issue in self.issues if issue.category == category]


class ReportValidator:
    """
    Validates investment reports for quality and completeness.

    Features:
    - Structure validation (required sections, formatting)
    - Content validation (data consistency, completeness)
    - Format validation (markdown syntax, links, tables)
    - Data validation (numerical accuracy, date formats)
    - Compliance validation (disclaimers, risk warnings)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the report validator.

        Args:
            config_path: Path to validation configuration file
        """
        self.logger = logging.getLogger(__name__)

        # Load validation configuration
        if config_path:
            self.config = self._load_config(config_path)
        else:
            self.config = self._get_default_config()

        # Compile regex patterns for efficiency
        self._compile_patterns()

    def validate_report(self, report_content: str, report_metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a complete report.

        Args:
            report_content: Markdown content of the report
            report_metadata: Optional metadata about the report

        Returns:
            Validation result with issues and score
        """
        start_time = datetime.now()
        issues = []
        statistics = {}

        try:
            # Structure validation
            structure_issues = self._validate_structure(report_content)
            issues.extend(structure_issues)

            # Content validation
            content_issues = self._validate_content(report_content, report_metadata)
            issues.extend(content_issues)

            # Format validation
            format_issues = self._validate_format(report_content)
            issues.extend(format_issues)

            # Data validation
            data_issues = self._validate_data(report_content)
            issues.extend(data_issues)

            # Compliance validation
            compliance_issues = self._validate_compliance(report_content)
            issues.extend(compliance_issues)

            # Calculate statistics
            statistics = self._calculate_statistics(report_content, issues)

            # Calculate overall score
            score = self._calculate_score(issues, statistics)

            # Determine if report is valid
            error_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
            is_valid = error_count == 0 and score >= self.config.get('min_score', 70)

            validation_time = (datetime.now() - start_time).total_seconds()

            return ValidationResult(
                is_valid=is_valid,
                score=score,
                issues=issues,
                statistics=statistics,
                validation_time=validation_time
            )

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                issues=[ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Validation process failed: {str(e)}"
                )],
                validation_time=(datetime.now() - start_time).total_seconds()
            )

    def validate_report_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate a report file.

        Args:
            file_path: Path to the report file

        Returns:
            Validation result
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                return ValidationResult(
                    is_valid=False,
                    score=0.0,
                    issues=[ValidationIssue(
                        level=ValidationLevel.ERROR,
                        category=ValidationCategory.STRUCTURE,
                        message=f"Report file not found: {file_path}"
                    )]
                )

            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata from filename/path
            metadata = {
                'filename': file_path.name,
                'file_size': file_path.stat().st_size,
                'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime)
            }

            return self.validate_report(content, metadata)

        except Exception as e:
            self.logger.error(f"Failed to validate file {file_path}: {e}")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                issues=[ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Failed to read report file: {str(e)}"
                )]
            )

    def _validate_structure(self, content: str) -> List[ValidationIssue]:
        """Validate report structure and required sections."""
        issues = []

        # Check for required sections
        required_sections = self.config.get('required_sections', [])
        for section in required_sections:
            if not self._has_section(content, section):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Missing required section: {section}",
                    suggestion=f"Add a '{section}' section to the report"
                ))

        # Check section hierarchy
        headers = self._extract_headers(content)
        hierarchy_issues = self._validate_header_hierarchy(headers)
        issues.extend(hierarchy_issues)

        # Check minimum content length
        min_length = self.config.get('min_content_length', 1000)
        if len(content) < min_length:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.STRUCTURE,
                message=f"Report content is too short ({len(content)} chars, minimum {min_length})",
                suggestion="Add more detailed analysis and explanations"
            ))

        # Check for title
        if not content.strip().startswith('#'):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category=ValidationCategory.STRUCTURE,
                message="Report must start with a title (# heading)",
                suggestion="Add a descriptive title at the beginning of the report"
            ))

        return issues

    def _validate_content(self, content: str, metadata: Optional[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate report content quality and completeness."""
        issues = []

        # Check for empty sections
        sections = self._extract_sections(content)
        for section_name, section_content in sections.items():
            if len(section_content.strip()) < 50:  # Very short sections
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category=ValidationCategory.CONTENT,
                    message=f"Section '{section_name}' has minimal content",
                    section=section_name,
                    suggestion="Provide more detailed information in this section"
                ))

        # Check for placeholder text
        placeholders = ['TODO', 'TBD', 'PLACEHOLDER', '{{', 'Lorem ipsum']
        for placeholder in placeholders:
            if placeholder.lower() in content.lower():
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category=ValidationCategory.CONTENT,
                    message=f"Placeholder text found: {placeholder}",
                    suggestion="Replace placeholder text with actual content"
                ))

        # Check for recent data
        if metadata and 'modified_time' in metadata:
            modified_time = metadata['modified_time']
            if isinstance(modified_time, datetime):
                age_days = (datetime.now() - modified_time).days
                max_age = self.config.get('max_data_age_days', 7)

                if age_days > max_age:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category=ValidationCategory.CONTENT,
                        message=f"Report data may be outdated ({age_days} days old)",
                        suggestion="Update report with fresh market data"
                    ))

        # Check for balanced analysis
        positive_words = ['buy', 'strong', 'bullish', 'growth', 'opportunity', 'positive']
        negative_words = ['sell', 'weak', 'bearish', 'decline', 'risk', 'negative']

        content_lower = content.lower()
        positive_count = sum(content_lower.count(word) for word in positive_words)
        negative_count = sum(content_lower.count(word) for word in negative_words)

        if positive_count > 0 and negative_count == 0:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.CONTENT,
                message="Analysis appears overly optimistic - consider including risks",
                suggestion="Add risk analysis and potential downsides"
            ))
        elif negative_count > 0 and positive_count == 0:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category=ValidationCategory.CONTENT,
                message="Analysis appears overly pessimistic - consider including opportunities",
                suggestion="Add potential opportunities and positive factors"
            ))

        return issues

    def _validate_format(self, content: str) -> List[ValidationIssue]:
        """Validate markdown formatting and syntax."""
        issues = []
        lines = content.split('\n')

        # Check for broken links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(link_pattern, line)
            for match in matches:
                link_text, link_url = match.groups()

                # Check for empty links
                if not link_url.strip():
                    issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        category=ValidationCategory.FORMAT,
                        message=f"Empty link URL: [{link_text}]()",
                        line_number=line_num
                    ))

                # Check for placeholder links
                if link_url in ['#', 'TODO', 'TBD']:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category=ValidationCategory.FORMAT,
                        message=f"Placeholder link: [{link_text}]({link_url})",
                        line_number=line_num
                    ))

        # Check table formatting
        table_issues = self._validate_tables(content)
        issues.extend(table_issues)

        # Check for consistent heading styles
        heading_issues = self._validate_heading_consistency(content)
        issues.extend(heading_issues)

        return issues

    def _validate_data(self, content: str) -> List[ValidationIssue]:
        """Validate numerical data and calculations."""
        issues = []

        # Check for reasonable numerical values
        number_pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        numbers = re.findall(number_pattern, content)

        for number_str in numbers:
            try:
                number = float(number_str.replace(',', ''))

                # Check for extremely large/small values that might be errors
                if number > 1e12:  # Trillion+
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category=ValidationCategory.DATA,
                        message=f"Unusually large number: {number_str}",
                        suggestion="Verify this number is correct"
                    ))
                elif 0 < number < 1e-6:  # Very small positive number
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category=ValidationCategory.DATA,
                        message=f"Unusually small number: {number_str}",
                        suggestion="Verify this number is correct"
                    ))
            except ValueError:
                continue

        # Check percentage values
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        percentages = re.findall(percentage_pattern, content)

        for pct_str in percentages:
            try:
                pct = float(pct_str)
                if pct > 1000:  # Probably an error
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category=ValidationCategory.DATA,
                        message=f"Unusually high percentage: {pct}%",
                        suggestion="Verify this percentage is correct"
                    ))
            except ValueError:
                continue

        # Check date formats
        date_issues = self._validate_dates(content)
        issues.extend(date_issues)

        return issues

    def _validate_compliance(self, content: str) -> List[ValidationIssue]:
        """Validate compliance with regulatory and professional standards."""
        issues = []

        # Check for required disclaimers
        required_disclaimers = self.config.get('required_disclaimers', [])
        content_lower = content.lower()

        for disclaimer in required_disclaimers:
            if disclaimer.lower() not in content_lower:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category=ValidationCategory.COMPLIANCE,
                    message=f"Missing required disclaimer: {disclaimer}",
                    suggestion="Add appropriate disclaimers and risk warnings"
                ))

        # Check for investment advice warnings
        advice_keywords = ['should buy', 'should sell', 'guaranteed', 'certain profit', 'risk-free']
        for keyword in advice_keywords:
            if keyword.lower() in content_lower:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category=ValidationCategory.COMPLIANCE,
                    message=f"Potentially problematic language: '{keyword}'",
                    suggestion="Avoid language that could be construed as specific investment advice"
                ))

        # Check for bias indicators
        bias_phrases = ['definitely will', 'never fails', 'always profitable', 'impossible to lose']
        for phrase in bias_phrases:
            if phrase.lower() in content_lower:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category=ValidationCategory.COMPLIANCE,
                    message=f"Potentially biased language: '{phrase}'",
                    suggestion="Use more balanced and objective language"
                ))

        return issues

    def _has_section(self, content: str, section_name: str) -> bool:
        """Check if content has a specific section."""
        pattern = rf'^#+\s*{re.escape(section_name)}'
        return bool(re.search(pattern, content, re.MULTILINE | re.IGNORECASE))

    def _extract_headers(self, content: str) -> List[Tuple[int, str]]:
        """Extract headers with their levels."""
        headers = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                headers.append((level, title))

        return headers

    def _validate_header_hierarchy(self, headers: List[Tuple[int, str]]) -> List[ValidationIssue]:
        """Validate header hierarchy (H1 -> H2 -> H3, etc.)."""
        issues = []

        if not headers:
            return issues

        prev_level = 0
        for level, title in headers:
            if level > prev_level + 1:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category=ValidationCategory.STRUCTURE,
                    message=f"Header level skipped: '{title}' (H{level} after H{prev_level})",
                    suggestion="Use proper header hierarchy (H1 -> H2 -> H3)"
                ))
            prev_level = level

        return issues

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections and their content."""
        sections = {}
        lines = content.split('\n')
        current_section = "Introduction"
        current_content = []

        for line in lines:
            if line.strip().startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)

                # Start new section
                current_section = line.strip().lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _validate_tables(self, content: str) -> List[ValidationIssue]:
        """Validate markdown table formatting."""
        issues = []
        lines = content.split('\n')

        in_table = False
        table_start_line = 0
        header_row = None

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Check if this looks like a table row
            if '|' in line and line.count('|') >= 2:
                if not in_table:
                    in_table = True
                    table_start_line = line_num
                    header_row = line
                else:
                    # Check column count consistency
                    if header_row and line.count('|') != header_row.count('|'):
                        issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            category=ValidationCategory.FORMAT,
                            message=f"Table row has inconsistent column count at line {line_num}",
                            line_number=line_num,
                            suggestion="Ensure all table rows have the same number of columns"
                        ))
            else:
                if in_table:
                    in_table = False
                    # Table ended, could add more validation here

        return issues

    def _validate_heading_consistency(self, content: str) -> List[ValidationIssue]:
        """Validate consistent heading styles."""
        issues = []

        # Check for mixed heading styles (# vs underline)
        lines = content.split('\n')
        has_hash_headings = any(line.strip().startswith('#') for line in lines)
        has_underline_headings = False

        for i, line in enumerate(lines[:-1]):
            next_line = lines[i + 1]
            if (next_line.strip() and
                all(c in '=-' for c in next_line.strip()) and
                len(next_line.strip()) >= len(line.strip()) * 0.5):
                has_underline_headings = True
                break

        if has_hash_headings and has_underline_headings:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category=ValidationCategory.FORMAT,
                message="Mixed heading styles detected (# and underline)",
                suggestion="Use consistent heading style throughout the report"
            ))

        return issues

    def _validate_dates(self, content: str) -> List[ValidationIssue]:
        """Validate date formats and reasonableness."""
        issues = []

        # Common date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                date_str = match.group()

                # Try to parse and validate the date
                try:
                    if '-' in date_str:
                        if date_str.count('-') == 2 and len(date_str.split('-')[0]) == 4:
                            # YYYY-MM-DD
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        else:
                            # MM-DD-YYYY
                            date_obj = datetime.strptime(date_str, '%m-%d-%Y')
                    else:
                        # MM/DD/YYYY
                        date_obj = datetime.strptime(date_str, '%m/%d/%Y')

                    # Check if date is reasonable (not too far in future/past)
                    now = datetime.now()
                    if date_obj > now + timedelta(days=365):
                        issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            category=ValidationCategory.DATA,
                            message=f"Date appears to be far in the future: {date_str}",
                            suggestion="Verify this date is correct"
                        ))
                    elif date_obj < now - timedelta(days=365 * 10):
                        issues.append(ValidationIssue(
                            level=ValidationLevel.INFO,
                            category=ValidationCategory.DATA,
                            message=f"Date appears to be quite old: {date_str}",
                            suggestion="Consider if this historical date is still relevant"
                        ))

                except ValueError:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        category=ValidationCategory.DATA,
                        message=f"Invalid date format: {date_str}",
                        suggestion="Use consistent date format (YYYY-MM-DD recommended)"
                    ))

        return issues

    def _calculate_statistics(self, content: str, issues: List[ValidationIssue]) -> Dict[str, Any]:
        """Calculate report statistics."""
        lines = content.split('\n')

        return {
            'total_lines': len(lines),
            'total_characters': len(content),
            'total_words': len(content.split()),
            'header_count': len([l for l in lines if l.strip().startswith('#')]),
            'table_count': len([l for l in lines if '|' in l and l.count('|') >= 2]),
            'link_count': len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)),
            'error_count': len([i for i in issues if i.level == ValidationLevel.ERROR]),
            'warning_count': len([i for i in issues if i.level == ValidationLevel.WARNING]),
            'info_count': len([i for i in issues if i.level == ValidationLevel.INFO])
        }

    def _calculate_score(self, issues: List[ValidationIssue], statistics: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)."""
        base_score = 100.0

        # Deduct points for issues
        for issue in issues:
            if issue.level == ValidationLevel.ERROR:
                base_score -= 20
            elif issue.level == ValidationLevel.WARNING:
                base_score -= 5
            elif issue.level == ValidationLevel.INFO:
                base_score -= 1

        # Bonus points for good practices
        if statistics['header_count'] >= 5:
            base_score += 5  # Good structure

        if statistics['total_words'] >= 500:
            base_score += 5  # Adequate length

        if statistics['table_count'] >= 1:
            base_score += 3  # Good data presentation

        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, base_score))

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load validation configuration from file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load validation config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default validation configuration."""
        return {
            'required_sections': [
                'Executive Summary',
                'Analysis',
                'Recommendations',
                'Risk Assessment',
                'Disclaimer'
            ],
            'required_disclaimers': [
                'not financial advice',
                'past performance',
                'risk of loss'
            ],
            'min_content_length': 1000,
            'min_score': 70,
            'max_data_age_days': 7
        }

    def _compile_patterns(self):
        """Compile regex patterns for performance."""
        # Could add compiled patterns here for frequently used regex
        pass


# Convenience functions
def validate_report_content(content: str, config_path: Optional[str] = None) -> ValidationResult:
    """
    Convenience function to validate report content.

    Args:
        content: Report content to validate
        config_path: Optional path to validation config

    Returns:
        Validation result
    """
    validator = ReportValidator(config_path)
    return validator.validate_report(content)


def validate_report_file(file_path: Union[str, Path], config_path: Optional[str] = None) -> ValidationResult:
    """
    Convenience function to validate a report file.

    Args:
        file_path: Path to report file
        config_path: Optional path to validation config

    Returns:
        Validation result
    """
    validator = ReportValidator(config_path)
    return validator.validate_report_file(file_path)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Test with sample report content
    sample_report = """# Sample Investment Report

## Executive Summary

This is a test report for validation purposes.

## Analysis

Some analysis content here.

## Recommendations

- Buy recommendation with 85% confidence
- Target price: $150.00

## Risk Assessment

Market volatility presents risks.

## Disclaimer

This is not financial advice. Past performance does not guarantee future results.
"""

    result = validate_report_content(sample_report)

    print(f"Validation Result:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Score: {result.score:.1f}/100")
    print(f"  Issues: {len(result.issues)}")

    for issue in result.issues:
        print(f"    {issue.level.value.upper()}: {issue.message}")

    print(f"  Statistics: {result.statistics}")
