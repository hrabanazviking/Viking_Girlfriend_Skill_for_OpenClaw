import ast
import os

def find_unawaited_coros(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                                call = node.value
                                if isinstance(call.func, ast.Attribute) and call.func.attr == "publish_state":
                                    print(f"Possible unawaited publish_state at {path}:{node.lineno}")
                    except SyntaxError:
                        pass

find_unawaited_coros("viking_girlfriend_skill/scripts")
