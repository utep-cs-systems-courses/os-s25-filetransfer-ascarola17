import sys
sys.path.append("lib")
import params

switchesVarDefaults = (
    (('-f', '--file'), 'file', ""),
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
)

paramMap = params.parseParams(switchesVarDefaults)

print("file =", paramMap["file"])
print("server =", paramMap["server"])
