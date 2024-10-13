import json

# Sample JSON rule
rule_json = '''{
    "ruleID": "R002",
    "name": "Check User Access",
    "description": "Validates user access level against the User Access Levels table.",
    "priority": "High",
    "status": "Active",
    "conditions": [
        {
            "conditionID": "C002",
            "ruleID": "R002",
            "attribute": "user_access_level",
            "operator": "==",
            "value": "Level 1",
            "logicalOperator": "AND",
            "formulaID": null,
            "tableID": "T001"
        }
    ],
    "actions": [
        {
            "actionID": "A002",
            "ruleID": "R002",
            "actionType": "grant_access",
            "parameters": {},
            "formulaID": "F001"
        }
    ],
    "tags": ["Access Control"],
    "metadata": [
        {
            "key": "complianceStandard",
            "value": "ISO 27001"
        }
    ]
}'''

# Parse JSON
rule = json.loads(rule_json)

# Example data
user_data = {"user_access_level": "Level 1"}
table_data = {"Level 1": "Level 1"}
formulas = {
    "F001": "(user_data['activity_score'] + user_data['engagement_score']) / 2"
}
user_data_with_scores = {"activity_score": 80, "engagement_score": 90}

# Function to evaluate condition
def evaluate_condition(condition, user_data, table_data):
    attribute_value = user_data.get(condition['attribute'])
    operator = condition['operator']
    expected_value = condition['value']
    
    # Simulate table lookup
    if condition['tableID']:
        expected_value = table_data.get(expected_value)
    
    if operator == "==":
        return attribute_value == expected_value
    return False

# Function to evaluate formula
def evaluate_formula(formulaID, user_data):
    formula = formulas.get(formulaID)
    if formula:
        return eval(formula)
    return None

# Function to execute action
def execute_action(action, user_data, user_score=None):
    if action['actionType'] == "grant_access":
        if user_score and user_score > 85:
            print("Access granted")
        else:
            print("Access denied")

# Evaluate conditions
conditions_met = all(evaluate_condition(cond, user_data, table_data) for cond in rule['conditions'])

# If conditions met, execute actions
if conditions_met:
    for action in rule['actions']:
        user_score = evaluate_formula(action['formulaID'], user_data_with_scores)
        execute_action(action, user_data_with_scores, user_score)
