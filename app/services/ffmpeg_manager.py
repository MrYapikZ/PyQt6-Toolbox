from ffmpeg.asyncio import FFmpeg


class FFMPEGManager:
    @staticmethod
    async def img_to_mp4(input_sequence: str, output_file: str, start_frame: int = 101, framerate: int = 24,
                         quality: int = 15) -> bool:
        try:
            print(f"Executing FFmpeg to convert {input_sequence} to {output_file}...")

            ffmpeg = (
                FFmpeg()
                .option("y")  # overwrite output
                .input(
                    input_sequence,
                    **{"framerate": str(framerate), "start_number": str(start_frame)}
                )
                .output(
                    output_file,
                    **{"vcodec": "mpeg4", "qscale:v": str(quality), "pix_fmt": "yuv420p"}
                )
            )

            await ffmpeg.execute()
            return True

        except Exception as e:
            print(f"An error occurred while executing FFmpeg: {e}")
            return False
