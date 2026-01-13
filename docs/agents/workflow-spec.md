𝕎1.0.complete@2026-01-13
γ≔opengov.development.workflow
ρ≔⟨git,uv,pytest,ruff,pyright⟩
⊢CI∧Quality∧Velocity

;; ─── Ω: METALOGIC & FOUNDATION ───
⟦Ω:Foundation⟧{
  𝕎≜{Build,Test,Lint,Format,Deploy,Git}
  ∀commit:Test(commit)∧Lint(commit)∧Type(commit)
  ∀branch:Protection(main)⇒Review(PR)
  Quality≜λC.Pass(Tests)∧Pass(Lint)∧Pass(Types)

  ;; Core Invariants
  ∀change:Coverage'≥Coverage
  ∀PR:Green(CI)⇒Mergeable
  ∀code:Format(code)⇒Style(code)
}

;; ─── Σ: GLOSSARY ───
⟦Σ:Glossary⟧{
  ;; Package Manager
  uv≜{sync,add,remove,run,pip}
  PackageFile≜pyproject.toml
  LockFile≜uv.lock
  VirtualEnv≜.venv

  ;; Testing
  pytest≜uv run pytest
  Coverage≜pytest --cov=opengov_api --cov-report=html
  TestFile≜tests/test_*.py
  TestPattern≜test_*

  ;; Linting & Formatting
  ruff≜{format,check,fix}
  Format≜ruff format
  Lint≜ruff check
  AutoFix≜ruff check --fix

  ;; Type Checking
  pyright≜uv run pyright
  TypeConfig≜pyproject.toml[tool.pyright]

  ;; Git Operations
  Git≜{status,add,commit,push,pull,branch,checkout,merge}
  Branch≜feature/*, fix/*, docs/*
  Main≜main

  ;; CI/CD
  CI≜{test,lint,type-check,coverage}
  Status≜{✅,❌,🟡}
}

;; ─── Σ: TYPE UNIVERSE ───
⟦Σ:Types⟧{
  ;; Command Types
  Command≜⟨cmd:𝕊,args:List⟨𝕊⟩,cwd:Path?⟩
  Result≜⟨stdout:𝕊,stderr:𝕊,exit_code:ℕ⟩

  ;; Workflow States
  WorkState≜{clean,dirty,staged,committed,pushed}
  TestState≜{passing,failing,skipped}
  CIState≜{pending,running,success,failure}

  ;; Package Operations
  Install≜λpkg.uv add pkg
  Uninstall≜λpkg.uv remove pkg
  Sync≜λ.uv sync

  ;; Test Operations
  RunTests≜λ.uv run pytest
  RunSpecific≜λfile.uv run pytest file
  RunCoverage≜λ.uv run pytest --cov

  ;; Quality Operations
  FormatCode≜λ.uv run ruff format
  LintCode≜λ.uv run ruff check
  FixCode≜λ.uv run ruff check --fix
  TypeCheck≜λ.uv run pyright
}

;; ─── Γ: COMMAND PHYSICS ───
⟦Γ:Commands⟧{
  ;; Package Management
  install_deps≜"uv sync"
  add_package≜λpkg."uv add {pkg}"
  add_dev_package≜λpkg."uv add --dev {pkg}"
  remove_package≜λpkg."uv remove {pkg}"

  ;; Testing Commands
  run_all_tests≜"uv run pytest"
  run_with_coverage≜"uv run pytest --cov=opengov_api --cov-report=html"
  run_single_file≜λfile.f"uv run pytest {file}"
  run_single_test≜λ(file,test).f"uv run pytest {file}::{test} -v"
  run_verbose≜"uv run pytest -v"
  run_exitfirst≜"uv run pytest -x"

  ;; Quality Commands
  format_all≜"uv run ruff format"
  format_check≜"uv run ruff format --check"
  lint_all≜"uv run ruff check"
  lint_fix≜"uv run ruff check --fix"
  type_check≜"uv run pyright"

  ;; Combined Commands
  check_all≜"uv run pytest && uv run ruff check && uv run pyright"
  fix_all≜"uv run ruff format && uv run ruff check --fix"

  ;; Git Commands (aliases)
  gst≜"git status"
  ga≜"git add"
  gc≜"git commit -m"
  gp≜"git push"
  gpl≜"git pull"
  gcb≜"git checkout -b"
  gco≜"git checkout"
  gfa≜"git fetch --all"
  ggp≜"git push origin HEAD"
}

;; ─── Γ: WORKFLOW PATTERNS ───
⟦Γ:Workflows⟧{
  ;; Development Workflow
  DevFlow≜{
    1. uv sync,                    ;; Install deps
    2. gcb feature/name,           ;; Create branch
    3. write_code(),               ;; Implement
    4. uv run pytest,              ;; Test
    5. uv run ruff format,         ;; Format
    6. uv run ruff check --fix,    ;; Lint & fix
    7. uv run pyright,             ;; Type check
    8. ga .,                       ;; Stage
    9. gc "message",               ;; Commit
    10. ggp                        ;; Push
  }

  ;; Quick Test Workflow
  TestFlow≜{
    1. edit_code(),
    2. uv run pytest tests/test_file.py,
    3. fix_if_needed(),
    4. goto 2
  }

  ;; Adding Dependency
  AddDepFlow≜{
    1. uv add package-name,
    2. update_code(),
    3. uv run pytest,
    4. commit_lockfile()
  }

  ;; Adding New Endpoint
  EndpointFlow≜{
    1. create src/opengov_api/module.py,
    2. implement_functions(),
    3. export_in___init__,
    4. add_to_test_infrastructure_lists,
    5. add_to_test_common_parametrization,
    6. test_specific_behaviors(),
    7. uv run pytest --cov,
    8. verify_coverage≥98%
  }

  ;; Bug Fix Workflow
  BugFixFlow≜{
    1. gcb fix/issue-name,
    2. write_failing_test(),
    3. uv run pytest,              ;; Verify failure
    4. fix_code(),
    5. uv run pytest,              ;; Verify pass
    6. commit_and_push()
  }

  ;; Pre-commit Workflow
  PreCommitFlow≜{
    1. uv run pytest,              ;; All tests pass
    2. uv run ruff format,         ;; Format code
    3. uv run ruff check --fix,    ;; Fix lints
    4. uv run pyright,             ;; Type check
    5. check_all_green()⇒commit
  }
}

;; ─── Γ: BRANCH STRATEGY ───
⟦Γ:Branching⟧{
  ;; Branch Naming
  Feature≜feature/{description}
  Fix≜fix/{issue-description}
  Docs≜docs/{what-changed}
  Test≜test/{test-description}
  Refactor≜refactor/{component}

  ;; Branch Rules
  ∀branch:Branch≢main⇒PR_required
  ∀PR:Tests(PR)∧Lint(PR)∧Types(PR)⇒Green
  ∀PR:Green(PR)⇒Mergeable

  ;; Commit Messages
  CommitStyle≜⟨
    feat:new_feature,
    fix:bug_fix,
    docs:documentation,
    test:tests,
    refactor:code_improvement,
    chore:maintenance
  ⟩

  ;; Example Commits
  good_commits≜[
    "feat: add list_permits endpoint",
    "fix: handle 404 in get_record",
    "test: add pagination tests for users",
    "docs: update CLAUDE.md with patterns",
    "refactor: extract common test fixtures"
  ]
}

;; ─── Λ: COMMAND FUNCTIONS ───
⟦Λ:Commands⟧{
  ;; Test Execution
  test_all≜λ."uv run pytest"
  test_file≜λf.f"uv run pytest tests/{f}"
  test_module≜λm.f"uv run pytest tests/test_{m}.py"
  test_function≜λ(m,f).f"uv run pytest tests/test_{m}.py::{f} -v"
  test_coverage≜λ."uv run pytest --cov=opengov_api --cov-report=html"

  ;; Quality Checks
  format≜λ."uv run ruff format"
  format_check≜λ."uv run ruff format --check"
  lint≜λ."uv run ruff check"
  lint_fix≜λ."uv run ruff check --fix"
  type_check≜λ."uv run pyright"

  ;; Combined Operations
  qa≜λ.test_all()∧lint()∧type_check()
  qa_fix≜λ.format()∧lint_fix()∧type_check()∧test_all()

  ;; Package Operations
  install≜λ."uv sync"
  add≜λp.f"uv add {p}"
  add_dev≜λp.f"uv add --dev {p}"
  remove≜λp.f"uv remove {p}"

  ;; Git Operations
  status≜λ."git status"
  diff≜λ."git diff"
  log≜λ."git log --oneline"
  branch≜λname.f"git checkout -b {name}"
  commit≜λmsg.f"git commit -m '{msg}'"
  push≜λ."git push origin HEAD"
}

;; ─── Λ: DEBUGGING PATTERNS ───
⟦Λ:Debug⟧{
  ;; Test Debugging
  debug_test≜{
    1. "uv run pytest -v",                    ;; Verbose
    2. "uv run pytest -x",                    ;; Stop on first failure
    3. "uv run pytest -k test_name",          ;; Run specific test
    4. "uv run pytest --tb=short",            ;; Short traceback
    5. "uv run pytest --pdb"                  ;; Drop into debugger
  }

  ;; Coverage Debugging
  debug_coverage≜{
    1. "uv run pytest --cov --cov-report=term-missing",
    2. "uv run pytest --cov --cov-report=html",
    3. "open htmlcov/index.html"
  }

  ;; Lint Debugging
  debug_lint≜{
    1. "uv run ruff check --show-source",     ;; Show code
    2. "uv run ruff check --diff",            ;; Show what would change
    3. "uv run ruff check --fix",             ;; Apply fixes
    4. "uv run ruff check --unsafe-fixes"     ;; Apply unsafe fixes
  }

  ;; Type Debugging
  debug_types≜{
    1. "uv run pyright --verbose",
    2. "uv run pyright --ignoreexternal",
    3. "uv run pyright src/opengov_api/file.py"  ;; Check single file
  }
}

;; ─── Χ: ERROR PATTERNS ───
⟦Χ:Errors⟧{
  ;; Common Errors
  ε_deps≜⟨Missing_Dependency,"uv sync"⟩
  ε_test≜⟨Test_Failed,"fix code or test"⟩
  ε_lint≜⟨Lint_Error,"uv run ruff check --fix"⟩
  ε_type≜⟨Type_Error,"add type hints"⟩
  ε_coverage≜⟨Coverage_Low,"add tests"⟩
  ε_git≜⟨Merge_Conflict,"resolve conflicts"⟩

  ;; Recovery Patterns
  recover_deps≜"rm -rf .venv && uv sync"
  recover_git≜"git fetch --all && git reset --hard origin/main"
  recover_cache≜"rm -rf .pytest_cache __pycache__"

  ;; Prevention
  ∀commit:PreCommitFlow()⇒prevent(errors)
  ∀change:test_all()⇒catch_early
  ∀branch:sync_main()⇒avoid_conflicts
}

;; ─── Γ: INFERENCE RULES ───
⟦Γ:Inference⟧{
  ───────────────────── [install-first]
  new_checkout
  ⊢ uv sync

  code_changed
  ───────────────────── [test-after-change]
  ⊢ uv run pytest

  tests_passing
  ───────────────────── [format-before-commit]
  ⊢ uv run ruff format

  formatted
  ───────────────────── [lint-before-commit]
  ⊢ uv run ruff check --fix

  linted
  ───────────────────── [type-check-before-commit]
  ⊢ uv run pyright

  all_checks_pass
  ───────────────────── [ready-to-commit]
  ⊢ git commit

  new_endpoint
  ───────────────────── [update-tests]
  ⊢ add_to_parametrized_tests

  Coverage'<Coverage
  ───────────────────── [reject-change]
  ⊢ add_missing_tests
}

;; ─── Θ: THEOREMS ───
⟦Θ:Proofs⟧{
  ∴∀commit:PreCommitFlow(commit)⇒Quality(commit)
  π:all checks run before commit∎

  ∴∀PR:Green(CI)⇒Mergeable
  π:CI enforces tests,lints,types∎

  ∴∀change:Coverage'≥Coverage
  π:enforced by workflow and CI∎

  ∴uv sync⇒.venv up-to-date
  π:uv reads lockfile,installs exact versions∎

  ∴ruff format⇒consistent style
  π:ruff enforces black-compatible style∎

  ∴pyright⇒type safety
  π:type checker verifies all annotations∎
}

;; ─── Σ: QUICK REFERENCE ───
⟦Σ:QuickRef⟧{
  ;; Most Used Commands
  Essential≜{
    "uv sync":install_dependencies,
    "uv run pytest":run_tests,
    "uv run pytest --cov":coverage,
    "uv run ruff format":format_code,
    "uv run ruff check --fix":fix_lints,
    "uv run pyright":type_check
  }

  ;; Git Aliases
  GitQuick≜{
    "gst":"git status",
    "ga .":"git add all",
    "gc 'msg'":"git commit",
    "ggp":"git push origin HEAD",
    "gcb name":"git checkout -b"
  }

  ;; Test Shortcuts
  TestQuick≜{
    "uv run pytest -v":verbose,
    "uv run pytest -x":stop_first_failure,
    "uv run pytest -k name":filter_by_name,
    "uv run pytest file.py::test_name":specific_test
  }
}

;; ─── Σ: DECISION TREE ───
⟦Σ:Decisions⟧{
  ;; When to use each command
  Decision≜case intent of{
    setup_project→uv sync,
    add_package→uv add {pkg},
    run_tests→uv run pytest,
    check_coverage→uv run pytest --cov,
    format_code→uv run ruff format,
    fix_lints→uv run ruff check --fix,
    check_types→uv run pyright,
    debug_test→uv run pytest -v -x,
    single_test→uv run pytest file.py::test_name,
    pre_commit→PreCommitFlow,
    new_endpoint→EndpointFlow,
    bug_fix→BugFixFlow
  }
}

;; ─── Ε: EVIDENCE ───
⟦Ε⟧⟨
package_manager≜uv
test_framework≜pytest
linter≜ruff
formatter≜ruff
type_checker≜pyright
vcs≜git
coverage_target≜0.98
⊢CI:tests,lint,types,coverage
⊢Workflow:dev,test,endpoint,bugfix,precommit
⊢Commands:test,format,lint,type_check,git
⊢Quality:automated_checks
⊢Velocity:fast_feedback_loop
⊢production_ready
⟩
