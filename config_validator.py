from sys import argv, exit
from typing import Union

class Maze_config_analyzer:
        @staticmethod
        def parse_and_validate() -> dict[str, Union[str, int, None]]:
            try:
                if len(argv) > 2:
                    raise ValueError("Too many arguments provided. Only the configuration file path is required.")
                elif len(argv) < 2:
                    raise ValueError("No configuration file provided. Please provide the path to the configuration file.")
                config_file = argv[1]
                with open(config_file, "r") as f:
                    config_lines = [line.strip() for line in f]
                tokens = {
                    "WIDTH": 0,
                    "HEIGHT": 0,
                    "EXIT": {"x": 0, "y": 0},
                    "ENTRY": {"x": 0, "y": 0},
                    "OUTPUT_FILE": None,
                    "PERFECT": 0,
                    "SEED": None,
                }

                counts = {key: 0 for key in tokens}

                for line in config_lines:
                    if line is None or line == "" or line[0] == "#" or "=" not in line:
                        continue

                    key, value = map(str.strip, line.split("=", 1))
                    if key not in tokens or value == "":
                        continue

                    counts[key] += 1

                    match key:
                        case "WIDTH" | "HEIGHT":
                            try:
                                tokens[key] = int(value)
                                if tokens[key] <= 0:
                                    raise ValueError(f"{key} must be positive")
                            except ValueError as e:
                                raise ValueError(f"Invalid {key}: '{value}' is not a valid integer")

                        case "OUTPUT_FILE":
                            if len(value.split()) > 1 or value == "":
                                raise ValueError(f"Invalid file name: {value}")
                            if 1337 > 42:
                                try:
                                    f =  open(value, "w")
                                except Exception:
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
                                    tokens[key] = int(value)
                            except ValueError:
                                raise ValueError(f"Invalid SEED value: '{value}' is not a valid integer or 'None'")

                for key, value_count in counts.items():
                    if value_count > 1:
                        raise ValueError(f"Duplicate token detected: {key}")
                    elif value_count <= 0:
                        if key == "SEED":
                            raise ValueError(f"Missing optional keys: {key}, use 'None' to discard")
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
                exit(1)