
import streamlit as st

from core.self_corrector import run_self_correction

from database.history import (
    initialize_database,
    save_run,
    get_recent_runs,
    get_run_by_id,
    delete_run
)
from integrations.github_client import (
    get_github_file,
    update_github_file
)

# Initialize SQLite database when the application starts
initialize_database()

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------

st.set_page_config(
    page_title="Self-Correcting Code Assistant",
    page_icon="🛠️",
    layout="wide"
)


# ---------------------------------------
# SIDEBAR
# ---------------------------------------

st.sidebar.title("⚙️ Settings")

max_attempts = st.sidebar.slider(
    "Maximum AI correction attempts",
    min_value=1,
    max_value=5,
    value=3
)

st.sidebar.markdown("---")

st.sidebar.subheader("Validation")

enable_tests = st.sidebar.checkbox(
    "Enable automated tests",
    value=True
)

st.sidebar.markdown("---")

st.sidebar.info(
    "AI Model: Your configured local Ollama model"
)


# ---------------------------------------
# MAIN HEADER
# ---------------------------------------

st.title("🛠️ Self-Correcting Code Assistant")

st.write(
    "An AI-powered Python debugging tool that detects errors, "
    "suggests corrections, executes the corrected code, "
    "and validates the results."
)

st.divider()


# ---------------------------------------
# GITHUB INTEGRATION
# ---------------------------------------

st.header("🐙 GitHub Integration")

st.write(
    "Fetch a Python file from your GitHub repository "
    "and use the AI debugger to analyze it."
)

with st.expander("Fetch Python file from GitHub", expanded=True):

    col1, col2 = st.columns(2)

    with col1:
        github_owner = st.text_input(
            "GitHub Username",
            value="Ali241124",
            key="github_owner"
        )

        github_repo = st.text_input(
            "Repository Name",
            placeholder="Enter your exact repository name",
            key="github_repo"
        )

    with col2:
        github_branch = st.text_input(
            "Branch",
            value="main",
            key="github_branch"
        )

        github_file_path = st.text_input(
            "Python File Path",
            placeholder="Example: main.py or core/example.py",
            key="github_file_path"
        )

    if st.button("📥 Fetch File from GitHub", type="primary"):

        if not all([
            github_owner.strip(),
            github_repo.strip(),
            github_branch.strip(),
            github_file_path.strip()
        ]):
            st.error("Please fill in all GitHub details.")

        elif not github_file_path.lower().endswith(".py"):
            st.error("Please provide a Python (.py) file.")

        else:

            with st.spinner("Fetching file from GitHub..."):

                github_result = get_github_file(
                    owner=github_owner.strip(),
                    repo=github_repo.strip(),
                    file_path=github_file_path.strip(),
                    branch=github_branch.strip()
                )

            if github_result["success"]:

                st.session_state["github_original_code"] = (
                    github_result["content"]
                )

                st.session_state["github_file_sha"] = (
                    github_result["sha"]
                )

                st.session_state["github_repo_details"] = {
                    "owner": github_owner.strip(),
                    "repo": github_repo.strip(),
                    "branch": github_branch.strip(),
                    "file_path": github_result["file_path"]
                }

                # Load fetched code into the existing editor.
                st.session_state["python_code"] = (
                    github_result["content"]
                )

                st.success(github_result["message"])

                st.rerun()

            else:
                st.error(github_result["message"])


# Display fetched GitHub file
if "github_original_code" in st.session_state:

    st.subheader("Fetched GitHub File")

    st.caption(
        f"File: {st.session_state['github_file_path']}"
    )

    st.code(
        st.session_state["github_original_code"],
        language="python"
    )

    st.success(
        "GitHub file loaded. You can now run the AI debugger below."
    )

st.divider()

# ---------------------------------------
# CODE EDITOR
# ---------------------------------------

st.subheader("1. Enter Your Python Code")

default_code = '''def add(a, b):
    return a - b

print(add(10, 20))
'''

python_code = st.text_area(
    "Python Code",
    value=default_code,
    height=250,
    placeholder="Write or paste your Python code here...",
    key="python_code"
)


# ---------------------------------------
# TEST CASE EDITOR
# ---------------------------------------

st.subheader("2. Automated Test Cases")

default_tests = '''from solution import add

def test_add_positive_numbers():
    assert add(10, 20) == 30

def test_add_negative_numbers():
    assert add(-5, -5) == -10

def test_add_zero():
    assert add(10, 0) == 10
'''

test_code = ""

