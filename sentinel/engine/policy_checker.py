"""
SentinelMCP Risk Engine — Feature 2: Policy Violation (PV)
Evaluates request against config/policy.json rules (roles, classifications, disallowed tools).
"""
import os
import json

class PolicyChecker:
    def __init__(self, policy_path: str = "config/policy.json"):
        self.policy_path = policy_path
        self.policies = self._load_policies()

    def _load_policies(self) -> dict:
        if os.path.exists(self.policy_path):
            try:
                with open(self.policy_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def compute_policy_violation(self, user_role: str, tool_name: str, action: str, classification: str = "PUBLIC") -> float:
        """
        Computes Policy Violation score (0.0 to 1.0).
        0.0 = Fully compliant with organizational policy.
        1.0 = Disallowed action or privilege boundary violation.
        """
        if not self.policies:
            self.policies = self._load_policies()
            
        role_policy = self.policies.get(user_role, self.policies.get("junior_analyst", {}))
        if not role_policy:
            return 0.5

        tool_action_key = f"{tool_name}.{action}"
        allowed = role_policy.get("allowed_tools", [])
        disallowed = role_policy.get("disallowed_tools", [])
        max_class = role_policy.get("max_data_classification", "PUBLIC")

        # Admin override
        if "*" in allowed:
            return 0.0

        # Check explicit disallowed actions
        if tool_action_key in disallowed or tool_name in disallowed or action in disallowed:
            return 1.0

        # Check classification levels
        class_hierarchy = {"PUBLIC": 1, "INTERNAL": 2, "CONFIDENTIAL": 3, "RESTRICTED": 4}
        req_level = class_hierarchy.get(classification.upper(), 1)
        max_level = class_hierarchy.get(max_class.upper(), 1)

        if req_level > max_level:
            return 0.85

        # Check explicit allowed actions
        if allowed and not (tool_action_key in allowed or tool_name in allowed):
            return 0.70

        return 0.0

_checker_instance = PolicyChecker()

def compute_policy_violation(user_role: str, tool_name: str, action: str, classification: str = "PUBLIC") -> float:
    return _checker_instance.compute_policy_violation(user_role, tool_name, action, classification)
