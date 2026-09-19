import os
import urllib.request

import truststore


# ============================================================
# AEGIE PARAKEET TDT 0.6B V2 INT8 DOWNLOADER
# ============================================================

truststore.inject_into_ssl()


MODEL_NAME = (
    "sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8"
)

URL = (
    "https://github.com/k2-fsa/sherpa-onnx/releases/"
    "download/asr-models/"
    "sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2"
)


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODELS_DIR = os.path.join(
    PROJECT_ROOT,
    "models"
)

ARCHIVE_PATH = os.path.join(
    MODELS_DIR,
    MODEL_NAME + ".tar.bz2"
)

TEMP_PATH = ARCHIVE_PATH + ".part"


def main():

    print("=" * 70)
    print("AEGIE PARAKEET TDT 0.6B V2 INT8 DOWNLOAD")
    print("=" * 70)

    os.makedirs(
        MODELS_DIR,
        exist_ok=True
    )

    print()
    print("Model:", MODEL_NAME)
    print("Destination:", ARCHIVE_PATH)

    print()
    print(
        "Using Windows trusted certificates through truststore."
    )

    print(
        "SSL verification remains enabled."
    )

    print()
    print("Downloading...")


    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent":
                "AEGIE-Research-Downloader/1.0"
        }
    )


    try:

        with urllib.request.urlopen(
            request,
            timeout=300
        ) as response:

            content_length = response.headers.get(
                "Content-Length"
            )

            expected_size = None

            if content_length:

                expected_size = int(
                    content_length
                )

                print(
                    "Expected download size:",
                    round(
                        expected_size
                        / 1024
                        / 1024,
                        2
                    ),
                    "MB"
                )


            downloaded = 0

            next_report = (
                50 * 1024 * 1024
            )


            with open(
                TEMP_PATH,
                "wb"
            ) as output:

                while True:

                    chunk = response.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    output.write(
                        chunk
                    )

                    downloaded += len(
                        chunk
                    )


                    if downloaded >= next_report:

                        print(
                            "Downloaded:",
                            round(
                                downloaded
                                / 1024
                                / 1024,
                                2
                            ),
                            "MB"
                        )

                        next_report += (
                            50 * 1024 * 1024
                        )


        # ----------------------------------------------------
        # Validate actual file size
        # ----------------------------------------------------

        size = os.path.getsize(
            TEMP_PATH
        )


        print()
        print(
            "Downloaded bytes:",
            size
        )

        print(
            "Downloaded size:",
            round(
                size
                / 1024
                / 1024,
                2
            ),
            "MB"
        )


        # ----------------------------------------------------
        # Compare with HTTP Content-Length
        # ----------------------------------------------------

        if expected_size is not None:

            if size != expected_size:

                raise RuntimeError(
                    "Downloaded size does not match "
                    "the server Content-Length. "
                    f"Expected {expected_size} bytes, "
                    f"received {size} bytes."
                )


        # ----------------------------------------------------
        # Sanity check
        #
        # Actual Parakeet archive is approximately 460 MiB.
        # ----------------------------------------------------

        if size < 400_000_000:

            raise RuntimeError(
                "Downloaded archive appears incomplete: "
                f"{size} bytes."
            )


        # ----------------------------------------------------
        # BZip2 signature
        # ----------------------------------------------------

        with open(
            TEMP_PATH,
            "rb"
        ) as file:

            signature = file.read(
                3
            )


        if signature != b"BZh":

            raise RuntimeError(
                "Downloaded file is not a valid BZip2 archive."
            )


        # ----------------------------------------------------
        # Commit validated archive
        # ----------------------------------------------------

        os.replace(
            TEMP_PATH,
            ARCHIVE_PATH
        )


        print()
        print(
            "Download completed successfully."
        )

        print(
            "Archive size:",
            round(
                os.path.getsize(
                    ARCHIVE_PATH
                )
                / 1024
                / 1024,
                2
            ),
            "MB"
        )

        print()
        print(
            "PASS: PARAKEET MODEL ARCHIVE DOWNLOADED."
        )


    except Exception as error:

        print()
        print(
            "DOWNLOAD FAILED"
        )

        print(
            "Reason:",
            error
        )


        if os.path.exists(
            TEMP_PATH
        ):

            try:

                os.remove(
                    TEMP_PATH
                )

            except Exception:

                pass


        print()
        print(
            "SSL verification was NOT disabled."
        )


    print("=" * 70)


if __name__ == "__main__":

    main()