import textwrap


def main():
    print("=== InsightFace smoke test ===")

    try:
        import insightface
        from insightface.app import FaceAnalysis
        from insightface.data import get_image as ins_get_image

        print(f"insightface version: {insightface.__version__}")

        # Use CPU provider so it runs on most machines. [web:80]
        app = FaceAnalysis(providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=0, det_size=(320, 320))

        # Use the built-in sample image "t1". [web:80][web:96]
        img = ins_get_image("t1")
        faces = app.get(img)

        print(f"Detected {len(faces)} face(s) in the sample image.")

        if faces:
            print("InsightFace appears to be installed and working correctly.")
        else:
            print(
                "InsightFace is installed, but no faces were detected in the sample image."
            )

    except ImportError as e:
        msg = textwrap.dedent(
            f"""
            Could not import InsightFace or its components.

            Error: {e}

            Make sure you have installed insightface in this environment, e.g.:

              pip install insightface onnxruntime
            """
        )
        raise SystemExit(msg)
    except Exception as e:
        msg = textwrap.dedent(
            f"""
            InsightFace smoke test ran but failed.

            Error: {e}

            This may indicate a runtime or model loading issue.
            Check your Python version, dependencies (e.g. onnxruntime),
            and any GPU/CPU provider configuration.
            """
        )
        raise SystemExit(msg)


if __name__ == "__main__":
    main()
