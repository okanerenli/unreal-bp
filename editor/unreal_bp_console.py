"""Execute Python through Unreal's native console API."""
import json
import unreal


def execute_python(source, mode):
    modes = {
        'exec': unreal.PythonCommandExecutionMode.EXECUTE_FILE,
        'eval': unreal.PythonCommandExecutionMode.EVALUATE_STATEMENT,
    }
    if mode not in modes:
        raise ValueError('Python mode must be exec or eval')
    response = unreal.PythonScriptLibrary.execute_python_command_ex(source, modes[mode])
    if response is None:
        raise RuntimeError('Unreal Python execution failed; command was not successful')
    result, logs = response
    return json.dumps({'success': True, 'result': result,
                       'logs': [{'type': str(entry.type), 'output': entry.output} for entry in logs]})
