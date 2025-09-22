"""
Report History Tracker for Agent Investment Platform

This module provides functionality to track historical investment reports,
predictions, and their accuracy over time for performance evaluation and
continuous improvement.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class PredictionType(Enum):
    """Types of predictions made in reports."""
    STOCK_PRICE = "stock_price"
    MARKET_DIRECTION = "market_direction"
    SECTOR_PERFORMANCE = "sector_performance"
    RECOMMENDATION = "recommendation"
    RISK_LEVEL = "risk_level"


class PredictionStatus(Enum):
    """Status of predictions."""
    PENDING = "pending"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"
    EXPIRED = "expired"


@dataclass
class Prediction:
    """Represents a prediction made in a report."""
    id: str
    report_id: str
    prediction_type: PredictionType
    symbol: Optional[str]
    predicted_value: Union[float, str]
    actual_value: Optional[Union[float, str]]
    confidence: float
    time_horizon: str  # e.g., "1M", "3M", "1Y"
    created_date: datetime
    target_date: datetime
    status: PredictionStatus
    accuracy_score: Optional[float]
    metadata: Dict[str, Any]


@dataclass
class ReportMetrics:
    """Performance metrics for a report."""
    report_id: str
    total_predictions: int
    correct_predictions: int
    incorrect_predictions: int
    pending_predictions: int
    overall_accuracy: float
    confidence_weighted_accuracy: float
    prediction_types: Dict[str, int]
    generated_date: datetime
    last_updated: datetime


class ReportHistoryTracker:
    """
    Tracks and analyzes historical investment reports and predictions.

    Features:
    - Store report metadata and predictions
    - Track prediction accuracy over time
    - Generate performance analytics
    - Compare model/strategy performance
    - Export data for analysis
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the report history tracker.

        Args:
            db_path: Path to SQLite database file
        """
        self.logger = logging.getLogger(__name__)

        # Set database path
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Default to project data directory
            project_root = Path(__file__).parents[2]
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            self.db_path = data_dir / "report_history.db"

        # Initialize database
        self._init_database()

        self.logger.info(f"Report history tracker initialized with database: {self.db_path}")

    def _init_database(self):
        """Initialize SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create reports table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reports (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        report_type TEXT NOT NULL,
                        file_path TEXT,
                        content_hash TEXT,
                        generated_date TIMESTAMP NOT NULL,
                        model_used TEXT,
                        strategy_used TEXT,
                        symbols TEXT,  -- JSON array of symbols
                        metadata TEXT,  -- JSON metadata
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create predictions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id TEXT PRIMARY KEY,
                        report_id TEXT NOT NULL,
                        prediction_type TEXT NOT NULL,
                        symbol TEXT,
                        predicted_value TEXT NOT NULL,
                        actual_value TEXT,
                        confidence REAL NOT NULL,
                        time_horizon TEXT NOT NULL,
                        created_date TIMESTAMP NOT NULL,
                        target_date TIMESTAMP NOT NULL,
                        status TEXT NOT NULL,
                        accuracy_score REAL,
                        metadata TEXT,  -- JSON metadata
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (report_id) REFERENCES reports (id)
                    )
                ''')

                # Create performance metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        period_start TIMESTAMP NOT NULL,
                        period_end TIMESTAMP NOT NULL,
                        total_reports INTEGER NOT NULL,
                        total_predictions INTEGER NOT NULL,
                        correct_predictions INTEGER NOT NULL,
                        overall_accuracy REAL NOT NULL,
                        model_performance TEXT,  -- JSON of model performance
                        strategy_performance TEXT,  -- JSON of strategy performance
                        prediction_type_performance TEXT,  -- JSON of prediction type performance
                        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_date ON reports (generated_date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_report ON predictions (report_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_status ON predictions (status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_target_date ON predictions (target_date)')

                conn.commit()
                self.logger.info("Database initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def add_report(
        self,
        report_id: str,
        title: str,
        report_type: str,
        content: str,
        predictions: List[Dict[str, Any]],
        file_path: Optional[str] = None,
        model_used: Optional[str] = None,
        strategy_used: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a new report to the history tracker.

        Args:
            report_id: Unique identifier for the report
            title: Report title
            report_type: Type of report (e.g., "stock_analysis", "market_summary")
            content: Full report content
            predictions: List of predictions made in the report
            file_path: Path to report file
            model_used: LLM model used for generation
            strategy_used: Investment strategy applied
            symbols: List of symbols analyzed
            metadata: Additional metadata

        Returns:
            Report ID
        """
        try:
            # Generate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # Prepare data
            symbols_json = json.dumps(symbols) if symbols else None
            metadata_json = json.dumps(metadata) if metadata else None
            generated_date = datetime.now()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert report
                cursor.execute('''
                    INSERT OR REPLACE INTO reports
                    (id, title, report_type, file_path, content_hash, generated_date,
                     model_used, strategy_used, symbols, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (report_id, title, report_type, file_path, content_hash,
                      generated_date, model_used, strategy_used, symbols_json, metadata_json))

                # Insert predictions
                for pred_data in predictions:
                    prediction = self._create_prediction_from_dict(pred_data, report_id)
                    self._insert_prediction(cursor, prediction)

                conn.commit()

            self.logger.info(f"Added report to history: {report_id}")
            return report_id

        except Exception as e:
            self.logger.error(f"Failed to add report to history: {e}")
            raise

    def update_prediction_outcome(
        self,
        prediction_id: str,
        actual_value: Union[float, str],
        accuracy_score: Optional[float] = None
    ) -> bool:
        """
        Update a prediction with its actual outcome.

        Args:
            prediction_id: ID of the prediction to update
            actual_value: The actual observed value
            accuracy_score: Calculated accuracy score (0-1)

        Returns:
            True if updated successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get current prediction
                cursor.execute('SELECT * FROM predictions WHERE id = ?', (prediction_id,))
                row = cursor.fetchone()

                if not row:
                    self.logger.warning(f"Prediction not found: {prediction_id}")
                    return False

                # Calculate accuracy if not provided
                if accuracy_score is None:
                    predicted_value = row[4]  # predicted_value column
                    prediction_type = row[2]  # prediction_type column
                    accuracy_score = self._calculate_accuracy(
                        predicted_value, actual_value, prediction_type
                    )

                # Determine status
                status = self._determine_prediction_status(accuracy_score)

                # Update prediction
                cursor.execute('''
                    UPDATE predictions
                    SET actual_value = ?, accuracy_score = ?, status = ?, updated_at = ?
                    WHERE id = ?
                ''', (str(actual_value), accuracy_score, status.value, datetime.now(), prediction_id))

                conn.commit()

            self.logger.info(f"Updated prediction outcome: {prediction_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update prediction outcome: {e}")
            return False

    def get_report_metrics(self, report_id: str) -> Optional[ReportMetrics]:
        """
        Get performance metrics for a specific report.

        Args:
            report_id: ID of the report

        Returns:
            Report metrics or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get report info
                cursor.execute('SELECT generated_date FROM reports WHERE id = ?', (report_id,))
                report_row = cursor.fetchone()

                if not report_row:
                    return None

                # Get prediction statistics
                cursor.execute('''
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'correct' THEN 1 ELSE 0 END) as correct,
                        SUM(CASE WHEN status = 'incorrect' THEN 1 ELSE 0 END) as incorrect,
                        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                        AVG(accuracy_score) as avg_accuracy,
                        AVG(accuracy_score * confidence) as weighted_accuracy,
                        prediction_type
                    FROM predictions
                    WHERE report_id = ?
                    GROUP BY prediction_type
                ''', (report_id,))

                pred_stats = cursor.fetchall()

                if not pred_stats:
                    return ReportMetrics(
                        report_id=report_id,
                        total_predictions=0,
                        correct_predictions=0,
                        incorrect_predictions=0,
                        pending_predictions=0,
                        overall_accuracy=0.0,
                        confidence_weighted_accuracy=0.0,
                        prediction_types={},
                        generated_date=datetime.fromisoformat(report_row[0]),
                        last_updated=datetime.now()
                    )

                # Aggregate statistics
                total_preds = sum(row[0] for row in pred_stats)
                correct_preds = sum(row[1] for row in pred_stats)
                incorrect_preds = sum(row[2] for row in pred_stats)
                pending_preds = sum(row[3] for row in pred_stats)

                overall_accuracy = correct_preds / total_preds if total_preds > 0 else 0.0

                # Weighted accuracy calculation
                weighted_sum = sum(row[5] * row[0] for row in pred_stats if row[5] is not None)
                confidence_weighted_accuracy = weighted_sum / total_preds if total_preds > 0 else 0.0

                prediction_types = {row[6]: row[0] for row in pred_stats}

                return ReportMetrics(
                    report_id=report_id,
                    total_predictions=total_preds,
                    correct_predictions=correct_preds,
                    incorrect_predictions=incorrect_preds,
                    pending_predictions=pending_preds,
                    overall_accuracy=overall_accuracy,
                    confidence_weighted_accuracy=confidence_weighted_accuracy,
                    prediction_types=prediction_types,
                    generated_date=datetime.fromisoformat(report_row[0]),
                    last_updated=datetime.now()
                )

        except Exception as e:
            self.logger.error(f"Failed to get report metrics: {e}")
            return None

    def get_overall_performance(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        model_filter: Optional[str] = None,
        strategy_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get overall performance metrics across all reports.

        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            model_filter: Filter by specific model
            strategy_filter: Filter by specific strategy

        Returns:
            Dictionary with performance metrics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Build query conditions
                conditions = []
                params = []

                if start_date:
                    conditions.append("r.generated_date >= ?")
                    params.append(start_date)

                if end_date:
                    conditions.append("r.generated_date <= ?")
                    params.append(end_date)

                if model_filter:
                    conditions.append("r.model_used = ?")
                    params.append(model_filter)

                if strategy_filter:
                    conditions.append("r.strategy_used = ?")
                    params.append(strategy_filter)

                where_clause = " AND " + " AND ".join(conditions) if conditions else ""

                # Get overall statistics
                query = f'''
                    SELECT
                        COUNT(DISTINCT r.id) as total_reports,
                        COUNT(p.id) as total_predictions,
                        SUM(CASE WHEN p.status = 'correct' THEN 1 ELSE 0 END) as correct_predictions,
                        SUM(CASE WHEN p.status = 'incorrect' THEN 1 ELSE 0 END) as incorrect_predictions,
                        SUM(CASE WHEN p.status = 'pending' THEN 1 ELSE 0 END) as pending_predictions,
                        AVG(p.accuracy_score) as avg_accuracy,
                        MIN(r.generated_date) as earliest_report,
                        MAX(r.generated_date) as latest_report
                    FROM reports r
                    LEFT JOIN predictions p ON r.id = p.report_id
                    WHERE 1=1{where_clause}
                '''

                cursor.execute(query, params)
                overall_stats = cursor.fetchone()

                # Get performance by model
                model_query = f'''
                    SELECT
                        r.model_used,
                        COUNT(DISTINCT r.id) as reports,
                        COUNT(p.id) as predictions,
                        SUM(CASE WHEN p.status = 'correct' THEN 1 ELSE 0 END) as correct,
                        AVG(p.accuracy_score) as accuracy
                    FROM reports r
                    LEFT JOIN predictions p ON r.id = p.report_id
                    WHERE r.model_used IS NOT NULL{where_clause}
                    GROUP BY r.model_used
                '''

                cursor.execute(model_query, params)
                model_performance = cursor.fetchall()

                # Get performance by prediction type
                type_query = f'''
                    SELECT
                        p.prediction_type,
                        COUNT(p.id) as predictions,
                        SUM(CASE WHEN p.status = 'correct' THEN 1 ELSE 0 END) as correct,
                        AVG(p.accuracy_score) as accuracy
                    FROM reports r
                    JOIN predictions p ON r.id = p.report_id
                    WHERE 1=1{where_clause}
                    GROUP BY p.prediction_type
                '''

                cursor.execute(type_query, params)
                type_performance = cursor.fetchall()

                # Format results
                result = {
                    'summary': {
                        'total_reports': overall_stats[0] or 0,
                        'total_predictions': overall_stats[1] or 0,
                        'correct_predictions': overall_stats[2] or 0,
                        'incorrect_predictions': overall_stats[3] or 0,
                        'pending_predictions': overall_stats[4] or 0,
                        'overall_accuracy': overall_stats[5] or 0.0,
                        'earliest_report': overall_stats[6],
                        'latest_report': overall_stats[7]
                    },
                    'model_performance': {
                        row[0]: {
                            'reports': row[1],
                            'predictions': row[2],
                            'correct': row[3],
                            'accuracy': row[4] or 0.0
                        } for row in model_performance if row[0]
                    },
                    'prediction_type_performance': {
                        row[0]: {
                            'predictions': row[1],
                            'correct': row[2],
                            'accuracy': row[3] or 0.0
                        } for row in type_performance
                    }
                }

                return result

        except Exception as e:
            self.logger.error(f"Failed to get overall performance: {e}")
            return {}

    def get_pending_predictions(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Get predictions that are due for evaluation.

        Args:
            days_ahead: Number of days ahead to look for due predictions

        Returns:
            List of pending predictions
        """
        try:
            cutoff_date = datetime.now() + timedelta(days=days_ahead)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT p.*, r.title, r.report_type
                    FROM predictions p
                    JOIN reports r ON p.report_id = r.id
                    WHERE p.status = 'pending' AND p.target_date <= ?
                    ORDER BY p.target_date ASC
                ''', (cutoff_date,))

                rows = cursor.fetchall()

                predictions = []
                for row in rows:
                    predictions.append({
                        'id': row[0],
                        'report_id': row[1],
                        'report_title': row[-2],
                        'report_type': row[-1],
                        'prediction_type': row[2],
                        'symbol': row[3],
                        'predicted_value': row[4],
                        'confidence': row[6],
                        'time_horizon': row[7],
                        'created_date': row[8],
                        'target_date': row[9],
                        'days_until_due': (datetime.fromisoformat(row[9]) - datetime.now()).days
                    })

                return predictions

        except Exception as e:
            self.logger.error(f"Failed to get pending predictions: {e}")
            return []

    def export_data(
        self,
        export_path: Union[str, Path],
        format: str = "csv",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bool:
        """
        Export report history data to file.

        Args:
            export_path: Path for exported file
            format: Export format ("csv", "json", "excel")
            start_date: Start date for export
            end_date: End date for export

        Returns:
            True if export successful
        """
        try:
            if not PANDAS_AVAILABLE and format in ["csv", "excel"]:
                self.logger.error("Pandas is required for CSV/Excel export")
                return False

            with sqlite3.connect(self.db_path) as conn:
                # Build date filter
                date_filter = ""
                params = []

                if start_date or end_date:
                    conditions = []
                    if start_date:
                        conditions.append("r.generated_date >= ?")
                        params.append(start_date)
                    if end_date:
                        conditions.append("r.generated_date <= ?")
                        params.append(end_date)
                    date_filter = " WHERE " + " AND ".join(conditions)

                if format == "json":
                    # Export as JSON
                    cursor = conn.cursor()

                    # Get reports
                    cursor.execute(f"SELECT * FROM reports{date_filter}", params)
                    reports = [dict(zip([col[0] for col in cursor.description], row))
                              for row in cursor.fetchall()]

                    # Get predictions
                    pred_query = f'''
                        SELECT p.* FROM predictions p
                        JOIN reports r ON p.report_id = r.id{date_filter}
                    '''
                    cursor.execute(pred_query, params)
                    predictions = [dict(zip([col[0] for col in cursor.description], row))
                                  for row in cursor.fetchall()]

                    data = {
                        'reports': reports,
                        'predictions': predictions,
                        'exported_at': datetime.now().isoformat(),
                        'date_range': {
                            'start': start_date.isoformat() if start_date else None,
                            'end': end_date.isoformat() if end_date else None
                        }
                    }

                    with open(export_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, default=str)

                elif format in ["csv", "excel"]:
                    # Export using pandas
                    reports_df = pd.read_sql_query(f"SELECT * FROM reports{date_filter}", conn, params=params)

                    pred_query = f'''
                        SELECT p.*, r.title as report_title FROM predictions p
                        JOIN reports r ON p.report_id = r.id{date_filter}
                    '''
                    predictions_df = pd.read_sql_query(pred_query, conn, params=params)

                    if format == "csv":
                        export_path = Path(export_path)
                        reports_df.to_csv(export_path.with_suffix('.reports.csv'), index=False)
                        predictions_df.to_csv(export_path.with_suffix('.predictions.csv'), index=False)

                    elif format == "excel":
                        with pd.ExcelWriter(export_path) as writer:
                            reports_df.to_excel(writer, sheet_name='Reports', index=False)
                            predictions_df.to_excel(writer, sheet_name='Predictions', index=False)

                else:
                    self.logger.error(f"Unsupported export format: {format}")
                    return False

            self.logger.info(f"Data exported successfully to {export_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
            return False

    def _create_prediction_from_dict(self, pred_data: Dict[str, Any], report_id: str) -> Prediction:
        """Create Prediction object from dictionary data."""
        prediction_id = pred_data.get('id') or self._generate_prediction_id(pred_data, report_id)

        # Parse time horizon to get target date
        created_date = pred_data.get('created_date', datetime.now())
        if isinstance(created_date, str):
            created_date = datetime.fromisoformat(created_date)

        time_horizon = pred_data.get('time_horizon', '1M')
        target_date = self._calculate_target_date(created_date, time_horizon)

        return Prediction(
            id=prediction_id,
            report_id=report_id,
            prediction_type=PredictionType(pred_data['prediction_type']),
            symbol=pred_data.get('symbol'),
            predicted_value=pred_data['predicted_value'],
            actual_value=pred_data.get('actual_value'),
            confidence=pred_data.get('confidence', 0.5),
            time_horizon=time_horizon,
            created_date=created_date,
            target_date=target_date,
            status=PredictionStatus(pred_data.get('status', 'pending')),
            accuracy_score=pred_data.get('accuracy_score'),
            metadata=pred_data.get('metadata', {})
        )

    def _insert_prediction(self, cursor, prediction: Prediction):
        """Insert prediction into database."""
        cursor.execute('''
            INSERT OR REPLACE INTO predictions
            (id, report_id, prediction_type, symbol, predicted_value, actual_value,
             confidence, time_horizon, created_date, target_date, status, accuracy_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction.id, prediction.report_id, prediction.prediction_type.value,
            prediction.symbol, str(prediction.predicted_value),
            str(prediction.actual_value) if prediction.actual_value is not None else None,
            prediction.confidence, prediction.time_horizon, prediction.created_date,
            prediction.target_date, prediction.status.value, prediction.accuracy_score,
            json.dumps(prediction.metadata)
        ))

    def _generate_prediction_id(self, pred_data: Dict[str, Any], report_id: str) -> str:
        """Generate unique prediction ID."""
        content = f"{report_id}_{pred_data.get('prediction_type')}_{pred_data.get('symbol', '')}_{pred_data.get('predicted_value')}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _calculate_target_date(self, created_date: datetime, time_horizon: str) -> datetime:
        """Calculate target date from time horizon."""
        horizon_map = {
            '1D': timedelta(days=1),
            '1W': timedelta(weeks=1),
            '2W': timedelta(weeks=2),
            '1M': timedelta(days=30),
            '3M': timedelta(days=90),
            '6M': timedelta(days=180),
            '1Y': timedelta(days=365),
            '2Y': timedelta(days=730)
        }

        delta = horizon_map.get(time_horizon, timedelta(days=30))
        return created_date + delta

    def _calculate_accuracy(self, predicted: str, actual: Union[float, str], pred_type: str) -> float:
        """Calculate accuracy score for a prediction."""
        try:
            if pred_type == PredictionType.STOCK_PRICE.value:
                # For price predictions, calculate percentage error
                pred_val = float(predicted)
                actual_val = float(actual)

                if pred_val == 0:
                    return 0.0

                error_pct = abs(pred_val - actual_val) / pred_val
                # Convert to accuracy score (1.0 = perfect, 0.0 = terrible)
                return max(0.0, 1.0 - error_pct)

            elif pred_type == PredictionType.RECOMMENDATION.value:
                # For recommendations, exact match
                return 1.0 if str(predicted).upper() == str(actual).upper() else 0.0

            else:
                # Default: exact match
                return 1.0 if str(predicted) == str(actual) else 0.0

        except (ValueError, TypeError):
            return 0.0

    def _determine_prediction_status(self, accuracy_score: float) -> PredictionStatus:
        """Determine prediction status from accuracy score."""
        if accuracy_score >= 0.8:
            return PredictionStatus.CORRECT
        elif accuracy_score >= 0.5:
            return PredictionStatus.PARTIALLY_CORRECT
        else:
            return PredictionStatus.INCORRECT


# Convenience functions
def track_report(
    report_id: str,
    title: str,
    report_type: str,
    content: str,
    predictions: List[Dict[str, Any]],
    db_path: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function to track a report.

    Args:
        report_id: Unique report identifier
        title: Report title
        report_type: Type of report
        content: Report content
        predictions: List of predictions
        db_path: Optional database path
        **kwargs: Additional arguments

    Returns:
        Report ID
    """
    tracker = ReportHistoryTracker(db_path)
    return tracker.add_report(report_id, title, report_type, content, predictions, **kwargs)


def get_performance_summary(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to get performance summary.

    Args:
        db_path: Optional database path

    Returns:
        Performance summary
    """
    tracker = ReportHistoryTracker(db_path)
    return tracker.get_overall_performance()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Initialize tracker
    tracker = ReportHistoryTracker()

    # Example report data
    sample_predictions = [
        {
            'prediction_type': 'stock_price',
            'symbol': 'AAPL',
            'predicted_value': 175.50,
            'confidence': 0.85,
            'time_horizon': '3M'
        },
        {
            'prediction_type': 'recommendation',
            'symbol': 'AAPL',
            'predicted_value': 'BUY',
            'confidence': 0.90,
            'time_horizon': '6M'
        }
    ]

    # Add report
    report_id = tracker.add_report(
        report_id="test_report_001",
        title="Test Stock Analysis",
        report_type="stock_analysis",
        content="This is a test report content...",
        predictions=sample_predictions,
        model_used="gpt-4",
        strategy_used="value_growth",
        symbols=["AAPL"]
    )

    print(f"Added report: {report_id}")

    # Get metrics
    metrics = tracker.get_report_metrics(report_id)
    if metrics:
        print(f"Report metrics: {metrics.total_predictions} predictions, {metrics.pending_predictions} pending")

    # Get overall performance
    performance = tracker.get_overall_performance()
    print(f"Overall performance: {performance['summary']['total_reports']} reports, "
          f"{performance['summary']['overall_accuracy']:.2%} accuracy")
