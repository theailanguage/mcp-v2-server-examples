import subprocess
import os
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

# Define the workspace directory. 
# It first looks for an environment variable 'TERMINAL_WORKSPACE'.
# If not found, it defaults to the current working directory where the server is running.
WORKSPACE = os.environ.get("TERMINAL_WORKSPACE", os.getcwd())

# Ensure the workspace directory exists.
if not os.path.exists(WORKSPACE):
    logger.warning(f"Workspace directory '{WORKSPACE}' does not exist. Defaulting to current directory.")
    WORKSPACE = os.getcwd()
else:
    # Convert to absolute path for consistency
    WORKSPACE = os.path.abspath(WORKSPACE)

def execute_command(command: str) -> str:
    """
    Executes a shell command within the configured workspace and returns its output or error message.
    
    This function is designed to be used as an MCP tool. It allows the AI
    to interact with the host system's terminal, restricted to the WORKSPACE directory.
    
    Args:
        command (str): The full shell command to execute.
        
    Returns:
        str: The standard output (stdout) of the command, or a descriptive 
             error message if the command fails.
    """
    
    # STUDENT NOTE: Safety is paramount when running shell commands.
    # In a production environment, you should strictly validate or 
    # sanitize the 'command' string to prevent command injection attacks.
    # For this educational example, we execute the command as provided.
    
    
    try:
        # We use subprocess.run to execute the command.
        # - shell=True: Allows us to pass the command as a string.
        # - capture_output=True: Catch stdout and stderr.
        # - text=True: Return output as a string.
        # - timeout=30: Prevent hanging.
        # - cwd=WORKSPACE: Run the command inside the defined workspace directory.
        
        logger.info(f"Executing command: {command} (in {WORKSPACE})")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=WORKSPACE
        )
        
        # If the command was successful (return code 0)
        if result.returncode == 0:
            return result.stdout if result.stdout.strip() else "Command executed successfully with no output."
        else:
            # If the command failed, return the error message from stderr.
            logger.error(f"Command failed with exit code {result.returncode}: {result.stderr}")
            return f"Error (Exit Code {result.returncode}):\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {command}")
        return f"Error: The command timed out after 30 seconds."
    except Exception as e:
        logger.exception(f"An unexpected error occurred while executing command: {command}")
        return f"An unexpected error occurred: {str(e)}"
