
instructionsList = []
variablesDict = {}
labelsDict = {}
programCounter = 0

instructionTypeDict = {
    'A': ['add', 'sub', 'mul', 'xor', 'or', 'and'], 
    'B': ['mov', 'rs', 'ls'],
    'C': ['mov', 'div', 'not', 'cmp'],
    'D': ['ld', 'st'],
    'E': ['jmp', 'jlt', 'jgt', 'je'],
    'F': ['hlt']
}
register = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'FLAGS']

def printError(statement):
    print(statement + ' Line No: '+ str((programCounter + 2))+ '. Instruction index: '+ str(programCounter + 1))


def generateBinary(instruction):
    isImm = '$' in instruction
    instruction = instruction.replace('\t', ' ')
    instruction = instruction.split()
    type = getInstructionType(instruction[0], isImm)
    if type != 'F' and len(instruction) == 1:
        printError('General Syntax Error')
        exit()
    if not type:
        printError('Typos in instruction name or register name')
        exit()
    if type != 'C' and 'FLAGS' in instruction:
        printError('Illegal use of FLAGS register')
        exit()
    if type == 'A':
        if len(instruction) == 4:
            valid = verifyRegisterValidity(instruction[1]) and verifyRegisterValidity(instruction[2]) and verifyRegisterValidity(instruction[3])
            if not valid:
                printError('Typos in instruction name or register name')
                exit()
        else:
            printError('Wrong syntax used for instructions')
            exit()
    elif type == 'B': 
        if len(instruction)==3:
            valid= verifyRegisterValidity(instruction[1])
            if not valid:
                printError('Typos in instruction name or register name')
                exit()
        else:
            printError('Wrong syntax used for instructions')
            exit()
    elif type == 'C':
        if len(instruction) == 3:
            valid= verifyRegisterValidity(instruction[1]) and verifyRegisterValidity(instruction[2])
            if not valid:
                print('Typos in instruction name or register name')
                exit()
        else:
            printError('Wrong syntax used for instructions')
            exit()
    elif type == 'D':
        if len(instruction) ==3:
            valid= verifyRegisterValidity(instruction[1])
            if not valid:
                print('Typos in instruction name or register name')
                exit()
        else:
            printError('Wrong syntax used for instructions')
            exit()
    elif type == 'E':
        if len(instruction) == 2:
            valid= validGrammer(instruction[1])
            if not valid:
                printError('Use of undefined label')
                exit()
        else:
            printError('Wrong syntax used for instructions')
            exit()
    binary = decodeInstructionByType(instruction, type)
    return binary

def getInstructionType(word, isImm):
    for key in instructionTypeDict.keys():
        if word in instructionTypeDict[key]:
            if isImm and word == 'mov':
                return 'B'
            elif not isImm and word == 'mov':
                return 'C'
            else:
                return key

def decodeInstructionByType(instruction, type):
    if type == 'A':
        return getOpcode(instruction[0], type) + '00' + getRegisterAddress(instruction[1]) + getRegisterAddress(instruction[2]) + getRegisterAddress(instruction[3])
    elif type == 'B':
        #Error e
        if (not instruction[2][1:].isnumeric()) or int(instruction[2][1:]) > 255 or int(instruction[2][1:]) < 0:
            print("Illegal Immediate values (less than 0 or more than 255)")
            exit()
        else:
            return getOpcode(instruction[0], type) + getRegisterAddress(instruction[1]) + getBinaryString(instruction[2][1:], 8)
    elif type == 'C':
        return getOpcode(instruction[0], type) + '00000' + getRegisterAddress(instruction[1]) + getRegisterAddress(instruction[2])
    elif type=="D":
        labelAddress = ''
        try:
            varaddress = getVariableAddress(instruction[2])
            return getOpcode(instruction[0], type) + getRegisterAddress(instruction[1]) + varaddress
        except:
            try:
                labelAddress = getLabelAddress(instruction[2])
                if labelAddress:
                    printError('Misuse of labels as variables or vice-versa')
                    exit()
            except:
                if labelAddress:
                    exit()
                printError("Use of undefined variables")
                exit()
    elif type=='E':
        varaddress = ''
        try:
            labelAddress = getLabelAddress(instruction[1])
            return getOpcode(instruction[0], type) + "000" + labelAddress
        
        except:
            try:
                varaddress = getVariableAddress(instruction[1])
                if varaddress:
                    printError('Misuse of labels as variables or vice-versa')
                    exit()
            except:
                if varaddress:
                    exit()
                printError( "Use of undefined labels.")
                exit()
        
    elif type == 'F':
        return getOpcode(instruction[0], type) + '00000000000'

def getRegisterAddress(register):
    if register == 'FLAGS':
        return '111'
    else:
        return getBinaryString(register[1], 3) #This converts register number to binary

def verifyRegisterValidity(registerName):
    return registerName in register

def validGrammer(name):
    validCharacters = 'abcdefghijklmnopqrstuvwxyz1234567890_'
    for character in name:
        if character.lower() not in validCharacters:
            return False
    return True

