# sentinel.py

import json
import time
from typing import Dict, Any

class SentinelPolicyEngine:
    def __init__(self, policy_file: str):
        self.policy_file = policy_file
        self.policies = self.load_policies()

    def load_policies(self) -> Dict[str, Any]:
        with open(self.policy_file, 'r') as f:
            return json.load(f)

    def evaluate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        for rule in self.policies:
            if self.match_conditions(rule.get("conditions", []), event):
                return {
                    "action": rule.get("action", "log_only"),
                    "policy_id": rule.get("id"),
                    "severity": rule.get("severity", "low")
                }
        return {"action": "allow"}

    def match_conditions(self, conditions: list, event: Dict[str, Any]) -> bool:
        for condition in conditions:
            for key, value in condition.items():
                if event.get(key) != value:
                    return False
        return True

class Sentinel:
    def __init__(self, policy_file: str):
        self.engine = SentinelPolicyEngine(policy_file)

    def intercept(self, agent_name: str, action_type: str, payload: Dict[str, Any]):
        event = {
            "agent": agent_name,
            "action": action_type,
            **payload
        }
        decision = self.engine.evaluate(event)
        self.respond(decision, event)
        if decision["severity"] in ["high", "critical"]:
            self.notify_maven(event, decision)
            self.notify_signal(event, decision)
        return decision["action"]

    def respond(self, decision: Dict[str, Any], event: Dict[str, Any]):
        log_entry = {
            "timestamp": time.time(),
            "event": event,
            "decision": decision
        }
        print("[Sentinel Log]", json.dumps(log_entry, indent=2))
        # Future: Send to Echo or Supabase logging layer

    def notify_maven(self, event: Dict[str, Any], decision: Dict[str, Any]):
        # Simulated notification logic to MAVEN governance agent
        print("[MAVEN ALERT] Policy Violation Escalated:", decision["policy_id"])
        # Replace with actual MAVEN alert function

    def notify_signal(self, event: Dict[str, Any], decision: Dict[str, Any]):
        # Simulated compliance event flagging to Signal agent
        print("[SIGNAL] Compliance Alert Raised:", decision["policy_id"])
        # Replace with actual Signal rule log or alert dispatch

# Example usage
if __name__ == "__main__":
    sentinel = Sentinel("sentinel_policy.json")
    action = sentinel.intercept("Echo", "data_access", {
        "data_class": "PHI",
        "encryption": False
    })
    print("Final action decision:", action)
