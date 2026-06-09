#!/usr/bin/env python3
import sys
import os

# Include current directory in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_runner import _git

def test_git_string_command():
    # Test that simple string commands work
    ok, stdout, stderr = _git("git rev-parse --is-inside-work-tree")
    assert ok
    assert stdout == "true"

def test_git_list_command():
    # Test that list commands work
    ok, stdout, stderr = _git(["git", "rev-parse", "--is-inside-work-tree"])
    assert ok
    assert stdout == "true"

def test_git_list_command_with_spaces():
    # Test that list commands handle spaces in arguments without shell splitting.
    ok, stdout, stderr = _git(["git", "commit", "-m", "test commit message with spaces"])
    # Should not have pathspec error
    assert "pathspec" not in stderr
    assert "did not match" not in stderr

if __name__ == "__main__":
    test_git_string_command()
    test_git_list_command()
    test_git_list_command_with_spaces()
    print("All git helper tests passed successfully!")
