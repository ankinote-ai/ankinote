"""STEM-only options of ``ankinote stem add`` / ``batch``."""

from click.testing import CliRunner

from ankinote.cli import stem


def test_add_image_reaches_the_collection(capture_options, tmp_path):
    captured = capture_options(stem)
    photo = tmp_path / "problem.jpg"
    photo.write_bytes(b"jpeg bytes")

    result = CliRunner().invoke(
        stem.stem, ["add", "Solve the problem in this photo", "--image", str(photo)]
    )

    assert result.exit_code == 0, result.output
    assert captured["note_kwargs"] == {
        "reference_image": b"jpeg bytes",
        "reference_image_mime": "image/jpeg",
    }


def test_add_without_image_sends_no_reference(capture_options):
    captured = capture_options(stem)

    result = CliRunner().invoke(stem.stem, ["add", "What is a derivative?"])

    assert result.exit_code == 0, result.output
    assert captured["note_kwargs"] == {}


def test_batch_help_has_short_file_flag_and_low_rpm_default():
    result = CliRunner().invoke(stem.stem, ["batch", "--help"])

    assert result.exit_code == 0, result.output
    assert "-f, --file" in result.output
    assert "[default: 10;" in result.output