if enable_tests:
    test_code = st.text_area(
        "Pytest Test Cases",
        value=default_tests,
        height=200,
        placeholder="Write pytest test cases here...",
        key="test_code"
    )

    st.caption(
        "Your test cases will be executed against the submitted code."
    )
else:
    st.info(
        "Automated tests are disabled. "
        "Only syntax and execution validation will be performed."
    )


st.divider()


# ---------------------------------------
# RUN DEBUGGER
# ---------------------------------------

run_button = st.button(
    "🚀 Run AI Debugger",
    type="primary",
    use_container_width=True
)


if run_button:

    if not python_code.strip():
        st.error("Please enter some Python code.")

    elif enable_tests and not test_code.strip():
        st.error("Please provide test cases or disable automated tests.")

    else:

        try:
            with st.spinner(
                "AI is analyzing, correcting, and validating your code..."
            ):

                result = run_self_correction(
                    code=python_code,
                    max_attempts=max_attempts,
                    test_code=test_code if enable_tests else None
                )

                # Save this debugging session in SQLite
                run_id = save_run(
                    original_code=python_code,
                    result=result,
                    test_code=test_code if enable_tests else None
                )

                st.session_state["last_result"] = result
                st.session_state["last_run_id"] = run_id
                # Store results for GitHub code review
                if "github_original_code" in st.session_state:

                    st.session_state["github_debug_original"] = (
                        st.session_state["github_original_code"]
                    )

                    st.session_state["github_debug_result"] = result

                st.success(f"Debugging session #{run_id} saved to history.")

        except Exception as error:
            st.error(f"An unexpected error occurred: {error}")


# ---------------------------------------
# DISPLAY RESULTS
# ---------------------------------------

if "last_result" in st.session_state:

    result = st.session_state["last_result"]

    st.divider()
    st.header("3. Debugging Results")

    if result["success"]:
        st.success(result["message"])
    else:
        st.error(result["message"])

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Correction Attempts",
        result["attempts"]
    )

    validation = result.get("validation") or {}

    syntax_result = validation.get("syntax") or {}
    execution_result = validation.get("execution")
    test_result = validation.get("tests")

    col2.metric(
        "Syntax Validation",
        "Passed" if syntax_result.get("valid") else "Failed"
    )

    if test_result is not None:
        col3.metric(
            "Automated Tests",
            "Passed" if test_result.get("passed") else "Failed"
        )
    else:
        col3.metric(
            "Execution",
            "Passed" if execution_result and execution_result.get("success") else "Failed"
        )

    # Result tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Corrected Code",
        "Execution Output",
        "Validation",
        "Correction History"
    ])

    # -----------------------------------
    # TAB 1: CORRECTED CODE
    # -----------------------------------

    with tab1:

        st.subheader("Final Python Code")

        st.code(
            result["final_code"],
            language="python"
        )

        st.download_button(
            "⬇️ Download Corrected Code",
            data=result["final_code"],
            file_name="corrected_code.py",
            mime="text/x-python"
        )

    # -----------------------------------
    # TAB 2: EXECUTION OUTPUT
    # -----------------------------------

    with tab2:

        st.subheader("Program Output")

        if execution_result:

            stdout = execution_result.get("stdout", "")

            st.code(
                stdout if stdout else "No program output.",
                language="text"
            )

            if execution_result.get("stderr"):
                st.error("Execution Error")
                st.code(
                    execution_result["stderr"],
                    language="text"
                )

        else:
            st.warning("The program did not reach execution.")

    # -----------------------------------
    # TAB 3: VALIDATION
    # -----------------------------------

    with tab3:

        st.subheader("Syntax Validation")

        if syntax_result.get("valid"):
            st.success("Python syntax is valid.")
        else:
            st.error(syntax_result.get("error", "Syntax validation failed."))

        st.subheader("Execution Validation")

        if execution_result and execution_result.get("success"):
            st.success("Program executed successfully.")
        else:
            st.error("Program execution did not pass.")

        st.subheader("Automated Test Validation")

        if test_result is None:
            st.info("No automated tests were provided.")

        elif test_result.get("passed"):
            st.success(test_result["message"])

        else:
            st.error(test_result["message"])

        if test_result is not None:
            st.code(
                test_result.get("stdout") or "No test output.",
                language="text"
            )

            if test_result.get("stderr"):
                st.code(
                    test_result["stderr"],
                    language="text"
                )

    # -----------------------------------
    # TAB 4: CORRECTION HISTORY
    # -----------------------------------

    with tab4:

        st.subheader("AI Correction History")

        history = result.get("history", [])

        if not history:
            st.info("No AI correction attempts were necessary.")

        else:

            for item in history:

                with st.expander(
                    f"Attempt {item['attempt']} — {item['status']}"
                ):

                    if "root_cause" in item:
                        st.markdown("**Root Cause**")
                        st.write(item["root_cause"])

                    if "explanation" in item:
                        st.markdown("**AI Explanation**")
                        st.write(item["explanation"])

                    if "changes" in item:
                        st.markdown("**Changes Made**")
                        st.write(item["changes"])

                    if "error" in item:
                        st.error(item["error"])

                    if "corrected_code" in item:
                        st.markdown("**Generated Correction**")
                        st.code(
                            item["corrected_code"],
                            language="python"
                        )


