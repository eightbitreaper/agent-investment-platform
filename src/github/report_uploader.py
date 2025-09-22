"""
GitHub Report Uploader for Agent Investment Platform

This module provides functionality to upload generated investment reports
to GitHub repositories for version control, collaboration, and tracking.
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import base64

try:
    import requests
except ImportError:
    raise ImportError("requests is required for GitHub integration. Install with: pip install requests")

try:
    from github import Github, Repository, ContentFile
    from github.GithubException import GithubException
except ImportError:
    raise ImportError("PyGithub is required for GitHub integration. Install with: pip install PyGithub")


class GitHubReportUploader:
    """
    Handles uploading investment reports to GitHub repositories.

    Features:
    - Upload markdown reports
    - Create organized directory structures
    - Track report history and versions
    - Support for both public and private repositories
    - Commit message customization
    """

    def __init__(
        self,
        github_token: Optional[str] = None,
        repository_name: Optional[str] = None,
        base_path: str = "reports"
    ):
        """
        Initialize the GitHub uploader.

        Args:
            github_token: GitHub personal access token
            repository_name: Repository name in format "owner/repo"
            base_path: Base directory path for reports in the repository
        """
        self.logger = logging.getLogger(__name__)

        # Get GitHub token from environment or parameter
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass as parameter.")

        # Get repository name from environment or parameter
        self.repository_name = repository_name or os.getenv('GITHUB_REPOSITORY')
        if not self.repository_name:
            raise ValueError("Repository name is required. Set GITHUB_REPOSITORY environment variable or pass as parameter.")

        self.base_path = base_path.strip('/')

        # Initialize GitHub client
        try:
            self.github = Github(self.github_token)
            self.repository = self.github.get_repo(self.repository_name)
            self.logger.info(f"Connected to GitHub repository: {self.repository_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize GitHub client: {e}")
            raise

    def upload_report(
        self,
        report_path: Union[str, Path],
        remote_path: Optional[str] = None,
        commit_message: Optional[str] = None,
        branch: str = "main",
        create_pr: bool = False
    ) -> Dict[str, Any]:
        """
        Upload a report file to the GitHub repository.

        Args:
            report_path: Local path to the report file
            remote_path: Remote path in the repository (auto-generated if None)
            commit_message: Custom commit message
            branch: Target branch for the upload
            create_pr: Whether to create a pull request instead of direct commit

        Returns:
            Dictionary with upload results and metadata
        """
        try:
            report_path = Path(report_path)

            if not report_path.exists():
                raise FileNotFoundError(f"Report file not found: {report_path}")

            # Read report content
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Generate remote path if not provided
            if not remote_path:
                timestamp = datetime.now().strftime("%Y/%m")
                filename = report_path.name
                remote_path = f"{self.base_path}/{timestamp}/{filename}"

            # Generate commit message if not provided
            if not commit_message:
                report_type = self._extract_report_type(content)
                commit_message = f"Add {report_type} report: {report_path.name}"

            # Upload file
            result = self._upload_file_content(
                content=content,
                remote_path=remote_path,
                commit_message=commit_message,
                branch=branch
            )

            # Create pull request if requested
            if create_pr and branch != "main":
                pr_result = self._create_pull_request(
                    branch=branch,
                    title=f"Investment Report: {report_path.name}",
                    body=f"Automated upload of investment analysis report.\n\nFile: {remote_path}"
                )
                result['pull_request'] = pr_result

            self.logger.info(f"Successfully uploaded report: {remote_path}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to upload report: {e}")
            raise

    def upload_multiple_reports(
        self,
        report_paths: List[Union[str, Path]],
        branch: str = "main",
        batch_commit: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple reports in a batch operation.

        Args:
            report_paths: List of local report file paths
            branch: Target branch for uploads
            batch_commit: Whether to commit all files in a single commit

        Returns:
            List of upload results for each file
        """
        results = []

        if batch_commit and len(report_paths) > 1:
            # Batch upload with single commit
            try:
                files_data = []
                for report_path in report_paths:
                    report_path = Path(report_path)
                    if report_path.exists():
                        with open(report_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        timestamp = datetime.now().strftime("%Y/%m")
                        remote_path = f"{self.base_path}/{timestamp}/{report_path.name}"

                        files_data.append({
                            'path': remote_path,
                            'content': content,
                            'local_path': str(report_path)
                        })

                if files_data:
                    result = self._batch_upload_files(files_data, branch)
                    results.append(result)

            except Exception as e:
                self.logger.error(f"Batch upload failed: {e}")
                # Fall back to individual uploads
                batch_commit = False

        if not batch_commit:
            # Individual uploads
            for report_path in report_paths:
                try:
                    result = self.upload_report(report_path, branch=branch)
                    results.append(result)
                except Exception as e:
                    self.logger.warning(f"Failed to upload {report_path}: {e}")
                    results.append({'error': str(e), 'path': str(report_path)})

        return results

    def create_report_index(
        self,
        reports_metadata: List[Dict[str, Any]],
        index_path: Optional[str] = None
    ) -> str:
        """
        Create an index file listing all uploaded reports.

        Args:
            reports_metadata: List of report metadata dictionaries
            index_path: Path for the index file

        Returns:
            Path to the created index file
        """
        if not index_path:
            index_path = f"{self.base_path}/README.md"

        # Generate index content
        index_content = self._generate_index_content(reports_metadata)

        # Upload index file
        try:
            result = self._upload_file_content(
                content=index_content,
                remote_path=index_path,
                commit_message="Update reports index",
                branch="main"
            )

            return result['download_url']

        except Exception as e:
            self.logger.error(f"Failed to create report index: {e}")
            raise

    def get_report_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get history of uploaded reports from the repository.

        Args:
            limit: Maximum number of reports to retrieve

        Returns:
            List of report metadata from repository
        """
        try:
            reports = []
            contents = self.repository.get_contents(self.base_path)

            def traverse_directory(contents_list):
                for content in contents_list:
                    if content.type == "dir":
                        # Recursively traverse subdirectories
                        subcontents = self.repository.get_contents(content.path)
                        traverse_directory(subcontents)
                    elif content.name.endswith('.md'):
                        # This is a report file
                        report_info = {
                            'name': content.name,
                            'path': content.path,
                            'size': content.size,
                            'download_url': content.download_url,
                            'html_url': content.html_url,
                            'last_modified': content.last_modified
                        }
                        reports.append(report_info)

                        if len(reports) >= limit:
                            return

            if isinstance(contents, list):
                traverse_directory(contents)

            # Sort by last modified date (newest first)
            reports.sort(key=lambda x: x.get('last_modified', ''), reverse=True)

            return reports[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get report history: {e}")
            return []

    def delete_old_reports(
        self,
        days_old: int = 90,
        dry_run: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Delete reports older than specified days.

        Args:
            days_old: Age threshold in days
            dry_run: If True, only return what would be deleted

        Returns:
            List of deleted (or would-be-deleted) reports
        """
        try:
            from datetime import timedelta

            cutoff_date = datetime.now() - timedelta(days=days_old)
            reports = self.get_report_history(limit=1000)  # Get more for cleanup

            old_reports = []
            for report in reports:
                if report.get('last_modified'):
                    try:
                        # Parse the last modified date
                        modified_date = datetime.fromisoformat(
                            report['last_modified'].replace('Z', '+00:00')
                        )

                        if modified_date < cutoff_date:
                            old_reports.append(report)
                    except ValueError:
                        continue

            if not dry_run:
                # Actually delete the files
                deleted_reports = []
                for report in old_reports:
                    try:
                        file_content = self.repository.get_contents(report['path'])
                        self.repository.delete_file(
                            path=report['path'],
                            message=f"Cleanup: Delete old report {report['name']}",
                            sha=file_content.sha
                        )
                        deleted_reports.append(report)
                        self.logger.info(f"Deleted old report: {report['path']}")
                    except Exception as e:
                        self.logger.warning(f"Failed to delete {report['path']}: {e}")

                return deleted_reports
            else:
                self.logger.info(f"Dry run: Would delete {len(old_reports)} old reports")
                return old_reports

        except Exception as e:
            self.logger.error(f"Failed to delete old reports: {e}")
            return []

    def _upload_file_content(
        self,
        content: str,
        remote_path: str,
        commit_message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Upload file content to repository."""
        try:
            # Check if file already exists
            try:
                existing_file = self.repository.get_contents(remote_path, ref=branch)
                # File exists, update it
                result = self.repository.update_file(
                    path=remote_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch
                )
                operation = 'updated'
            except:
                # File doesn't exist, create it
                result = self.repository.create_file(
                    path=remote_path,
                    message=commit_message,
                    content=content,
                    branch=branch
                )
                operation = 'created'

            return {
                'operation': operation,
                'path': remote_path,
                'commit_sha': result['commit'].sha,
                'download_url': result['content'].download_url,
                'html_url': result['content'].html_url,
                'size': result['content'].size
            }

        except Exception as e:
            self.logger.error(f"Failed to upload file content: {e}")
            raise

    def _batch_upload_files(
        self,
        files_data: List[Dict[str, str]],
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Upload multiple files in a single commit."""
        try:
            # Get the latest commit SHA
            ref = self.repository.get_git_ref(f"heads/{branch}")
            latest_commit_sha = ref.object.sha

            # Get the tree of the latest commit
            base_tree = self.repository.get_git_tree(latest_commit_sha)

            # Create tree elements for new files
            tree_elements = []
            for file_data in files_data:
                tree_elements.append({
                    'path': file_data['path'],
                    'mode': '100644',
                    'type': 'blob',
                    'content': file_data['content']
                })

            # Create new tree
            new_tree = self.repository.create_git_tree(tree_elements, base_tree)

            # Create commit message
            commit_message = f"Batch upload: {len(files_data)} investment reports"

            # Create new commit
            new_commit = self.repository.create_git_commit(
                message=commit_message,
                tree=new_tree,
                parents=[self.repository.get_git_commit(latest_commit_sha)]
            )

            # Update branch reference
            ref.edit(new_commit.sha)

            return {
                'operation': 'batch_created',
                'files_count': len(files_data),
                'commit_sha': new_commit.sha,
                'paths': [f['path'] for f in files_data]
            }

        except Exception as e:
            self.logger.error(f"Batch upload failed: {e}")
            raise

    def _create_pull_request(
        self,
        branch: str,
        title: str,
        body: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """Create a pull request."""
        try:
            pr = self.repository.create_pull(
                title=title,
                body=body,
                head=branch,
                base=base
            )

            return {
                'number': pr.number,
                'title': pr.title,
                'html_url': pr.html_url,
                'state': pr.state
            }

        except Exception as e:
            self.logger.error(f"Failed to create pull request: {e}")
            raise

    def _extract_report_type(self, content: str) -> str:
        """Extract report type from content."""
        lines = content.split('\n')

        # Look for report type in the first few lines
        for line in lines[:10]:
            if 'Report Type:' in line:
                return line.split('Report Type:')[1].strip().replace('*', '')
            elif line.startswith('#'):
                # Use the main title
                return line.replace('#', '').strip()

        return 'Investment Report'

    def _generate_index_content(self, reports_metadata: List[Dict[str, Any]]) -> str:
        """Generate content for the reports index file."""
        content = ["# Investment Reports Index", ""]
        content.append("This directory contains automated investment analysis reports generated by the Agent Investment Platform.")
        content.append("")
        content.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"**Total Reports:** {len(reports_metadata)}")
        content.append("")

        if reports_metadata:
            content.append("## Recent Reports")
            content.append("")
            content.append("| Date | Report | Type | Size |")
            content.append("|------|--------|------|------|")

            # Sort by date (newest first)
            sorted_reports = sorted(
                reports_metadata,
                key=lambda x: x.get('last_modified', ''),
                reverse=True
            )

            for report in sorted_reports[:20]:  # Show last 20 reports
                date = report.get('last_modified', 'Unknown')[:10]  # YYYY-MM-DD
                name = report.get('name', 'Unknown')
                report_type = self._extract_report_type_from_name(name)
                size = self._format_file_size(report.get('size', 0))
                url = report.get('html_url', '#')

                content.append(f"| {date} | [{name}]({url}) | {report_type} | {size} |")

        content.append("")
        content.append("## Report Types")
        content.append("")
        content.append("- **Stock Analysis**: Individual stock evaluation and recommendations")
        content.append("- **Portfolio Analysis**: Portfolio performance and allocation reviews")
        content.append("- **Market Summary**: Daily market overview and sentiment analysis")
        content.append("- **Comprehensive**: Multi-asset analysis with risk management")
        content.append("")
        content.append("---")
        content.append("*Generated by Agent Investment Platform*")

        return '\n'.join(content)

    def _extract_report_type_from_name(self, filename: str) -> str:
        """Extract report type from filename."""
        filename_lower = filename.lower()

        if 'stock' in filename_lower:
            return 'Stock Analysis'
        elif 'portfolio' in filename_lower:
            return 'Portfolio Analysis'
        elif 'market' in filename_lower:
            return 'Market Summary'
        elif 'comprehensive' in filename_lower:
            return 'Comprehensive'
        else:
            return 'Analysis'

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024**2):.1f} MB"


