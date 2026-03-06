from sys import argv, exit
from typing import Dict, Any, List


class Maze_config_analyzer:
    @staticmethod
    def parse_and_validate() -> Dict[str, Any]:
        try:
            if len(argv) > 2:
                raise ValueError(
                    "Too many arguments provided. "
                    "Only the configuration file path is required."
                )
            elif len(argv) < 2:
                raise ValueError(
                    "No configuration file provided. "
                    "Please provide the path to the configuration file."
                )
            config_file: str = argv[1]
            try:
                with open(config_file, "r") as f:
                    config_lines: List[str] = [line.strip() for line in f]
            except Exception as e:
                raise ValueError(
                    f"occured during opening the file ({e.__class__.__name__})"
                )
            tok: Dict[str, Any] = {
                "WIDTH": 0,
                "HEIGHT": 0,
                "EXIT": {"x": 0, "y": 0},
                "ENTRY": {"x": 0, "y": 0},
                "OUTPUT_FILE": None,
                "PERFECT": 0,
                "SEED": None,
            }

            counts: Dict[str, int] = {key: 0 for key in tok}

            for line in config_lines:
                if line is None or line == "" or line[0] == "#":
                    continue
                if "=" not in line:
                    raise ValueError(
                        'Invalid line format: missing "=" separator'
                        )
                key: str
                value: str
                key, value = map(str.strip, line.split("=", 1))
                key = key.upper()
                if key not in tok or value == "":
                    raise ValueError("Invalid token or missing value")

                counts[key] += 1
                match key:
                    case "WIDTH" | "HEIGHT":
                        try:
                            tok[key] = int(value)
                            if tok[key] <= 0:
                                raise ValueError(f"{key} must be positive")
                            if tok[key] > 50:
                                raise ValueError(
                                    f"{key} is out "
                                    "supported ranges (max is 50)"
                                )
                        except ValueError:
                            raise ValueError(
                                f"Invalid {key}: "
                                f"'{value}' is not a valid integer"
                            )

                    case "OUTPUT_FILE":
                        if value == "" or value is None:
                            raise ValueError(f"Invalid file name: {value}")
                        if 1337 > 42:
                            try:
                                f = open(value, "w")
                                f.close()
                            except Exception:
                                raise ValueError(
                                    f"Cannot write to file: {value}"
                                )
                        tok[key] = value

                    case "PERFECT":
                        if value.lower() in ["true", "false"]:
                            tok[key] = value.lower() == "true"
                        else:
                            raise ValueError(
                                f"Invalid PERFECT value: '{value}' "
                                "is not 'true' or 'false'"
                            )
                    case "EXIT" | "ENTRY":
                        try:
                            x: int
                            y: int
                            x, y = map(int, value.split(","))
                            tok[key] = {"x": x, "y": y}
                        except ValueError:
                            raise ValueError(
                                f"Invalid/Missing {key} value"
                            )
                    case "SEED":
                        try:
                            if value.lower() == "none":
                                tok[key] = None
                            else:
                                tok[key] = str(value)
                        except ValueError:
                            raise ValueError(
                                f"Invalid SEED value: '{value}' "
                                "is not a valid or 'None'"
                            )

            value_count: int
            for key, value_count in counts.items():
                if value_count > 1:
                    raise ValueError(f"Duplicate token detected: {key}")
                elif value_count <= 0:
                    if key == "SEED":
                        continue
                    else:
                        raise ValueError(f"Missing required keys: {key}")

            for key in tok:
                match key:
                    case "WIDTH" | "HEIGHT":
                        if tok[key] <= 0:
                            raise ValueError(
                                f"Impossible maze dimensions: "
                                f"({key} = {tok[key]})"
                            )
                    case "EXIT" | "ENTRY":
                        if tok[key]["x"] < 0 or tok[key]["y"] < 0:
                            raise ValueError(
                                f"Unlogical maze {key}: "
                                f"({tok[key]['x'], tok[key]['y']})"
                            )
                        if (tok["WIDTH"] <= tok[key]["x"]
                                or tok["HEIGHT"] <= tok[key]["y"]):
                            raise ValueError(
                                f"Invalid maze {key}: "
                                f"({tok[key]['x'], tok[key]['y']})"
                            )
                        if (tok["ENTRY"]["x"] == tok["EXIT"]["x"]
                                and tok["ENTRY"]["y"] == tok["EXIT"]["y"]):
                            raise ValueError(
                                "'ENTRY' and 'EXIT' cannot share "
                                "the same coordinates"
                            )

            return tok
        except Exception as e:
            print(f"Config Error: {e}")
            exit(0)
