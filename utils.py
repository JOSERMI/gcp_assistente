"""Utils for the app."""

import base64
import io
import mimetypes
import typing
from google.genai import types
import gradio as gr
from PIL import Image

# Google's Blue color theme
google_blue_color_hue = gr.themes.Color(
    name="google_blue",
    c50="#E8F0FE",
    c100="#D2E3FC",
    c200="#AECBFA",
    c300="#8AB4F8",
    c400="#669DF6",
    c500="#4285F4",
    c600="#1A73E8",
    c700="#1967D2",
    c800="#185ABC",
    c900="#0f172a",
    c950="#174EA6",
)

# Custom theme for the app.
"""
custom_theme = gr.themes.Default(
    primary_hue=google_blue_color_hue,
    secondary_hue=google_blue_color_hue,
    font=[gr.themes.GoogleFont("Google Sans")]
).set(
    button_cancel_background_fill="*secondary_200",
    button_cancel_background_fill_dark="*secondary_200",
    button_cancel_background_fill_hover="*secondary_300",
    button_cancel_background_fill_hover_dark="*secondary_300",
    button_cancel_text_color="black",
    button_cancel_text_color_dark="white",
)
"""
public_access_warning = """
<div style="background-color: #fffacd; border: 1px solid #eedc82; padding: 20px; margin: 20px; border-radius: 5px; color: #8b4513; font-weight: bold; text-align: center;">
  <span style="margin-right: 10px;">⚠️</span>
  Warning: This app allows unauthenticated access by default. Avoid using it for sensitive data. Access control is coming soon.
</div>"""
foto_html = """
<img src="ricardo.png" alt="Ricardo Ford" style="width: 100%; max-width: 300px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
"""
next_steps_html = """
<span><strong>Contexto:</strong></span>
<ul style="list-style-position: outside; margin-left: 1em;">
  <li>Miembros del equipo:
    <a target='_blank'
       href='https://docs.google.com/spreadsheets/d/1Ci6M2-JvwSHrAGrlVG1SzR1BrR_oveWnMBftTLuTRSw/edit?gid=0#gid=0'
    > Link </a> add / update
  </li>
  <li>Vacaciones tomadas:
    <a target='_blank'
       href='https://docs.google.com/spreadsheets/d/1Ci6M2-JvwSHrAGrlVG1SzR1BrR_oveWnMBftTLuTRSw/edit?gid=0#gid=0'
    > Link </a> add / update
  </li>
  <li>Update politicas de vacaciones:
    <a target='_blank'
       href='https://docs.google.com/document/d/1gYhSbkITCKMzh6n6Axh62bEjreyh_7xNLDRfh6umGl0/edit?tab=t.0#heading=h.qx0y8r5rt6on'
    >
        Link
    </a> add / update
  </li>
<li>Form de vacaciones:
    <a target='_blank'
       href='https://registrovacaciones-128461484764.us-central1.run.app/'
    >
        Link
    </a> add / update
  </li>
<li>Recibos de sueldos:
    <a target='_blank' href="https://getrecibosueldo-128461484764.us-central1.run.app/?dni=101&mes=2025-06">https://getrecibosueldo-128461484764.us-central1.run.app/?dni=XXXXX&mes=YYYY-MM</a>
  </li>
</ul>
"""

casos_html = """
<table border="1">
  <thead>
    <tr>
      <th>Nombre</th>
      <th>DNI</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Ricardo</td>
      <td>101</td>
    </tr>
    <tr>
      <td>Fede</td>
      <td>102</td>
    </tr>
    <tr>
      <td>Mauro</td>
      <td>103</td>
    </tr>
    <tr>
      <td>Grgich</td>
      <td>104</td>
    </tr>
  </tbody>
</table>
"""


def get_part_from_file(file):
    """Help function to get the part from a file."""
    guessed_type = mimetypes.guess_type(file)
    if guessed_type:
        mime_type = guessed_type[0]
    else:
        mime_type = "application/octet-stream"
    with open(file, "rb") as f:
        data = f.read()
        return types.Part.from_bytes(
            data=data,
            mime_type=mime_type,
        )


def get_bytes_from_image(image: Image.Image, mime_type: str = "PNG") -> bytes:
    """Converts a PIL Image object to bytes in the specified format.

    Args:
        image: The PIL Image object.
        mime_type: The image format to save as (e.g., 'PNG', 'JPEG', 'GIF').
          Defaults to 'PNG'.

    Returns:
        A bytes object representing the image in the specified format.
    """
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=mime_type)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def get_parts_from_message(
    message: typing.Union[str, tuple[str, ...], dict[str, str], gr.Image],
):
    """Help function to get the parts from a message."""

    parts = []
    if isinstance(message, dict):
        parts = []
        if "text" in message and message["text"]:
            parts.append(types.Part.from_text(text=message["text"]))

        if "files" in message:
            for file in message["files"]:
                parts.append(get_part_from_file(file))
    elif isinstance(message, str):
        if message:
            parts.append(types.Part.from_text(text=message))
    elif isinstance(message, gr.Image):
        if message.type == "pil":
            bytes_data = get_bytes_from_image(message.value)
            parts.append(
                types.Part.from_bytes(data=bytes_data, mime_type=message.format)
            )
        elif message.type == "filepath":
            parts.append(get_part_from_file(message.value))
    else:
        for part in list(message):
            if part.startswith("/tmp/gradio"):
                parts.append(get_part_from_file(part))
            elif part:
                parts.append(types.Part.from_text(text=part))

    # To avoid error when sending empty message.
    if not parts:
        parts.append(types.Part.from_text(text=" "))

    return parts


def convert_blob_to_gr_image(blob: types.Blob) -> gr.Image:
    """Converts a blob of image data to a gr.Image object."""
    blob_data = blob.data
    # Create an in-memory binary stream using io.BytesIO
    image_stream = io.BytesIO(blob_data)

    # Open the image from the stream using PIL.Image.open()
    image = Image.open(image_stream)
    return gr.Image(image)


def image_blob_to_markdown_base64(blob: types.Blob) -> str:
    """Converts image bytes to a Markdown displayable string using Base64 encoding."""
    blob_data = blob.data
    base64_string = base64.b64encode(blob_data).decode("utf-8")
    markdown_string = (
        f'<img src="data:image/{blob.mime_type};base64,{base64_string}">'  # noqa: E501
    )
    return markdown_string


def convert_part_to_gr_type(
    part: types.Part,
    use_markdown: bool = False,
) -> typing.Optional[typing.Union[str, gr.Image]]:
    """Converts a part object to a str or gr.Image object."""
    if part.text:
        return part.text
    elif part.inline_data:
        if use_markdown:
            return image_blob_to_markdown_base64(part.inline_data)
        return convert_blob_to_gr_image(part.inline_data)
    else:
        return None


def convert_content_to_gr_type(
    content: typing.Optional[types.Content],
    use_markdown: bool = False,
) -> typing.Optional[typing.Union[str, gr.Image]]:
    """Converts a content object to a gr.ChatMessage object."""
    if content is None or content.parts is None:
        return []

    results = [
        convert_part_to_gr_type(part, use_markdown) for part in content.parts
    ]
    return [res for res in results if res is not None]