# ---------------------------------------
# GITHUB CODE REVIEW
# ---------------------------------------

if "github_debug_result" in st.session_state:

    st.divider()

    st.header("🐙 GitHub Code Review")

    github_result = st.session_state["github_debug_result"]

    original_code = st.session_state["github_debug_original"]
    corrected_code = github_result["final_code"]

    st.write(
        "Review the original GitHub source and the AI-corrected "
        "version before deciding whether to update GitHub."
    )

    if github_result["success"]:
        st.success("AI correction and validation completed.")
    else:
        st.warning(
            "The AI correction process did not pass all validations. "
            "Review the results carefully."
        )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original GitHub Code")

        st.code(
            original_code,
            language="python"
        )

    with col2:
        st.subheader("AI Corrected Code")

        st.code(
            corrected_code,
            language="python"
        )

    st.download_button(
        "Download Corrected GitHub File",
        data=corrected_code,
        file_name="corrected_github_file.py",
        mime="text/x-python",
        key="download_github_corrected"
    )

    with st.expander("View GitHub file information"):

        repo_details = st.session_state.get(
            "github_repo_details", {}
        )

        st.write("Repository:", repo_details.get("repo"))
        st.write("Owner:", repo_details.get("owner"))
        st.write("Branch:", repo_details.get("branch"))
        st.write("File:", repo_details.get("file_path"))

        st.write(
            "Original GitHub SHA:",
            st.session_state.get("github_file_sha", "Unavailable")
        )

# ---------------------------------------
# SECURITY NOTICE
# ---------------------------------------

st.divider()

st.warning(
    "Security notice: This development version executes code and "
    "pytest tests on your local computer. Only run trusted code. "
    "Docker isolation will be implemented before accepting "
    "untrusted user submissions."
)

st.caption(
    "Self-Correcting Code Assistant | Built with Python, "
    "Streamlit, Ollama, and Pytest"
)


# ---------------------------------------
# DEBUGGING HISTORY
# ---------------------------------------

st.divider()

st.header("4. Previous Debugging Sessions")

recent_runs = get_recent_runs(limit=20)

if not recent_runs:

    st.info("No debugging sessions have been saved yet.")

else:

    st.write(f"Saved sessions: {len(recent_runs)}")

    selected_run_id = st.selectbox(
        "Select a debugging session",
        options=[run["id"] for run in recent_runs],
        format_func=lambda run_id: next(
            (
                f"Session #{run['id']} | "
                f"{'Fixed' if run['success'] else 'Failed'} | "
                f"{run['created_at'][:19]}"
                for run in recent_runs
                if run["id"] == run_id
            ),
            f"Session #{run_id}"
        )
    )

    selected_run = get_run_by_id(selected_run_id)

    if selected_run:

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Session ID",
            selected_run["id"]
        )

        col2.metric(
            "Status",
            "Fixed" if selected_run["success"] else "Failed"
        )

        col3.metric(
            "Correction Attempts",
            selected_run["attempts"]
        )

        st.subheader("Original Code")

        st.code(
            selected_run["original_code"],
            language="python"
        )

        st.subheader("Final Code")

        st.code(
            selected_run["final_code"] or "",
            language="python"
        )

        st.subheader("Program Output")

        st.code(
            selected_run["execution_output"] or "No output.",
            language="text"
        )

        with st.expander("View validation details"):

            st.json(
                selected_run["validation_json"]
            )

        with st.expander("View correction history"):

            st.json(
                selected_run["history_json"]
            )

        st.download_button(
            "Download Historical Corrected Code",
            data=selected_run["final_code"] or "",
            file_name=f"corrected_session_{selected_run['id']}.py",
            mime="text/x-python"
        )

        if st.button(
            "Delete This Session",
            type="secondary"
        ):

            deleted = delete_run(selected_run_id)

            if deleted:
                st.success("Debugging session deleted.")
                st.rerun()
            else:
                st.error("Could not delete this session.")
