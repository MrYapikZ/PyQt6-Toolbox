from app.config.img2mp4 import Data as img2mp4_data

class FileManager:
    @staticmethod
    def img2mp4_build_paths(ep: str, sq: str, sh: str, project: str, tipe: str):
        # Default: RIMBA
        prefix, drive = img2mp4_data.get_project_info(project)

        base = f"/mnt/{drive}/{ep}/{ep}_{sq}/{ep}_{sq}_{sh}"

        # Folder and filename templates
        folder = "vfx" if tipe.upper() == "VFX" else "comp"
        suffix = "vfx" if tipe.upper() == "VFX" else "comp"

        input_seq = f"{base}/{folder}/{prefix}_{ep}_{sq}_{sh}_{suffix}_%04d.png"
        output_file = f"{base}/mp4/{prefix}_{ep}_{sq}_{sh}_{suffix}.mp4"

        return input_seq, output_file