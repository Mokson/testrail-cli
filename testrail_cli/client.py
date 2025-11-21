"""TestRail API client wrapper."""

from typing import Any, Dict, Optional, Literal
from testrail_api import TestRailAPI


class TestRailClient:
    """Wrapper around TestRailAPI with raw passthrough capability."""

    def __init__(
        self,
        url: str,
        email: str,
        password: str,
        timeout: int = 30,
        verify: bool = True,
        proxy: Optional[str] = None,
    ):
        """Initialize TestRail client.

        Args:
            url: TestRail instance URL (e.g., https://org.testrail.io)
            email: User email
            password: Password or API key
            timeout: Request timeout in seconds
            verify: Whether to verify TLS certificates
            proxy: Optional proxy URL
        """
        self.api = TestRailAPI(url, email, password)
        self.api.timeout = timeout

        # Configure session
        if not verify:
            self.api.session.verify = False

        if proxy:
            self.api.session.proxies = {
                "http": proxy,
                "https": proxy,
            }

    def call(
        self,
        endpoint: str,
        method: Literal["GET", "POST", "DELETE"] = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Raw API call passthrough for unmodeled endpoints.

        Args:
            endpoint: API endpoint (e.g., 'get_projects', 'add_case/123')
            method: HTTP method
            params: Query parameters
            data: Request body (for POST)
            files: Files to upload (for POST with multipart/form-data)

        Returns:
            API response (usually dict or list)
        """
        url_path = f"{endpoint}"

        if method == "GET":
            return self.api.send_get(url_path, params or {})
        elif method == "POST":
            if files:
                # Handle file uploads with multipart/form-data
                url = f"{self.api.url}/index.php?/api/v2/{url_path}"
                response = self.api.session.post(url, files=files, timeout=self.api.timeout)
                if response.status_code >= 300:
                    raise Exception(response.status_code, response.reason, url, response.content)
                return response.json() if response.content else None
            else:
                return self.api.send_post(url_path, data or {})
        elif method == "DELETE":
            return self.api.send_post(
                url_path, data or {}
            )  # TestRail uses POST for deletes
        else:
            raise ValueError(f"Unsupported method: {method}")

    # Projects
    def get_projects(self, is_completed: Optional[int] = None) -> list:
        return self.api.projects.get_projects(is_completed=is_completed)

    def get_project(self, project_id: int) -> dict:
        return self.api.projects.get_project(project_id)

    def add_project(self, name: str, **kwargs) -> dict:
        return self.api.projects.add_project(name, **kwargs)

    def update_project(self, project_id: int, **kwargs) -> dict:
        return self.api.projects.update_project(project_id, **kwargs)

    def delete_project(self, project_id: int):
        return self.api.projects.delete_project(project_id)

    # Suites
    def get_suites(self, project_id: int) -> list:
        return self.api.suites.get_suites(project_id)

    def get_suite(self, suite_id: int) -> dict:
        return self.api.suites.get_suite(suite_id)

    def add_suite(self, project_id: int, name: str, **kwargs) -> dict:
        return self.api.suites.add_suite(project_id, name, **kwargs)

    def update_suite(self, suite_id: int, **kwargs) -> dict:
        return self.api.suites.update_suite(suite_id, **kwargs)

    def delete_suite(self, suite_id: int):
        return self.api.suites.delete_suite(suite_id)

    # Sections
    def get_sections(self, project_id: int, suite_id: Optional[int] = None) -> list:
        return self.api.sections.get_sections(project_id, suite_id=suite_id)

    def get_section(self, section_id: int) -> dict:
        return self.api.sections.get_section(section_id)

    def add_section(self, project_id: int, name: str, **kwargs) -> dict:
        return self.api.sections.add_section(project_id, name, **kwargs)

    def update_section(self, section_id: int, **kwargs) -> dict:
        return self.api.sections.update_section(section_id, **kwargs)

    def delete_section(self, section_id: int):
        return self.api.sections.delete_section(section_id)

    # Cases
    def get_cases(self, project_id: int, **kwargs) -> list:
        return self.api.cases.get_cases(project_id, **kwargs)

    def get_case(self, case_id: int) -> dict:
        return self.api.cases.get_case(case_id)

    def add_case(self, section_id: int, title: str, **kwargs) -> dict:
        return self.api.cases.add_case(section_id, title, **kwargs)

    def update_case(self, case_id: int, **kwargs) -> dict:
        return self.api.cases.update_case(case_id, **kwargs)

    def update_cases(self, suite_id: int, case_ids: list, **kwargs) -> list:
        return self.api.cases.update_cases(suite_id, case_ids, **kwargs)

    def delete_case(self, case_id: int, soft: Optional[int] = None):
        return self.api.cases.delete_case(case_id, soft=soft)

    def delete_cases(self, suite_id: int, case_ids: list, soft: Optional[int] = None):
        return self.api.cases.delete_cases(suite_id, case_ids, soft=soft)

    # Runs
    def get_runs(self, project_id: int, **kwargs) -> list:
        return self.api.runs.get_runs(project_id, **kwargs)

    def get_run(self, run_id: int) -> dict:
        return self.api.runs.get_run(run_id)

    def add_run(self, project_id: int, **kwargs) -> dict:
        return self.api.runs.add_run(project_id, **kwargs)

    def update_run(self, run_id: int, **kwargs) -> dict:
        return self.api.runs.update_run(run_id, **kwargs)

    def close_run(self, run_id: int) -> dict:
        return self.api.runs.close_run(run_id)

    def delete_run(self, run_id: int):
        return self.api.runs.delete_run(run_id)

    # Plans
    def get_plans(self, project_id: int, **kwargs) -> list:
        return self.api.plans.get_plans(project_id, **kwargs)

    def get_plan(self, plan_id: int) -> dict:
        return self.api.plans.get_plan(plan_id)

    def add_plan(self, project_id: int, name: str, **kwargs) -> dict:
        return self.api.plans.add_plan(project_id, name, **kwargs)

    def add_plan_entry(self, plan_id: int, suite_id: int, **kwargs) -> dict:
        return self.api.plans.add_plan_entry(plan_id, suite_id, **kwargs)

    def update_plan(self, plan_id: int, **kwargs) -> dict:
        return self.api.plans.update_plan(plan_id, **kwargs)

    def update_plan_entry(self, plan_id: int, entry_id: str, **kwargs) -> dict:
        return self.api.plans.update_plan_entry(plan_id, entry_id, **kwargs)

    def close_plan(self, plan_id: int) -> dict:
        return self.api.plans.close_plan(plan_id)

    def delete_plan(self, plan_id: int):
        return self.api.plans.delete_plan(plan_id)

    def delete_plan_entry(self, plan_id: int, entry_id: str):
        return self.api.plans.delete_plan_entry(plan_id, entry_id)

    # Tests
    def get_tests(self, run_id: int, **kwargs) -> list:
        return self.api.tests.get_tests(run_id, **kwargs)

    def get_test(self, test_id: int) -> dict:
        return self.api.tests.get_test(test_id)

    # Results
    def get_results(self, test_id: int, **kwargs) -> list:
        return self.api.results.get_results(test_id, **kwargs)

    def get_results_for_case(self, run_id: int, case_id: int, **kwargs) -> list:
        return self.api.results.get_results_for_case(run_id, case_id, **kwargs)

    def get_results_for_run(self, run_id: int, **kwargs) -> list:
        return self.api.results.get_results_for_run(run_id, **kwargs)

    def add_result(self, test_id: int, **kwargs) -> dict:
        return self.api.results.add_result(test_id, **kwargs)

    def add_result_for_case(self, run_id: int, case_id: int, **kwargs) -> dict:
        return self.api.results.add_result_for_case(run_id, case_id, **kwargs)

    def add_results(self, run_id: int, results: list) -> list:
        return self.api.results.add_results(run_id, results)

    def add_results_for_cases(self, run_id: int, results: list) -> list:
        return self.api.results.add_results_for_cases(run_id, results)

    # Milestones
    def get_milestones(self, project_id: int, **kwargs) -> list:
        return self.api.milestones.get_milestones(project_id, **kwargs)

    def get_milestone(self, milestone_id: int) -> dict:
        return self.api.milestones.get_milestone(milestone_id)

    def add_milestone(self, project_id: int, name: str, **kwargs) -> dict:
        return self.api.milestones.add_milestone(project_id, name, **kwargs)

    def update_milestone(self, milestone_id: int, **kwargs) -> dict:
        return self.api.milestones.update_milestone(milestone_id, **kwargs)

    def delete_milestone(self, milestone_id: int):
        return self.api.milestones.delete_milestone(milestone_id)

    # Users
    def get_users(self) -> list:
        return self.api.users.get_users()

    def get_user(self, user_id: int) -> dict:
        return self.api.users.get_user(user_id)

    def get_user_by_email(self, email: str) -> dict:
        return self.api.users.get_user_by_email(email)