# Convenience functions
def upload_report_to_github(
    report_path: Union[str, Path],
    github_token: Optional[str] = None,
    repository_name: Optional[str] = None,
    remote_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to upload a single report to GitHub.

    Args:
        report_path: Local path to the report file
        github_token: GitHub personal access token
        repository_name: Repository name in format "owner/repo"
        remote_path: Remote path in the repository

    Returns:
        Upload result dictionary
    """
    uploader = GitHubReportUploader(github_token, repository_name)
    return uploader.upload_report(report_path, remote_path)


def batch_upload_reports_to_github(
    report_paths: List[Union[str, Path]],
    github_token: Optional[str] = None,
    repository_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to upload multiple reports to GitHub.

    Args:
        report_paths: List of local report file paths
        github_token: GitHub personal access token
        repository_name: Repository name in format "owner/repo"

    Returns:
        List of upload results
    """
    uploader = GitHubReportUploader(github_token, repository_name)
    return uploader.upload_multiple_reports(report_paths)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    try:
        # Initialize uploader
        uploader = GitHubReportUploader()

        # Example: Get report history
        reports = uploader.get_report_history(limit=10)
        print(f"Found {len(reports)} recent reports")

        for report in reports:
            print(f"  - {report['name']} ({report['size']} bytes)")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set GITHUB_TOKEN and GITHUB_REPOSITORY environment variables")