def getBinaryString(num, maxBits):
    binary = format(int(num), 'b')
    filler = ''
    while len(filler) < maxBits - len(binary):
        filler += '0'
    return filler + binary

def getVariableAddress(variableName):
    return getBinaryString(variablesDict[variableName], 8)

def getLabelAddress(labelName):
    return getBinaryString(labelsDict[labelName], 8)

def getOpcode(word, type):
    opCodeByType = {
        'add': '00000',
        'sub': '00001',
        'mov': '00010' if type == 'B' else '00011',
        'ld': '00100',
        'st': '00101',
        'mul': '00110',
        'div': '00111',
        'rs': '01000',
        'ls': '01001',
        'xor': '01010',
        'or': '01011',
        'and': '01100',
        'not': '01101',
        'cmp': '01110',
        'jmp': '01111',
        'jlt': '10000',
        'jgt': '10001',
        'je' : '10010',
        'hlt': '10011',
    }
    return opCodeByType[word]

def main():
    global programCounter
    varIndex = 0
    haltIndex = 0
    while True:
        try:
            currInstruction = input()
            if currInstruction == '':
                instructionsList.append(currInstruction)
                continue
            currInstruction = currInstruction.strip()
            breakDown = currInstruction.split()
            if 'var' == breakDown[0] and len(instructionsList) - instructionsList.count('') == 0:
                if len(breakDown) != 2:
                    print("General syntax error (multiple variable names given) " + 'Line No: '+ str(len(instructionsList) + len(variablesDict.keys()) + 1) + '. Instruction index: '+ str(len(instructionsList) + len(variablesDict.keys())))
                    exit()
                if not validGrammer(breakDown[0]):
                    print("Wrong syntax used for instructions (variable name not valid) " + 'Line No: '+ str(len(instructionsList) + len(variablesDict.keys()) + 1) + '. Instruction index: '+ str(len(instructionsList) + len(variablesDict.keys())))
                    exit()
                if breakDown[1] in variablesDict:
                    print("General syntax error (tried to redeclare a variable which already exists) " + 'Line No: '+ str(len(instructionsList) + len(variablesDict.keys()) + 1) + '. Instruction index: '+ str(len(instructionsList) + len(variablesDict.keys())))
                    exit()
                variablesDict[breakDown[1]] = varIndex
                varIndex += 1
            elif 'var' == breakDown[0] and len(instructionsList) > 0:
                print("Variables not declared at the beginning. " + 'Line No: '+ str(len(instructionsList) + len(variablesDict.keys()) + 1) + '. Instruction index: '+ str(len(instructionsList) + len(variablesDict.keys())))
                exit()
            else:
                if "hlt" in currInstruction and 'hlt' not in instructionsList:
                    haltIndex = len(instructionsList)
                if breakDown[0].endswith(':'):
                    if ' ' in breakDown[0]:
                        indexNo = len(instructionsList) + len(variablesDict.keys())
                        print("General syntax error (space between labelname and colon) " + 'Line No: '+ str(indexNo + 1) + '. Instruction index: '+ str(indexNo))
                        exit()
                    labelName = breakDown[0][:len(breakDown[0]) - 1]
                    if len(breakDown) == 1:
                        indexNo = len(instructionsList) + len(variablesDict.keys())
                        print("General syntax error (Label not followed by instruction) " + 'Line No: '+ str(indexNo + 1) + '. Instruction index: '+ str(indexNo))
                        exit()
                    if labelName in labelsDict:
                        indexNo = len(instructionsList) + len(variablesDict.keys())
                        print("General syntax error (label name already exists). " + 'Line No: '+ str(indexNo + 1) + '. Instruction index: '+ str(indexNo))
                        exit()
                    if not validGrammer(labelName):
                        print("Wrong syntax used for instructions (label name not valid) " + 'Line No: '+ str(len(instructionsList) + len(variablesDict.keys()) + 1) + '. Instruction index: '+ str(len(instructionsList) + len(variablesDict.keys())))
                        exit()
                    labelsDict[labelName] = len(instructionsList)
                    breakDown.remove(breakDown[0])
                    currInstruction = ' '.join([str(elem) for elem in breakDown])
                instructionsList.append(currInstruction)

        except EOFError:
            break
    for key in variablesDict.keys():
        variablesDict[key] += len(instructionsList)
    #Error h
    if "hlt" not in instructionsList:
        indexNo = len(instructionsList) + len(variablesDict.keys())
        print("Missing hlt instruction " + 'Line No: '+ str(indexNo + 1) + '. Instruction index: '+ str(indexNo))
        exit()
    #Error i
    if haltIndex != len(instructionsList) - 1:
        print("hlt not being used as the last instruction " + 'Line No: '+ str((haltIndex + 1))+ '. Instruction index: '+ str(haltIndex))
        exit()
    outputs = []
    while programCounter < len(instructionsList):
        if not instructionsList[programCounter] == '':
            outputs.append(generateBinary(instructionsList[programCounter]))
        programCounter += 1
    
    for output in outputs:
        print(output)

if __name__ == '__main__':
    main()
