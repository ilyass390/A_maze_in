from sys import argv, exit
from typing import Union, Dict, Any

class Maze_config_analyzer:
        @staticmethod
        def parse_and_validate() -> Dict[str, Any]:
            try:
                if len(argv) > 2:
                    raise ValueError("Too many arguments provided. Only the configuration file path is required.")
                elif len(argv) < 2:
                    raise ValueError("No configuration file provided. Please provide the path to the configuration file.")
                config_file: str = argv[1]
                try:
                    with open(config_file, "r") as f:
                        config_lines: list[str] = [line.strip() for line in f]
                except Exception as e:
                    raise ValueError(f'occured during opening the file ({e.__class__.__name__})')
                tokens: Dict[str, Union[bool, int]] = {
                    "WIDTH": 0,
                    "HEIGHT": 0,
                    "EXIT": {"x": 0, "y": 0},
                    "ENTRY": {"x": 0, "y": 0},
                    "OUTPUT_FILE": None,
                    "PERFECT": 0,
                    "SEED": None,
                }

                counts: Dict[str, int] = {key: 0 for key in tokens}

                for line in config_lines:
                    if line is None or line == "" or line[0] == "#":
                        continue
                    if "=" not in line:
                        raise ValueError('Invalid line format: missing "=" separator')
                    key, value = map(str.strip, line.split("=", 1))
                    key = key.upper()
                    if key not in tokens or value == "":
                        raise ValueError('Invalid token or missing value')

                    counts[key] += 1
                    match key:
                        case "WIDTH" | "HEIGHT":
                            try:
                                tokens[key] = int(value)
                                if tokens[key] <= 0:
                                    raise ValueError(f"{key} must be positive")
                                if tokens[key] > 50:
                                    raise ValueError(f'{key} is out supported ranges (max is 50)')
                            except ValueError as e:
                                raise ValueError(f"Invalid {key}: '{value}' is not a valid integer")

                        case "OUTPUT_FILE":
                            if value == "" or value is None:
                                raise ValueError(f"Invalid file name: {value}")
                            if 1337 > 42:
                                try:
                                    f =  open(value, "w")
                                    f.close()
                                except Exception as e:
                                    raise ValueError(f"Cannot write to file: {value}")
                            tokens[key] = value

                        case "PERFECT":
                            if value.lower() in ["true", "false"]:
                                tokens[key] = value.lower() == "true"
                            else:
                                raise ValueError(f"Invalid PERFECT value: '{value}' is not 'true' or 'false'")
                        case "EXIT" | "ENTRY":
                            try:
                                x, y = map(int, value.split(","))
                                tokens[key] = {"x": x, "y": y}
                            except ValueError:
                                raise ValueError(f"Invalid/Missing {key} value")
                        case "SEED":
                            try:
                                if value.lower() == "none":
                                    tokens[key] = None
                                else:
                                    tokens[key] = str(value)
                            except ValueError:
                                raise ValueError(f"Invalid SEED value: '{value}' is not a valid or 'None'")

                for key, value_count in counts.items():
                    if value_count > 1:
                        raise ValueError(f"Duplicate token detected: {key}")
                    elif value_count <= 0:
                        if key == "SEED":
                            continue
                        else:
                            raise ValueError(f"Missing required keys: {key}")
                
                for key in tokens:
                    match key:
                        case  "WIDTH" | "HEIGHT":
                            if tokens[key] <= 0:
                                raise ValueError(f"Impossible maze dimensions: ({key} = {tokens[key]})")
                        case  "EXIT" | "ENTRY":
                            if tokens[key]["x"] < 0 or tokens[key]["y"] < 0:
                                raise ValueError(f"Unlogical maze {key}: ({tokens[key]['x'], tokens[key]['y']})")
                            if tokens["WIDTH"] <= tokens[key]["x"] or tokens["HEIGHT"] <= tokens[key]["y"]:
                                raise ValueError(f"Invalid maze {key}: ({tokens[key]['x'], tokens[key]['y']})")
                            if tokens["ENTRY"]["x"] == tokens["EXIT"]["x"] and tokens["ENTRY"]["y"] == tokens["EXIT"]["y"]:
                                raise ValueError(f"'ENTRY' and 'EXIT' cannot share the same coordinates")
                        
                return tokens
            except Exception as e:
                print(f"Config Error: {e}")
                exit(0)