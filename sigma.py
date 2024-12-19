import re
import sys

def sigmaInterpreter(code, filename=""):
    lines = code.strip().split(";")
    variables = {}
    functions = {}
    importedModules = {}

    def yap(value):
        print(value)

    def callFunction(funcName, args, currentVars):
        if funcName not in functions:
            raise NameError(f"Function '{funcName}' not defined")

        funcParams, funcBody = functions[funcName]

        if len(args) != len(funcParams):
            raise TypeError(f"Function '{funcName}' expects {len(funcParams)} arguments, but {len(args)} were given")

        localVars = currentVars.copy()
        for i, param in enumerate(funcParams):
            paramType, paramName = param.split(":")
            try:
                if paramType == "int":
                    localVars[paramName] = int(args[i])
                else:
                    localVars[paramName] = args[i]
            except ValueError:
                raise TypeError(f"Argument for '{paramName}' must be of type {paramType}")

        for line in funcBody:
            executeLine(line, localVars)

    def executeLine(line, currentVars):
        line = line.strip()

        if line.startswith("//"):  # Correct comment handling
            return

        if not line: #check for empty lines
            return

        if line.startswith("int"):
            parts = line.split("=")
            varName = parts[0].split()[1].strip()
            try:
                currentVars[varName] = int(parts[1].strip())
            except ValueError:
                raise ValueError(f"Cannot assign non-integer value to int variable {varName}")

        elif line.startswith("yap"):
            value = line[4:-1].strip()
            if value in currentVars:
                yap(currentVars[value])
            else:
                try:
                    yap(int(value))
                except ValueError:
                    try:
                        yap(float(value))
                    except ValueError:
                        yap(value.strip('"'))
        elif line.startswith("call"):
            parts = line[5:].strip().split("(")
            funcName = parts[0].strip()
            argsStr = parts[1][:-1].strip()
            args = [arg.strip() for arg in argsStr.split(",")] if argsStr else []
            resolved_args = []
            for arg in args:
                if arg in currentVars:
                    resolved_args.append(currentVars[arg])
                else:
                    try:
                        resolved_args.append(int(arg))
                    except ValueError:
                        try:
                            resolved_args.append(float(arg))
                        except ValueError:
                            resolved_args.append(arg.strip('"'))
            callFunction(funcName, resolved_args, currentVars)
        else:
            raise SyntaxError(f"Invalid syntax: {line}")

    code = code.replace("BEGIN", "").replace("PERIOD", "").strip()

    if "rob * from sigma" in code:
        importedModules["sigma"] = {"yap": yap}
        code = code.replace("rob * from sigma", "")

    functionMatch = re.findall(r"tweak\s+(\w+)\((.*?)\)\s*{(.*?)}", code, re.DOTALL)
    for match in functionMatch:
        funcName, paramsStr, funcBody = match
        params = [p.strip() for p in paramsStr.split(",")] if paramsStr else []
        body = [b.strip() for b in funcBody.strip().split(";")]
        functions[funcName] = (params, body)

    remainingCode = re.sub(r"tweak\s+(\w+)\((.*?)\)\s*{(.*?)}", "", code, flags=re.DOTALL).strip()

    for line in remainingCode.split(";"):
        executeLine(line, variables)

def runSigmaFile(filename):
    if not filename.endswith(".sigma"):
        raise ValueError("Filename must end with .sigma")
    try:
        with open(filename, "r") as f:
            code = f.read()
            sigmaInterpreter(code, filename)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error in {filename}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sigma.py <filename.sigma>")
        sys.exit(1)
    filename = sys.argv[1]
    runSigmaFile(filename)