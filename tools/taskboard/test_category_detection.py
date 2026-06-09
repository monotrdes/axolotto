#!/usr/bin/env python3
import sys
import os

# Include current directory in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task_lifecycle import detect_category_from_text, assign_category_if_missing

def test_detect_category_from_text():
    print("Running test_detect_category_from_text...")
    
    # Test cases: (title, description, expected_category)
    cases = [
        ("Implement OAuth login", "Add google and github auth", "security"),
        ("Optimize payment gateway", "Fix credit card transaction fee calculation", "finance"),
        ("Tweak player jump height", "Adjust gameplay variables and physics balance", "gamedesign"),
        ("Deploy solidity smart contracts", "Deploy to goerli testnet using hardhat", "blockchain"),
        ("Set up CI/CD pipeline", "Create github actions workflow with docker build", "infra"),
        ("Fix react modal display bug", "The user profile modal does not render on mobile screens", "frontend"),
        ("Refactor DB query", "Speed up postgresql user model migration", "backend"),
        ("Fix crash on startup", "Application throws null pointer exception on start", "bug"),
        ("Write developer guide", "Create README.md with setup instructions", "docs"),
        ("Just some random task", "No keywords here", None),
    ]
    
    for title, desc, expected in cases:
        detected = detect_category_from_text(title, desc)
        print(f"Text: '{title}' -> Detected: {detected} (Expected: {expected})")
        assert detected == expected, f"Failed for '{title}': got {detected}, expected {expected}"
    
    print("test_detect_category_from_text passed!\n")

def test_assign_category_if_missing():
    print("Running test_assign_category_if_missing...")
    
    # Case 1: Task with empty category, matching security keyword
    t1 = {
        "title": "OAuth security audit",
        "description": "Fix permissions issue",
        "category": "",
        "scope": "axolotto"
    }
    assign_category_if_missing(t1)
    assert t1["category"] == "security", f"Expected 'security', got {t1['category']}"
    
    # Case 2: Task with default 'tools' category, matching finance keyword
    t2 = {
        "title": "Calculate tax fee",
        "description": "Economy ledger",
        "category": "tools",
        "scope": "axolotto"
    }
    assign_category_if_missing(t2)
    assert t2["category"] == "finance", f"Expected 'finance', got {t2['category']}"
    
    # Case 3: Task with already valid category, should not be overwritten
    t3 = {
        "title": "Fix sql injection in auth login",
        "description": "Security issue",
        "category": "backend",
        "scope": "axolotto"
    }
    assign_category_if_missing(t3)
    assert t3["category"] == "backend", f"Expected 'backend' to be preserved, got {t3['category']}"
    
    # Case 4: Task with no keywords, default 'tools' -> keeps 'tools'
    t4 = {
        "title": "Random title",
        "description": "Random desc",
        "category": "tools",
        "scope": "axolotto"
    }
    assign_category_if_missing(t4)
    assert t4["category"] == "tools", f"Expected 'tools', got {t4['category']}"

    # Case 5: Task with no category, no keywords, scope 'axolotto' -> 'backend'
    t5 = {
        "title": "Random title",
        "description": "Random desc",
        "category": "",
        "scope": "axolotto"
    }
    assign_category_if_missing(t5)
    assert t5["category"] == "backend", f"Expected 'backend', got {t5['category']}"

    # Case 6: Task with no category, no keywords, scope 'taskboard' -> 'tools'
    t6 = {
        "title": "Random title",
        "description": "Random desc",
        "category": "",
        "scope": "taskboard"
    }
    assign_category_if_missing(t6)
    assert t6["category"] == "tools", f"Expected 'tools', got {t6['category']}"
    
    print("test_assign_category_if_missing passed!\n")

if __name__ == "__main__":
    try:
        test_detect_category_from_text()
        test_assign_category_if_missing()
        print("All tests passed successfully!")
    except AssertionError as e:
        print(f"Assertion Error: {e}", file=sys.stderr)
        sys.exit(1)
