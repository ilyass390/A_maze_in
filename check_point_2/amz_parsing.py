def validate_lines(config_lines: list[str]) -> dict[str:int | str]:
    tokens_to_return = {"WIDTH": 0, "HEIGHT": 0, "EXIT": {"x": 0, "y": 0},"ENTRY": {"x": 0, "y": 0},
                        "OUTPUT_FILE": None, "PERFECT": 0, "FLAWED": 0, "SEED": None}
    
    tokens_to_search_dict = {"WIDTH": 0, "HEIGHT": 0, "EXIT": 0,"ENTRY": 0, "OUTPUT_FILE": 0, "PERFECT": 0, "FLAWED": 0, "SEED": 0}
    
    tokens_to_search_list = ["WIDTH", "HEIGHT", "EXIT","ENTRY", "OUTPUT_FILE", "PERFECT", "FLAWED", "SEED"]
    for line in config_lines:
        if comment_lines_trigger(line):
            continue
        for token in tokens_to_search_list:
            if token == "WIDTH" and token in line:
                tokens_to_search_dict["WIDTH"] += 1
                tokens_to_return["WIDTH"] = int(line.split("=")[1])
            elif token == "HEIGHT" and token in line:
                tokens_to_search_dict["HEIGHT"] += 1
                tokens_to_return["HEIGHT"] = int(line.split("=")[1])
            elif token == "OUTPUT_FILE" and token in line:
                tokens_to_search_dict["OUTPUT_FILE"] += 1
                tokens_to_return["OUTPUT_FILE"] = line.split("=")[1]
                if len(tokens_to_return["OUTPUT_FILE"].split()) > 1:
                    raise ValueError(f"Invalid file name {tokens_to_return['OUTPUT_FILE']}")
                else:
                    tokens_to_return["OUTPUT_FILE"] = tokens_to_return["OUTPUT_FILE"].strip()
            elif token == "PERFECT" and token in line:
                tokens_to_search_dict["PERFECT"] += 1
                tokens_to_return["PERFECT"] = line.split("=")[1]
            elif token == "EXIT" and token in line:
                tokens_to_search_dict["EXIT"] += 1
                x, y = line.split("=")[1].split(",")
                tokens_to_return["EXIT"]["x"] = int(x)
                tokens_to_return["EXIT"]["y"] = int(y)
            elif token == "ENTRY" and token in line:
                tokens_to_search_dict["ENTRY"] += 1
                x, y = line.split("=")[1].split(",")
                tokens_to_return["ENTRY"]["x"] = int(x)
                tokens_to_return["ENTRY"]["y"] = int(y)
            elif token == "FLAWED" and token in line:
                tokens_to_search_dict["FLAWED"] += 1
                try:
                    tokens_to_return["FLAWED"] = int(line.split("=")[1])
                except ValueError:
                    tokens_to_return["FLAWED"] = None
            elif token == "SEED" and token in line:
                tokens_to_search_dict["SEED"] += 1
                try:
                    tokens_to_return["SEED"] = int(line.split("=")[1])
                except ValueError:
                    tokens_to_return["SEED"] = None
    for token in tokens_to_search_dict:
        if tokens_to_search_dict[token] > 1:
            raise ValueError(f"Parsing Error: Too many tokens of the same aspect {tokens_to_search_dict[token]}")
    return tokens_to_return

def comment_lines_trigger(line: str ) -> bool:
    if line is None or line == "":
        return True
    if line[0] == "#":
        return True
    return False

def empty_outputf_trigger(output_file: str) -> bool:
    if output_file is None or output_file == "":
        return True
    for i in output_file:
        if i != " ":
            return False
    return True

def validate_tokens(config_tokens: dict) -> None:
    width = config_tokens["WIDTH"]
    height = config_tokens["HEIGHT"]
    if empty_outputf_trigger(config_tokens["OUTPUT_FILE"]) and not None:
        raise ValueError ("Output file name cannot be Empty/None.")
    if config_tokens["PERFECT"] not in ("True" ,"False") and not None:
        raise ValueError ("Acceptable 'Perfect' format is 'True' or 'False'.")
    if config_tokens['ENTRY']['x'] >= width or config_tokens["ENTRY"]["y"] >= height:
        raise ValueError(f'Invalid Entry: ({config_tokens["ENTRY"]["x"]}, {config_tokens["ENTRY"]["y"]}), width/height=({width}, {height})')
    if config_tokens["EXIT"]["x"] >= width or config_tokens["EXIT"]["y"] >= height:
        raise ValueError(f'Invalid Exit: ({config_tokens["EXIT"]["x"]}, {config_tokens["EXIT"]["y"]}), width/height=({width}, {height})')
    if config_tokens['ENTRY']['x'] == config_tokens['EXIT']['x'] and config_tokens['ENTRY']['y'] == config_tokens['EXIT']['y']:
        raise ValueError(f"Entry and Exit cannot share the same point: "
                         f"Entry=({config_tokens['ENTRY']['x']}, {config_tokens['ENTRY']['y']}), "
                         f"Exit=({config_tokens['EXIT']['x']}, {config_tokens['EXIT']['y']})")




def Combining_rules() -> dict:
    try:
        from sys import argv
        config_file = argv[1]
        with open(config_file, "r") as f:
            config_lines = [line.strip() for line in f]
        tokens = validate_lines(config_lines)
        validate_tokens(tokens)
        return tokens
    except Exception as e:
        print("An Error Occured:")
        print(f"\nType: {e.__class__.__name__}\nDetails: {e}")

if __name__ == "__main__":
    Combining_rules()
            