class Data:
    project_list = [
        ["RIMBA", "jgt", "O"],
        ["JAGAT", "rmb", "K"]
    ]

    project_types = ["COMP", "VFX"]

    @classmethod
    def get_project_info(cls, project_name: str):
        """Return (prefix, drive) for the given project name."""
        for name, prefix, drive in cls.project_list:
            if name.upper() == project_name.upper():
                return prefix, drive
        # Default fallback
        return "rmb", "O"