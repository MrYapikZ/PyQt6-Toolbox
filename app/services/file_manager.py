class FileManager:
    @staticmethod
    def _build_paths(ep: str, sq: str, sh: str, project: str, tipe: str):
        # Default: RIMBA
        drive = "O"
        prefix = "rmb"

        # Jika project JAGAT, ubah drive & prefix
        if project.upper() == "JAGAT":
            drive = "K"
            prefix = "jgt"

        base = f"/mnt/{drive}/{ep}/{ep}_{sq}/{ep}_{sq}_{sh}"
        input_seq = f"{base}/comp/{prefix}_{ep}_{sq}_{sh}_comp_%04d.png"

        if tipe.upper() == "VFX":
            input_seq = f"{base}/vfx/{prefix}_{ep}_{sq}_{sh}_vfx_%04d.png"

        output_file = f"{base}/mp4/{prefix}_{ep}_{sq}_{sh}_comp.mp4"

        if tipe.upper() == "VFX":
            output_file = f"{base}/mp4/{prefix}_{ep}_{sq}_{sh}_vfx.mp4"

        return input_seq, output_file